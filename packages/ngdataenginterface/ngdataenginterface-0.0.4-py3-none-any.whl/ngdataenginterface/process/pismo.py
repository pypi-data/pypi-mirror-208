import boto3, json
import string
from datetime import datetime

from pyspark.sql.types import *
from pyspark.sql.window import Window
from pyspark.sql.functions import col, row_number
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import lit

# Import Custom Packages
from ngdataenginterface.core.utils_emr import (
    get_secret,
)
from ngdataenginterface.core.aws_interface import get_object_aws


def write_file(
    df: DataFrame, path: string, type_file: string, execution_date: datetime
):

    year = execution_date.strftime("%Y")
    month = execution_date.strftime("%m")
    day = execution_date.strftime("%d")

    print(f"Writing partition {year} - {month} - {day}")

    df.withColumn("part_year", lit(year)).withColumn(
        "part_month", lit(month)
    ).withColumn("part_day", lit(day)).write.partitionBy(
        "part_year", "part_month", "part_day"
    ).mode(
        "append"
    ).format(
        type_file
    ).save(
        path
    )

    return


def write_file_without_partition(df: DataFrame, path: string, type_file: string):

    df.write.mode("append").format(type_file).save(path)

    return


def get_year_month_day(execution_date):
    year = execution_date.strftime("%Y")
    month = execution_date.strftime("%m")
    day = execution_date.strftime("%d")
    return year, month, day


def get_ngcash_client(pismo_integration_secret_arn, ngcash_pismo_role_arn):
    pismo_integration_secret = get_secret(
        pismo_integration_secret_arn,
        "us-east-1",
    )

    pismo_integration_client = boto3.client(
        "sts",
        aws_access_key_id=pismo_integration_secret["aws_access_key_id"],
        aws_secret_access_key=pismo_integration_secret["aws_secret_access_key"],
    )

    pismo_integration_credentials = pismo_integration_client.assume_role(
        RoleArn=ngcash_pismo_role_arn, RoleSessionName="NGCASHPismoRole"
    )

    ACCESS_KEY = pismo_integration_credentials["Credentials"]["AccessKeyId"]
    SECRET_KEY = pismo_integration_credentials["Credentials"]["SecretAccessKey"]
    SESSION_TOKEN = pismo_integration_credentials["Credentials"]["SessionToken"]

    ngcash_session = boto3.Session(
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        aws_session_token=SESSION_TOKEN,
    )

    return ngcash_session.client("sts")


def start_pismo_session(
    pismo_integration_secret_arn, ngcash_pismo_role_arn, pismo_role_arn
):
    ngcash_client = get_ngcash_client(
        pismo_integration_secret_arn, ngcash_pismo_role_arn
    )
    # assuming Pismo role
    pismo_credentials = ngcash_client.assume_role(
        RoleArn=pismo_role_arn,
        RoleSessionName="PismoAWSRole",
    )
    ACCESS_KEY = pismo_credentials["Credentials"]["AccessKeyId"]
    SECRET_KEY = pismo_credentials["Credentials"]["SecretAccessKey"]
    SESSION_TOKEN = pismo_credentials["Credentials"]["SessionToken"]
    pismo_session = boto3.Session(
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        aws_session_token=SESSION_TOKEN,
    )
    return pismo_session


def get_domain_event_type(event_type_path, i, j):
    schema_path = "/".join(event_type_path.split("/")[i:j])
    return schema_path.replace("-", "_")


def get_path(ngcash_bucket, writting_path, event_table_path, i, j):
    return (
        ngcash_bucket
        + "/"
        + writting_path
        + get_domain_event_type(event_table_path, i, j)
    )


def save_event_table(
    ngcash_bucket, df, writting_path, event_table_path, file_type, execution_date, i, j
):
    path = get_path(ngcash_bucket, writting_path, event_table_path, i, j)
    print("Writting in path:", path)
    write_file(df, path, file_type, execution_date)


def save_event_table_without_partition(
    ngcash_bucket, df, writting_path, event_table_path, file_type, i, j
):
    path = get_path(ngcash_bucket, writting_path, event_table_path, i, j)
    print("Writting in path:", path)
    write_file_without_partition(df, path, file_type)


def get_pyspark_schema_path(event_type_path, i, j):
    schema_path = get_domain_event_type(event_type_path, i, j)
    return schema_path + ".json"


def get_pyspark_schema(
    datalake_client,
    ngcash_repository_bucket,
    default_schema_path,
    event_type_path,
    i,
    j,
):
    pyspark_schema_path = get_pyspark_schema_path(event_type_path, i, j)
    print("Bucket: ", ngcash_repository_bucket)
    print("Key: ", default_schema_path + pyspark_schema_path)
    object = get_object_aws(
        datalake_client,
        ngcash_repository_bucket,
        default_schema_path + pyspark_schema_path,
    )
    pyspark_schema_str = object.decode("utf8").replace("\n    ", "")
    pyspark_schema_json = json.loads(pyspark_schema_str)
    return StructType.fromJson(pyspark_schema_json)


def list_event_tables(datalake_client, ngcash_landing_bucket, events_path):
    events = []
    domain_results = datalake_client.list_objects(
        Bucket=ngcash_landing_bucket, Prefix=events_path, Delimiter="/"
    )
    if domain_results.get("CommonPrefixes"):
        for domain in domain_results.get("CommonPrefixes"):
            event_type_results = datalake_client.list_objects(
                Bucket=ngcash_landing_bucket, Prefix=domain.get("Prefix"), Delimiter="/"
            )
            print("Domain: ", domain.get("Prefix"))
            for event_type in event_type_results.get("CommonPrefixes"):
                print("Event type:", event_type.get("Prefix"))
                events.append(event_type.get("Prefix"))
    return events


def handle_pypspark_timestamp(pyspark_schema):
    def is_struct_type(field):
        return field.simpleString()[:6] == "struct"

    def is_array_type(field):
        return field.simpleString()[:5] == "array"

    for field in pyspark_schema.fields:
        field_metadata = field.metadata
        print(field.dataType.simpleString())
        if is_struct_type(field.dataType):
            handle_pypspark_timestamp(field.dataType)
        elif is_array_type(field.dataType):
            if is_struct_type(field.dataType.elementType):
                handle_pypspark_timestamp(field.dataType.elementType)
        elif "format" in field_metadata.keys():
            field_format = field_metadata["format"]
            if field_format in ("date-time", "date"):
                field.dataType = TimestampType()
    return pyspark_schema


def force_uniqueness_from_field(df, unique_field: str):
    wind = Window.partitionBy(unique_field).orderBy(col("event_id").desc())
    return (
        df.withColumn("row", row_number().over(wind))
        .filter(col("row") == 1)
        .drop("row")
    )


def get_partition_path_from_execution_date(execution_date):
    year, month, day = get_year_month_day(execution_date)
    return f"part_year={year}/part_month={month}/part_day={day}/"
