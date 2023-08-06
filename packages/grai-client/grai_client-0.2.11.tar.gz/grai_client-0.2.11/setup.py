# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['grai_client',
 'grai_client.endpoints',
 'grai_client.endpoints.v1',
 'grai_client.schemas',
 'grai_client.testing',
 'grai_client.utilities']

package_data = \
{'': ['*']}

install_requires = \
['brotli>=1.0.9,<2.0.0',
 'grai-schemas>=0.1.11,<0.2.0',
 'httpx[http2]>=0.24.0,<0.25.0',
 'multimethod>=1.9,<2.0',
 'orjson>=3.8.3,<4.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'pyyaml>=6.0,<7.0',
 'requests>=2.28.1,<3.0.0',
 'tqdm>=4.65.0,<5.0.0',
 'trio>=0.22.0,<0.23.0']

setup_kwargs = {
    'name': 'grai-client',
    'version': '0.2.11',
    'description': '',
    'long_description': "# Grai Client\n\n`grai-client` is Grai's python connector for communication with the Grai server.\nIt provides easy to use functionality for querying your metadata graph.\n",
    'author': 'Ian Eaves',
    'author_email': 'ian@grai.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://www.grai.io/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
