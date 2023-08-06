from typing import Any, List, Optional, Tuple

from pyspark.sql.functions import col, first, percentile_approx, when, avg
from pyspark.sql.window import Window

from sefazetllib import Builder, field
from sefazetllib.transform.Transform import Transform


@Builder
class QuartileTransform(Transform):
    df: Optional[Any] = None
    reference: str = field(default="")
    output: str = field(default="")
    partitions: List[str] = field(default_factory=list)
    target: str = field(default="")
    outlier: bool = field(default=False)
    median: bool = field(default=False)
    average: bool = field(default=False)
    
    def __get_window(self):
        if self.partitions is not None:
            self.window = Window.partitionBy(self.partitions)

    def __get_quartile(self, percentile):
        quartile = percentile_approx(self.target, percentile)

        if self.window is not None:
            return quartile.over(self.window)

        return quartile

    def execute(self) -> Tuple[str, Any]:
        self.__get_window()

        df_quartile = (
            self.df.withColumn(f"Q1_{self.target}", self.__get_quartile(0.25))
            .withColumn(f"Q2_{self.target}", self.__get_quartile(0.5))
            .withColumn(f"Q3_{self.target}", self.__get_quartile(0.75))
        )

        if self.outlier:
            df_quartile = df_quartile.withColumn(
                f"OUT_{self.target}",
                col(f"Q3_{self.target}")
                + 3 * (col(f"Q3_{self.target}") - col(f"Q1_{self.target}")),
            )

        if (self.median | self.average):
            group_columns = [
                *self.partitions,
                f"Q1_{self.target}",
                f"Q2_{self.target}",
                f"Q3_{self.target}",
            ]

            if self.outlier:
                group_columns.append(f"OUT_{self.target}")

            df_quartile = (
                df_quartile.withColumn(
                    f"STA_R_{self.target}",
                    when(col(self.target) <= col(f"Q1_{self.target}"), 1)
                    .when(
                        (col(self.target) > col(f"Q1_{self.target}"))
                        & (col(self.target) <= col(f"Q2_{self.target}")),
                        2,
                    )
                    .when(
                        (col(self.target) > col(f"Q2_{self.target}"))
                        & (col(self.target) <= col(f"Q3_{self.target}")),
                        3,
                    )
                    .when(col(self.target) > col(f"Q3_{self.target}"), 4),
                )
            )
            
            if self.median:
                df_quartile = (df_quartile
                    .withColumn(
                        f"MEDIAN_Q_{self.target}",
                        percentile_approx(self.target, 0.5).over(
                            Window.partitionBy([*self.partitions, f"STA_R_{self.target}"])
                        ),
                    )
                    .groupBy(group_columns)
                    .pivot(f"STA_R_{self.target}")
                    .agg(first(col(f"MEDIAN_Q_{self.target}")))
                    .withColumnRenamed("1", f"MEDIAN_R1_{self.target}")
                    .withColumnRenamed("2", f"MEDIAN_R2_{self.target}")
                    .withColumnRenamed("3", f"MEDIAN_R3_{self.target}")
                    .withColumnRenamed("4", f"MEDIAN_R4_{self.target}")
            )
            if self.average:
                df_quartile = (df_quartile
                    .withColumn(
                        f"AVG_Q_{self.target}",
                        avg(self.target).over(
                            Window.partitionBy([*self.partitions, f"STA_R_{self.target}"])
                        ),
                    )
                    .groupBy(group_columns)
                    .pivot(f"STA_R_{self.target}")
                    .agg(first(col(f"AVG_Q_{self.target}")))
                    .withColumnRenamed("1", f"AVG_R1_{self.target}")
                    .withColumnRenamed("2", f"AVG_R2_{self.target}")
                    .withColumnRenamed("3", f"AVG_R3_{self.target}")
                    .withColumnRenamed("4", f"AVG_R4_{self.target}")
            )

        if self.output is None:
            self.output = self.reference

        return self.output, df_quartile
