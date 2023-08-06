# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fiat', 'fiat.apps']

package_data = \
{'': ['*']}

install_requires = \
['docker>=6.0.1,<7.0.0',
 'envd>=0.3.21,<0.4.0',
 'ray[default]>=2.4.0,<3.0.0',
 'typer[all]>=0.7.0,<0.8.0']

entry_points = \
{'console_scripts': ['fiat = fiat.main:app']}

setup_kwargs = {
    'name': 'fiat-cli',
    'version': '0.7.0',
    'description': '🤩 - Fiat CLI Component',
    'long_description': '# Fiat CLI\n\n#### Description\n\n🛸 - The awesome Fiat CLI component!',
    'author': 'Jiacheng Li',
    'author_email': 'cheng2029@foxmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
