# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oqpy']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.20.2,<2.0.0',
 'openpulse-poc @ vendor/openpulse_poc-0.0.9-py3-none-any.whl',
 'pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'oqpy',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'Philip Reinhold',
    'author_email': 'pcrein@amazon.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
