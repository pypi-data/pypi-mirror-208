"""
.. include:: ../README.md
"""

from importlib.metadata import version, PackageNotFoundError

from . import brain_utils
from . import packing
from . import search


try:
    __version__ = version("brain-loop-search")
except PackageNotFoundError:
    __version__ = "UNKNOWN"