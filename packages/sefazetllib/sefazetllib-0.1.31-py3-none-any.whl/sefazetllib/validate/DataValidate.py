from typing import Any, List, Optional

from pydeequ.checks import Check, CheckLevel
from pydeequ.verification import VerificationResult, VerificationSuite
from pyspark.sql import Row

from sefazetllib import Builder, field
from sefazetllib.factory.platform.dataframe.Default import Default
from sefazetllib.factory.platform.Platform import Platform
from sefazetllib.validate.Validate import Validate


@Builder
class DataValidate(Validate):
    df: Optional[Any] = None
    check: Optional[Any] = None
    check_name: str = field(default="")
    custom_check: List[dict] = field(default_factory=list)
    reference: str = field(default="")
    output: str = field(default="")
    platform: Platform = field(default=Default())
    table_validation: dict = field(default_factory=dict)
    column_validation: dict = field(default_factory=dict)

    def __get_lambda_assert(self, operator, value):
        return {
            "gt": lambda x: x > value,
            "gte": lambda x: x >= value,
            "lw": lambda x: x < value,
            "lwe": lambda x: x <= value,
            "e": lambda x: x == value,
        }[operator]

    def __set_custom_check(self, status=False, constraint="", constraint_message=""):
        if status:
            self.custom_check.append(
                {
                    "check": self.check_name,
                    "check_level": "Error",
                    "check_status": "Success",
                    "constraint": constraint,
                    "constraint_status": "Success",
                    "constraint_message": constraint_message,
                }
            )
        else:
            self.custom_check.append(
                {
                    "check": self.check_name,
                    "check_level": "Error",
                    "check_status": "Error",
                    "constraint": constraint,
                    "constraint_status": "Failure",
                    "constraint_message": constraint_message,
                }
            )

    def __check_columns(self, columns):
        if set(columns) == set(self.df.columns):
            self.__set_custom_check(
                status=True, constraint=f"ColumnsConstraint(Columns({self.reference}))"
            )
        else:
            self.__set_custom_check(
                status=False,
                constraint=f"ColumnsConstraint(Columns({self.reference}))",
                constraint_message=(
                    "Columns differs by "
                    + f"{set(columns).symmetric_difference(self.df.columns)}"
                ),
            )

    def __check_size(self, assertion, hook_reference):
        if "reference" in assertion:
            comparison_df = hook_reference(assertion["reference"])

        if "operator" not in assertion:
            assertion["operator"] = "igual"

        if "column_reference" not in assertion:
            assertion["column_reference"] = self.df.columns

        if "value" not in assertion:
            assertion["value"] = comparison_df.select(
                assertion["column_reference"]
            ).count()

        self.check.hasSize(
            self.__get_lambda_assert(
                assertion["operator"],
                assertion["value"],
            )
        )

    def __check_distinctness(self, assertion):
        if assertion:
            self.check.hasDistinctness(self.df.columns, lambda x: x == 1.0),

    def __check_sk(self, assertion):
        if assertion in self.df.columns:
            self.__set_custom_check(
                status=True,
                constraint=f"HasSKConstraint(HasSK({self.reference}))",
            )
        else:
            self.__set_custom_check(
                status=False,
                constraint=f"HasSKConstraint(HasSK({self.reference}))",
                constraint_message=(f"There is no {assertion} in {self.reference}!"),
            )

    def __check_completeness(self, column, assertion):
        if isinstance(assertion, dict):
            self.check.hasCompleteness(
                column,
                self.__get_lambda_assert(assertion["operator"], assertion["value"]),
            )
        elif assertion:
            self.check.isComplete(column)

    def __check_uniqueness(self, column, assertion):
        if isinstance(assertion, dict):
            self.check.hasUniqueness(
                [column],
                self.__get_lambda_assert(assertion["operator"], assertion["value"]),
            )
        elif assertion:
            self.check.isUnique(column)

    def __check_data_type(self, column, column_type):
        assert_column_type = dict((key, value) for key, value in self.df.dtypes)[column]

        if column_type == assert_column_type:
            self.__set_custom_check(
                status=True,
                constraint=f"DataTypeConstraint(DataType({column}, {column_type}))",
            )
        else:
            self.__set_custom_check(
                status=False,
                constraint=f"DataTypeConstraint(DataType({column}, {column_type}))",
                constraint_message=(
                    f"{column} of type '{assert_column_type}'"
                    f"does not meet type '{column_type}' requirement!"
                ),
            )

    def __check_min(self, column, value):
        self.check.hasMin(column, lambda x: x >= value)

    def __check_max(self, column, value):
        self.check.hasMax(column, lambda x: x <= value)

    def execute(self, **kwargs):
        if isinstance(self.platform, Default):
            self.setPlatform(kwargs["platform"])

        if self.check_name == "":
            self.check_name = f"validacao_{self.reference}"

        self.check = Check(self.platform.session, CheckLevel.Error, self.check_name)

        check_call_map = {
            "columns": self.__check_columns,
            "size": self.__check_size,
            "distinctness": self.__check_distinctness,
            "SK": self.__check_sk,
            "completeness": self.__check_completeness,
            "uniqueness": self.__check_uniqueness,
            "data_type": self.__check_data_type,
            "min": self.__check_min,
            "max": self.__check_max,
            "contained": self.check.isContainedIn,
        }

        for verification, assertion in self.table_validation.items():
            if verification == "size":
                check_call_map[verification](assertion, kwargs["hook_reference"])
            else:
                check_call_map[verification](assertion)

        for column, assertion in self.column_validation.items():
            for verification in assertion.keys():
                check_call_map[verification](column, assertion[verification])

        if self.custom_check:
            return (
                self.output,
                VerificationResult.checkResultsAsDataFrame(
                    self.platform.session,
                    VerificationSuite(self.platform.session)
                    .onData(self.df)
                    .addCheck(self.check)
                    .run(),
                ).union(
                    self.platform.session.createDataFrame(
                        Row(**i) for i in self.custom_check
                    )
                ),
            )

        return (
            self.output,
            VerificationResult.checkResultsAsDataFrame(
                self.platform.session,
                VerificationSuite(self.platform.session)
                .onData(self.df)
                .addCheck(self.check)
                .run(),
            ),
        )
