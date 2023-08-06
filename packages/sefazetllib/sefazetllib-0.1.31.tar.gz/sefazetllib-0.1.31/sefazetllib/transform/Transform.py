from abc import ABC, abstractmethod


class Transform(ABC):
    """
    Abstract base class for data transformation.

    Defines abstract methods to setup connection and execute the transformation process.
    """

    def setup(self) -> None:
        """
        Sets up the transformation process.
        """
        pass

    @abstractmethod
    def execute(self, **kwargs):
        """
        Abstract method to execute the transformation process.

        Parameters:
            **kwargs: Arbitrary keyword arguments.
        """
        pass
