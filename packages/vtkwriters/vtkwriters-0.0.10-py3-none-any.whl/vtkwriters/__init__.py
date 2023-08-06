import verstr

try:
    from . import _version

    __version__ = verstr.verstr(_version.version)
except ImportError:
    __version__ = None

from ._vtkwriters import *
