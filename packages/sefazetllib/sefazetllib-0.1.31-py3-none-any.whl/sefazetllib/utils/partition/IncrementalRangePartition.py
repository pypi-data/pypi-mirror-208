from sefazetllib.Builder import Builder
from sefazetllib.utils.partition.Partition import Partition


@Builder
class IncrementalRangePartition(Partition):
    """
    Implementation of the abstract base class 'Partition' for incremental range partitioning.

    Defines the method to get the partition.
    """

    init: int = 1
    limit: int = 1
    desc: bool = True
    offset: int = 1

    def get(self):
        """
        Get the partition.

        Returns:
            The list of integers representing the partition.
        """
        return [i for i in range(self.init - self.limit, self.init + 1, self.offset)]
