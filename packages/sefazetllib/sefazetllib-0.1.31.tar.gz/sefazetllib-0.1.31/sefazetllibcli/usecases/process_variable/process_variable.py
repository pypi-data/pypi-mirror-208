from abc import ABC, abstractmethod

from sefazetllibcli.errors import MethodNotImplemented


class ProcessVariable(ABC):
    """Interface `ProcessVariable`.

    A interface define como as suas classes que a implemêntam devem processar a
    saída da variável em questão.
    """

    variable = ''

    @abstractmethod
    def process(self, entity, sources, columns):
        """Retorna uma string do processamento da variável.

        Parâmetros:
            - `entity (Dict)`: Entidade que terá um notebook de teste gerado.
            - `sources (List[Dict])`: Dataframes das fontes que são usadas no
            notebook original da entidade.
            - `columns (Dict)`: Colunas do Dataframe gerado pelo notebook
            original.
        Saída:
            `processed_variable (str)`: String do processamento da variável.
        """
        raise MethodNotImplemented('Deve implementar o método: proccess')
