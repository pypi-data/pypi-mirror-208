import string

from pyspark.sql import DataFrame


def create_cast_field_expr(field: string, field_meta: dict):
    if field_meta["type"] == "timestamp":  # flexibility example
        return [
            f"cast (`{field_meta['name']}` as {field_meta['type']}) `{field_meta['name']}`"
        ]
    return [
        f"cast (`{field_meta['name']}` as {field_meta['type']}) `{field_meta['name']}`"
    ]


def create_convert_names_field_expr(field: string, field_meta: dict):
    return [f"`{field}` AS `{field_meta['name']}`"]


def create_drop_cols_field_expr(field: string, field_meta: dict):
    if field_meta["keep"]:
        return [f"`{field_meta['name']}`"]
    return []


FIELD_EXPR = {
    "cast_types": lambda field, field_meta: create_cast_field_expr(field, field_meta),
    "convert_names": lambda field, field_meta: create_convert_names_field_expr(
        field, field_meta
    ),
    "drop_cols": lambda field, field_meta: create_drop_cols_field_expr(
        field, field_meta
    ),
}


def generate_expr(meta: dict, step: string):
    expr = []
    for field in meta:
        for field_expr in FIELD_EXPR[step](field, meta[field]):
            expr.append(field_expr)

    print(f"Expr: {expr}")
    return expr


def convert_names(self: DataFrame, meta: dict):
    return self.selectExpr(generate_expr(meta, "convert_names"))


def cast_types(self: DataFrame, meta: dict):
    return self.selectExpr(generate_expr(meta, "cast_types"))


# def validate_uniqueness(self: DataFrame, field: string):

#     if self.groupBy(field).count().where("count > 1").count():
#         raise Exception(f"Error, pipeline with duplicate values on column {field}")


def validations(self: DataFrame, meta: dict):
    for field in meta:
        if meta[field]["validations"]:
            for transf in meta[field]["validations"]:
                self = meta[field]["validations"][transf](self, meta[field])
    return self


def transformations(self: DataFrame, meta: dict):
    for field in meta:
        if meta[field]["transformations"]:
            for transf in meta[field]["transformations"]:
                self = meta[field]["transformations"][transf](self, meta[field])
    return self


def drop_cols(self: DataFrame, meta: dict):
    return self.selectExpr(generate_expr(meta, "drop_cols"))


def data_cleansing(self: DataFrame, meta: dict):
    df = self

    print("Original Table")
    df.printSchema()
    df.show()
    print("Convert Names Table")
    df2 = df.convert_names(meta)
    df2.printSchema()
    df2.show()
    print("Transformations Table")
    df3 = df2.transformations(meta)
    df3.printSchema()
    df3.show()
    print("Cast Types Table")
    df4 = df3.cast_types(meta)
    df4.printSchema()
    df4.show()
    print("Validations and Drop Cols Table")
    df5 = df4.validations(meta).drop_cols(meta)
    df5.printSchema()
    df5.show()

    return (
        self.convert_names(meta)
        .transformations(meta)
        .cast_types(meta)
        .validations(meta)
        .drop_cols(meta)
    )


def data_modifications(self: DataFrame, meta: dict, **kwargs):
    """Modify the table getting applying functions to it

    The current table (self: DataFrame) is modified
    for each function inside meta dictionary

    Parameters
    ----------
    self : DataFrame
        Table to be modified
    meta : dict
        Table metadata that contains the modifications functions

    Returns
    -------
    DataFrame
        the table with modifications
    """
    for step in meta:
        self = step["function"](self, step["params"], **kwargs)

    return self


setattr(DataFrame, "data_modifications", data_modifications)
setattr(DataFrame, "data_cleansing", data_cleansing)
setattr(DataFrame, "convert_names", convert_names)
setattr(DataFrame, "cast_types", cast_types)
setattr(DataFrame, "transformations", transformations)
setattr(DataFrame, "validations", validations)
setattr(DataFrame, "drop_cols", drop_cols)

# setattr(DataFrame, "validate_uniqueness", validate_uniqueness)
