"""Tests for colorsysx.yuv"""

# Imports::

from .context import colorsysx

from sys import float_info
import itertools


# Module vars::

EPSILON = float_info.epsilon
WEIGHTS = (
    colorsysx.weights.W_RGB_REC601,
    colorsysx.weights.W_RGB_REC709,
    colorsysx.weights.W_RGB_REC2020,
)


# Test funcs::

def test_grey_is_grey():
    """Neutral grey is always neutral grey."""
    for w in WEIGHTS:
        y, u, v = colorsysx.rgb_to_yuv(0.5, 0.5, 0.5, w_rgb=w)
        assert abs(y - 0.5) <= EPSILON
        assert u <= EPSILON
        assert v <= EPSILON


def test_pure_components_match_weights():
    """Pure r, g, and b produce the corresponding weight value in y."""
    for w in WEIGHTS:
        wr, wg, wb = w
        y, u, v = colorsysx.rgb_to_yuv(1, 0, 0, w_rgb=w)
        assert abs(y - wr) <= EPSILON
        y, u, v = colorsysx.rgb_to_yuv(0, 1, 0, w_rgb=w)
        assert abs(y - wg) <= EPSILON
        y, u, v = colorsysx.rgb_to_yuv(0, 0, 1, w_rgb=w)
        assert abs(y - wb) <= EPSILON


def test_round_trips():
    """Should be able to convert to GHLS and back to RGB accurately."""
    n = 16
    for w in WEIGHTS:
        for rn, gn, bn in itertools.product(range(n+1), repeat=3):
            r0, g0, b0 = (rn/n, gn/n, bn/n)
            y, u, v = colorsysx.rgb_to_yuv(r0, g0, b0, w_rgb=w)
            assert 0 <= y <= 1
            r1, g1, b1 = colorsysx.yuv_to_rgb(y, u, v, w_rgb=w)
            assert 0 <= r1 <= 1
            assert 0 <= g1 <= 1
            assert 0 <= b1 <= 1
            assert abs(r1 - r0) <= EPSILON * 2  # doubled, due to clamping
            assert abs(g1 - g0) <= EPSILON * 2
            assert abs(b1 - b0) <= EPSILON * 2
