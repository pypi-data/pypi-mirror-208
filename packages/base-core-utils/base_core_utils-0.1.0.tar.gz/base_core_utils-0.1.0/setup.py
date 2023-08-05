# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['base_core_utils', 'base_core_utils.db', 'base_core_utils.models']

package_data = \
{'': ['*']}

install_requires = \
['asyncpg>=0.27.0,<0.28.0',
 'grpcio-tools>=1.54.0,<2.0.0',
 'grpcio>=1.54.0,<2.0.0',
 'grpclib>=0.4.4,<0.5.0',
 'protobuf>=4.23.0,<5.0.0',
 'sqlalchemy>=2.0.13,<3.0.0']

setup_kwargs = {
    'name': 'base-core-utils',
    'version': '0.1.0',
    'description': 'Common base classes for microservices',
    'long_description': '',
    'author': 'Dmitry Roshupkin',
    'author_email': 'd3po13@yandex.ru',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
