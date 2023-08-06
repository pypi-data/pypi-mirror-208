"""YUV (YPbPr) colour model.

YUV defines colour in terms of a luma term (Y), and two absolute colour
difference terms (U and V). Coordinates are Cartesian.

This colour model is a counterpart to the YIQ colour space defined by
the Python standard library's colorsys module.  YIQ is used for NTSC
standard television, amongst other things. What this package calls YUV
is the family of analogue colour representations used in PAL, SDTV,
HDTV, and UHDTV. The YUV functions here use the analogue Y'PbPr
transformation, from which the corresponding digital transformations can
be derived.

Different weights can be provided for R, G, and B when converting to and
from YUV. The defaults make manipulating colours to meet WCAG
2.2 or draft 3.0 contrast criteria easier. You should use appropriately
gamma corrected R'G'B' values before converting to Y'UV, if you're doing
this.

YUV preserves absolute colourfulness when you manipulate Y alone, which
is nice, but it's quite easy to drift outside the RGB gamut envelope.
You may prefer HCY for this purpose.

References:

* https://en.wikipedia.org/wiki/YUV#Related_color_models
* https://en.wikipedia.org/wiki/YCbCr#R'G'B'_to_Y'PbPr

"""

# Imports::

from . import weights
from ._helpers import matmul
from ._helpers import clamp


# Default values::

DEFAULT_WEIGHTS = weights.W_RGB_REC709


# Conversion functions::

def rgb_to_yuv(r, g, b, w_rgb=None):
    """Convert RGB to YUV (YPbBr).

    The r, g, and b parameters are floats bwtween 0 and 1 inclusive.
    If given, w_rgb specifies the luma weighting coefficients for the r,
    g, and b components, in that order. It must be a tuple of 3 floats
    that sum to 1, but this is not enforced. The default is
    colorsysx.weights.W_RGB_REC709.

    Returns a tuple (y, u, v).

    """
    kr, kg, kb = (w_rgb is None) and DEFAULT_WEIGHTS or w_rgb
    color_matrix = [
        [kr,               kg,                kb],
        [-0.5 * kr/(1-kb), -0.5 * kg/(1-kb),  0.5],
        [0.5,              -0.5 * kg/(1-kr), -0.5 * kb/(1-kr)],
    ]
    [[y], [u], [v]] = matmul(color_matrix, [[r], [g], [b]])
    return (y, u, v)


def yuv_to_rgb(y, u, v, w_rgb=None):
    """Convert from YUV to RGB.

    The y, u, and v parameters are floats between 0 and 1 inclusive.
    w_rgb has the same meaning and default value as in rgb_to_yuv().

    Returns a tuple (r, g, b), clamped to between 0 and 1 inclusive.

    """
    kr, kg, kb = (w_rgb is None) and DEFAULT_WEIGHTS or w_rgb
    inverse_color_matrix = [
        [1., 0.,                 2 - 2*kr],
        [1., -(kb/kg)*(2-2*kb), -(kr/kg)*(2-2*kr)],
        [1., 2-2*kb,             0.],
    ]
    [[r], [g], [b]] = matmul(inverse_color_matrix, [[y], [u], [v]])
    return (clamp(c, 0, 1) for c in (r, g, b))
