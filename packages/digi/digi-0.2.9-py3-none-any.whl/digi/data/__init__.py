import os
import logging

"""
The digi.data module provides a set of functions to load and query 
the digi's data router.
"""

logger = logging.getLogger(__name__)
if "LAKE" in os.environ:
    lake_url = os.environ["LAKE"]
elif "ZED_LAKE" in os.environ:
    lake_url = os.environ["ZED_LAKE"]
else:
    lake_url = "http://localhost:9867"

from digi.data.pool import create_pool
from digi.data.router import create_router
from digi.data.zed import Client
from digi.data.sync import Sync, Watch

# singleton used by the digi driver; router creates its own client(s)
lake = Client()

__all__ = [
    "Sync", "Watch",
    "create_router", "create_pool"
]
