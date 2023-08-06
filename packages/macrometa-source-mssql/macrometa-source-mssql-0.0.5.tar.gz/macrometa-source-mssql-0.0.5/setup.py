# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'macrometa_source_mssql'}

packages = \
['macrometa_source_mssql',
 'macrometa_source_mssql.sync_strategies',
 'sync_strategies']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=16.3.0',
 'c8connector>=0.0.20',
 'pendulum>=1.2.0',
 'pipelinewise-singer-python==1.2.0',
 'pymssql>=2.2.1']

entry_points = \
{'console_scripts': ['macrometa-source-mssql = macrometa_source_mssql:main']}

setup_kwargs = {
    'name': 'macrometa-source-mssql',
    'version': '0.0.5',
    'description': 'Macrometa Source for extracting data from Microsoft SQL Server.',
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
