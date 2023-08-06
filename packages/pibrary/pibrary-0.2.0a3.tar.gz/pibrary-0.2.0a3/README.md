# Pibrary

<p align="center">
    <em>Pibrary framework: A package for reusable code for ML projects</em>
</p>
<p align="center">
    <a href="https://github.com/connectwithprakash/pibrary/actions?query=workflow%3ATest+event%3Apush+branch%3Amain" target="_blank">
        <img src="https://github.com/connectwithprakash/pibrary/workflows/Test/badge.svg?event=push&branch=main" alt="Test">
    </a>
    <a href='https://pibrary.readthedocs.io/en/latest/?badge=latest'>
        <img src='https://readthedocs.org/projects/pibrary/badge/?version=latest' alt='Documentation Status' />
    </a>
    <a href="https://pypi.org/project/pibrary" target="_blank">
        <img src="https://img.shields.io/pypi/v/pibrary?color=%2334D058&label=pypi%20package" alt="Package version">
    </a>
    <a href="https://pypi.org/project/pibrary" target="_blank">
        <img src="https://img.shields.io/pypi/pyversions/pibrary.svg?color=%2334D058" alt="Supported Python versions">
    </a>
    <a href="https://opensource.org/licenses/MIT" target="_blank">
        <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
    </a>
</p>

## Installation

```bash
pip install pibrary
```

## Usage
```python
from pibrary.file import File
from pibrary.logger import timeit
from pibrary.string import String

# File Class
dataframe = File(file_path).read().csv()
File(file_path).write(dataframe).csv()

json_data = File(file_path).read().json()
File(file_path).write(json_data).csv()

pickle_data = File(file_path).read().pickle()
File(file_path).write(pickle_data).csv()

# Logger
@timeit
def some_function(...):
    ...

# String Class
new_text = String(text).lower().remove_digits().remove_punctuation().strip()
```

## Documentation

The full documentation for Pibrary is available at https://pibrary.readthedocs.io/en/latest/.

## Contributing
Contributions are welcome! Please read [CONTRIBUTING](CONTRIBUTING) for details on how to contribute to this project.


# License
This project is licensed under the terms of the [MIT license](LICENSE).
