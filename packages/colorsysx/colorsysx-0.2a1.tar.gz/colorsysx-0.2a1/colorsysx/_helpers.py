"""Helper functions."""


def matmul(a, b):
    """Matrix multiplication (pure Python lists - slow!)"""
    return [
        [
            sum(a[i][k] * b[k][j] for k in range(len(b)))
            for j in range(len(b[0]))
        ]
        for i in range(len(a))
    ]


def clamp(n, lo, hi):
    """Forces a number to lie within a given range"""
    return min(max(lo, n), hi)
