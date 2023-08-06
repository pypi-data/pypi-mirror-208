import string
import boto3
from pyspark import SQLContext
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.types import StructType
from pyspark.sql.window import Window
from pyspark.sql.functions import col, row_number

from ngdataenginterface.core.aws_interface import list_objects_key_aws
from ngdataenginterface.core.schema import retrive_schema
from ngdataenginterface.core.partition import handle_partition_path
from ngdataenginterface.core.validations import read_input_validation

CSV = "csv"
JSON = "json"
PARQUET = "parquet"

"""
read_api_input = {
    "path": {
        "bucket_name": "",  # s3 bucket name   -   s3://ngcash-datalake-prd-trusted
        "object_path": "",  # s3 object path   -   baas_pismo/events/transaction/creation_1
        "partition": "",  # partition          -   part_year/part_month/part_day
        "file_type": "",  # file type          -   parquet
    },
    "schema": {
        "bucket_name": "",  # s3 bucket name   -   s3://ngcash-datalake-prd-repository
        "object_path": "",  # s3 object path   -   schemas/baas_pismo/transaction/creation_1.json
    },
    "meta": {
        "spark": "",  # spark session
        "date": "",  # extracting table reference date
    },
}
"""


def handle_read_input_api(read_params):
    env = read_params["env"]
    layer = read_params["layer"]
    object_path = read_params["object_path"]
    partition = read_params["partition"]
    file_type = read_params["file_type"]
    schema_path = read_params["schema_path"]

    return {
        "path": {
            "bucket_name": f"s3://ngcash-datalake-{env}-{layer}",
            "object_path": object_path,
            "partition": partition,
            "file_type": file_type,
        },
        "schema": {
            "bucket_name": f"s3://ngcash-datalake-{env}-repository",
            "object_path": schema_path,
        },
    }


def merge_tables(df1, df2, merge_params):
    partition_columns = merge_params["partition_columns"]
    order_columns = merge_params["order_columns"]
    df = df1.union(df2)
    wind = Window.partitionBy([col(x) for x in partition_columns]).orderBy(
        [col(x).desc() for x in order_columns]
    )
    df.withColumn("row_number", row_number().over(wind)).show(truncate=False)
    return (
        df.withColumn("row", row_number().over(wind))
        .filter(col("row") == 1)
        .drop("row")
    )


def check_for_new_data(self, meta):
    path_info = self["path"]
    metadata = meta

    # construct the table partition path without the bucket name
    if path_info["partition"]:
        partition_path = handle_partition_path(path_info["partition"], metadata["date"])
        path = f"""{path_info["object_path"]}/{partition_path}/"""
    else:
        path = f"""{path_info["object_path"]}/"""

    datalake_resource = boto3.resource("s3")
    print("Checking object within path: ", path)
    object_list = list_objects_key_aws(
        datalake_resource, path_info["bucket_name"][5:], path
    )
    print(f"Objects: ", object_list)
    return len(object_list) != 0


def check_aggregation_parameters_for_new_data(aggregate_parameters, execution_date):
    new_data = True
    for table_name, table_info in aggregate_parameters["tables"].items():
        new_data *= check_for_new_data(table_info, {"date": execution_date})
    return new_data


def read_data(
    spark: SparkSession,
    type_file: string,
    path,
    schema: StructType,
    header: bool = False,
):

    if type_file == CSV:

        return (
            spark.read.option("header", header)
            .format(type_file)
            .schema(schema)
            .load(path)
        )
    elif type_file == JSON:

        return spark.read.format(type_file).schema(schema).load(path)

    elif type_file == PARQUET:
        sql = SQLContext(spark)
        return sql.read.schema(schema).parquet(path)

    return spark.read.format(type_file).schema(schema).load(path)


def read_table(self: dict, schema: StructType, meta: dict) -> DataFrame:
    """Read pyspark dataframe from table information. Retrives the partition
    path (part_yar=2022,..) from current `execution_date`

    Parameters
    ----------
    table_info : dict
        Dictionary that contains the `path` and `schema` information of the table.
    schema.
    meta : dict
        Dictionary that contains additional information such as `spark` sessio, `datalake_client`,
    `execution_date`, etc.

    Returns
    -------
    DataFrame
        the pyspark dataframe
    """

    # assign self variables
    path_info = self["path"]
    metadata = meta

    # construct the table partition path
    if path_info["partition"]:
        partition_path = handle_partition_path(path_info["partition"], metadata["date"])
        path = f"""{path_info["bucket_name"]}/{path_info["object_path"]}/{partition_path}"""
    else:
        path = f"""{path_info["bucket_name"]}/{path_info["object_path"]}"""

    # read data from path and schema into a pyspark dataframe
    return read_data(
        spark=metadata["spark"],
        type_file=path_info["file_type"],
        path=path,
        schema=schema,
    )


def read(self: dict, meta: dict) -> DataFrame:
    """Read pyspark dataframe from input

    Parameters
    ----------
    self : dict
        Parameters to read pyspark dataframe from datalake

    Returns
    -------
    DataFrame
        the pyspark dataframe
    """

    # validate input
    read_input_validation(self)
    # get schema
    schema = retrive_schema(self["schema"])
    # read table
    return read_table(self, schema, meta)
