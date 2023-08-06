from typing import Callable, List, Optional

from sefazetllib.Builder import Builder, field
from sefazetllib.utils.key.Key import Key


@Builder
class SurrogateKey(Key):
    """Implementation of the abstract base class 'Key' for surrogate key generation.

    Defines the method to generate the surrogate key.
    """

    name: Optional[str] = None
    method: Callable[..., int] = lambda columns: 0
    columns: List[str] = field(default_factory=list)
    distribute: bool = field(default=True)

    def get(self):
        """Generate the surrogate key.

        Returns:
            The generated surrogate key.
        """
        if not self.distribute:
            return self.method(self.columns)

        return self.method(*self.columns)
