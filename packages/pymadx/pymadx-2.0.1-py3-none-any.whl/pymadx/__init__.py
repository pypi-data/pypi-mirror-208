"""
pymadx - Royal Holloway utility to manipulate MADX data and models.

Authors:

 * Laurie Nevay
 * Andrey Abramov
 * Stewart Boogert
 * William Shields
 * Jochem Snuverink
 * Stuart Walker

Copyright Royal Holloway, University of London 2023.

"""
try:
    from ._version import version as __version__
    from ._version import version_tuple
except ImportError:
    __version__ = "unknown version"
    version_tuple = (0, 0, "unknown version")

from . import Beam
from . import Builder
from . import Compare
from . import Convert
from . import Data
from . import Plot
from . import Ptc
from . import PtcAnalysis

__all__ = ['Beam',
           'Builder',
           'Compare',
           'Convert',
           'Data',
           'Plot',
           'Ptc',
           'PtcAnalysis']
