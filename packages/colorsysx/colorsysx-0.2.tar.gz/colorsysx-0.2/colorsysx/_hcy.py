"""HCY colour model.

HCY is a tractable hue, chroma and lightness colour space based on the
work of Kuzma Shapran. HCY uses a luma term (Y) to define how bright a
colour is, a Hue term that defines where on the colour wheel it sits,
and a relative Chroma term that descibes how colourful it is.

It's very like HSLuv, but its luma term is the same as the equivalent
YUV model's.

HCY can be thought of as a cylindrical expansion of the YUV/YPbPr solid:
the "C" term is the proportion of the maximum permissible chroma within
the RGB gamut at a given hue and luma. Planes of constant Y are
equiluminant.

It's also a special case of the GHLS colour model, with the right
weighting parameters.

Different weights can be provided for R, G, and B when converting to and
from HCY. The defaults make manipulating colours to meet WCAG 2.2 or
draft 3.0 contrast criteria easier. You should use appropriately gamma
corrected R'G'B' values before converting to HCY['], if you're doing this.

References:

* https://chilliant.com/rgb2hsv.html
* https://www.hsluv.org/

"""

# Imports::

from . import weights
from ._helpers import clamp
from . import _swizzle


# Default values::

DEFAULT_WEIGHTS = weights.W_RGB_REC709


# Conversion functions::

def rgb_to_hcy(r, g, b, w_rgb=None):
    """Converts from RGB to HCY.

    The r, g, and b parameters are floats between 0 and 1 inclusive.  If
    given, w_rgb specifies the luma weighting coefficients for the r, g,
    and b components, in that order. It must be a tuple of 3 floats that
    sum to 1, but this is not enforced. The default is
    colorsysx.weights.W_RGB_REC709.

    Returns a tuple (h, c, y).

    """

    # Luma is a weighted sum of the three components.
    if w_rgb is None:
        w_rgb = DEFAULT_WEIGHTS

    # Hue. First pick a sector based on the greatest RGB component, then add
    # the scaled difference of the other two RGB components.
    (comp_min, w_min), (comp_mid, w_mid), (comp_max, w_max) \
        = sorted(zip([r, g, b], w_rgb))

    if comp_max == comp_min:
        return (0.0, 0.0, comp_max)

    # Compute hue
    mid_minus_min = comp_mid - comp_min
    max_minus_min = comp_max - comp_min
    max_minus_mid = comp_max - comp_mid
    if r > g >= b:
        sector = 0
    elif g >= r > b:
        sector = 1
    elif g > b >= r:
        sector = 2
    elif b >= g > r:
        sector = 3
    elif b > r >= g:
        sector = 4
    else:  # r >= b > g
        sector = 5

    # Hue within sector
    if (sector % 2) == 0:
        f = mid_minus_min / max_minus_min
    else:
        f = max_minus_mid / max_minus_min

    h = (sector + f) / 6.0

    # Compute luma and critial luma
    y = w_max*comp_max + w_mid*comp_mid + w_min*comp_min
    y_q = w_mid * mid_minus_min / max_minus_min + w_max

    # Then relative chroma
    if y <= y_q:
        c = (y - comp_min) / y
    else:
        c = (comp_max - y) / (1.0 - y)

    return (h, c, y)


def hcy_to_rgb(h, c, y, w_rgb=None):
    """Converts from HCY to RGB.

    The h, c, and y parameters are floats between 0 and 1 inclusive.
    w_rgb has the same meaning and default value as in rgb_to_hcy().

    Returns a tuple of floats in the form (r, g, b), where each
    component is between 0 and 1 inclusive.

    """

    if w_rgb is None:
        w_rgb = DEFAULT_WEIGHTS

    # Achromatic case
    if c == 0:
        return tuple(clamp(c, 0.0, 1.0) for c in (y, y, y))

    # Pick a sector based on the hue angle.
    # This determines the order in which {r, g, b} are selected from
    # the {min, mid, max} components we're going to be calculating
    # later.
    sector = int((h % 1.0) * 6.0)
    f = ((h % 1.0) * 6.0) - sector
    if (sector % 2) == 0:
        ff = f
    else:
        ff = 1.0 - f

    # Put the weights in min-to-max order.
    mapping_indices = _swizzle.FROM_RGB_TO_MIN2MAX[sector]
    w_min, w_mid, w_max = (w_rgb[i] for i in mapping_indices)

    # Calculate the RGB components in min-to-max order.
    y_q = (w_mid * ff) + w_max
    if y <= y_q:
        comp_max = y + y*c*(1-y_q)/y_q
        comp_mid = y + y*c*(ff-y_q)/y_q
        comp_min = y - (y*c)
    else:
        comp_max = y + (1-y)*c
        comp_mid = y + (1-y)*c*(ff-y_q)/(1-y_q)
        comp_min = y - (1-y)*c*y_q/(1-y_q)

    # Back to RGB order
    comps_min2max = (comp_min, comp_mid, comp_max)
    comps_rgb = [
        clamp(comps_min2max[i], 0.0, 1.0)
        for i in _swizzle.FROM_MIN2MAX_TO_RGB[sector]
    ]
    return comps_rgb
