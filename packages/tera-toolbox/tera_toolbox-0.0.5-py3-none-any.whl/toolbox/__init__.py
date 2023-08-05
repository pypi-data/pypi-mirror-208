from . import version

__version__ = version.version
__author__ = "Tera Capital"

from . import utils
from . import stats
from . import data
__all__ = ['utils', 'stats', 'data']
