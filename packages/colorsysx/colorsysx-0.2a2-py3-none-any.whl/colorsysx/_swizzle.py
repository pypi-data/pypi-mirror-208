"""Mappings from lists in RGB order to MIN2MAX based on hue sector.

These are an implementation detail of GLHS-family models. Each mapping
contains indexes into the "from" list that turn it into the "to" list,
like this:

    ord1 = [ord2[i] for i in FROM_ORD2_TO_ORD1[sector]]

The mapping lists are keyed by the hue sector number (0 to 5).

"""

# Sectoral swizzles::

FROM_MIN2MAX_TO_RGB = [
    (2, 1, 0),
    (1, 2, 0),
    (0, 2, 1),
    (0, 1, 2),
    (1, 0, 2),
    (2, 0, 1),
]

FROM_RGB_TO_MIN2MAX = [
    (2, 1, 0),
    (2, 0, 1),
    (0, 2, 1),
    (0, 1, 2),
    (1, 0, 2),
    (1, 2, 0),
]

# Hint: calcuate one from the other like so:
#
# FROM_A_TO_B = [
#   tuple(s.index(i) for i in (0, 1, 2))
#   for s in FROM_B_TO_A
# ]
