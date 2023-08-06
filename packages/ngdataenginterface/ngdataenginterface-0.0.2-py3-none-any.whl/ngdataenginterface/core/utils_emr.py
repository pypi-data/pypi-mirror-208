import string
from datetime import datetime
import boto3
import boto3 as boto3
import json
import ast
import re

from pyspark import SQLContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.types import StructType

CSV = "csv"
JSON = "json"
PARQUET = "parquet"


def get_secret(secret_name, region_name):

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = get_secret_value_response["SecretString"]
    return ast.literal_eval(secret)


def get_pyspark_session(name):

    return (
        SparkSession.builder.appName(name)
        .config("spark.sql.parquet.datetimeRebaseModeInRead", "LEGACY")
        .config("spark.sql.parquet.datetimeRebaseModeInWrite", "LEGACY")
        .config("spark.sql.parquet.int96RebaseModeInWrite", "LEGACY")
        .getOrCreate()
    )


def handle_execution_date_args(dt: string):
    match = re.search(r"(?<=\.).+?(?=\:)", dt)
    if match:
        dt = dt.replace(f".{match.group()[:-3]}", "")
    return datetime.strptime("".join(dt.rsplit(":", 1)), "%Y-%m-%dT%H:%M:%S%z")


def validate_uniqueness(self: DataFrame, field: string):

    if self.groupBy(field).count().where("count > 1").count():
        raise Exception(f"Error, pipeline with duplicate values on column {field}")


def generate_select_query_from_schema(table: string, schema: StructType):

    query = f"SELECT "
    columns = schema.fieldNames()

    for column in columns:
        query += f'"{column}",'

    query = query[:-1] + f' FROM "{table}"'

    return query


def print_dictionary_readable(d: dict):
    print(json.dumps(d, indent=4, sort_keys=True))


def import_from_custom_package(package_name, variable):
    # importing variable from custom package
    return getattr(__import__(package_name), variable)


def import_table_current_step_params(params, table, current_step):
    # importing table current step params from database params
    return params[table][current_step]
