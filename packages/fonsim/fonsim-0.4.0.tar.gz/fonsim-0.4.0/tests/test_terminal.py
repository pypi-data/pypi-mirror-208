"""
Test terminal.py
2022, May 06
"""

import pytest

from fonsim.core.terminal import Terminal
from fonsim.core.variable import Variable


def test_init():
    """Method __init__"""
    var1 = Variable(key='pressure', orientation='across')
    var2 = Variable(key='massflow', orientation='through')
    term = Terminal(label='abc', variables=[var1, var2])

    assert term.label == 'abc'
    assert term.variables_across['pressure'].key == 'pressure'
    assert term.variables_across['pressure'].orientation == 'across'
    assert term.variables_through['massflow'].key == 'massflow'
    assert term.variables_through['massflow'].orientation == 'through'
    assert term.component is None
    assert term.isconnected is False


def test_init_exception_same_key():
    """
    Exception should be raised
    when given two Variable object with same key
    """
    var1 = Variable(key='pressure', orientation='across')
    var2 = Variable(key='pressure', orientation='through')

    with pytest.raises(ValueError) as msg:
        term = Terminal(label='abc', variables=[var1, var2])

    msg = str(msg.value).lower()
    assert 'key' in msg
    assert 'pressure' in msg


def assert_compare_variables(var_a, var_b):
    """Compares whether two variable objects"""
    assert var_a.key == var_b.key
    assert var_b.orientation == var_b.orientation


def get_terminal_with_two_variables():
    var1o = Variable(key='pressure', orientation='across')
    var2o = Variable(key='massflow', orientation='through')
    term = Terminal(label='a', variables=[var1o, var2o])
    var1 = term.variables_across['pressure']
    var2 = term.variables_through['massflow']
    return term, var1o, var2o, var1, var2


def test_variable_copying():
    term, var1o, var2o, var1, var2 = get_terminal_with_two_variables()

    # Variables should not refer to same objects anymore
    assert var1 != var1o
    assert var2 != var2o
    # Do check that the orientation and key are copied properly.
    assert_compare_variables(var1, var1o)
    assert_compare_variables(var2, var2o)


def test_get_variables():
    """Method get_variables"""
    term, var1o, var2o, var1, var2 = get_terminal_with_two_variables()

    assert term.get_variables(orientation='across') == [var1]
    assert term.get_variables(orientation='through') == [var2]
    assert (term.get_variables() == [var1, var2]) or (term.get_variables() == [var2, var1])
    assert term.get_variables(orientation='') == []


def test_get_variable():
    """Method get_variable"""
    term, var1o, var2o, var1, var2 = get_terminal_with_two_variables()

    assert term.get_variable('pressure') == var1
    assert term.get_variable('massflow') == var2
