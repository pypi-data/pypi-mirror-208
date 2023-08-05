"""
datapress_client

DataPress API client and utilities.
"""

from . import ons
from . import dataset
from . import api
from . import nomis
from . import extract
from . import geo
from .dataset import get_dataset
from .__version__ import __version__ as version
print('Loading datapress_client version: ' + version)
