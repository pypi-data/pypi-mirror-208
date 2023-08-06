"""Luma/luminance/lightness weighting coefficients.

Each set of weights is a tuple of three floats that sum to exactly 1.
They are used for calculating lightness terms by this module's colour
models.

"W_RGB_*" weights are applied to the red, green, and blue component
values, and are given in that order.

"W_MIN2MAX_*" weights are applied to the components with the lowest,
middle, and highest numerical values, and are given in that order. These
are only for use with GLHS, and make its conversion functions produce
different colour models.

References:

* https://doi.org/10.1006/cgip.1993.1019

"""

# R-G-B ordered weightings::

W_RGB_REC601 = (0.299, 0.587, 0.114)
"""Luma weighting coefficients as used in SDTV.

Ref: ITU-R Recommendation BT.601 (or BT.470)
"""

W_RGB_REC709 = (0.2126, 0.7152, 0.0722)
"""Luma weighting coefficients as used in HDTV.

Ref: ITU-R Recommendation BT.709
"""

W_RGB_REC2020 = (0.2627, 0.678, 0.0593)
"""Luma weighting coefficients as used in UHDTV.

Ref: ITU-R Recommendation BT.2020
"""

# Min-Mid-Max ordered weightings for GLHS only::

W_MIN2MAX_HSI = (1/3, 1/3, 1/3)
"""Weighting coefficients for the HSI model.

The Intensity (or Lightness) term is the arithmetic mean of all three
R,G and B components. The GLHS paper calls this the "HSL Triangle"
model.

"""

W_MIN2MAX_HSV = (0, 0, 1)
"""Weighting coefficients for the HSV "hexcone" model.

The Value term is the maximum of all three R, G and B components.

This produces the same results as colorsys.rgb_to_hsv() and
colorsys.hsv_to_rgb().

"""

W_MIN2MAX_HLS = (1/2, 0, 1/2)
"""Weighting coefficients for the HLS "double hexcone" model.

The Lightness term is an average of the highest and lowest valued RGB
component.

This produces the same results as colorsys.rgb_to_hls() and
colorsys.hls_to_rgb().

"""
