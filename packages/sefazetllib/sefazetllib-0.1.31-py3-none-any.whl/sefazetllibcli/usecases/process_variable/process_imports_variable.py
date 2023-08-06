from .process_variable import ProcessVariable


class ProcessImportsVariable(ProcessVariable):
    """Classe `ProcessExtractVariable`.

    A classe implementa o procedimento da saída da variavel `IMPORTS`.
    """

    variable = 'IMPORTS'

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

        return {
            "Pandas": "from pandas import *",
            "Spark": "from pyspark.sql import DataFrame, Window \nfrom pyspark.sql.functions import *"
        }[entity['platform']['factory']]
