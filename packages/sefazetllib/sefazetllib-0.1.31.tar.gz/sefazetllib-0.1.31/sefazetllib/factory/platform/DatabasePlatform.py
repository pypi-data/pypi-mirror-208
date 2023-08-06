from abc import abstractmethod

from sefazetllib.factory.platform.Platform import Platform


class DatabasePlatform(Platform):
    """
    The Platform interface declares the operations that all concrete products
    must implement.
    """

    @abstractmethod
    def get_url(self):
        pass

    @abstractmethod
    def get_table_name(self):
        pass
