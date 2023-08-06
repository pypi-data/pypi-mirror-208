"""Test colorsysx.glhs"""

# Imports::

from .context import colorsysx
import colorsys

from sys import float_info
import itertools


# Module vars::

EPSILON = float_info.epsilon
WEIGHTS = (
    colorsysx.weights.W_MIN2MAX_HSI,
    colorsysx.weights.W_MIN2MAX_HSV,
    colorsysx.weights.W_MIN2MAX_HLS,
)


# Test funcs::

def test_grey_is_grey():
    """Neutral grey is always neutral grey."""
    for w in WEIGHTS:
        l, h, s = colorsysx.rgb_to_glhs(0.5, 0.5, 0.5, w_min2max=w)
        assert abs(l - 0.5) <= EPSILON
        assert h <= EPSILON
        assert s <= EPSILON  # just a convention


def test_ranges():
    """Output should lie within the stated bounds, and cover that range"""
    n = 16
    min_l, max_l = [1, 0]
    min_h, max_h = [1, 0]
    min_s, max_s = [1, 0]
    for w in WEIGHTS:
        for rn, gn, bn in itertools.product(range(n+1), repeat=3):
            r0, g0, b0 = (rn/n, gn/n, bn/n)
            l, h, s = colorsysx.rgb_to_glhs(r0, g0, b0, w_min2max=w)
            assert 0-EPSILON <= l <= 1+EPSILON
            assert 0-EPSILON <= h <= 1+EPSILON
            assert 0-EPSILON <= s <= 1+EPSILON
            min_l, max_l = min(l, min_l), max(l, max_l)
            min_h, max_h = min(h, min_h), max(h, max_h)
            min_s, max_s = min(s, min_s), max(s, max_s)
    assert min_l < EPSILON
    assert max_l > 1-EPSILON
    assert min_h < 1/12
    assert max_h > 1 - 1/12
    assert min_s < EPSILON
    assert max_s > 1-EPSILON


def test_round_trips():
    """Should be able to convert to GHLS and back to RGB accurately."""
    n = 16
    for w in WEIGHTS:
        for rn, gn, bn in itertools.product(range(n+1), repeat=3):
            r0, g0, b0 = (rn/n, gn/n, bn/n)
            l, h, s = colorsysx.rgb_to_glhs(r0, g0, b0, w_min2max=w)
            assert 0 <= l <= 1
            r1, g1, b1 = colorsysx.glhs_to_rgb(l, h, s, w_min2max=w)
            assert 0 <= r1 <= 1
            assert 0 <= g1 <= 1
            assert 0 <= b1 <= 1

            # See note in test_hcy.test_round_trips()
            fudge = 4
            assert abs(r1 - r0) <= EPSILON*fudge
            assert abs(g1 - g0) <= EPSILON*fudge
            assert abs(b1 - b0) <= EPSILON*fudge


def test_equivalences():
    """The GHLS funcs can reproduce other models with dedicated funcs."""
    n = 16
    for rn, gn, bn in itertools.product(range(n+1), repeat=3):
        r, g, b = (rn/n, gn/n, bn/n)

        # Don't need much fudge for colorsys funcs
        fudge = 1   # wow!

        # "HLS" double hexcone model
        (gl1, gh1, gs1) = colorsysx.rgb_to_glhs(
            r, g, b,
            w_min2max=colorsysx.weights.W_MIN2MAX_HLS,
        )
        (h1, l1, s1) = colorsys.rgb_to_hls(r, g, b)
        assert abs(gl1 - l1) <= EPSILON*fudge
        assert abs(gs1 - s1) <= EPSILON*fudge
        assert abs(gh1 - h1) <= EPSILON*fudge

        # "HSV" hexcone model
        (gl2, gh2, gs2) = colorsysx.rgb_to_glhs(
            r, g, b,
            w_min2max=colorsysx.weights.W_MIN2MAX_HSV,
        )
        (h2, s2, v2) = colorsys.rgb_to_hsv(r, g, b)
        assert abs(gl2 - v2) <= EPSILON*fudge
        assert abs(gs2 - s2) <= EPSILON*fudge
        assert abs(gh2 - h2) <= EPSILON*fudge

        # Use more fudge for the standalone HCY stuff
        fudge = 4

        # "HCY" luma-based model
        (gl3, gh3, gs3) = colorsysx.rgb_to_glhs(
            r, g, b,
            w_rgb=colorsysx.weights.W_RGB_REC709,
        )
        (h3, c3, y3) = colorsysx.rgb_to_hcy(
            r, g, b,
            w_rgb=colorsysx.weights.W_RGB_REC709,
        )
        assert abs(gl3 - y3) <= EPSILON*fudge
        assert abs(gs3 - c3) <= EPSILON*fudge
        assert abs(gh3 - h3) <= EPSILON*fudge
