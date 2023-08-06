from sefazetllib.factory.platform.Platform import Platform


class Default(Platform):
    def __init__(self) -> None:
        self.name = None
        self.session = None

    def read(self, **kwargs):
        pass

    def load(self, **kwargs):
        pass
