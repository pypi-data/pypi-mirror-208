from sefazetllib.factory.platform.DatabasePlatform import DatabasePlatform


class MySQL(DatabasePlatform):
    def __init__(self, name="MySQL Job", configs=[]) -> None:
        self.name = name
        self.session = None

    def get_url(self, **kwargs):
        host = kwargs["host"]
        format = kwargs["format"]
        operator = kwargs["operator"]
        database = kwargs["database"].lower()
        port = kwargs["port"]
        schema = kwargs["schema"]
        return f"{format}{operator}{database}://{host}:{port}/{schema}"

    def get_table_name(self, **kwargs):
        table = kwargs["table"]
        return table

    def read(self, **kwargs):
        pass

    def load(self, **kwargs):
        pass
