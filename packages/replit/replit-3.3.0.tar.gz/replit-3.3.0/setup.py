# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['replit',
 'replit.audio',
 'replit.database',
 'replit.goval',
 'replit.goval.api',
 'replit.goval.api.features',
 'replit.goval.api.repl',
 'replit.identity',
 'replit.web']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.0.0,<3.0.0',
 'Werkzeug>=2.0.0,<3.0.0',
 'aiohttp>=3.6.2,<4.0.0',
 'protobuf>=4.21.8,<5.0.0',
 'pyseto>=1.6.11,<2.0.0',
 'requests>=2.25.1,<3.0.0',
 'typing_extensions>=3.7.4,<4.0.0']

entry_points = \
{'console_scripts': ['replit = replit.__main__:cli']}

setup_kwargs = {
    'name': 'replit',
    'version': '3.3.0',
    'description': 'A library for interacting with features of repl.it',
    'long_description': '### `>>> import replit`\n\n![compute](https://github.com/kennethreitz42/replit-py/blob/kr-cleanup/ext/readme.gif?raw=true)\n\nThis repository is the home for the `replit` Python package, which provides:\n\n- A fully-featured database client for [Replit DB](https://docs.repl.it/misc/database).\n- A Flask–based application framework for accelerating development on the platform.\n- Replit user profile metadata retrieval (more coming here!).\n- A simple audio library that can play tones and audio files!\n\n### Open Source License\n\nThis library is licensed under the [ISC License](https://en.wikipedia.org/wiki/ISC_license) and is free for you to use, change, or even profit from!\n',
    'author': 'Repl.it',
    'author_email': 'contact@repl.it',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/replit/replit-py',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
