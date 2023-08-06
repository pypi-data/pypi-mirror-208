"""
Test interpolate.py

2022, April 27
"""

import numpy as np
import pytest

from fonsim.data.interpolate import interpolate_fdf


def ip(x, xa, xb, ya, yb):
    """
    Basic interpolation that interpolates
    between two points (xa, ya) and (xb, yb).
    """
    return ya + (yb-ya)*(x-xa)/(xb-xa), (yb-ya)/(xb-xa)


def test_00():
    """
    Arrays of different length.
    """
    x = 0
    xs = np.array([1, 3, 5], dtype=float)
    ys = np.array([2, 4, 6, 8], dtype=float)
    with pytest.raises(ValueError) as msg:
        f, df = interpolate_fdf(x, xs, ys)

    msg = str(msg.value).lower()
    assert 'length' in msg


def test_01():
    """
    Arrays of length zero.
    """
    x = 2.8
    xs = np.array([], dtype=float)
    ys = np.array([], dtype=float)
    with pytest.raises(ValueError) as msg:
        f, df = interpolate_fdf(x, xs, ys)

    msg = str(msg.value).lower()
    assert 'length' in msg


def test_02():
    """
    Arrays of length one.
    """
    x = 2.6
    xs = np.array([1.1], dtype=float)
    ys = np.array([2.2], dtype=float)
    f, df = interpolate_fdf(x, xs, ys)

    assert (f, df) == (2.2, 0)


# Arrays of length two, inside
@pytest.mark.parametrize("test_input", [
    (2.8, 1, 3, 2, 5),      # Increasing
    (2.8, 3, 1, 2, 5),      # Decreasing
])
def test_03(test_input):
    x, xa, xb, ya, yb = test_input
    xs = np.array([xa, xb], dtype=float)
    ys = np.array([ya, yb], dtype=float)
    f, df = interpolate_fdf(x, xs, ys)

    assert (f, df) == (ip(x, xa, xb, ya, yb))


# Arrays of length two, outside (extrapolation disabled by default)
@pytest.mark.parametrize("test_input, expected", [
    ((3.8, 1, 3, 2, 5), (5, 0)),    # Right side, increasing
    ((0.9, 1, 3, 2, 5), (2, 0)),    # Left side, increasing
    ((0.5, 3, 1, 2, 5), (5, 0)),    # Right side, decreasing
    ((3.2, 3, 1, 2, 5), (2, 0)),    # Left side, decreasing
])
def test_05(test_input, expected):
    x, xa, xb, ya, yb = test_input
    xs = np.array([xa, xb], dtype=float)
    ys = np.array([ya, yb], dtype=float)
    f, df = interpolate_fdf(x, xs, ys)

    assert (f, df) == expected


# Arrays of length two, outside, extrapolation both enabled.
@pytest.mark.parametrize("test_input", [
    (3.8, 1, 3, 2, 5, True, True),  # Right side, increasing
    (0.9, 1, 3, 2, 5, True, True),  # Left side, increasing
    (0.5, 3, 1, 2, 5, True, True),  # Right side, decreasing
    (3.2, 3, 1, 2, 5, True, True),  # Left side, decreasing
])
def test_13(test_input):
    x, xa, xb, ya, yb, extrapolate, extrapolate_derivative = test_input
    xs = np.array([xa, xb], dtype=float)
    ys = np.array([ya, yb], dtype=float)
    f, df = interpolate_fdf(x, xs, ys, extrapolate=extrapolate, extrapolate_derivative=extrapolate_derivative)

    assert (f, df) == (ip(x, xa, xb, ya, yb))


# Arrays of length three
@pytest.mark.parametrize("test_input", [
    (2.9, (1, 3, 8), (2, 5, 6)),    # First pair, increasing
    (2.9, (-1, 1, 3), (-6, 2, 5)),  # Second pair, increasing
    (2.9, (3, 1, -8), (2, 5, 6)),   # First pair, decreasing
    (2.9, (8, 3, 1), (-6, 2, 5)),   # Second pair, decreasing
])
def test_08(test_input):
    x, xarr, yarr = test_input
    xs = np.array(xarr, dtype=float)
    ys = np.array(yarr, dtype=float)
    f, df = interpolate_fdf(x, xs, ys)

    if xs[0] <= x <= xs[1] or xs[1] <= x <= xs[0]:
        xa, xb, ya, yb = xs[0], xs[1], ys[0], ys[1]
    elif xs[1] <= x <= xs[2] or xs[2] <= x <= xs[1]:
        xa, xb, ya, yb = xs[1], xs[2], ys[1], ys[2]
    else:
        raise Exception()
    assert (f, df) == (ip(x, xa, xb, ya, yb))


def test_12():
    """
    Arrays of length six, increasing
    """
    x = 1.99
    xa, xb = 1, 3
    ya, yb = 2, 5
    xs = np.array([-5, -3,  0, xa, xb, 8], dtype=float)
    ys = np.array([-8, -7, -4, ya, yb, 6], dtype=float)
    f, df = interpolate_fdf(x, xs, ys)

    assert (f, df) == (ip(x, xa, xb, ya, yb))

