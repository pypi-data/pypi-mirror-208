import pandas as pd
from sqlalchemy import inspect, exists
from sqlalchemy.schema import CreateSchema
from sqlalchemy import Table, MetaData, select, insert, delete

from jhdata.filehelper import Files
from jhdata.data_tools.dataframes import *


def create_schema_if_not_exists(schema_name: str, filehelper=None):
    filehelper = filehelper if filehelper is not None else Files
    engine = filehelper.get_engine()
    with engine.connect() as conn:
        if schema_name not in conn.dialect.get_schema_names(conn):
            conn.execute(CreateSchema(schema_name))


def create_table_if_not_exists(table_name: str, table_schema = None, schema_name: str = None, filehelper = None):
    filehelper = filehelper if filehelper is not None else Files
    table_schema = table_schema if table_schema is not None else filehelper.read_table_schema(table_name, schema_name)
    engine = filehelper.get_engine()

    inspector = inspect(engine)

    if schema_name is not None:
        create_schema_if_not_exists(schema_name, filehelper)

    if not inspector.has_table(table_name, schema=schema_name):
        filehelper.write_sql(table_name, table_schema.make_df(), schema=schema_name)

    return Table(table_name, MetaData(engine), autoload_with=engine, schema=schema_name)


def table_exists(table_name: str, schema_name: str = None, filehelper = None):
    filehelper = filehelper if filehelper is not None else Files
    engine = filehelper.get_engine()

    inspector = inspect(engine)
    return inspector.has_table(table_name, schema=schema_name)


def upsert(update_df: pd.DataFrame, table_name: str, table_schema = None, schema_name: str = None, filehelper = None):
    filehelper = filehelper if filehelper is not None else Files
    table_schema = table_schema if table_schema is not None else filehelper.read_table_schema(table_name, schema_name)

    create_table_if_not_exists(table_name, table_schema, schema_name, filehelper)

    current_df = filehelper.read_sql_table(table_name, schema=schema_name)
    updated_df = upsert_dataframes(current_df, update_df, table_schema)

    validated_df = table_schema.validate(updated_df)

    return filehelper.write_sql(table_name, validated_df, schema=schema_name, table_schema=table_schema)


def insert_missing(update_df: pd.DataFrame, table_name: str, table_schema = None, schema_name: str = None, filehelper = None):
    filehelper = filehelper if filehelper is not None else Files
    table_schema = table_schema if table_schema is not None else filehelper.read_table_schema(table_name, schema_name)

    validated_df = table_schema.validate(update_df)

    create_table_if_not_exists(table_name, table_schema, schema_name, filehelper)

    current_df = filehelper.read_sql_table(table_name, schema=schema_name)
    insert_df = append_missing_values(current_df, validated_df, table_schema)

    return filehelper.write_sql(table_name, insert_df, schema=schema_name, table_schema=table_schema)


def delete_append(update_df: pd.DataFrame, table_name: str, table_schema = None, schema_name: str = None, filehelper = None):
    filehelper = filehelper if filehelper is not None else Files
    table_schema = table_schema if table_schema is not None else filehelper.read_table_schema(table_name, schema_name)

    validated_df = table_schema.validate(update_df)

    create_table_if_not_exists(table_name, table_schema, schema_name, filehelper)

    current_df = filehelper.read_sql_table(table_name, schema=schema_name)
    df = apply_delete_columns(current_df, validated_df, table_schema)
    df = df.append(validated_df)

    return filehelper.write_sql(table_name, df, schema=schema_name, table_schema=table_schema)


def insert_one(item: dict, table_name: str, table_schema = None, skip_if_pk_match = False, schema_name: str = None, filehelper = None):
    filehelper = filehelper if filehelper is not None else Files
    table_schema = table_schema if table_schema is not None else filehelper.read_table_schema(table_name, schema_name)

    table = create_table_if_not_exists(table_name, table_schema, schema_name, filehelper)

    if skip_if_pk_match:
        statement = exists(table)
        for key in table_schema.primary_keys:
            statement = statement.where(table.c[key] == item[key])

        statement = select(statement)
        item_exists = filehelper.sql(statement).fetchone()[0]
        if item_exists:
            return

    statement = insert(table).values(**item)

    return filehelper.sql(statement)


def overwrite_table(new_data_df: pd.DataFrame, table_name: str, schema_name: str = None, table_schema: Schema = None, filehelper = None):
    filehelper = filehelper if filehelper is not None else Files
    table_schema = table_schema if table_schema is not None else filehelper.read_table_schema(table_name, schema_name)

    validated_df = table_schema.validate(new_data_df)

    filehelper.write_sql(table_name, validated_df, table_schema, schema_name=schema_name)
