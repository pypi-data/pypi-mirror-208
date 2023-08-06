from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from io import TextIOWrapper

from sefazetllibcli.errors import MethodNotImplemented
from sefazetllibcli.usecases.replace_template import ReplaceTemplate


@dataclass(init=False)
class Generator(ABC):
    entities: list = field(default_factory=list)
    template_file: str = field(default_factory=str)
    root_path: str = field(default_factory=str)
    target: str = field(default_factory=str)
    replace_template: ReplaceTemplate = field(default=None)
    template: str = field(init=False, default=None)

    def __post_init__(self):
        with open(self.template_file, 'r', encoding='utf-8') as file_template:
            object.__setattr__(self, 'template', file_template.read())

    @abstractmethod
    def generate(self):
        raise MethodNotImplemented('Deve implementar o método: proccess')
