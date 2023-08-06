# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'macrometa_source_postgres'}

packages = \
['macrometa_source_postgres',
 'macrometa_source_postgres.sync_strategies',
 'sync_strategies']

package_data = \
{'': ['*']}

install_requires = \
['c8connector>=0.0.20',
 'pipelinewise-singer-python==1.2.0',
 'psycopg2-binary==2.9.3',
 'strict-rfc3339==0.7']

entry_points = \
{'console_scripts': ['macrometa-source-postgres = '
                     'macrometa_source_postgres:main']}

setup_kwargs = {
    'name': 'macrometa-source-postgres',
    'version': '0.0.48',
    'description': 'Macrometa Source for extracting data from PostgreSQL.',
    'long_description': 'None',
    'author': 'Macrometa',
    'author_email': 'info@macrometa.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.1,<3.11',
}


setup(**setup_kwargs)
