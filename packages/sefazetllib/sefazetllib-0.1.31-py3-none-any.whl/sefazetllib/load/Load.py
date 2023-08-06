from abc import ABC, abstractmethod


class Load(ABC):
    """Abstract base class for loading data.

    Defines abstract methods to setup connection, build connection string and execute the loading process.
    """

    def setup(self) -> None:
        """
        Sets up the connection for data loading.
        """
        pass

    @abstractmethod
    def build_connection_string(self):
        """Abstract method to build connection string for data loading."""
        pass

    @abstractmethod
    def execute(self, **kwargs):
        """Abstract method to execute data loading.

        Parameters:
            **kwargs: Arbitrary keyword arguments.
        """
        pass
