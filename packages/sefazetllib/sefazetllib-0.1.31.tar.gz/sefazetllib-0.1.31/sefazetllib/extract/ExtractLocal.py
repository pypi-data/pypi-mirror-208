from typing import Any, Dict, List

from sefazetllib.Builder import Builder, field
from sefazetllib.extract.Extract import Extract
from sefazetllib.factory.platform.dataframe.Default import Default
from sefazetllib.factory.platform.Platform import Platform


@Builder
class ExtractLocal(Extract):
    platform: Platform = field(default_factory=Default)
    file_format: str = field(default="")
    format_properties: Dict[str, Any] = field(default_factory=dict)
    repository: str = field(default="")
    url: str = field(default="")
    partition: List[str] = field(default_factory=list)
    reference: str = field(default="")
    columns: List = field(default_factory=list)
    duplicates: bool = field(default=False)
    optional: bool = field(default=False)

    def build_connection_string(self):
        if self.partition != []:
            for partition in self.partition:
                self.setUrl(f"{self.url}/{partition}")

        return self.url

    def execute(self, **kwargs):
        if isinstance(self.platform, Default):
            self.setPlatform(kwargs["platform"])

        if self.repository == "":
            self.setRepository(kwargs["repository"])

        url = self.build_connection_string()

        if kwargs:
            args = kwargs["args"]
            if args.extractRepository:
                self.setRepository(args.extractRepository)

            if args.extractPartitions:
                self.setPartition(args.extractPartitions)

            if args.extractUrl:
                url = args.extractUrl

        return (
            self.reference,
            self.platform.read(
                file_format=self.file_format,
                format_properties=self.format_properties,
                repository=self.repository,
                url=url,
                reference=self.reference,
                columns=self.columns,
                duplicates=self.duplicates,
                optional=self.optional,
            ),
        )
