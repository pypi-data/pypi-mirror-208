"""
Test node.py
2022, May 06
"""

import pytest

from fonsim.core.node import Node
from fonsim.core.terminal import Terminal
from fonsim.core.variable import Variable


# Three variables to use
def get_three_variables():
    var1 = Variable('pressure', 'across')
    var2 = Variable('massflow', 'through')
    var3 = Variable('temperature', 'across')
    return [var1, var2, var3]


@pytest.mark.parametrize('test_input, expected', [
    (([Terminal('abc', get_three_variables())
       ], 'across', 'pressure'), 1),
    (([Terminal('abc', get_three_variables())
       ], 'across', None), 2),
    (([Terminal('abc', get_three_variables())
       ], None, 'massflow'), 1),
    (([Terminal('abc', get_three_variables())
       ], None, None), 3),
    (([Terminal('abc', get_three_variables()), Terminal('def', get_three_variables())
       ], 'across', 'pressure'), 2),
    (([Terminal('abc', get_three_variables()), Terminal('def', get_three_variables())
       ], 'across', None), 4),
    (([Terminal('abc', get_three_variables()), Terminal('def', get_three_variables())
       ], None, 'pressure'), 2),
    (([Terminal('abc', get_three_variables()), Terminal('def', get_three_variables())
       ], None, None), 6)
])
def test_get_variables(test_input, expected):
    """Function get_variables"""
    terminals, orientation, key = test_input
    nb_variables = expected

    mynode = Node(*terminals)
    vars = mynode.get_variables(orientation=orientation, key=key)

    assert len(vars) == nb_variables
    if key is not None:
        assert [v.key == key for v in vars]
    if orientation is not None:
        assert [v.orientation == orientation for v in vars]
    # All Variable objects should be unique
    assert len(set(vars)) == len(vars)
