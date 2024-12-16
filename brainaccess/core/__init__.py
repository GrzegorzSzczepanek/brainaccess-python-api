import ctypes
from brainaccess.libload import load_library

_dll = load_library("bacore")

from brainaccess.core.version import Version


# init()
_dll.ba_core_init.argtypes = [ctypes.POINTER(Version)]
_dll.ba_core_init.restype = ctypes.c_int
# close()
_dll.ba_core_close.argtypes = []
_dll.ba_core_close.restype = None
# get_version()
_dll.ba_core_get_version.argtypes = []
_dll.ba_core_get_version.restype = ctypes.POINTER(Version)


def init(expected_version):
    """Initializes the library
    This function reads the config file, starts logging, etc. It first
    checks if the version of the library that the application expects and the
    version of the library installed are compatible.

    Parameters
    -----------
    version
        The version of the library that the application expects.

    Warning
    -------
    Must bet called before any other BrainAccess Core library function. Only call once.
    """
    err = _dll.ba_core_init(ctypes.pointer(expected_version))
    if err == 0:
        return
    elif err == 1:
        raise RuntimeError("Already initialized")
    elif err == 2:
        raise RuntimeError("Config file contains a setting with the wrong type")
    elif err == 3:
        raise RuntimeError("Cannot parse config file")
    else:
        raise RuntimeError("Unknown error")


def close():
    """Closes the library and cleans up afterwards.

    Warning
    --------
    Must be called after all BrainAccess Core library functions used by the application.
    Only call once.
    If initialization failed, do not call this function.
    """
    _dll.ba_core_close()


def get_version():
    """Returns the installed library's actual version"""
    return _dll.ba_core_get_version()[0]
