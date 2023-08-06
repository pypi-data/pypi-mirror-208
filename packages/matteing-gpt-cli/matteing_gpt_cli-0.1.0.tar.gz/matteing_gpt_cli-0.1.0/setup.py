# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gpt_cli']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'openai>=0.27.4,<0.28.0',
 'rich>=13.3.4,<14.0.0',
 'yaspin>=2.3.0,<3.0.0']

entry_points = \
{'console_scripts': ['gpt-cli = gpt_cli:main']}

setup_kwargs = {
    'name': 'matteing-gpt-cli',
    'version': '0.1.0',
    'description': '',
    'long_description': '',
    'author': 'Sergio Mattei',
    'author_email': 'sergiomattei@outlook.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
