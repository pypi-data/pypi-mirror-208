# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyokx', 'pyokx.tests']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.6.0,<0.7.0',
 'pandas>=1.4.3,<2.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'requests>=2.28.1,<3.0.0',
 'typeguard>=2.13.3,<3.0.0']

setup_kwargs = {
    'name': 'pyokx',
    'version': '0.7.0',
    'description': 'Unofficial python wrapper for the OKX V5 API',
    'long_description': '# pyokx \n[![Downloads](https://pepy.tech/badge/pyokx)](https://pepy.tech/project/pyokx)\n![Tests](https://github.com/nicelgueta/pyokx/actions/workflows/pyokx.yml/badge.svg)\n## Installation\n\n```shell\npip install pyokx\n```\n\n## Introduction\n\npyokx is a completely unofficial python API wrapper developed to interact with the OKX V5 API. \nIt\'s unique insofar as that it has been developed by scraping the API documentation to dynamically generate python code to provide an intuitive\npythonic interface for exact same API. This idea essentially is to avoid the need to create separate documentation for this wrapper and instead you can simply refer to the official OKX docs for API usage.\n\nIt\'s used by creating a base client instance to make and receive requests and passing that client to each API class (`APIComponent`), which has been dynamically generated from the API docs.\n\n\n**Let\'s start with an example.**\n\nLet\'s say we want to check all current positions.\n\nCheck out the docs for get balance here: https://www.okx.com/docs-v5/en/#rest-api-account-get-positions\n\nWe can see the endpoint belongs to the Account API and needs to be called with 3 parameters:\n![OKX-docs](get-pos.png)\n\nIn pyokx, you can see the method signature for the Account class is exactly the same:\n```python\ndef get_positions(\n        self,\n        instType: str = None,\n        instId: str = None,\n        posId: str = None,\n        use_proxy: bool = False,\n    ) -> APIReturn:\n```\n\nSo this can be easily implemented like so:\n\n1. Create `.env` file that contains your API information:\n```\n    KEY = replace_your_key_here\n    SECRET = replace_your_secret_here\n    PASSPHRASE = replace_your_passphrase_here\n```\n\n2. Read API information from `.env` and create the base client:\n```python\nimport os\n\n# python-dotenv should have been installed from the dependencies\nfrom dotenv import load_dotenv\nfrom pyokx import OKXClient, Account\n\n# read information from .env file\nload_dotenv()\n\n# create the base client:\nclient = OKXClient(\n    key = os.getenv(\'KEY\'),\n    secret = os.getenv(\'SECRET\'),\n    passphrase = os.getenv(\'PASSPHRASE\'),\n)\n...\n```\n\n3. Now you can create Account object and call endpoints\n```python\n...\n# create a component for the Account API by passing the client dependency\naccount = Account(client)\n\n# get positions\napi_response = account.get_positions()\n\n# you can convert to a pandas dataframe to make it more readable\ndf_response = api_response.to_df()\nprint(df_response)\n\n# or you can get the raw response\nraw_response = api_response.response\nprint(raw_response)\n```\n\nThat simple.\n\n______\n\n\n## Key features\n\n### APIReturn\n\nThis is essentially a wrapper around the response that is returned from every endpoint. This is to provide some useful helper methods such as dataframe conversion.\n\n### Proxies\n\nAs is common with a lot of exchange APIs, for calls that require authentication (usually account/trade-related), it is strongly encouraged to limit your API key to a select list IP addresses to protect your account. On some systems this may require routing traffic through a forward proxy. pyokx supports this pattern by allowing you to pass the necessary proxies to the base client and you can trigger this behaviour by setting the `use_proxy` parameter to `True`.\nFor example:\n```python\nproxies = {\n    "http": "http://your-proxy-server.com",\n    "https": "https://your-proxy-server.com",\n}\nclient = OKXClient(\n    key="key",\n    secret="secret",\n    passphrase="passphrase",\n    proxies=proxies\n)\n\n# trigger the use of the proxy server with use_proxy\naccount = Account(client)\napi_response = account.get_positions(use_proxy=True)\n\n```\n\n## Development progress\n\n**It\'s still a very early version - so issues, feature requests and bugs are very welcome!**\n\n- [x] REST API implementation.\n- [x] Fix pythonic naming conventions when API names contain special characters\n- [ ] Enhance documentation\n- [ ] Websocket API implementation. \n\n## Disclaimer\n> NB. pyokx is totally unofficial and is in no way affiliated with OKEX Crypto exchange and simply exists as a helpful wrapper to interact with the V5 API.',
    'author': 'nicelgueta',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
