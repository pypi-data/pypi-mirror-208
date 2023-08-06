from .process_variable import ProcessVariable


class ProcessTransformsVariable(ProcessVariable):
    """Classe `ProcessTransformsVariable`.

    A classe implementa o procedimento da saída da variavel `TRANSFORMS`.
    """

    variable = 'TRANSFORMS'

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
        transforms = [
            etl for etl in entity['ETL'] if etl['type'] == 'transform'
        ]
        template_transform = """@Builder
class TRANSFORMATION(Transform):
REFERENCES

    def setup(self):
        SETUP

    def execute(self) -> Tuple[str, DataFrame]:
        return ("REFERENCE", CODE,)
"""
        results = []
        for transform in transforms:
            references = []
            setups = []
            for reference in transform["references"]:
                references.append(
                    f"    {reference}: Optional[DataFrame] = None")

            references = "\n".join(references)

            if bool(transform["setup"]):
                for setup in transform["setup"]:
                    setups.append(f"self.{setup['name']}={setup['code']}")

                setups = "\n".join(setups)
            else:
                setups = 'pass'

            results.append(template_transform
                           .replace('TRANSFORMATION', transform["name"])
                           .replace('REFERENCES', references)
                           .replace('SETUP', setups)
                           .replace('REFERENCE', transform["reference"])
                           .replace('CODE', transform["code"]))

        return "\n".join(results)
