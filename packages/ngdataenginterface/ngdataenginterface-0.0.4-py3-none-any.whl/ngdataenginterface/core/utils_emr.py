import string
from datetime import datetime
import boto3
import boto3 as boto3
import json
import ast
import re

from pyspark import SQLContext
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.sql.functions import lit
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.types import StructType

CSV = "csv"
JSON = "json"
PARQUET = "parquet"


def get_secret(secret_name: str, region_name: str):
    """
    Retrieve a secret value from AWS Secrets Manager.

    Args:
        secret_name (str): The name or ARN of the secret.
        region_name (str): The AWS region where the secret is located.

    Returns:
        dict: The secret value as a dictionary.

    Example:
        secret = get_secret("my-secret", "us-west-2")
    """
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    # Retrieve the secret value from AWS Secrets Manager
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = get_secret_value_response["SecretString"]

    # Convert the secret string to a dictionary using ast.literal_eval
    return ast.literal_eval(secret)


def set_spark_config(name, aws_access_key_id, aws_secret_access_key):
    # Create a SparkConf object and set the application name
    config = SparkConf().setAppName(name)

    # Set the Parquet datetimeRebaseModeInRead, datetimeRebaseModeInWrite, and int96RebaseModeInWrite to "LEGACY"
    config.set("spark.sql.parquet.datetimeRebaseModeInRead", "LEGACY")
    config.set("spark.sql.parquet.datetimeRebaseModeInWrite", "LEGACY")
    config.set("spark.sql.parquet.int96RebaseModeInWrite", "LEGACY")

    # Set the packages to be used by Spark for Hadoop AWS integration
    config.set("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.1")

    # Add AWS credentials to Spark config if provided
    # This is needed when running GitLab CI or running locally
    # If the credentials are not provided, the Spark application will use the IAM role assigned to the EMR cluster
    if aws_access_key_id and aws_secret_access_key:
        config.set("spark.hadoop.fs.s3a.access.key", aws_access_key_id)
        config.set("spark.hadoop.fs.s3a.secret.key", aws_secret_access_key)

    return config


def get_pyspark_session(name, aws_access_key_id=None, aws_secret_access_key=None):
    """
    Create a PySpark session with the given name and optional AWS credentials.

    Args:
        name (str): The name of the Spark application.
        aws_access_key_id (str, optional): AWS access key ID. Defaults to None.
        aws_secret_access_key (str, optional): AWS secret access key. Defaults to None.

    Returns:
        SparkSession: The PySpark session.
    """
    # Set the Spark configuration based on the provided AWS credentials and application name
    conf = set_spark_config(name, aws_access_key_id, aws_secret_access_key)

    # Create the SparkSession using the specified configuration
    return SparkSession.builder.config(conf=conf).getOrCreate()


def handle_execution_date_args(dt: str):
    """
    Parse and handle the execution date argument.

    Args:
        dt (str): The execution date argument.

    Returns:
        datetime: The parsed execution date.

    Example:
        Input: "2022-01-01T00:00:00+0000"
        Output: datetime.datetime(2022, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
    """
    # Use regular expression to find the substring between "." and ":" (if exists)
    match = re.search(r"(?<=\.).+?(?=\:)", dt)

    if match:
        # Replace the substring found with an empty string to remove it from the input string
        dt = dt.replace(f".{match.group()[:-3]}", "")

    # Reverse split the input string by the last occurrence of ":" and join the remaining parts
    # This removes the colon in the timezone offset to make it compatible with the datetime format
    dt = "".join(dt.rsplit(":", 1))

    # Parse the modified input string into a datetime object using the specified format
    return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S%z")


def validate_uniqueness(self: DataFrame, field: str):
    """
    Validate the uniqueness of values in a DataFrame column.

    Args:
        self (DataFrame): The DataFrame to validate.
        field (str): The name of the column to check for uniqueness.

    Raises:
        Exception: If duplicate values are found in the column.

    Example:
        df = spark.createDataFrame([(1, "A"), (2, "B"), (3, "A")], ["id", "category"])
        df.validate_uniqueness("category")  # Raises an exception
    """
    # Group the DataFrame by the specified column and count the occurrences
    count_df = self.groupBy(field).count()

    # Check if there are any counts greater than 1, indicating duplicate values
    if count_df.where("count > 1").count() > 0:
        raise Exception(f"Error: Duplicate values found in column '{field}'")


def generate_select_query_from_schema(table: string, schema: StructType):
    query = f"SELECT "
    columns = schema.fieldNames()

    for column in columns:
        query += f'"{column}",'

    query = query[:-1] + f' FROM "{table}"'

    return query


def print_dictionary_readable(d: dict):
    """
    Print a dictionary in a human-readable format.

    Args:
        d (dict): The dictionary to print.

    Example:
        Input: print_dictionary_readable({'name': 'John', 'age': 30})
        Output:
        {
            "age": 30,
            "name": "John"
        }
    """
    # Convert the dictionary to a JSON string with indentation and sorted keys
    json_str = json.dumps(d, indent=4, sort_keys=True)

    # Print the JSON string
    print(json_str)


def import_from_custom_package(package_name, variable):
    """
    Import a variable from a custom package.

    Args:
        package_name (str): The name of the custom package.
        variable (str): The name of the variable to import from the package.

    Returns:
        Any: The imported variable.

    Example:
        Input: import_from_custom_package("my_package", "my_variable")
        Output: The value of my_variable imported from the my_package module.
    """
    # Import the package dynamically using the __import__ function
    # This returns the top-level module of the package
    package_module = __import__(package_name)

    # Retrieve the desired variable from the package using getattr
    imported_variable = getattr(package_module, variable)

    return imported_variable


def import_table_current_step_params(params, table, current_step):
    # importing table current step params from database params
    return params[table][current_step]
