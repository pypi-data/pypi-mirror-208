from abc import ABC, abstractmethod


class Creator(ABC):
    """The Creator class declares the factory method that is supposed to return an object of a Platform class. The Creator's subclasses usually provide the implementation of this method."""

    @abstractmethod
    def factory_method(self):
        """Note that the Creator may also provide some default implementation of the factory method."""
        pass

    def execute(self, **kwargs):
        """Also note that, despite its name, the Creator's primary responsibility is not creating products. Usually, it contains some core business logic that relies on Platform objects, returned by the factory method.  Subclasses can indirectly change that business logic by overriding the factory method and returning a different type of product from it.

        Parameters:
            **kwargs: Keyword arguments for the execute method.
        """
        return self.factory_method(**kwargs)
