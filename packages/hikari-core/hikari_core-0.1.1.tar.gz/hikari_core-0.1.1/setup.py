# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hikari_core', 'hikari_core.Html_Render', 'hikari_core.moudle']

package_data = \
{'': ['*'],
 'hikari_core': ['Template/*'],
 'hikari_core.Html_Render': ['templates/*', 'templates/katex/*']}

install_requires = \
['APScheduler>=3.10.1,<4.0.0',
 'aiofiles>=0.8.0',
 'asyncio>=3.4.3,<4.0.0',
 'httpx[http2]>=0.24.0',
 'jinja2>=3.1.2,<4.0.0',
 'orjson>=3.8.11,<4.0.0',
 'playwright>=1.17.2',
 'pydantic>=1.10.7,<2.0.0']

setup_kwargs = {
    'name': 'hikari-core',
    'version': '0.1.1',
    'description': '',
    'long_description': '# Hikari-core\nSDK for yuyuko API\n',
    'author': 'benx1n',
    'author_email': '1119809439@qq.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
