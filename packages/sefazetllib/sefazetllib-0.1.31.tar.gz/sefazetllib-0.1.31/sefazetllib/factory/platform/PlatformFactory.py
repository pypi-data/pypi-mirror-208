from sefazetllib.factory.Factory import Creator
from sefazetllib.factory.platform.database import MySQL, PostgreSQL
from sefazetllib.factory.platform.dataframe import Default, Pandas, Spark


class PlatformFactory(Creator):
    """
    Note that the signature of the method still uses the abstract product type,
    even though the concrete product is actually returned from the method. This
    way the Creator can stay independent of concrete product classes.
    """

    def __init__(self, platform) -> None:
        self.platform = platform

    def create(self, **kwargs):
        """
        The client code works with an instance of a concrete creator, albeit through
        its base interface. As long as the client keeps working with the creator via
        the base interface, you can pass it any creator's subclass.
        """
        return self.execute(**kwargs)

    def factory_method(self, **kwargs):
        try:
            return globals()[self.platform](**kwargs)
        except KeyError:
            return Default(**kwargs)
