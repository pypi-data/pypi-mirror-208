"""Test shim.

Importing this allows pytest to find the source tree's colorsysx module.

"""

# Imports and sys.path manipulations::

import sys as _sys
from os.path import dirname as _dirname
from os.path import join as _join

_sys.path.insert(0, _join(_dirname(__file__), ".."))

import colorsysx  # noqa: F401, E402
