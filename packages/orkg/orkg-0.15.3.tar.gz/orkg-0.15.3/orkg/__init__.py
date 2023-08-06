from orkg.client import ORKG
from orkg.common import OID
from orkg.graph import subgraph

import logging

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logger = logging.getLogger("ORKG")
logger.addHandler(logging.NullHandler())
