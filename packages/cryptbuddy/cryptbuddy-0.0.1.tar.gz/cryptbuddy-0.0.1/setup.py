# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cryptbuddy',
 'cryptbuddy.commands',
 'cryptbuddy.cryptlib',
 'cryptbuddy.cryptlib.symmetric']

package_data = \
{'': ['*']}

install_requires = \
['PyNaCl>=1.5.0,<2.0.0',
 'appdirs>=1.4.4,<2.0.0',
 'msgpack>=1.0.5,<2.0.0',
 'password-strength>=0.0.3.post2,<0.0.4',
 'tabulate>=0.9.0,<0.10.0',
 'typer[all]>=0.9.0,<0.10.0']

entry_points = \
{'console_scripts': ['cb = cryptbuddy.main:app',
                     'crypt = cryptbuddy.main:app',
                     'cryptbuddy = cryptbuddy.main:app']}

setup_kwargs = {
    'name': 'cryptbuddy',
    'version': '0.0.1',
    'description': '',
    'long_description': '',
    'author': 'Kush Patel',
    'author_email': 'kush@kush.in',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
