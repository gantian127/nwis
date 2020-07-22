from .nwis import Nwis
from .bmi import BmiNwis
from ._version import get_versions

__all__ = ["Nwis", "BmiNwis"]

__version__ = get_versions()['version']
del get_versions

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
