# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'source/packages'}

packages = \
['mojo', 'mojo.networking']

package_data = \
{'': ['*']}

install_requires = \
['netifaces>=0.11.0,<0.12.0', 'requests>=2.29.0,<3.0.0']

setup_kwargs = {
    'name': 'mojo-networking',
    'version': '0.0.5',
    'description': 'Automation Mojo Netorking Package (mojo-networking)',
    'long_description': '# python-package-template\nThis is a template repository that can be used to quickly create a python package project.\n',
    'author': 'None',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
