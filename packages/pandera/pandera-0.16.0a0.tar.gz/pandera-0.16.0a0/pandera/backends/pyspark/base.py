"""pyspark Parsing, Validation, and Error Reporting Backends."""

import warnings
from typing import (
    Any,
    Dict,
    FrozenSet,
    Iterable,
    List,
    NamedTuple,
    Optional,
    TypeVar,
    Union,
)

from pyspark.sql import DataFrame
from pyspark.sql.functions import col

from pandera.backends.base import BaseSchemaBackend
from pandera.backends.pyspark.error_formatters import (  # format_vectorized_error_message,; consolidate_failure_cases,; summarize_failure_cases,; reshape_failure_cases,
    format_generic_error_message,
    scalar_failure_case,
)
from pandera.backends.pyspark.utils import ConfigParams
from pandera.errors import FailureCaseMetadata, SchemaError


class ColumnInfo(NamedTuple):
    """Column metadata used during validation."""

    sorted_column_names: Iterable
    expanded_column_names: FrozenSet
    destuttered_column_names: List
    absent_column_names: List
    lazy_exclude_column_names: List


FieldCheckObj = Union[col, DataFrame]

T = TypeVar(
    "T",
    col,
    DataFrame,
    FieldCheckObj,
    covariant=True,
)


class PysparkSchemaBackend(BaseSchemaBackend):
    """Base backend for pyspark schemas."""

    try:
        params = ConfigParams("pyspark", "parameters.yaml")
    except Exception as err:
        raise err

    def subsample(
        self,
        check_obj: DataFrame,
        sample: Optional[float] = None,
        seed: Optional[int] = None,
    ):
        if sample is not None:
            return check_obj.sample(
                withReplacement=False, fraction=sample, seed=seed
            )
        return check_obj

    def run_check(
        self,
        check_obj,
        schema,
        check,
        check_index: int,
        *args,
    ) -> bool:
        """Handle check results, raising SchemaError on check failure.

        :param check_index: index of check in the schema component check list.
        :param check: Check object used to validate pyspark object.
        :param check_args: arguments to pass into check object.
        :returns: True if check results pass or check.raise_warning=True, otherwise
            False.
        """

        check_result = check(check_obj, *args)
        if not check_result.check_passed:
            if check_result.failure_cases is None:
                # encode scalar False values explicitly
                failure_cases = scalar_failure_case(check_result.check_passed)
                error_msg = format_generic_error_message(schema, check)

            # raise a warning without exiting if the check is specified to do so
            if check.raise_warning:
                warnings.warn(error_msg, UserWarning)
                return True

            raise SchemaError(
                schema,
                check_obj,
                error_msg,
                failure_cases=failure_cases,
                check=check,
                check_index=check_index,
                check_output=check_result.check_output,
            )
        return check_result.check_passed

    def failure_cases_metadata(
        self,
        schema_name: str,
        schema_errors: List[Dict[str, Any]],
    ) -> FailureCaseMetadata:
        """Create failure cases metadata required for SchemaErrors exception."""

        return FailureCaseMetadata(
            failure_cases=None,
            message=schema_errors,
            error_counts=None,
        )
