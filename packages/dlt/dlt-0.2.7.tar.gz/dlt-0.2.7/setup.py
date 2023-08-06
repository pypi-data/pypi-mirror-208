# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dlt',
 'dlt.cli',
 'dlt.common',
 'dlt.common.configuration',
 'dlt.common.configuration.providers',
 'dlt.common.configuration.specs',
 'dlt.common.data_types',
 'dlt.common.data_writers',
 'dlt.common.destination',
 'dlt.common.json',
 'dlt.common.normalizers',
 'dlt.common.normalizers.json',
 'dlt.common.normalizers.naming',
 'dlt.common.reflection',
 'dlt.common.runners',
 'dlt.common.runtime',
 'dlt.common.schema',
 'dlt.common.storages',
 'dlt.destinations',
 'dlt.destinations.bigquery',
 'dlt.destinations.duckdb',
 'dlt.destinations.dummy',
 'dlt.destinations.postgres',
 'dlt.destinations.redshift',
 'dlt.extract',
 'dlt.helpers',
 'dlt.helpers.dbt',
 'dlt.load',
 'dlt.normalize',
 'dlt.pipeline',
 'dlt.reflection',
 'dlt.sources',
 'dlt.sources.helpers',
 'dlt.sources.helpers.requests']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1',
 'SQLAlchemy>=1.4.0',
 'astunparse>=1.6.3',
 'asyncstdlib>=3.10.5',
 'cachetools>=5.2.0',
 'click>=7.1',
 'cron-descriptor>=1.2.32',
 'deprecated>=1.2.13,<2.0.0',
 'gitpython>=3.1.29',
 'giturlparse>=0.10.0',
 'hexbytes>=0.2.2',
 'humanize>=4.4.0',
 'json-logging==1.4.1rc0',
 'jsonpath-ng>=1.5.3,<2.0.0',
 'makefun>=1.15.0',
 'pathvalidate>=2.5.2',
 'pendulum>=2.1.2',
 'pipdeptree>=2.3.3',
 'psutil>=5.9.5,<6.0.0',
 'pytz>=2022.6',
 'requests>=2.26.0',
 'requirements-parser>=0.5.0',
 'semver>=2.13.0',
 'sentry-sdk>=1.4.3',
 'setuptools>=65.6.0',
 'simplejson>=3.17.5',
 'tenacity>=8.2.2,<9.0.0',
 'tomlkit>=0.11.3',
 'typing-extensions>=4.0.0',
 'tzdata>=2022.1']

extras_require = \
{':platform_python_implementation != "PyPy"': ['orjson>=3.8.6,<4.0.0'],
 'bigquery': ['grpcio>=1.50.0',
              'google-cloud-bigquery>=2.26.0',
              'pyarrow>=8.0.0'],
 'dbt': ['dbt-core>=1.3.0,<1.5.0',
         'dbt-redshift>=1.3.0,<1.5.0',
         'dbt-bigquery>=1.3.0,<1.5.0',
         'dbt-duckdb>=1.3.0,<1.5.0'],
 'duckdb': ['duckdb>=0.6.1,<0.8.0'],
 'gcp': ['grpcio>=1.50.0', 'google-cloud-bigquery>=2.26.0', 'pyarrow>=8.0.0'],
 'postgres': ['psycopg2-binary>=2.9.1'],
 'postgres:platform_python_implementation == "PyPy"': ['psycopg2cffi>=2.9.0'],
 'redshift': ['psycopg2-binary>=2.9.1'],
 'redshift:platform_python_implementation == "PyPy"': ['psycopg2cffi>=2.9.0']}

entry_points = \
{'console_scripts': ['dlt = dlt.cli._dlt:_main']}

setup_kwargs = {
    'name': 'dlt',
    'version': '0.2.7',
    'description': 'DLT is an open-source python-native scalable data loading framework that does not require any devops efforts to run.',
    'long_description': '<h1 align="center">\n    <strong>data load tool (dlt) — the open-source Python library for data loading</strong>\n</h1>\n<p align="center">\nBe it a Google Colab notebook, AWS Lambda function, an Airflow DAG, your local laptop,<br/>or a GPT-4 assisted development playground—<strong>dlt</strong> can be dropped in anywhere.\n</p>\n\n<div align="center">\n  <a target="_blank" href="https://join.slack.com/t/dlthub-community/shared_invite/zt-1slox199h-HAE7EQoXmstkP_bTqal65g" style="background:none">\n    <img src="https://img.shields.io/badge/slack-join-dlt.svg?labelColor=191937&color=6F6FF7&logo=slack" />\n  </a>\n  <a target="_blank" href="https://pypi.org/project/dlt/" style="background:none">\n    <img src="https://img.shields.io/pypi/v/dlt?labelColor=191937&color=6F6FF7">\n  </a>\n  <a target="_blank" href="https://pypi.org/project/dlt/" style="background:none">\n    <img src="https://img.shields.io/pypi/pyversions/dlt?labelColor=191937&color=6F6FF7">\n  </a>\n</div>\n\n## Installation\n\ndlt supports Python 3.8+.\n\n```bash\npip install dlt\n```\n\n## Quick Start\n\nLoad chess game data from chess.com API and save it in DuckDB:\n\n```python\nimport dlt\nfrom chess import chess # a utility function that grabs data from the chess.com API\n\n# create a dlt pipeline that will load chess game data to the DuckDB destination\npipeline = dlt.pipeline(\n    pipeline_name=\'chess_pipeline\',\n    destination=\'duckdb\',\n    dataset_name=\'games_data\'\n)\n\n# use chess.com API to grab data about a few players\ndata = chess([\'magnuscarlsen\', \'rpragchess\'], start_month=\'2022/11\', end_month=\'2022/12\')\n\n# extract, normalize, and load the data\npipeline.run(data)\n```\n\nTry it out in our **[Colab Demo](https://colab.research.google.com/drive/1NfSB1DpwbbHX9_t5vlalBTf13utwpMGx?usp=sharing)**\n\n## Features\n\n- **Automatic Schema:** Data structure inspection and schema creation for the destination.\n- **Data Normalization:** Consistent and verified data before loading.\n- **Seamless Integration:** Colab, AWS Lambda, Airflow, and local environments.\n- **Scalable:** Adapts to growing data needs in production.\n- **Easy Maintenance:** Clear data pipeline structure for updates.\n- **Rapid Exploration:** Quickly explore and gain insights from new data sources.\n- **Versatile Usage:** Suitable for ad-hoc exploration to advanced loading infrastructures.\n- **Start in Seconds with CLI:** Powerful CLI for managing, deploying and inspecting local pipelines.\n- **Incremental Loading:** Load only new or changed data and avoid loading old records again.\n- **Open Source:** Free and Apache 2.0 Licensed.\n\n## Ready to use Pipelines and Destinations\n\nExplore ready to use pipelines (e.g. Google Sheets) in the [Pipelines docs](https://dlthub.com/docs/pipelines/chess) and supported destinations (e.g. DuckDB) in the [Destinations docs](https://dlthub.com/docs/destinations/bigquery).\n\n## Documentation\n\nFor detailed usage and configuration, please refer to the [official documentation](https://dlthub.com/docs).\n\n## Examples\n\nYou can find examples for various use cases in the [examples](docs/examples) folder.\n\n## Get Involved\n\nThe dlt project is quickly growing, and we\'re excited to have you join our community! Here\'s how you can get involved:\n\n- **Connect with the Community**: Join other dlt users and contributors on our [Slack](https://join.slack.com/t/dlthub-community/shared_invite/zt-1slox199h-HAE7EQoXmstkP_bTqal65g)\n- **Report issues and suggest features**: Please use the [GitHub Issues](https://github.com/dlt-hub/dlt/issues) to report bugs or suggest new features. Before creating a new issue, make sure to search the tracker for possible duplicates and add a comment if you find one.\n- **Contribute Pipelines**: Pipelines are data processing steps that help move and transform data between various sources and destinations. Contribute your custom pipelines to the [dlt-hub/pipelines](https://github.com/dlt-hub/pipelines) to help other folks in handling their data tasks.\n- **Contribute code**: Check out our [contributing guidelines](CONTRIBUTING.md) for information on how to make a pull request.\n- **Improve documentation**: Help us enhance the dlt documentation.\n\n## License\n\nDLT is released under the [Apache 2.0 License](LICENSE.txt).\n',
    'author': 'dltHub Inc.',
    'author_email': 'services@dlthub.com',
    'maintainer': 'Marcin Rudolf',
    'maintainer_email': 'marcin@dlthub.com',
    'url': 'https://github.com/dlt-hub',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
