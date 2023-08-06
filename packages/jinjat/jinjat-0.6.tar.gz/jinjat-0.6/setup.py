# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['jinjat',
 'jinjat.core',
 'jinjat.core.dbt',
 'jinjat.core.routes',
 'jinjat.core.schema',
 'jinjat.core.util',
 'jinjat.deploy']

package_data = \
{'': ['*']}

install_requires = \
['bottle>=0.12.23,<0.13.0',
 'click>7',
 'dbt-core==1.5.0',
 'deepmerge>=1.1.0,<2.0.0',
 'fastapi>=0.85.0,<0.86.0',
 'jinja2-simple-tags>=0.4.0,<0.5.0',
 'jmespath>=1.0.1,<2.0.0',
 'jsonref>=1.1.0,<2.0.0',
 'jsonschema>=3.0,<4.0',
 'openapi-schema-pydantic>=1.2.4,<2.0.0',
 'orjson>=3.8.0,<4.0.0',
 'pandas>=1.5.3,<2.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'rich>=10',
 'ruamel.yaml>=0.17',
 'sqlglot==12.3.0',
 'uvicorn[standard]>=0.18.3,<0.19.0',
 'watchdog>=2.2.1']

extras_require = \
{':extra == "deploy"': ['fal-serverless==0.6.29', 'modal-client==0.49.2059'],
 'duckdb': ['duckcli>=0.2.1,<0.3.0', 'dbt-duckdb>=1.5.0,<2.0.0'],
 'playground': ['streamlit>=1.0.0',
                'streamlit-ace>=0.1.0',
                'graphviz>=0.17',
                'pydot>=1.4.2',
                'streamlit-agraph>=0.0.35',
                'streamlit-pandas-profiling>=0.1.3',
                'streamlit-aggrid>=0.2.2',
                'scipy>=1.3.1,<2.0.0',
                'feedparser>=6.0.10,<7.0.0']}

entry_points = \
{'console_scripts': ['jinjat = jinjat.main:cli']}

setup_kwargs = {
    'name': 'jinjat',
    'version': '0.6',
    'description': 'A low-code data application framework that uses dbt Core and OpenAPI',
    'long_description': '# Jinjat\n\n## Develop data applications with dbt, SQL, and OpenAPI\n\n### Installation\n\n```commandline\npip install jinjat\n```\n\n### Create your first API\n\nCreate an [analysis]() in `analysis/my_first_api.sql`:\n```sql\n{%- set query = request().query %}\n\nselect \'{{query.example}}\' as col1\n```\n\nAnd create a YML file in `analysis/schema.yml`:\n\n```yml\nversion: 2\n\nanalyses:\n  - name: my_first_api\n    config:\n      jinjat:\n        method: get\n        openapi:\n          parameters:\n            - in: query\n              name: example\n              schema:\n                type: number\n```\n\nStart Jinjat as follows:\n\n```commandline\njinjat serve --project-dir [YOUR_DBT_PROJECT_DIRECTORY]\n```\n\nAnd then run the following CURL command to test the API:\n\n```commandline\ncurl -XGET \'http://127.0.0.1:8581?example=value\'\n```\n\nIt should return the following response:\n\n```json\n[\n  "col1": "3"\n]\n```\n\nJinjat uses OpenAPI to validate the requests and create an API documentation automatically for your API.\n\n## Integrations\n\npoetry install --extras "duckdb"\n\n### Playground\n\npoetry install --extras "playground"\n\n\n#### Installation\n\n```commandline\npip install jinjat[playground]\n```\n\nJinjat Playground is a Streamlit app that lets you develop APIs in your browser.\nOnce you write the template, you can save it to your dbt project as an analysis and expose the API.',
    'author': 'buremba',
    'author_email': 'emrekabakci@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/jinjat-data/jinjat',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8.1,<4',
}


setup(**setup_kwargs)
