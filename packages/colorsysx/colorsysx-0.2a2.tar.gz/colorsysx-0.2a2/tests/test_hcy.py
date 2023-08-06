"""Tests for colorsysx.hcy"""

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
        h, c, y = colorsysx.rgb_to_hcy(0.5, 0.5, 0.5, w_rgb=w)
        assert abs(y - 0.5) <= EPSILON
        assert c <= EPSILON
        assert h <= EPSILON  # just a convention


def test_pure_components_match_weights():
    """Pure r, g, and b produce the corresponding weight value in y."""
    for w in WEIGHTS:
        wr, wg, wb = w
        h, c, y = colorsysx.rgb_to_hcy(1, 0, 0, w_rgb=w)
        assert abs(y - wr) <= EPSILON
        h, c, y = colorsysx.rgb_to_hcy(0, 1, 0, w_rgb=w)
        assert abs(y - wg) <= EPSILON
        h, c, y = colorsysx.rgb_to_hcy(0, 0, 1, w_rgb=w)
        assert abs(y - wb) <= EPSILON


def test_ranges():
    """Output should lie within the stated bounds, and cover that range"""
    n = 16
    min_h, max_h = [1, 0]
    min_c, max_c = [1, 0]
    min_y, max_y = [1, 0]
    for w in WEIGHTS:
        for rn, gn, bn in itertools.product(range(n+1), repeat=3):
            r0, g0, b0 = (rn/n, gn/n, bn/n)
            h, c, y = colorsysx.rgb_to_hcy(r0, g0, b0, w_rgb=w)
            assert 0-EPSILON <= h <= 1+EPSILON
            assert 0-EPSILON <= c <= 1+EPSILON
            assert 0-EPSILON <= y <= 1+EPSILON
            min_h, max_h = min(h, min_h), max(h, max_h)
            min_c, max_c = min(c, min_c), max(c, max_c)
            min_y, max_y = min(y, min_y), max(y, max_y)
    assert min_h < 1/12
    assert max_h > 1 - 1/12
    assert min_c < EPSILON
    assert max_c > 1-EPSILON
    assert min_y < EPSILON
    assert max_y > 1-EPSILON


def test_round_trips():
    """Should be able to convert to GHLS and back to RGB accurately."""
    n = 16
    for w in WEIGHTS:
        for rn, gn, bn in itertools.product(range(n+1), repeat=3):
            r0, g0, b0 = (rn/n, gn/n, bn/n)
            h, c, y = colorsysx.rgb_to_hcy(r0, g0, b0, w_rgb=w)
            assert 0 <= y <= 1
            r1, g1, b1 = colorsysx.hcy_to_rgb(h, c, y, w_rgb=w)
            assert 0 <= r1 <= 1
            assert 0 <= g1 <= 1
            assert 0 <= b1 <= 1

            # Oddly, the current GLHS implementation is worse (20×Epsilon)
            # for the same 3 sets of coefficients.
            fudge = 9
            assert abs(r1 - r0) <= EPSILON*fudge
            assert abs(g1 - g0) <= EPSILON*fudge
            assert abs(b1 - b0) <= EPSILON*fudge
