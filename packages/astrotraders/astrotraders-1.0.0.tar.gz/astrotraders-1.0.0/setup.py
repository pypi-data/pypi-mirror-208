# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['astrotraders', 'astrotraders.api', 'astrotraders.api.resources']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.24.0,<0.25.0', 'orjson>=3.8.12,<4.0.0', 'pydantic>=1.10.7,<2.0.0']

setup_kwargs = {
    'name': 'astrotraders',
    'version': '1.0.0',
    'description': 'A typed, handwrited and powerful spacetraders API wrapper',
    'long_description': '# astrotraders\n\nA typed, handwrited and powerful library for spacetraders.io game.\n\nSpaceTraders is an API-based game where you acquire and manage a fleet of ships to explore, trade, and fight your way across the galaxy.\n\nThis client based on [HTTPX](https://www.python-httpx.org/) and [Pydantic](https://docs.pydantic.dev/latest/).\n\n## Install\n```\npip install astrotraders\n```\n\n## Usage\n\nCurrently, you can use API wrapper which  represented by `AstroTradersClient` class:\n\n```python\nfrom astrotraders import AstroTradersClient\nclient = AstroTradersClient.set_up(\n    "token_here",\n)\n```\n\nAfter initializing client you can use API resources, for example:\n\n```python\nagent = client.agents.info()\nsystems = client.systems.list()\ncontracts = client.contracts.list()\nfactions = client.factions.list()\n```\n\n## TODO\n1. "Game objects" with data caching and more pythonic usage\n2. CLI tool for manage fleet (and as example)\n',
    'author': 'kiriharu',
    'author_email': 'me@kiriha.ru',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
