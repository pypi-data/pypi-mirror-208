from abc import ABC, abstractmethod


class Partition(ABC):
    """
    Abstract base class for partitioning.

    Defines abstract methods to setup partitioning and get the partition.
    """

    def setup(self) -> None:
        """
        Sets up the partitioning process.
        """
        pass

    @abstractmethod
    def get(self):
        """
        Abstract method to get the partition.
        """
        pass
