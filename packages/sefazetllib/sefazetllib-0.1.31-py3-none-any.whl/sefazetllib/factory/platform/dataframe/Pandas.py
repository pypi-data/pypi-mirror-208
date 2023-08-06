from datetime import date

import pandas as pd
from pandas.util import hash_pandas_object

from sefazetllib.factory.platform.Platform import Platform


class Pandas(Platform):
    def __init__(self, name=None) -> None:
        self.session = pd
        self.name = name

    def __read_csv(self, url):
        return self.session.read_csv(url)

    def __read_parquet(self, url):
        return self.session.read_parquet(url)

    def __save_csv(self, df, url, properties):
        return df.to_csv(url, **properties)

    def __save_parquet(self, df, url, properties):
        return df.to_parquet(url, **properties)

    def __get_key_method(self, name):
        return {"SurrogateKey": hash_pandas_object}[name]

    def read(self, **kwargs):
        file_format = kwargs["file_format"]
        url = kwargs["url"]
        return {"csv": self.__read_csv, "parquet": self.__read_parquet}[file_format](
            url
        )

    def load(self, **kwargs):
        df = kwargs["df"]
        sk_name = kwargs["sk_name"]
        key = kwargs["key"]
        columns = kwargs["columns"]
        duplicates = kwargs["duplicates"]
        file_format = kwargs["file_format"]
        format_properties = kwargs["format_properties"]
        url = kwargs["url"]

        key.setColumns(df[key.columns])
        key.setMethod(self.__get_key_method(type(key).__name__))

        writer_format = df
        writer_format[sk_name] = key.get()
        writer_format["DAT_CARGA"] = date.today()

        if bool(columns):
            writer_format = writer_format[columns]

        if duplicates:
            writer_format = writer_format.drop_duplicates()

        return {"csv": self.__save_csv, "parquet": self.__save_parquet}[file_format](
            writer_format, url, format_properties
        )
