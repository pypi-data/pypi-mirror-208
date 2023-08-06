# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['psycopg2_helper',
 'psycopg2_helper.bp',
 'psycopg2_helper.dmo',
 'psycopg2_helper.svc']

package_data = \
{'': ['*']}

install_requires = \
['baseblock', 'psycopg2']

setup_kwargs = {
    'name': 'psycopg2-helper',
    'version': '0.1.5',
    'description': 'Helper Functions for Postgres',
    'long_description': '# Postgres Helper (psycopg2-helper)\n',
    'author': 'Craig Trim',
    'author_email': 'craigtrim@gmail.com',
    'maintainer': 'Craig Trim',
    'maintainer_email': 'craigtrim@gmail.com',
    'url': 'https://github.com/craigtrim/psycopg2-helper',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.5,<4.0.0',
}


setup(**setup_kwargs)
