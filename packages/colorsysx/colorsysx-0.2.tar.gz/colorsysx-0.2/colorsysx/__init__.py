"""Extra, human-relevant, colour spaces derived from RGB.

This package is an extension of the standard Python `colorsys` module.
It defines a few additional useful colour spaces, with an emphasis on
models of colour that are relevant to human vision and the perceived
lightness of different hues.

ColorsysX implements the following related families of model:

* colorsysx._yuv: a cubic space with Cartesian coordinates (YPbPr)
* colorsysx._hcy: Cylindrical Hue/Chroma/Luma
* colorsysx._glhs: Generalized Lightness/Hue/Saturation

See the corresponding module help texts for further details about each
model. All of the colour spaces added by this package can be
parameterized to tune them for different tasks. See the
colorsysx.weights module for details.

"""

__version__ = "0.2"

# Imports::

# Import just the functions,
# people wanting weights can import .weights submodule.
from ._yuv import rgb_to_yuv, yuv_to_rgb  # noqa: F401
from ._hcy import rgb_to_hcy, hcy_to_rgb  # noqa: F401
from ._glhs import rgb_to_glhs, glhs_to_rgb  # noqa: F401

# Also make the stock colorsys funcs available.
from colorsys import \
    rgb_to_hls, hls_to_rgb, \
    rgb_to_hsv, hsv_to_rgb, \
    rgb_to_yiq, yiq_to_rgb  # noqa: F401

# Exports::

__all__ = [
    "rgb_to_yuv", "yuv_to_rgb",
    "rgb_to_hcy", "hcy_to_rgb",
    "rgb_to_glhs", "glhs_to_rgb",
    "rgb_to_hls", "hls_to_rgb",
    "rgb_to_hsv", "hsv_to_rgb",
    "rgb_to_yiq", "yiq_to_rgb",
]
