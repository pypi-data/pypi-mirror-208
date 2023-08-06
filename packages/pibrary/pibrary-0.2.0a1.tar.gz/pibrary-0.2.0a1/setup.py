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
    'version': '0.2.0a1',
    'description': 'A package for reusable code for ML projects.',
    'long_description': '# Pibrary\n\n<p align="center">\n    <em>Pibrary framework: A package for reusable code for ML projects</em>\n</p>\n<p align="center">\n    <a href="https://github.com/connectwithprakash/pibrary/actions?query=workflow%3ATest+event%3Apush+branch%3Amain" target="_blank">\n        <img src="https://github.com/connectwithprakash/pibrary/workflows/Test/badge.svg?event=push&branch=main" alt="Test">\n    </a>\n    <a href="https://pypi.org/project/pibrary" target="_blank">\n        <img src="https://img.shields.io/pypi/v/pibrary?color=%2334D058&label=pypi%20package" alt="Package version">\n    </a>\n    <a href="https://pypi.org/project/pibrary" target="_blank">\n        <img src="https://img.shields.io/pypi/pyversions/pibrary.svg?color=%2334D058" alt="Supported Python versions">\n    </a>\n    <a href="https://opensource.org/licenses/MIT" target="_blank">\n        <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">\n    </a>\n</p>\n\n## Installation\n\n```bash\npip install pibrary\n```\n\n## Usage\n```python\nfrom pibrary.file import File\nfrom pibrary.logger import timeit\nfrom pibrary.string import String\n\n# File Class\ndataframe = File(file_path).read().csv()\nFile(file_path).write(dataframe).csv()\n\njson_data = File(file_path).read().json()\nFile(file_path).write(json_data).csv()\n\npickle_data = File(file_path).read().pickle()\nFile(file_path).write(pickle_data).csv()\n\n# Logger\n@timeit\ndef some_function(...):\n    ...\n\n# String Class\nnew_text = String(text).lower().remove_digits().remove_punctuation().strip()\n```\n\n## Contributing\nContributions are welcome! Please read [CONTRIBUTING](CONTRIBUTING) for details on how to contribute to this project.\n\n\n# License\nThis project is licensed under the terms of the [MIT license](LICENSE).\n',
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
