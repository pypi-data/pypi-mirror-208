"""Tools for interacting with Pitt-Google Broker data resources."""

try:
    from importlib import metadata

except ImportError:  # for Python<3.8
    import importlib_metadata as metadata

import logging
import os as os

from . import bigquery, figures, pubsub, utils

__version__ = metadata.version('pittgoogle-client')

for var in ["GOOGLE_CLOUD_PROJECT", "GOOGLE_APPLICATION_CREDENTIALS"]:
    if var not in os.environ:
        logger = logging.getLogger(__name__)
        logger.warning(
            f"Warning: The environment variable {var} is not set. "
            "This may impact your ability to connect to your "
            "Google Cloud Platform project."
        )
