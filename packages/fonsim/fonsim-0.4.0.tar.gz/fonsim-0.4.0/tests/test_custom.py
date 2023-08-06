"""
Test custom.py
2022, May 11
"""

import numpy as np
import pytest
from pytest import approx

from fonsim.wave.custom import isincreasing
from fonsim.wave.custom import Custom


# Test function isincreasing
@pytest.mark.parametrize('test_input, expected', [
    ([], True),
    ([1], True),
    ([1, 2, 3], True),
    ([1, 1, 2], False),
    ([1, 0, 2], False),
])
def test_isincreasing(test_input, expected):
    assert isincreasing(test_input) == expected


# Test whether exception raised
# when wave_array time indices not increasing (absolute)
# or not strictly positive (relative)
@pytest.mark.parametrize('test_input', [
    ([[1.0, 1.0], [ 0.5, 1.0], [1.5, 3.0]], 'absolute'),
    ([[1.0, 1.0], [-0.1, 1.0], [0.5, 3.0]], 'relative'),
])
def test_exception_timeseries(test_input):
    wave_array, time_notation = test_input
    with pytest.raises(ValueError):
        Custom(wave_array, time_notation)


# Test whether no exception raised
# when wave_array time correctly specified
@pytest.mark.parametrize('test_input', [
    ([[1, 1], [2, 1], [3, 3]], 'absolute'),
    ([[1, 1], [1, 1], [3, 3]], 'absolute'),
    ([[1, 1], [1, 1], [3, 3]], 'relative'),
    ([[1, 1], [0, 1], [3, 3]], 'relative'),
])
def test_exception_timeseries(test_input):
    wave_array, time_notation = test_input
    _ = Custom(wave_array, time_notation)


# Test whether different input shapes for wave_array
# are processed correctly
@pytest.mark.parametrize('test_input, expected', [
    ([[0.0, 1.1], [0.5, 1.6], [1.0, 2.1]], (np.array([0.0, 0.5, 1.0]), np.array([1.1, 1.6, 2.1]))),
    ([[0.0, 0.5, 1.0], [1.1, 1.6, 2.1]], (np.array([0.0, 0.5, 1.0]), np.array([1.1, 1.6, 2.1]))),
])
def test_shape_transpose(test_input, expected):
    customwave = Custom(test_input, 'absolute', 'previous')
    assert customwave.times == approx(expected[0])
    assert customwave.values == approx(expected[1])


# Test whether time_notation 'relative' processed correctly
# (correct conversion to absolute series)
def test_05():
    customwave = Custom([[1.0, 1], [0.5, 2], [0.6, 3]], 'relative')
    assert customwave.times == approx([1.0, 1.5, 2.1])


# Test various popular cases
# The interpolation is done using scipy.interpolate.interp1d,
# so the interpolation itself is not really tested much,
# more so the correct handling of that method etc.
arr1 = lambda: [[0.0, 1.0], [0.5, 1.5], [1.5, 1.2]]
@pytest.mark.parametrize('test_input, expected', [
    # Scalar
    ((arr1(), 'absolute', 'previous', 0.4), 1.0),
    # Interpolation
    ((arr1(), 'absolute', 'previous', (0.0, 0.4, 0.5, 0.8)), (1.0, 1.0, 1.5, 1.5)),
    ((arr1(), 'absolute', 'next', (0.0, 0.4, 0.5, 0.8)), (1.0, 1.5, 1.5, 1.2)),
    # Extrapolation
    ((arr1(), 'absolute', 'previous', (-0.1, 1.8)), (1.0, 1.2)),
    ((arr1(), 'absolute', 'next', (-0.1, 1.8)), (1.0, 1.2)),
])
def test_01(test_input, expected):
    wave_array, time_notation, kind, x = test_input
    customwave = Custom(wave_array, time_notation, kind)
    assert customwave(x) == approx(expected)
