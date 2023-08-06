# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['elefantolib',
 'elefantolib.auth',
 'elefantolib.context',
 'elefantolib.http_client',
 'elefantolib.provider',
 'elefantolib.provider.django_provider',
 'elefantolib.provider.fastapi_provider',
 'elefantolib.websocket_client']

package_data = \
{'': ['*']}

install_requires = \
['exceptiongroup>=1.1.1,<2.0.0',
 'httpx>=0.24.0,<0.25.0',
 'pyjwt>=2.7.0,<3.0.0',
 'pytest-env>=0.8.1,<0.9.0',
 'websockets>=11.0.3,<12.0.0']

setup_kwargs = {
    'name': 'elefantolib',
    'version': '0.11.1',
    'description': 'Elefanto lib',
    'long_description': 'Elefantolib\n-----------------------\n\n   **NOTE:** After clone this repository you should run command:\n\n   ``git config core.hooksPath .githooks``\n',
    'author': 'Elefanto',
    'author_email': 'elefanto@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/elefanto-organization/elefantolib',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
