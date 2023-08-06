# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['symbolconnectors',
 'symbolconnectors.bindings',
 'symbolconnectors.connector',
 'symbolconnectors.model']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp==3.8.4', 'symbol-sdk-python==3.0.7', 'zenlog==1.1']

setup_kwargs = {
    'name': 'symbol-connectors',
    'version': '0.0.1',
    'description': 'Symbol Connectors',
    'long_description': '# Python Connectors\n\nProvides partial Python wrappers for calling NEM and Symbol API functions.\n\nOnly a subset of APIs are currently supported.\n\nPRs are accepted for extending the set of APIs.\n',
    'author': 'Symbol Contributors',
    'author_email': 'contributors@symbol.dev',
    'maintainer': 'Symbol Contributors',
    'maintainer_email': 'contributors@symbol.dev',
    'url': 'https://github.com/symbol/product/tree/main/python/connectors',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
