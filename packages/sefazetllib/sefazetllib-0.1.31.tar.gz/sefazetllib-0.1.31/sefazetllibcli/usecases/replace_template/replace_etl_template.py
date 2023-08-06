from sefazetllibcli.usecases.process_variable import (
    ProcessETLVariable,
    ProcessExtractVariable,
    ProcessImportsVariable,
    ProcessKeyVariable,
    ProcessLoadVariable,
    ProcessPartitionVariable,
    ProcessTransformsVariable,
    ProcessValidateVariable,
)

from .replace_template import ReplaceTemplate


class ReplaceETLTemplate(ReplaceTemplate):
    """Classe `ReplaceETLTemplate`.

    A classe tem a finalidade de substituir as variáveis que estão definidas no
    template.
    """

    def replace(self):
        """Retorna o template com todas variáveis da lista já substituídas."""
        return self.replace_variables(
            ProcessETLVariable(),
            ProcessExtractVariable(),
            ProcessImportsVariable(),
            ProcessKeyVariable(),
            ProcessLoadVariable(),
            ProcessPartitionVariable(),
            ProcessTransformsVariable(),
            ProcessValidateVariable(),
        )
