# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nzooherd_torch']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'nzooherd-torch',
    'version': '0.1.3',
    'description': '',
    'long_description': '',
    'author': 'nzooherd',
    'author_email': 'nzooherd@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
