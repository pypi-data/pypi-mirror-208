import warnings
import functools

import pyspark.sql

from pandera.errors import SchemaError
from typing import List, Type
from pandera.api.pyspark.types import PysparkDefaultTypes


def register_input_datatypes(
    acceptable_datatypes: List[Type[PysparkDefaultTypes]] = None,
):
    """
    This decorator is used to register the input datatype for the check.
    An Error would br raised in case the type is not in the list of acceptable types.

    :param acceptable_datatypes: List of pyspark datatypes for which the function is applicable
    """

    def wrapper(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            # Get the pyspark object from arguments
            pyspark_object = [a for a in args][0]
            validation_df = pyspark_object.dataframe
            validation_column = pyspark_object.column_name
            pandera_schema_datatype = validation_df.pandera.schema.get_dtypes(
                validation_df
            )[validation_column].type.typeName
            # Type Name of the valid datatypes needed for comparison  to remove the parameterized values since
            # only checking type not the parameters
            valid_datatypes = [i.typeName for i in acceptable_datatypes]
            current_datatype = (
                validation_df.select(validation_column)
                .schema[0]
                .dataType.typeName
            )
            if pandera_schema_datatype != current_datatype:
                raise SchemaError(
                    schema=validation_df.pandera.schema,
                    data=validation_df,
                    message=f'The check with name "{func.__name__}" only accepts the following datatypes \n'
                    f"{[i.typeName() for i in acceptable_datatypes]} but got {current_datatype()} from the input. \n"
                    f" This error is usually caused by schema mismatch of value is different from schema defined in"
                    f" pandera schema",
                )
            if current_datatype in valid_datatypes:
                return func(*args, **kwargs)
            else:
                raise TypeError(
                    f'The check with name "{func.__name__}" only supports the following datatypes '
                    f'{[i.typeName() for i in acceptable_datatypes]} and not the given "{current_datatype()}" '
                    f"datatype"
                )

        return _wrapper

    return wrapper


def validate_params(params, scope):
    def _wrapper(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if scope == "SCHEMA":
                if (params["DEPTH"] == "SCHEMA_AND_DATA") or (
                    params["DEPTH"] == "SCHEMA_ONLY"
                ):
                    return func(self, *args, **kwargs)
                else:
                    warnings.warn(
                        "Skipping Execution of function as parameters set to DATA_ONLY "
                    )
                    if not kwargs:
                        for key, value in kwargs.items():
                            if isinstance(value, pyspark.sql.DataFrame):
                                return value
                    if args:
                        for value in args:
                            if isinstance(value, pyspark.sql.DataFrame):
                                return value

            elif scope == "DATA":
                if (params["DEPTH"] == "SCHEMA_AND_DATA") or (
                    params["DEPTH"] == "DATA_ONLY"
                ):
                    return func(self, *args, **kwargs)
                else:
                    warnings.warn(
                        "Skipping Execution of function as parameters set to SCHEMA_ONLY "
                    )

        return wrapper

    return _wrapper
