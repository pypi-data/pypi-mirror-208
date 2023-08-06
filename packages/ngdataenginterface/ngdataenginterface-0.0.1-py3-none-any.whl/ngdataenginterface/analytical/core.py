import boto3

# from data_api.core.read import read, handle_read_input_api

from pyspark.sql.dataframe import DataFrame


# """
# aggregate_params = {
#     "tables": {
#         "name_table_1": read_api_input_1,
#         "name_table_2": read_api_input_2
#     },
#     "meta": {
#         "execution_date":,
#         "session_name":
#     },
#     "function": aggregation_function
# }
# """


# def handle_analytical_parameters(
#     spark,
#     agg_params: dict,
#     env,
#     execution_date,
#     session_name,
#     aggregation_function,
# ):
#     parameters = {"tables": {}}
#     for table_name, table_params in agg_params.items():
#         table_params["env"] = env
#         parameters["tables"][table_name] = handle_read_input_api(table_params)

#     parameters["meta"] = {
#         "spark": spark,
#         "date": execution_date,
#         "session_name": session_name,
#     }

#     parameters["function"] = aggregation_function

#     return parameters


# def handle_inputs(parameters: dict) -> dict:
#     """Read the pyspark dataframe for each table defined in parameters and
#     store them into a dictionary with the respective metadata

#     Parameters
#     ----------
#     parameters : dict
#         Dictionary that stores the parameters for the aggregation.  It contains information
#     of each parent table (bucket_name, object_path, schema and metadata).

#     Returns
#     -------
#     dict
#         dictionary with all pyspark dataframe that will be used in aggregation
#     """

#     # initialize inputs
#     inputs = {}

#     # for each table, read pyspark table and store the respective metadata
#     for table_name, table_info in parameters["tables"].items():
#         inputs[table_name] = {}
#         inputs[table_name]["df"] = read(table_info, parameters["meta"])

#     return inputs


# def analytical(parameters: dict, **kwargs) -> DataFrame:
#     """Create an analytical DataFrame from other DataFrames especified in `parameters`

#     Parameters
#     ----------
#     parameters : dict
#         Dictionary that stores the parameters for the aggregation.  It contains information
#     of each parent table (bucket_name, object_path, schema and metadata).

#     Returns
#     -------
#     DataFrame
#         the resulting analytical pyspark dataframe
#     """

#     # construct aggregation inputs from parameters
#     inputs = handle_inputs(parameters)

#     # construct resultant dataframe from input and metadata
#     return parameters["function"](inputs, parameters["meta"])
