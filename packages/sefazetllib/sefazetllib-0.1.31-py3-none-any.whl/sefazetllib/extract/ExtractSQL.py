from typing import Any, Dict, List

from sefazetllib.Builder import Builder, field
from sefazetllib.extract.Extract import Extract
from sefazetllib.factory.platform.dataframe.Default import Default
from sefazetllib.factory.platform.Platform import Platform
from sefazetllib.factory.platform.PlatformFactory import PlatformFactory


@Builder
class ExtractSQL(Extract):
    platform: Platform = field(default=Default())
    format: str = field(default="jdbc")
    operator: str = field(default=":")
    host: str = field(default="")
    port: int = field(default=0)
    database: str = field(default="")
    instance: str = field(default="")
    driver: str = field(default="")
    schema: str = field(default="")
    table: str = field(default="")
    authentication: Dict[str, Any] = field(default_factory=dict)
    url: str = field(default="")
    reference: str = field(default="")
    columns: List[str] = field(default_factory=list)
    optional: bool = field(default=False)
    duplicates: bool = field(default=False)

    def __build_properties(self):
        self.properties = {
            "database": self.database,
            "driver": self.driver,
            "user": self.authentication["user"],
            "password": self.authentication["password"],
            "dbtable": self.table,
            "url": self.url,
        }

        return self.properties

    def build_connection_string(self):
        platform_db = PlatformFactory(self.database).create(
            name="get url jdbc",
        )
        self.url = platform_db.get_url(
            format=self.format,
            operator=self.operator,
            database=self.database,
            host=self.host,
            instance=self.instance,
            schema=self.schema,
            port=self.port,
        )

        self.table = platform_db.get_table_name(table=self.table, schema=self.schema)

        return self.url

    def execute(self, **kwargs):
        if isinstance(self.platform, Default):
            self.setPlatform(kwargs["platform"])

        url = self.build_connection_string()
        properties = self.__build_properties()

        if kwargs:
            args = kwargs["args"]

            if args.extractUrl:
                url = args.extractUrl

        return self.reference, self.platform.read(
            format=self.format,
            url=url,
            format_properties=properties,
            optional=self.optional,
            columns=self.columns,
            duplicates=self.duplicates,
        )
