from .process_variable import ProcessVariable


class ProcessPartitionVariable(ProcessVariable):
    """Classe `ProcessPartitionVariable`.

    A classe implementa o procedimento da saída da variavel `PARTITION`.
    """

    variable = 'PARTITION'

    def _get_factories(self, dictionary, factories):
        for prop, value in dictionary.items():
            if (
                prop != 'factory'
                and isinstance(value, dict)
                and 'factory' in value
            ):
                factories.append(value['factory'])
                self._get_factories(value, factories)

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
        if 'partition' in entity:
            partitions = entity['partition']
            factories = [partitions['factory']]
            self._get_factories(entity['partition'], factories)

            factories_without_duplicates = [*set(factories)]
            factories_without_duplicates.sort()

            return 'from sefazetllib.utils.partition import ' + ', '.join(
                factories_without_duplicates
            )
        return ''
