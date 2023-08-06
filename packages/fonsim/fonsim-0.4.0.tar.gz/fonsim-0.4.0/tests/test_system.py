"""
Test system.py
2022, May 06
"""

import pytest

from fonsim.core.system import System
from fonsim.components import Dummy as DummyComponent


def test_init():
    sys = System()
    assert sys.label is None


def get_three_components():
    c1 = DummyComponent('comp_1')
    c2 = DummyComponent('comp_2')
    c3 = DummyComponent('comp_3')
    return c1, c2, c3


def test_add_01():
    """Function add"""
    sys = System()
    c1, c2, c3 = get_three_components()

    sys.add(c1)

    assert sys.components == [c1]
    assert sys.components_by_label[c1.label] == c1
    assert len(sys.nodes) == len(c1.terminals)


def test_add_02():
    """Function add"""
    sys = System()
    c1, c2, c3 = get_three_components()

    sys.add(c1, c2, c3)

    assert set(sys.components) == set([c1, c2, c3])
    assert len(sys.components) == 3
    assert len(sys.nodes) == sum([len(c.terminals) for c in [c1,c2,c3]])


def test_add_exception_01():
    """Exception raised when two components with same label added"""
    sys = System()
    c1 = DummyComponent('foo')
    c2 = DummyComponent('foo')

    sys.add(c1)
    with pytest.raises(ValueError) as msg:
        sys.add(c2)

    msg = str(msg.value).lower()
    assert 'unique' in msg
    assert 'foo' in msg


def test_get():
    """Method get"""
    sys = System()
    c1, c2, c3 = get_three_components()
    sys.add(c1, c2, c3)

    assert sys.get('comp_1') == c1


def assert_one_connection(sys, term_a, term_b):
    """
    Assert that term_a is connected to term_b.
    """
    assert len(sys.nodes) == 5
    assert term_a.isconnected is True
    assert term_b.isconnected is True

    assert sum([len(mynode.terminals) == 0 for mynode in sys.nodes]) == 0
    assert sum([len(mynode.terminals) == 1 for mynode in sys.nodes]) == 4
    connection_node = list(filter(lambda x: True if len(x.terminals) == 2 else False, sys.nodes))[0]
    assert connection_node.contains_terminal(term_a)
    assert connection_node.contains_terminal(term_b)


def assert_two_connections(sys, term_0, term_1, term_2, term_3):
    """
    Assert that term_0 is connected to term_1
    and that term_2 is connected to term_3.
    """
    assert len(sys.nodes) == 4

    assert sum([len(mynode.terminals) == 0 for mynode in sys.nodes]) == 0
    assert sum([len(mynode.terminals) == 1 for mynode in sys.nodes]) == 2
    connection_nodes = list(filter(
        lambda x: True if len(x.terminals) == 2 else False,
        sys.nodes))
    cnode_1 = list(filter(lambda x: x.contains_terminal(term_0), connection_nodes))[0]
    cnode_2 = list(filter(lambda x: x.contains_terminal(term_2), connection_nodes))[0]
    assert cnode_1.contains_terminal(term_1)
    assert cnode_2.contains_terminal(term_3)


def assert_two_connections_common_terminal(sys, term_0, term_1, term_2):
    """
    Assert that term0, term1 and term_2 are connected to each other.
    """
    assert len(sys.nodes) == 4

    assert sum([len(mynode.terminals) == 0 for mynode in sys.nodes]) == 0
    assert sum([len(mynode.terminals) == 1 for mynode in sys.nodes]) == 3
    assert sum([len(mynode.terminals) == 2 for mynode in sys.nodes]) == 0
    connection_node = list(filter(lambda x: True if len(x.terminals) == 3 else False, sys.nodes))[0]
    assert connection_node.contains_terminal(term_0)
    assert connection_node.contains_terminal(term_1)
    assert connection_node.contains_terminal(term_2)


def test_connect_two_terminals_01():
    """Method connect_two_terminals: single connection"""
    sys = System()
    c1, c2, c3 = get_three_components()
    sys.add(c1, c2, c3)

    term_a = c1.get_terminal('a')
    term_b = c2.get_terminal('b')
    sys.connect_two_terminals(term_a, term_b)

    assert_one_connection(sys, term_a, term_b)


def test_connect_two_terminals_02():
    """Method connect_two_terminals: two connections"""
    sys = System()
    c1, c2, c3 = get_three_components()
    sys.add(c1, c2, c3)

    term_1a = c1.get_terminal('a')
    term_2a = c2.get_terminal('a')
    term_2b = c2.get_terminal('b')
    term_3a = c3.get_terminal('a')
    sys.connect_two_terminals(term_1a, term_2a)
    sys.connect_two_terminals(term_2b, term_3a)

    assert_two_connections(sys, term_1a, term_2a, term_2b, term_3a)


def test_connect_two_terminals_03():
    """Method connect_two_terminals: two connections, common terminal"""
    sys = System()
    c1, c2, c3 = get_three_components()
    sys.add(c1, c2, c3)

    term_1a = c1.get_terminal('a')
    term_2a = c2.get_terminal('a')
    term_3a = c3.get_terminal('a')
    sys.connect_two_terminals(term_1a, term_2a)
    sys.connect_two_terminals(term_1a, term_3a)

    assert_two_connections_common_terminal(sys, term_1a, term_2a, term_3a)


def test_connect_two_terminals_warning_01():
    """
    Method connect_two_terminals:
    warning thrown when trying to connect terminal
    belonging to component not in system
    """
    sys = System()
    c1, c2, _ = get_three_components()
    sys.add(c1)

    term_1a = c1.get_terminal('a')
    term_2a = c2.get_terminal('a')

    with pytest.warns(UserWarning):
        sys.connect_two_terminals(term_1a, term_2a)


# Test method get_component_and_terminal:
# the four methods to specify the arguments
def create_test_inputs_for_get_component_and_terminal():
    c1, c2, c3 = get_three_components()
    sys = System()
    sys.add(c1, c2, c3)
    t1a = c1.get_terminal('a')
    t1b = c1.get_terminal('b')
    t2a = c2.get_terminal('a')
    t2b = c2.get_terminal('b')
    tiae = [   # tiae = test_input_and_expected
        ((sys, c1), (c1, t1a)),
        ((sys, c2), (c2, t2a)),
        ((sys, t1a), (c1, t1a)),
        ((sys, t2b), (c2, t2b)),
        ((sys, 'comp_1'), (c1, t1a)),
        ((sys, 'comp_2'), (c2, t2a)),
        ((sys, ('comp_1', 'b')), (c1, t1b)),
        ((sys, ('comp_2', 'a')), (c2, t2a)),
    ]
    return tiae

# Test method get_component_and_terminal:
# the three methods to specify the arguments
@pytest.mark.parametrize('test_input, expected',
                         create_test_inputs_for_get_component_and_terminal())
def test_get_component_and_terminal(test_input, expected):
    sys, arg = test_input
    assert sys.get_component_and_terminal(arg) == expected


def test_connect_01():
    sys = System()
    c1, c2, c3 = get_three_components()
    sys.add(c1, c2, c3)

    sys.connect(('comp_1', 'a'), ('comp_2', 'a'))

    term_a = c1.get_terminal('a')
    term_b = c2.get_terminal('a')
    assert_one_connection(sys, term_a, term_b)


# Test method connect: three components connected (two connections)
def test_connect_02():
    sys = System()
    c1, c2, c3 = get_three_components()
    sys.add(c1, c2, c3)

    sys.connect(('comp_1', 'a'), ('comp_2', 'a'))
    sys.connect(('comp_2', 'b'), ('comp_3', 'a'))

    term_1a = c1.get_terminal('a')
    term_2a = c2.get_terminal('a')
    term_2b = c2.get_terminal('b')
    term_3a = c3.get_terminal('a')

    assert_two_connections(sys, term_1a, term_2a, term_2b, term_3a)


# Test method connect: three components connected, serial definition
def test_connect_03():
    sys = System()
    c1, c2, c3 = get_three_components()
    sys.add(c1, c2, c3)

    sys.connect(c1, c2, c3)

    term_1a = c1.get_terminal('a')
    term_2a = c2.get_terminal('a')
    term_2b = c2.get_terminal('b')
    term_3a = c3.get_terminal('a')

    assert_two_connections(sys, term_1a, term_2a, term_2b, term_3a)
