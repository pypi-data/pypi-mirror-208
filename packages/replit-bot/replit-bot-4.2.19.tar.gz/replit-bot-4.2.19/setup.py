# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['replit_bot', 'replit_bot.utils']

package_data = \
{'': ['*'], 'replit_bot': ['templates/*']}

install_requires = \
['Flask>=2.2.0,<3.0.0',
 'pyee>=9.0.4,<10.0.0',
 'replit>=3.2.4,<4.0.0',
 'requests>=2.28.1,<3.0.0',
 'waitress>=2.1.2,<3.0.0']

setup_kwargs = {
    'name': 'replit-bot',
    'version': '4.2.19',
    'description': 'make discord.py like bots on replit and/or do replapi-it style replit interactions',
    'long_description': None,
    'author': 'bigminboss',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0.0',
}


setup(**setup_kwargs)
