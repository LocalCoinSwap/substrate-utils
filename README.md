# substrate-utils
Substrate utility library providing functionality for exchange management and multi-signature trading, originally built for [LocalCoinSwap](https://localcoinswap.com)

![Python package](https://github.com/LocalCoinSwap/substrate-utils/workflows/Python%20package/badge.svg) [![PyPI pyversions](https://img.shields.io/pypi/pyversions/substrate-utils.svg?v-0.2.1)](https://pypi.org/project/substrate-utils/) [![PyPI version shields.io](https://img.shields.io/pypi/v/substrate-utils.svg?v-0.2.1)](https://pypi.python.org/pypi/substrate-utils/)

The focus of this library is on functionality needed to provide an exchange service, including:

- Account generation
- Balance checking
- Making transfers
- Creating N/M (2/3) escrow addresses
- Non-custodial trades
- Cancellation of trades
- Administration of trade disputes
- Verification of transactions
- Diagnostics for common problems
- Associated cryptography

For complete examples please review the documentation. If there's any exchange functionality you need which we haven't provided, feel free to raise an issue in Github.

----

## Installation
```
pip install substrate-utils
```

## Quick start
```
from substrateutils import Kusama, Polkadot, Kulupu
kusama = Kusama()
polkadot = Polkadot()
kulupu = Kulupu()
```

## Documentation

[https://localcoinswap.github.io/substrate-utils/](https://localcoinswap.github.io/substrate-utils/)

# Local development

## Pre-requisites

 - Python 3.8.1 (preferred)

We suggest using [`pyenv`](https://github.com/pyenv/pyenv-virtualenv) to easily manage python versions. Some of the following commands use `pyenv`.
Use [pyenv-installer](https://github.com/pyenv/pyenv-installer) for easy installation. Then add pyenv-virtualenv plugin to it.

### Configure local development setup

 - Install and activate python 3.8.1 in the root directory
    - `pyenv install 3.8.1`
    - `pyenv virtualenv 3.8.1 substrateutils`
    - `pyenv local substrateutils`

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

### Notes

Trade storage calls for 2/3 trades cost:  
```
Polkadot - 40.3040 DOT  
Kusama   - 6.71733331304 KSM  
```
