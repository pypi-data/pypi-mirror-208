from .version import get_versions

__author__ = str(get_versions()['author'])
__date__ = str(get_versions()['date'])
__version__ = str(get_versions()['version'])
del get_versions

__all__ = ['__version__']

from . import core
from .core import *
from . import util
from .util import *
from . import _enh
from ._enh import *

__all__.extend(core.__all__)
__all__.extend(util.__all__)
__all__.extend(_enh.__all__)

from . import config
from .config import *

__all__.extend(config.__all__)
