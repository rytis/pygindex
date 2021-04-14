# PyGIndex

Python library/framework to access and trade on IG Index

[![PyPI Version][pypi-image]][pypi-url]
[![Python Version][python-image]][pypi-url]
[![Build Status][build-image]][build-url]
[![Code Coverage][coverage-image]][coverage-url]
[![Code Quality][quality-image]][quality-url]
[![Documentation][rtd-image]][rtd-url]

# Installing

Install and update using pip:

    pip install -U pygindex

# Examples

## Get session details

    from pygindex.client import IGClient
    
    c = IGClient()
    s = c.get_session_details()
    print(s)

Will produce

    {'clientId': 'XXXXXXXXX', 
     'accountId': 'XXXXX', 
     'timezoneOffset': 1, 
     'locale': 'en_GB', 
     'currency': 'GBP', 
     'lightstreamerEndpoint': 'https://apd.marketdatasystems.com'}

# Links

* [Documentation][rtd-url]
* [PyPI][pypi-url]
* [Source](https://github.com/rytis/pygindex/)
* [Issues](https://github.com/rytis/pygindex/issues/)

<!-- Links -->

[python-image]: https://img.shields.io/pypi/pyversions/pygindex
[pypi-image]: https://img.shields.io/pypi/v/pygindex
[pypi-url]: https://pypi.org/project/pygindex/
[build-image]: https://github.com/rytis/pygindex/actions/workflows/build.yml/badge.svg
[build-url]: https://github.com/rytis/ppygindex/actions/workflows/build.yml
[coverage-image]: https://codecov.io/gh/rytis/pygindex/branch/main/graph/badge.svg
[coverage-url]: https://codecov.io/gh/rytis/pygindex
[quality-image]: https://api.codeclimate.com/v1/badges/85717ac8e0612fa5d695/maintainability
[quality-url]: https://codeclimate.com/github/rytis/pygindex
[rtd-image]: https://img.shields.io/readthedocs/pygindex
[rtd-url]: https://pygindex.readthedocs.io