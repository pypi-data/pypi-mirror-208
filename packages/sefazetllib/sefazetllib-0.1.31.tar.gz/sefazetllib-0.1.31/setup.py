# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sefazetllib',
 'sefazetllib.config',
 'sefazetllib.etl',
 'sefazetllib.extract',
 'sefazetllib.factory',
 'sefazetllib.factory.platform',
 'sefazetllib.factory.platform.database',
 'sefazetllib.factory.platform.dataframe',
 'sefazetllib.load',
 'sefazetllib.transform',
 'sefazetllib.utils',
 'sefazetllib.utils.key',
 'sefazetllib.utils.partition',
 'sefazetllib.validate',
 'sefazetllibcli',
 'sefazetllibcli.config',
 'sefazetllibcli.errors',
 'sefazetllibcli.generators',
 'sefazetllibcli.usecases',
 'sefazetllibcli.usecases.process_variable',
 'sefazetllibcli.usecases.replace_template',
 'sefazetllibcli.utils']

package_data = \
{'': ['*'], 'sefazetllibcli': ['templates/*']}

install_requires = \
['boto3>=1.24,<2.0',
 'click>=8.1,<9.0',
 'pandas>=1.3,<2.0',
 'pyarrow>=6.0,<7.0',
 'pydeequ>=1.0,<2.0',
 'pyyaml>=6.0,<7.0']

entry_points = \
{'console_scripts': ['sefazetllib = sefazetllibcli:cli']}

setup_kwargs = {
    'name': 'sefazetllib',
    'version': '0.1.31',
    'description': 'sefazetllib is a library that provides a simplified and abstracted way to construct ETL/ELT pipelines.',
    'long_description': '# sefazetllib\n\n[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)\n[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)\n[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n---\n\n**Documentation**: [https://main.d32to2oidohzrl.amplifyapp.com/](https://main.d32to2oidohzrl.amplifyapp.com/)\n\n**Source code**: [AWS CodeCommit](https://sa-east-1.console.aws.amazon.com/codesuite/codecommit/repositories/jobs-lib-sefaz-ce/browse?region=sa-east-1)\n\n---\n\n**sefazetllib** is a library that provides a simplified and abstracted way to construct ETL/ELT pipelines.\n\n## Features\n\n- Easy to use and understand library for constructing ETL/ELT pipelines.\n- Compatibility with popular data processing frameworks, such as [pandas](https://pandas.pydata.org/) and [PySpark](https://spark.apache.org/).\n- Support for file formats such as CSV and Parquet.\n- Provides the ability to extract, transform and load data with customizable configurations.\n\n## Requirements\n\n**sefazetllib** requires the following to run:\n\n- [Python](https://www.python.org/) 3.7.1+\n- [pandas](https://pandas.pydata.org/) 1.3+\n- [PyArrow](https://arrow.apache.org/) 6.0+\n- [PySpark](https://spark.apache.org/) 3.0+\n- [PyDeequ](https://pydeequ.readthedocs.io/) 1.0+\n- [Boto3](https://github.com/boto/boto3) 1.24+\n\n## Installation\n\nUse [pip](https://pip.pypa.io/en/stable/) to install **sefazetllib**:\n\n```bash\npip install sefazetllib\n```\n\n## Usage\n\nHere is an example of how to use the **sefazetllib**:\n\n```Python\nfrom typing import Tuple\n\nfrom pandas import DataFrame\n\nfrom sefazetllib import Builder\nfrom sefazetllib.etl import ETL\nfrom sefazetllib.extract import ExtractLocal\nfrom sefazetllib.factory.platform import PlatformFactory\nfrom sefazetllib.load import LoadLocal\nfrom sefazetllib.transform import Transform\nfrom sefazetllib.utils.key import SurrogateKey\n\n\n@Builder\nclass TestingDataFrame(Transform):\n    def execute(self) -> Tuple[str, DataFrame]:\n        return (\n            "dataframe",\n            DataFrame(\n                [["tom", 10], ["nick", 15], ["juli", 14]], columns=["Name", "Age"]\n            ),\n        )\n\n\n(\n    ETL()\n    .setPlatform(PlatformFactory("Pandas").create(name="test_pandas"))\n    .transform(TestingDataFrame)\n    .load(\n        LoadLocal()\n        .setFileFormat("parquet")\n        .setEntity("load_test")\n        .setMode("overwrite")\n        .setReference("dataframe")\n        .setDuplicates(True)\n        .setKey(SurrogateKey().setColumns(["Name", "Age"]).setDistribute(False))\n    )\n    .extract(\n        ExtractLocal()\n        .setFileFormat("parquet")\n        .setUrl("load_test.parquet")\n        .setReference("extract_test")\n    )\n)\n```\n\n## Testing\n\nTo run the unit tests, run the following command:\n\n```bash\npy -m unittest tests/main.py -v\n```\n\n## License\n\n**sefazetllib** is released under the [Apache-2.0](/LICENSE).\n',
    'author': 'Felipe Gochi',
    'author_email': 'felipe.gochi@elogroup.com.br',
    'maintainer': 'Bruno Santos',
    'maintainer_email': 'bruno.santos@elogroup.com.br',
    'url': 'https://sa-east-1.console.aws.amazon.com/codesuite/codecommit/repositories/jobs-lib-sefaz-ce/browse?region=sa-east-1',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
