"""
This module provides an SDK to assist in making requests to the Elliptic APIs

FUNCTIONS:
    AML:
        The AML function provides a configured Session from the requests
        package (https://pypi.org/project/requests/). It must be provided
        with your Elliptic API key and secret, and the client attribute
        on the returned instance holds the configured session, which
        can be called using the regular requests methods.

        Example:

        from elliptic import AML

        aml = AML(
            key="YOUR_ELLIPTIC_API_KEY",
            secret="YOUR_ELLIPTIC_API_SECRET",
        )

        # aml.client is a requests session
        response = aml.client.get("/v2/analyses")
"""
from .aml import AML

__all__ = ['AML', ]
