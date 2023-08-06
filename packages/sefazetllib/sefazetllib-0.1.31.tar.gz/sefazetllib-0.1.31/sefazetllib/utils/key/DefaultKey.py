from sefazetllib.Builder import Builder
from sefazetllib.utils.key.Key import Key


@Builder
class DefaultKey(Key):
    """Default implementation of the abstract base class 'Key' for key generation.

    Defines the method to generate the key.
    """

    def get(self):
        """Generate the default key."""
        pass
