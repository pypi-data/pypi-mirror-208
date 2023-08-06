"""
Test variable.py
2022, May 06
"""

import collections.abc
import warnings

from fonsim.core.variable import Variable
from fonsim.core.terminal import Terminal

import pytest


def test_hashable():
    # Test whether Variable object is hashable
    var = Variable(key='pressure', orientation='across')
    assert isinstance(var, collections.abc.Hashable)


def test_copy_and_attach():
    """Method copy_and_attach"""
    var_a = Variable(key='pressure', orientation='across')
    term = Terminal('a', [])
    var_b = var_a.copy_and_attach(term)

    assert var_a != var_b
    assert var_a.key == var_b.key
    assert var_a.orientation == var_b.orientation
    assert var_a.terminal is None
    assert var_b.terminal == term


@pytest.mark.parametrize('orientation, warning_expected', [
    ('across', False), ('through', False), ('local', False),
    ('over', True),
])
def test_unexpected_orientation(orientation, warning_expected):
    """Method __init__ given parameter value check"""
    if warning_expected:
        with pytest.warns():
            Variable(key='foo', orientation=orientation)
    else:
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            Variable(key='foo', orientation=orientation)
