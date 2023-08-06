import json
import boto3

from pyspark.sql.types import *

from ngdataenginterface.core.aws_interface import get_object_aws

"""
schema = (
    {
        "bucket_name": "",  # s3 bucket name   -   s3://ngcash-datalake-prd-repository
        "object_path": "",  # s3 object path   -   schemas/baas_pismo/transaction/creation_1.json
        "type": "",  # schema type      -   json-schema / pyspark-schema
    },
)
"""


def handle_pypspark_timestamp(pyspark_schema: StructType) -> StructType:
    """Recursive function that modifies StructType pyspark schema field to handle timestamp inconsistency when
    parsing JSON-Schema types.

    Parameters
    ----------
    pyspark_schema : StructType
        Pyspark schema

    Returns
    -------
    StructType
        the resultant schema in pyspark StructType format
    """

    def is_struct_type(field):
        return field.simpleString()[:6] == "struct"

    def is_array_type(field):
        return field.simpleString()[:5] == "array"

    # for each field in schema
    for field in pyspark_schema.fields:
        field_metadata = field.metadata
        if is_struct_type(field.dataType):
            handle_pypspark_timestamp(field.dataType)
        elif is_array_type(field.dataType):
            if is_struct_type(field.dataType.elementType):
                handle_pypspark_timestamp(field.dataType.elementType)
        # if 'format' is in field metadata key and the value is 'date-time' or 'date'
        # convert field type to TimestampType
        elif "format" in field_metadata.keys():
            field_format = field_metadata["format"]
            if field_format in ("date-time", "date"):
                field.dataType = TimestampType()
    return pyspark_schema


def retrive_schema(self: dict) -> StructType:
    """Constructs the schema from schema path information and boto3 client

    Parameters
    ----------
    self : dict
        Dictionary that contains the `bucket_name` and `object_path` of the schema

    Returns
    -------
    StructType
        the schema in pyspark StructType format
    """

    datalake_client = boto3.client("s3")

    print(f"""Bucket Name : {self["bucket_name"][5:]}""")
    print(f"""Object Path : {self["object_path"]}""")
    # get object from aws s3 bucket
    object = get_object_aws(
        datalake_client,
        self["bucket_name"][5:],
        self["object_path"],
    )

    # decode object to string
    schema_str = object.decode("utf8").replace("\n    ", "")
    # convert string to json
    schema_json = json.loads(schema_str)
    # convert pyspark json schema to pyspark struct type schema
    pyspark_schema = StructType.fromJson(schema_json)

    # handle timestamp issues in pyspark schema
    return handle_pypspark_timestamp(pyspark_schema)
