# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pibrary']

package_data = \
{'': ['*']}

install_requires = \
['joblib>=1.2.0,<2.0.0', 'loguru>=0.7.0,<0.8.0', 'pandas>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'pibrary',
    'version': '0.1.0a1',
    'description': 'A package for reusable code for ML projects.',
    'long_description': '# pibrary\nThis repo contains all the scripts/module that I have written and useful for other projects as well.\n',
    'author': 'Prakash Chaudhary',
    'author_email': 'connectwithprakash@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
