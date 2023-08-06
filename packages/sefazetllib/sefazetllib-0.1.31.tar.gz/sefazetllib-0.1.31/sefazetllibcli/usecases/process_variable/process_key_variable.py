from .process_variable import ProcessVariable


class ProcessKeyVariable(ProcessVariable):
    """Classe `ProcessKeyVariable`.

    A classe implementa o procedimento da saída da variavel `KEY`.
    """

    variable = 'KEY'

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
        factories = [
            etl['key']['factory']
            for etl in entity['ETL']
            if etl['type'] == 'load'
        ]
        factories_without_duplicates = [*set(factories)]
        factories_without_duplicates.sort()

        return 'from sefazetllib.utils.key import '+', '.join(factories_without_duplicates) if bool(factories_without_duplicates) else ''
