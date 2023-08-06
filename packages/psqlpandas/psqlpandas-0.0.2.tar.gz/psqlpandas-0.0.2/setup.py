# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['psqlpandas', 'psqlpandas.scripts']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.24.2,<2.0.0',
 'pandas>=2.0.1,<3.0.0',
 'psycopg2>=2.9.5,<3.0.0',
 'sqlalchemy>=2.0.3,<3.0.0']

setup_kwargs = {
    'name': 'psqlpandas',
    'version': '0.0.2',
    'description': 'Utilities to communicate with postgresql database through pandas dataframes.',
    'long_description': '# psqlpandas\nUtilities to communicate with postgresql database through pandas dataframes.\n\n## Installation\n```\npip install psqlpandas\n```\n\n## Usage\nDescribe how to launch and use psqlpandas project.\n',
    'author': 'Mattia Tantardini',
    'author_email': 'mattia.tantardini@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
