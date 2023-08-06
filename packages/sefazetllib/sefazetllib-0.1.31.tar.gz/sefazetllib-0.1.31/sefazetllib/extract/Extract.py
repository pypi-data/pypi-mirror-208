from abc import ABC, abstractmethod


class Extract(ABC):
    """Abstract base class for data extraction.

    Defines abstract methods to setup connection, build connection string and execute the extraction process.
    """

    def setup(self) -> None:
        """
        Sets up the connection for data extraction.
        """
        pass

    @abstractmethod
    def build_connection_string(self):
        """Abstract method to build connection string for data extraction."""
        pass

    @abstractmethod
    def execute(self, **kwargs):
        """Abstract method to execute data extraction.

        Parameters:
            **kwargs: Arbitrary keyword arguments.
        """
        pass
