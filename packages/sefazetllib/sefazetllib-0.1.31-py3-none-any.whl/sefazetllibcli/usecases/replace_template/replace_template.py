from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import reduce

from sefazetllibcli.config.logging import logger
from sefazetllibcli.errors import MethodNotImplemented, VariableProcessingError
from sefazetllibcli.usecases.process_variable import ProcessVariable


@dataclass
class ReplaceTemplate(ABC):
    template: str = field(default_factory=str)
    entity: str = field(default_factory=str)
    sources: str = field(default_factory=str)
    columns: str = field(default_factory=str)

    def __replace_variable(self, replaced_template, process_variable):
        try:
            return replaced_template.replace(
                f'TEMPLATE_VAR__{process_variable.variable}',
                process_variable.process(
                    entity=self.entity,
                    sources=self.sources,
                    columns=self.columns,
                ),
            )
        except VariableProcessingError as err:
            logger.warning(
                'Variável %s não processada devido ao erro: %s',
                'TEMPLATE_VAR_' + process_variable.variable,
                err,
            )
            return replaced_template.replace(
                f'TEMPLATE_VAR__{process_variable.variable}',
                '',
            )

    def replace_variables(self, *processes_variable: ProcessVariable):
        return reduce(
            self.__replace_variable, processes_variable, self.template
        )

    @abstractmethod
    def replace(self):
        """Retorna o template com todas variáveis da lista já substituídas."""
        raise MethodNotImplemented('Deve implementar o método: replace')
