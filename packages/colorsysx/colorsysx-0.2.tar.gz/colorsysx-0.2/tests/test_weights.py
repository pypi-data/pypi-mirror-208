"""Test colorsysx.weights"""

# Imports::

from .context import colorsysx

from sys import float_info


# Module vars::

EPSILON = float_info.epsilon


# Test funcs::

def test_rgb_ordered_weights():
    weights = [
        colorsysx.weights.W_RGB_REC601,
        colorsysx.weights.W_RGB_REC709,
        colorsysx.weights.W_RGB_REC2020,
    ]
    for w in weights:
        assert len(w) == 3
        assert abs(1.0 - sum(w)) <= EPSILON
        wr, rg, wb = w
        assert abs(1.0 - (1.0*wr + 1.0*rg + 1.0*wb)) <= EPSILON


def test_min2max_ordered_weights():
    weights = [
        colorsysx.weights.W_MIN2MAX_HSI,
        colorsysx.weights.W_MIN2MAX_HSV,
        colorsysx.weights.W_MIN2MAX_HLS,
    ]
    for w in weights:
        assert len(w) == 3
        assert abs(1.0 - sum(w)) <= EPSILON
