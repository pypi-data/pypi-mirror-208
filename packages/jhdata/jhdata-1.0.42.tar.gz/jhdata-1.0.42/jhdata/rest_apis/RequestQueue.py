import copy
from sqlalchemy import MetaData, select, delete, update

from jhdata.filehelper import *
from jhdata.data_tools.database import create_table_if_not_exists, insert_missing, insert_one
from jhdata.dates import current_timestamp


class RequestQueue:
    def __init__(self, table_name: str, schema: str = "request_queues", filehelper: FileHelper = None):
        self.table_name = table_name
        self.schema = schema
        self.filehelper = filehelper if filehelper is not None else Files
        self.meta = MetaData(self.filehelper.get_engine())
        self.sleep_duration = 3
        self.retries = 2
        self.request_queue_schema = self.filehelper.read_schema("request_queue")

        # make sure the table exists
        self.get_table()

    def get_table(self):
        return create_table_if_not_exists(self.table_name, self.request_queue_schema, self.schema, self.filehelper)

    def fetch_one(self, use_secrets=True):
        table = self.get_table()
        statement = (
            select(table)
            .where(table.c.failed == False)
            .order_by(
                table.c.priority.desc(),
                table.c.requested_at.desc()
            )
        )

        row = self.filehelper.sql(statement).first()

        if row is None:
            return None, None
        else:
            # Convert to dict to allow assignment later
            row = {key: row[key] for key in row.keys()}
            # Copy row to be able to mark it as done later
            row_raw = copy.deepcopy(row)
            # Substitute secret values and load JSON
            if use_secrets:
                row["metadata"] = self.filehelper.secrets.substitute(row["metadata"])

            row["metadata"] = json.loads(row["metadata"])
            return row, row_raw

    def mark_as_done(self, row: dict):
        table = self.get_table()
        statement = delete(table)

        for key in row.keys():
            statement = statement.where(table.c[key] == row[key])

        return self.filehelper.sql(statement)

    def mark_as_failed(self, row: dict, reason: str = "Failed"):
        table = self.get_table()
        statement = update(table)

        for key in row.keys():
            statement = statement.where(table.c[key] == row[key])

        statement = statement.values(
            failed=True,
            fail_reason=reason
        )

        return self.filehelper.sql(statement)

    def insert_many(self, items):
        DF_THRESHOLD = 10

        print(items[:3])
        items_parsed = [{
            "table_name": item["table_name"],
            "metadata": json.dumps(item["metadata"]),
            "priority": item["priority"],
            "failed": False,
            "requested_at": current_timestamp()
        } for item in items]

        if len(items_parsed) < DF_THRESHOLD:
            for item in items_parsed:
                item["failed"] = False

                insert_one(
                    item,
                    self.table_name,
                    schema_name=self.schema,
                    table_schema=self.request_queue_schema,
                    skip_if_pk_match=True
                )
        else:
            self.filehelper.logger.info(f"Queuing in bulk {len(items_parsed)} items")
            item_df = pd.DataFrame(items_parsed)
            insert_missing(item_df, self.table_name, schema_name=self.schema, table_schema=self.request_queue_schema)

    def insert_one(self, table_name: str, metadata: dict, priority: int = 0):
        return self.insert_many([
            {
                "table_name": table_name,
                "metadata": metadata,
                "priority": priority,
                "failed": False,
                "requested_at": current_timestamp()
            }
        ])


class RequestException(Exception):
    pass


class TooManyRequestsException(RequestException):
    pass


class QueueExecutionException(Exception):
    pass
