import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from sefazetllibcli.config.logging import logger
from sefazetllibcli.errors import UnsupportedFileExtension
from sefazetllibcli.usecases.replace_template import ReplaceETLTemplate, ReplaceTemplate
from sefazetllibcli.utils import ParseETL

from .generator import Generator


@dataclass
class ETLGenerator(Generator):
    template_file: str = field(
        default=Path(__file__).parent / '../templates/etl_template'
    )
    __parse_etl: ParseETL = field(default=ParseETL())
    replace_template: ReplaceTemplate = field(default=ReplaceETLTemplate)
    root_path: str = field(default=os.getcwd())

    def generate(self) -> None:
        for i, entity in enumerate(self.entities):
            try:
                etl_name, etl = entity

                logger.info(
                    '[%s/%s] Iniciando geração do ETL `%s`',
                    i + 1,
                    len(self.entities),
                    etl_name,
                )

                logger.info('Executando...')

                replace_template = self.replace_template(
                    template=self.template,
                    entity=etl,
                    sources=None,
                    columns=None,
                )

                output = replace_template.replace()

                logger.info('Gravando...')

                path = f'{self.root_path}/{self.target}/{etl_name}'
                os.makedirs(os.path.dirname(path), exist_ok=True)

                with open(
                    path,
                    'w',
                    encoding='utf-8',
                ) as file__output:
                    file__output.write(output)

                logger.info(
                    '[%s/%s] Geração do ETL `%s` concluída!',
                    i + 1,
                    len(self.entities),
                    etl_name,
                )
            except Exception as err:
                logger.error(
                    '[%s/%s] Um erro ocorreu na geração do ETL `%s`: %s',
                    i + 1,
                    len(self.entities),
                    etl_name,
                    err,
                )

    def derive(self) -> None:
        for i, entity in enumerate(self.entities):
            try:
                etl_name, etl = entity

                logger.info(
                    '[%s/%s] Iniciando derivação do ETL `%s`',
                    i + 1,
                    len(self.entities),
                    etl_name,
                )

                logger.info('Executando...')

                # print(self.__get_etl_context(etl))
                # self.__get_transform_context(etl)
                # print(self.__get_imports(etl))

                output = self.__parse_etl.parse(self.__get_etl_context(etl))

                path = f'{self.root_path}/{self.target}/{etl_name}'
                os.makedirs(os.path.dirname(path), exist_ok=True)

                with open(
                    path,
                    'w',
                    encoding='utf-8',
                ) as file__output:
                    extension_file = os.path.splitext(path)[1]
                    if extension_file == '.json':
                        file__output.write(json.dumps(output, indent=4))
                    elif extension_file == '.yaml':
                        file__output.write(yaml.dump(output, indent=4))
                    else:
                        raise UnsupportedFileExtension(
                            f'Extensão de arquivo não suportada: {path}'
                        )

                logger.info(
                    '[%s/%s] Derivação do ETL `%s` concluída!',
                    i + 1,
                    len(self.entities),
                    etl_name,
                )
            except Exception as err:
                logger.error(
                    '[%s/%s] Um erro ocorreu na geração do ETL `%s`: %s',
                    i + 1,
                    len(self.entities),
                    etl_name,
                    err,
                )

    def __get_etl_context(self, script):
        etl_pattern = re.compile(r'\((ETL.*)\)$')

        minified = re.sub(r'\s', '', script)
        return etl_pattern.search(minified).group(1)

    def __get_transform_context(self, script):
        etl_pattern = re.compile(r'(@Builder[\s\S]*?)(?=\n{3})')

        transforms = etl_pattern.findall(script)

        for transform in transforms:
            self.__get_transform_references(transform)
            self.__get_transform_setup(transform)
            self.__get_transform_private_methods(transform)
            self.__get_transform_method(transform)

        # return etl_pattern.search(minified).group(1)

    def __get_transform_references(self, transform):
        etl_pattern = re.compile(
            r'([(A-Z)|(a-z)].*?): Optional\[DataFrame\] = None')

        return etl_pattern.findall(transform)

    def __get_transform_setup(self, transform):
        etl_pattern = re.compile(
            r'self.__(\w[A-Z|a-z].*) = (Window*[\s\S]*?\)\n|[^\(][\s\S]*?\n|\([\s\S]*?\s\))')

        return etl_pattern.findall(transform)

    def __get_transform_private_methods(self, transform):
        etl_pattern = re.compile(
            r'def __(\w[A-Z|a-z].*)\(self\):([^\(][\s\S]*?\s\n)')

        return etl_pattern.findall(transform)

    def __get_transform_method(self, transform):
        etl_pattern = re.compile(
            r'def execute\(self\) \-> Tuple\[str, DataFrame\]:([\s\S]*?)\sreturn.*\n\s*.?\"([\s\S].*)\"\,([\s\S]*?)\)\n\n')
        print(etl_pattern.findall(etl_pattern))

    def __get_imports(self, etl):
        etl_pattern = re.compile(
            r'from ([^sefazetllib]\w.*) import ([^\(][\s\S]*?\n|[\(][\s\S]*?\s[\)])')
        return etl_pattern.findall(etl)
