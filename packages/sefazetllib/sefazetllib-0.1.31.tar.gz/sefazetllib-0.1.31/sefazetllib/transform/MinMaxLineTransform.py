from typing import Any, List, Optional

from pyspark.sql.functions import col, dense_rank
from pyspark.sql.window import Window

from sefazetllib import Builder, field
from sefazetllib.transform.Transform import Transform


@Builder
class MinMaxLineTransform(Transform):
    df: Optional[Any] = None
    reference: str = field(default="")
    output: str = field(default="")
    order: str = field(default="")
    orders: List[str] = field(default_factory=list)
    window: str = field(default="")
    max: bool = field(default=False)
    min: bool = field(default=False)

    def __get_window(self):
        if self.max:
            order_max = []

            for unique_order in self.orders:
                order_max.append(col(unique_order).desc())

            self.window = Window.orderBy(order_max)

        if self.min:
            self.window = Window.orderBy(self.orders)

        if self.order != "":
            if self.max:
                self.window = Window.orderBy(col(self.order).desc())

            if self.min:
                self.window = Window.orderBy(self.order)

    def execute(self):
        self.__get_window()
        return (
            self.output,
            (
                self.df.withColumn(
                    "FLG_FILTER_LINE",
                    dense_rank().over(self.window),
                )
                .filter(col("FLG_FILTER_LINE").eqNullSafe(1))
                .drop("FLG_FILTER_LINE")
            ),
        )
