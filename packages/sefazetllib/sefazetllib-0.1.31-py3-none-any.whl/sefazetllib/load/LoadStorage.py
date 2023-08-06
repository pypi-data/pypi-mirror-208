from typing import Any, Dict, List

from sefazetllib.Builder import Builder, field
from sefazetllib.factory.platform.dataframe.Default import Default
from sefazetllib.factory.platform.Platform import Platform
from sefazetllib.load.Load import Load
from sefazetllib.utils.key import DefaultKey, Key


@Builder
class LoadStorage(Load):
    platform: Platform = field(default=Default())
    file_format: str = field(default="")
    format_properties: Dict[str, Any] = field(default_factory=dict)
    reference: str = field(default="")
    url: str = field(default="")
    repository: str = field(default="")
    layer: str = field(default="")
    schema: str = field(default="")
    entity: str = field(default="")
    mode: str = field(default="")
    df_writer: Any = field(default="")
    duplicates: bool = field(default=False)
    key: Key = field(default=DefaultKey())
    columns: List = field(default_factory=list)
    protocol: str = field(default="")

    def build_connection_string(self):
        self.url = f"{self.protocol}://{self.repository}/{self.layer}/{self.schema}/{self.entity}"
        return self.url

    def execute(self, **kwargs):
        if isinstance(self.platform, Default):
            self.setPlatform(kwargs["platform"])

        if self.repository == "":
            self.setRepository(kwargs["repository"])

        url = self.build_connection_string()

        if kwargs:
            args = kwargs["args"]
            if args.loadRepository:
                self.setRepository(args.loadRepository)

            if args.loadUrl:
                url = args.loadUrl

        sk_name = f"SK_{self.entity}"
        if "/" in self.entity:
            entity = self.entity.split("/")[1]
            sk_name = f"SK_{entity}"

        return (
            self.reference,
            self.platform.load(
                df=self.df_writer,
                sk_name=sk_name,
                key=self.key,
                columns=self.columns,
                duplicates=self.duplicates,
                file_format=self.file_format,
                format_properties=self.format_properties,
                url=url,
                mode=self.mode,
            ),
        )
