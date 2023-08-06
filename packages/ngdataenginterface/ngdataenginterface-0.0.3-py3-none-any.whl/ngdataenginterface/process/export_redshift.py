from pyspark.sql.types import (
    StructType,
)


def generate_redshift_TableColumnTypes(meta: dict):
    print(meta)
    column_types = ""
    for field in meta:
        print(f"{meta} -> {field}")
        field_name = field.lower()
        redshift_type = meta[field]["redshift_type"]
        column_types += f"{field_name} {redshift_type}, "

    print(column_types[0:-1])
    return column_types[0:-2]
