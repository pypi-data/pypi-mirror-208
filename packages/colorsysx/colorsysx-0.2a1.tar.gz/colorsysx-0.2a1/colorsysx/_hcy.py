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
    wr, wg, wb = (w_rgb is None) and DEFAULT_WEIGHTS or w_rgb
    y = wr*r + wg*g + wb*b

    # Hue. First pick a sector based on the greatest RGB component, then add
    # the scaled difference of the other two RGB components.
    p = max(r, g, b)
    n = min(r, g, b)
    d = p - n   # An absolute measure of chroma: only used for scaling.
    if n == p:
        h = 0.0
    elif p == r:
        h = (g - b)/d
        if h < 0:
            h += 6.0
    elif p == g:
        h = ((b - r)/d) + 2.0
    else:  # p==b
        h = ((r - g)/d) + 4.0
    h /= 6.0

    # Chroma, relative to the RGB gamut envelope.
    if r == g == b:
        # Avoid a division by zero for the achromatic case.
        c = 0.0
    else:
        # For the derivation, see the GLHS paper.
        c = max((y-n)/y, (p-y)/(1-y))
    return (h, c, y)


def hcy_to_rgb(h, c, y, w_rgb=None):
    """Converts from HCY to RGB.

    The h, c, and y parameters are floats between 0 and 1 inclusive.
    w_rgb has the same meaning and default value as in rgb_to_hcy().

    Returns a tuple of floats in the form (r, g, b), where each
    component is between 0 and 1 inclusive.

    """

    wr, wg, wb = (w_rgb is None) and DEFAULT_WEIGHTS or w_rgb

    # Achromatic case
    if c == 0:
        return tuple(clamp(c, 0.0, 1.0) for c in (y, y, y))

    h %= 1.0
    h *= 6.0
    if h < 1:
        # implies (p==r and h==(g-b)/d and g>=b)
        th = h
        tm = wr + wg * th
    elif h < 2:
        # implies (p==g and h==((b-r)/d)+2.0 and b<r)
        th = 2.0 - h
        tm = wg + wr * th
    elif h < 3:
        # implies (p==g and h==((b-r)/d)+2.0 and b>=g)
        th = h - 2.0
        tm = wg + wb * th
    elif h < 4:
        # implies (p==b and h==((r-g)/d)+4.0 and r<g)
        th = 4.0 - h
        tm = wb + wg * th
    elif h < 5:
        # implies (p==b and h==((r-g)/d)+4.0 and r>=g)
        th = h - 4.0
        tm = wb + wr * th
    else:
        # implies (p==r and h==(g-b)/d and g<b)
        th = 6.0 - h
        tm = wr + wb * th
    # Calculate the RGB components in sorted order
    if tm >= y:
        p = y + y*c*(1-tm)/tm
        o = y + y*c*(th-tm)/tm
        n = y - (y*c)
    else:
        p = y + (1-y)*c
        o = y + (1-y)*c*(th-tm)/(1-tm)
        n = y - (1-y)*c*tm/(1-tm)

    # Back to RGB order
    if h < 1:
        rgb = (p, o, n)
    elif h < 2:
        rgb = (o, p, n)
    elif h < 3:
        rgb = (n, p, o)
    elif h < 4:
        rgb = (n, o, p)
    elif h < 5:
        rgb = (o, n, p)
    else:
        rgb = (p, n, o)

    return tuple(clamp(c, 0.0, 1.0) for c in rgb)
