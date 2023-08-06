from abc import ABC, abstractmethod


class Key(ABC):
    """Abstract base class for key generation.

    Defines abstract methods to setup key generation and generate the key.
    """

    def setup(self) -> None:
        """
        Sets up the key generation process.
        """
        pass

    @abstractmethod
    def get(self):
        """Abstract method to generate the key."""
        pass
