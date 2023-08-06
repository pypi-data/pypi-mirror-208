# Elliptic SDK for Python

## Installation

The SDK is available on PyPI:

``` shell
python -m pip install elliptic-python
```

This package requires Python 3.7 or greater

## Usage

The SDK provides an instance of the popular [Requests
package](https://requests.readthedocs.io/en/latest/), adding the
necessary steps to authenticate each request using your Elliptic API key
and secret.

``` python
from elliptic import AML

aml = AML(key="YOUR_ELLIPTIC_API_KEY", secret="YOUR_ELLIPTIC_API_SECRET")

# aml.client is an instance of a requests session
response = aml.client.get("/v2/analyses")
```

## API Documentation

Documentation for Elliptic APIs can be found at the [Elliptic Developer Center](https://developers.elliptic.co)

## License
This SDK is distributed under the Apache License, Version 2.0, see LICENSE and NOTICE for more information.