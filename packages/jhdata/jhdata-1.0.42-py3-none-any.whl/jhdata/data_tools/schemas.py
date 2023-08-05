import json
import pandas as pd
from pandera.io import from_json as pandera_from_json

"""
Schema formats:

Field: dict
{
    "name": "firstname",
    "dtype": "string",
    "primary": False,
    "nullable": True
}

Schema format: dict

{
    version: "1",
    fields: Field[]
}

Some notes: SQLAlchemy only references precision and length when creating tables: https://docs.sqlalchemy.org/en/14/core/tutorial.html

"""


class SchemaException(Exception):
    pass


class Schema:
    def __init__(self, schema_dict: dict, validate=True):
        if "pandera" not in schema_dict:
            print(json.dumps(schema_dict, indent=4))
            raise SchemaException("No pandera schema in schema dict")

        self.pandera = pandera_from_json(json.dumps(schema_dict["pandera"]))
        self.primary_keys = schema_dict.get("primary_keys", [])
        self.delete_columns = schema_dict.get("delete_columns", [])

        if validate:
            self.validate_self()

    def to_json(self):
        schema_dict = {
            "primary_keys": self.primary_keys,
            "delete_columns": self.delete_columns,
            "pandera": self.pandera.to_json()
        }

        return json.dumps(schema_dict, indent=4)

    def __str__(self):
        return self.to_json()

    def make_df(self):
        return pd.DataFrame({key: pd.Series(dtype=dtype) for key, dtype in self.dtype_dict.items()})

    @property
    def column_names(self):
        return [col for col in self.pandera.columns]

    @property
    def required_column_names(self):
        return [col for col in self.pandera.columns if col.required]

    @property
    def dtype_dict(self):
        return {key: str(dtype) for key, dtype in self.pandera.dtypes.items()}

    def validate_self(self):
        has_deletes = len(self.delete_columns) > 0
        has_pks = len(self.primary_keys) > 0

        if has_deletes and has_pks:
            raise SchemaException("Schema can only have one of delete columns or primary keys")

    def validate(self, df: pd.DataFrame):
        if self.pandera.coerce:
            df = self.reorder_columns(df)

        return self.pandera.validate(df)

    def reorder_columns(self, df: pd.DataFrame):
        return df[self.column_names]
