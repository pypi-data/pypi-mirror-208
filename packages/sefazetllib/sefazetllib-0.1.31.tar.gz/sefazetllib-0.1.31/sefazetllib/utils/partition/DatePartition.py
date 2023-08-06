from datetime import date
from typing import Optional

from sefazetllib.Builder import Builder
from sefazetllib.utils.partition.IncrementalRangePartition import (
    IncrementalRangePartition,
)
from sefazetllib.utils.partition.Partition import Partition


@Builder
class DatePartition(Partition):
    """
    Implementation of the abstract base class 'Partition' for date partitioning.

    Defines the methods to format and build the partition.
    """

    year: Optional[str] = None
    month: Optional[str] = None
    day: Optional[str] = None
    years: Optional[IncrementalRangePartition] = None
    months: Optional[IncrementalRangePartition] = None
    days: Optional[IncrementalRangePartition] = None

    def __format_partition(self, partition):
        """Format the given partition.

        Parameters:
            partition: The partition to be formatted.

        Returns:
            The formatted partition.
        """
        return f"{set(partition.get())}".replace(" ", "")

    def __build_partition(self):
        """Build the partition.

        Returns:
            The list of strings representing the partition.
        """
        partition = [
            self.__format_partition(self.years) if bool(self.years) else self.year
        ]

        if bool(self.month) or bool(self.months):
            partition.append(
                self.__format_partition(self.months)
                if bool(self.months)
                else self.month
            )

        if bool(self.day) or bool(self.days):
            partition.append(
                self.__format_partition(self.days) if bool(self.days) else self.day
            )

        return partition

    def get(self):
        """Get the partition.

        Returns:
            The list of strings representing the partition.
        """
        return self.__build_partition()

    def get_date(self):
        """Get the date of the partition.

        Returns:
            The date of the partition in the format 'YYYY/MM/DD'.
        """
        return date(*self.__build_partition()).strftime("%Y/%m/%d")
