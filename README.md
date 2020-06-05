# kusama-utils
Kusama utility library providing functionality for multi-signature trading, originally built for [LocalCoinSwap](https://localcoinswap.com)

![Python package](https://github.com/LocalCoinSwap/kusama-utils/workflows/Python%20package/badge.svg) [![PyPI pyversions](https://img.shields.io/pypi/pyversions/ksmutils.svg?v-0.0.3)](https://pypi.org/project/ksmutils/) [![PyPI version shields.io](https://img.shields.io/pypi/v/ksmutils.svg)](https://pypi.python.org/pypi/ksmutils/)



----

## Installation
```
pip install ksmutils
```

## Quick start
```
from ksmutils import Kusama
kusama = Kusama()
```

## Documentation

[https://localcoinswap.github.io/kusama-utils/](https://localcoinswap.github.io/kusama-utils/)

# Local development

## Pre-requisites

 - Python 3.8.1 (preferred)

We suggest using [`pyenv`](https://github.com/pyenv/pyenv-virtualenv) to easily manage python versions. Some of the following commands use `pyenv`.
Use [pyenv-installer](https://github.com/pyenv/pyenv-installer) for easy installation. Then add pyenv-virtualenv plugin to it.

### Configure local development setup

 - Install and activate python 3.8.1 in the root directory
    - `pyenv install 3.8.1`
    - `pyenv virtualenv 3.8.1 ksmutils`
    - `pyenv local ksmutils`

 - Install project requirements
    - `pip install -r requirements.txt`

 - Install precommit hook
    - `pre-commit install`

You're all set to hack!

Before making changes, let's ensure tests run successfully on local.

### Running Tests

 - Run all tests with coverage
    - `coverage run -m pytest -v`
 - Show report in terminal
    - `coverage report -m`
