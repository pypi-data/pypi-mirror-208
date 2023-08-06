# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vaillant_plus_cn_api']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.0,<4.0.0']

setup_kwargs = {
    'name': 'vaillant-plus-cn-api',
    'version': '0.3.5',
    'description': 'Python package for interacting with Vaillant devices sold in China mainland using API',
    'long_description': '# vaillant-plus-cn-api\nPython package for interacting with Vaillant devices sold in China mainland through APIs in Vaillant plus app.\n',
    'author': 'daxingplay',
    'author_email': 'daxingplay@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/daxingplay/vaillant-plus-cn-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9',
}


setup(**setup_kwargs)
