import json

from .process_variable import ProcessVariable


class ProcessETLVariable(ProcessVariable):
    """Classe `ProcessETLVariable`.

    A classe implementa o procedimento da saída da variavel `ETL`.
    """

    variable = 'ETL'

    def _get_platform(self, platform):
        factory = platform['factory']
        name = platform['name']
        return (
            f'.setPlatform(PlatformFactory("{factory}").create(name="{name}"))'
        )

    def _get_properties(self, properties, skip_columns=None, height=1):
        props = []
        for prop, value in properties.items():
            if prop not in skip_columns:
                prop_str = ''.join(
                    [word.capitalize() for word in prop.split('_')]
                )
                if isinstance(value, str):
                    value = f'"{value}"'
                elif isinstance(value, dict):
                    tabs = '\t' * height
                    if 'factory' in value:
                        value = (
                            '\n'
                            + tabs
                            + '\t'
                            + self._visit_factory(value, height + 1)
                            + '\n'
                            + tabs
                        )
                    else:
                        value = (
                            json.dumps(value, indent=4 * (height + 1))
                            .replace('}', tabs + '}')
                            .replace('true', 'True')
                            .replace('false', 'False')
                        )
                props.append(f'.set{prop_str}({value})')
        return props

    def _visit_factory(self, factory, height):
        name = f'{factory["factory"]}()'
        properties = self._get_properties(factory, ['factory', 'type'], height)
        tabs = '\n' + '\t' * height
        properties = tabs.join(properties)
        return name + tabs + properties

    def _get_etl(self, etls):
        list_etl = []
        for etl in etls:
            etl_type = etl['type']
            value = (
                etl['name']
                if etl_type == 'transform'
                else self._visit_factory(etl, 2)
            )
            tabs_ini = '\n\t\t'
            tabs_end = '\n\t'
            if etl_type == 'transform':
                tabs_ini = ''
                tabs_end = ''
            list_etl.append(f'.{etl_type}({tabs_ini}{value}{tabs_end})')

        return '\n\t'.join(list_etl)

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
        platform = '\n\t' + self._get_platform(entity['platform'])
        properties = self._get_properties(
            entity,
            skip_columns=['platform', 'ETL'],
            height=1,
        )
        properties = '\n\t' + '\n\t'.join(properties) if properties else ''
        print('inicio')
        etls = '\n\t' + self._get_etl(entity['ETL'])
        print('fim')
        return '(\n\tETL()' + f'{platform}{properties}{etls}\n)'
