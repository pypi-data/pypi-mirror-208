"""Test colorsysx._swizzle"""

from colorsysx import _swizzle


def test_swizzle_pairs_are_inverses():
    """The sectoral swizzles must be reverse mappings of each other"""

    from_min2max_to_rgb_generated = [
        tuple(s.index(i) for i in (0, 1, 2))
        for s in _swizzle.FROM_RGB_TO_MIN2MAX
    ]
    assert _swizzle.FROM_MIN2MAX_TO_RGB == from_min2max_to_rgb_generated

    from_rgb_to_min2max_generated = [
        tuple(s.index(i) for i in (0, 1, 2))
        for s in _swizzle.FROM_MIN2MAX_TO_RGB
    ]
    assert _swizzle.FROM_RGB_TO_MIN2MAX == from_rgb_to_min2max_generated
