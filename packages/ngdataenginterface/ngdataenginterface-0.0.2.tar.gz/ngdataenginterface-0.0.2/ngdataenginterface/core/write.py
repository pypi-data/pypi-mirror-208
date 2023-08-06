# import base packages
import boto3

# import pyspark packages
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import lit

# import custom packages
from ngdataenginterface.core.partition import handle_partition_path
from ngdataenginterface.core.aws_interface import delete_objects_aws, put_object_aws

# structure that maps the partition name to the function
# that retrives the partition value from datetime
PARTITION_MAP = {
    "part_year": lambda dt: dt.strftime("%Y"),
    "part_month": lambda dt: dt.strftime("%m"),
    "part_day": lambda dt: dt.strftime("%d"),
    "part_hour": lambda dt: dt.strftime("%H"),
}

"""
write_api_input = {
    "write": {
        "bucket_name": "s3://ngcash-datalake-dev-trusted",
        "object_path": "aggregated/financial",
        "partition": "part_year/part_month/part_day",
        "file_type": "parquet",
    }
    
}
"""


def handle_write_input_api(write_params):
    env = write_params["env"]
    layer = write_params["layer"]
    object_path = write_params["object_path"]
    partition = write_params["partition"]
    file_type = write_params["file_type"]
    schema_path = write_params["schema_path"]

    return {
        "write": {
            "bucket_name": f"s3://ngcash-datalake-{env}-{layer}",
            "object_path": object_path,
            "partition": partition,
            "file_type": file_type,
        },
        "schema": {
            "bucket_name": f"s3://ngcash-datalake-{env}-repository",
            "schema_path": schema_path,
        },
    }


def delete_table_to_overwrite(self, meta):
    """Delete all files under certain path in aws s3 bucket

    Parameters
    ----------
    parameters : dict
        Dictionary that stores the parameters for the aggregation.  It contains information
    of the writting path of the aggregation table, such as the bucket_name and the object_path.

    Returns
    -------
    None

    """
    write_info = self["write"]

    # skip overwriting if metadata contains this indicator
    if "overwrite" in meta:
        if meta["overwrite"] == False:
            return

    datalake_resource = boto3.resource("s3")

    if write_info["partition"]:
        partition_path = handle_partition_path(write_info["partition"], meta["date"])
        path = f"{write_info['object_path']}/{partition_path}"
    else:
        path = f"{write_info['object_path']}"

    delete_objects_aws(datalake_resource, write_info["bucket_name"][5:], path)

    return


def write_table(self: dict, df: DataFrame, meta):
    """Write aggregated dataframe in S3 bucket accordingly to parameters write path

    Parameters
    ----------
    df: DataFrame
        Resultant Aggregated DataFrame
    parameters : dict
        Dictionary that stores the parameters for the aggregation.  It contains information
    of the writting path of the aggregation table, such as the bucket_name and the object_path.

    Returns
    -------
    None

    """
    write_info = self["write"]

    # dataframe saving location in s3
    path = f"""{write_info["bucket_name"]}/{write_info["object_path"]}"""

    # gets every partition from partition string
    partitions = write_info["partition"].split("/")

    # conditional to verify if it should save table partitioned
    if partitions != [""]:
        for part in partitions:
            # add the partition column in the table
            df = df.withColumn(part, lit(PARTITION_MAP[part](meta["date"])))
        # write table partitioned
        df.write.partitionBy(partitions).mode("append").format(
            write_info["file_type"]
        ).save(path)
    else:
        # write table without partition
        df.write.mode("append").format(write_info["file_type"]).save(path)

    return


def write_schema(self: dict, df: DataFrame):
    ngcash_client = boto3.client("s3")

    write_schema_info = self["schema"]

    pyspark_schema = df.schema.jsonValue()

    put_object_aws(
        ngcash_client,
        write_schema_info["bucket_name"][5:],
        write_schema_info["schema_path"],
        pyspark_schema,
    )
    return


def write(self: dict, df: DataFrame, meta) -> None:
    # deleting destination path
    delete_table_to_overwrite(self, meta)
    # writing df table
    write_table(self, df, meta)
    # write df schema in s3 schemas repository
    write_schema(self, df)
    return
