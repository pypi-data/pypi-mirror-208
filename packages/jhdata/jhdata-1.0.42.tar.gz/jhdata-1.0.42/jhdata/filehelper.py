import io
import os
import re
import datetime

import requests
import boto3
import s3fs
import sqlalchemy

from jhdata.logger import *
from jhdata.data_tools.schemas import *
from jhdata.secrets import SecretInterfaceMemory
from jhdata.dates import DateFormats

"""
Useful stuff:
JSON schemas: https://specs.frictionlessdata.io/table-schema/#types-and-formats
"""


class FileHelper:
    def __init__(self, bucket_name: str = None, logger: Logger = None, environment: str = None, engine = None, secrets = None):
        self.environment = environment if environment else os.getenv("ENVIRONMENT", "dev")
        self.bucket_name = bucket_name if bucket_name else self.environment
        self.logger = logger if logger else Logger()
        self.engine = engine
        self.fs = None
        self.boto = None
        self.secrets = secrets if secrets is not None else SecretInterfaceMemory()

    def set_engine(self, engine):
        self.engine = engine

    def get_engine(self):
        if isinstance(self.engine, sqlalchemy.engine.Engine):
            return self.engine
        else:
            print(self.engine)
            raise Exception("No database engine defined, use connect_db() first")

    def connect_db(self, connection_string: str, **kwargs):
        self.set_engine(sqlalchemy.create_engine(connection_string, **kwargs))
        return self.get_engine()

    def connect_s3(self,
                   endpoint_url: str,
                   aws_access_key_id: str,
                   aws_secret_access_key: str,
                   aws_session_token: str = None):
        s3fs_config = {
            "anon": False,
            "key": aws_access_key_id,
            "secret": aws_secret_access_key,
            "token": aws_session_token,
            "use_ssl": False,
            "client_kwargs": {
                "endpoint_url": endpoint_url,
            }
        }

        boto3_config = {
            "service_name": "s3",
            "endpoint_url": endpoint_url,
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "aws_session_token": aws_session_token,
            "verify": True
        }

        self.fs = s3fs.S3FileSystem(**s3fs_config)
        self.boto = boto3.resource(**boto3_config)

        self.logger.info("Connected to s3")

        return self.fs, self.boto

    @property
    def bucket(self):
        if self.boto is None:
            raise Exception("No connection established, call connect_s3() first")

        return self.boto.Bucket(self.bucket_name)

    def sql(self, statement, **kwargs):
        with self.get_engine().connect() as connection:
            with connection.begin():
                return connection.execute(statement, **kwargs)

    # Get path for s3fs
    def fspath(self, path: str):
        return f"{self.bucket_name}/{path}"

    # Removes the bucket name from the path if present, leaves it unmodified otherwise
    def safe_path(self, path: str):
        bucket_prefix = f"{self.bucket_name}/"
        if path.startswith(bucket_prefix):
            return path[len(bucket_prefix):]
        else:
            return path

    def metadata(self, path: str):
        return self.fs.metadata(self.fspath(path))

    # Last modified as datetime
    def last_modified(self, path: str) -> datetime.datetime:
        return self.boto.Object(self.bucket_name, path).last_modified.strftime(DateFormats.datetime)

    # Check if path is a directory
    def is_directory(self, path: str) -> bool:
        return self.fs.isdir(self.fspath(path))

    # Check if a path exists
    def path_exists(self, path: str) -> bool:
        return self.fs.exists(self.fspath(path))

    # Check if a path exists and is a directory
    def directory_exists(self, path: str) -> bool:
        return self.path_exists(path) and self.is_directory(path)

    # Check if a path exists and is a file
    def file_exists(self, path: str) -> bool:
        return self.path_exists(path) and not self.is_directory(path)

    def find(self, path: str, **kwargs):
        return [self.safe_path(obj.key) for obj in self.bucket.objects.filter(Prefix=path, **kwargs)]

    def ls(self, path: str, **kwargs):
        return self.find(path, **kwargs)

    def find_regex(self, path: str, regex: str, **kwargs):
        files = self.find(path, **kwargs)
        results = []

        for file in files:
            filename = file.split("/")[-1]
            match = re.search(regex, filename)
            if match is not None:
                results.append((file, match.groupdict()))

        return results

    # Generate an URL to access a file
    def url(self, path: str, **kwargs):
        return self.fs.url(path=self.fspath(path), **kwargs)

    # Move file
    def move(self, path_from: str, path_to: str, recursive: bool = False):
        self.fs.move(self.fspath(path_from), self.fspath(path_to), recursive=recursive)

    # Copy file
    def copy(self, path_from: str, path_to: str, recursive: bool = False):
        self.fs.copy(self.fspath(path_from), self.fspath(path_to), recursive=recursive)

    # Delete file
    def delete(self, path: str, recursive: bool = False):
        self.fs.rm(self.fspath(path))

    # Get a readable file object
    def get_readable(self, path: str):
        return self.fs.open(self.fspath(path))

    # Get a readable file object
    def get_readable_bytes(self, path: str):
        return self.fs.open(self.fspath(path), "rb")

    # Get a writeable file object
    def get_writeable(self, path: str):
        return self.fs.open(self.fspath(path), "w")

    # Get a writeable file object
    def get_writeable_bytes(self, path: str):
        return self.fs.open(self.fspath(path), "wb")

    # Download a file into a ByteIO object
    def read_byteio(self, path: str):
        output = io.BytesIO()
        self.boto.Bucket(self.bucket_name).download_fileobj(Key=path, Fileobj=output)
        return output

    # Download file content as bytes
    def read_bytes(self, path: str):
        output = self.read_byteio(path)
        return output.getvalue()

    # Upload bytes into a file
    def write_bytes(self, path: str, data: bytes):
        self.logger.info(f"[{self.bucket_name}] Uploading bytes to {path}")
        result = self.boto.Bucket(self.bucket_name).put_object(Key=path, Body=data)
        return result

    # Download a file from an URL to bucket using HTTP
    def download_file(self, url: str, to_path: str, **kwargs):
        self.logger.info(f"[{self.bucket_name}] Reading file bytes from {url}")
        response = requests.get(url=url, **kwargs)
        self.write_bytes(to_path, response.content)

    # Download file content as text
    def read_text(self, path: str, encoding: str = "utf8"):
        byte_content = self.read_bytes(path)
        return byte_content.decode(encoding)

    # Upload text into a file
    def write_text(self, path: str, text: str, encoding: str = "utf8"):
        self.logger.info(f"[{self.bucket_name}] Uploading text to {path}")
        result = self.boto.Bucket(self.bucket_name).put_object(Key=path, Body=text.encode(encoding))
        return result

    def read_json_content(self, path: str, encoding: str = "utf8"):
        byte_content = self.read_bytes(path)
        text_content = byte_content.decode(encoding)
        return json.loads(text_content)

    # Read a JSON file into a Pandas DataFrame
    def read_json(self, path: str, schema: Schema = None, **kwargs):
        if isinstance(schema, Schema):
            return pd.read_json(self.get_readable(path), dtype=schema.dtype_dict, **kwargs)
        elif schema is None:
            return pd.read_json(self.get_readable(path), **kwargs)
        else:
            raise SchemaException("Expected an instance of Schema, got", schema)

    def json_normalize(self, data: list, **kwargs):
        return pd.json_normalize(data, **kwargs)

    # Write to a JSON file
    def write_json(self, path: str, df: pd.DataFrame, **kwargs):
        return df.to_json(self.get_writeable(path), **kwargs)

    # Read a Parquet file into a Pandas DataFrame
    def read_parquet(self, path: str, table_schema: Schema = None, **kwargs):
        return pd.read_parquet(self.get_readable(path), **kwargs)

    # Write to a parquet file
    def write_parquet(self, path: str, df: pd.DataFrame, **kwargs):
        return df.to_parquet(self.get_writeable_bytes(path), **kwargs)

    # Read a SQL table into a DataFrame
    def read_sql(self, table_name: str, table_schema: Schema = None, **kwargs):
        engine = self.get_engine()
        return pd.read_sql(table_name, engine, **kwargs)

    # Read a SQL table into a DataFrame
    def read_sql_table(self, table_name: str, table_schema: Schema = None, **kwargs):
        with self.get_engine().begin() as conn:
            return pd.read_sql_table(table_name, conn, **kwargs)

    # Read a CSV file into a dataframe
    def read_csv(self, path: str, **kwargs):
        return pd.read_csv(self.get_readable(path), **kwargs)

    # Write to a parquet file
    def write_csv(self, path: str, df: pd.DataFrame, table_schema = None, **kwargs):
        if isinstance(table_schema, Schema):
            df = table_schema.validate(df)
        elif table_schema is not None:
            raise SchemaException("Expected an instance of Schema, got", table_schema)

        return df.to_csv(self.get_writeable_bytes(path), **kwargs)

    # Write a DataFrame into a SQL table
    def write_sql(self, table_name: str, df: pd.DataFrame, table_schema: Schema = None, if_exists="replace", index=False, **kwargs):
        engine = self.get_engine()
        result = df.to_sql(table_name, engine, if_exists=if_exists, index=index, **kwargs)
        self.logger.success(f"Wrote to table {table_name} - result: {result}")

    # Read schema from disk
    def read_schema(self, path: str):
        try:
            schema_dict = json.loads(self.read_text(f"schemas/{path}.json"))
            return Schema(schema_dict)
        except Exception as e:
            raise Exception(f"Unable to load schema from {path}: {e}")


    # Read schema from default location for a SQL table
    def read_table_schema(self, table_name: str, schema_name: str = None):
        if schema_name is None:
            return self.read_schema(table_name)
        else:
            return self.read_schema(f"{schema_name}/{table_name}")

    # Write schema to disk
    def write_schema(self, path: str, schema: Schema):
        schema_string = schema.to_json()
        self.write_text(f"schemas/{path}.json", schema_string)


Files = FileHelper()
