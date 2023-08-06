from abc import ABC, abstractmethod


class Platform(ABC):
    """
    The Platform interface declares the operations that all concrete products
    must implement.
    """

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def load(self):
        pass
