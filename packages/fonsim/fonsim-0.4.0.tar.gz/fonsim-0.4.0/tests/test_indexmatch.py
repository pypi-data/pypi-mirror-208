"""
Test indexmatch.py

2022, April 28
"""

import pytest

from fonsim.conversion.indexmatch import get_index_of_best_match


@pytest.mark.parametrize("test_input,expected", [
    (('mass', ['volume', 'pressure', 'mass', 'massflow']), 2),      # Exact match possible
    (('massf', ['volume', 'pressure', 'mass', 'massflow']), 2),     # Small spelling error
    (('massflo', ['volume', 'pressure', 'mass', 'massflow']), 3),   # Small spelling error
    (('Mass', ['volume', 'pressure', 'mass', 'massflow']), 2),     # Upper instead of lowercase
])
def test_01(test_input, expected):
    """
    Exact match possible.
    """
    a, b = test_input
    i = get_index_of_best_match(a, b)

    assert i == expected
