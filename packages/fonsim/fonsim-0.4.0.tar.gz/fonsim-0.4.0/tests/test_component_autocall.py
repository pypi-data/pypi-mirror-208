"""
Test of autocall functionality in `core/component.py`
2022, October 15
"""

from fonsim.core import Variable, Terminal, Component

import pytest


terminal_fluidic = (Variable('p', 'across'), Variable('mf', 'through'))


def test_01():
    """Normal, correct case"""
    class Foo(Component):
        def __init__(self, label=None):
            super().__init__(label)
            self.set_terminals(
                Terminal('a', terminal_fluidic, {'p': 'p', 'mf': 'mf'}),)

            @self.auto
            def evaluate(t, p, mf):
                return [0]
            self.evaluate = evaluate
    foo = Foo()


def test_02():
    """Normal, correct case"""
    class Foo(Component):
        def __init__(self, label=None):
            super().__init__(label)
            self.set_terminals(
                Terminal('a', terminal_fluidic, {'p': 'p', 'mf': 'mf'}),)

            @self.auto
            def evaluate(p, mf):
                return [0]
            self.evaluate = evaluate
    foo = Foo()


def test_cache_argumentfetcher():
    class Foo(Component):
        def __init__(self, label=None):
            super().__init__(label)
            self.set_terminals(
                Terminal('a', terminal_fluidic, {'p': 'pa', 'mf': 'mfa'}),)
            self.set_states(Variable('mass', 'local', label='ma'),
                            Variable('mass', 'local', label='mb'))
    foo = Foo()

    f = lambda t, pa, ma, mb, mfa: 0
    i_pa, i_mfa = [[a.label for a in foo.arguments].index(lab) for lab in ('pa', 'mfa')]
    assert foo._cache_argumentfetcher(f, extra_args=('t',)) == [4, i_pa, 2, 3, i_mfa]


def test_arg_not_found_variable_labels():
    """Warn if arguments of `evaluate` cannot be found in variable labels
    """
    class Foo(Component):
        def __init__(self, label=None):
            super().__init__(label)
            self.set_terminals(
                Terminal('a', terminal_fluidic, {'p': 'p', 'mf': 'mmf'}),)

            @self.auto
            def evaluate(t, p, mff):
                return [0]
            self.evaluate = evaluate

    with pytest.raises(ValueError) as msg:
        Foo()
    msg = str(msg.value).lower()
    assert 'mmf' in msg
    assert 'mff' in msg


def test_arg_not_found_in_state_labels():
    """Warn if arguments of `evaluate` cannot be found in state labels
    """
    class Foo(Component):
        def __init__(self, label=None):
            super().__init__(label)
            self.set_states(Variable('mass', 'local', label='mass'))

            @self.auto
            def evaluate(t, mmas):
                return [0]
            self.evaluate = evaluate

    with pytest.raises(ValueError) as msg:
        Foo()
    msg = str(msg.value).lower()
    assert 'mmas' in msg
    assert 'mass' in msg


def test_extra_arg_in_var_labels():
    """Warn for name collision
    between argument and state variables and extra arguments
    """
    class Foo(Component):
        def __init__(self, label=None):
            super().__init__(label)
            self.set_states(Variable('mass', 'local', label='t'))

            @self.auto
            def evaluate(t):
                return [0]
            self.evaluate = evaluate

    with pytest.raises(ValueError) as msg:
        Foo()
    msg = str(msg.value).lower()
    assert 't' in msg


@pytest.mark.skip(reason='not implemented')
def test_state_return_not_found_in_state_labels():
    """Warn if arguments of `evaluate` cannot be found in state labels
    """
    class Foo(Component):
        def __init__(self, label=None):
            super().__init__(label)
            self.set_terminals(
                Terminal('a', terminal_fluidic, {'p': 'p', 'mf': 'mf'}),)
            self.set_states(Variable('mass', 'local', label='mass'))

            @self.auto
            def evaluate():
                return [0]
            self.evaluate = evaluate

            @self.auto_state
            def evaluate():
                return {'mss': 0}
            self.evaluate = evaluate

    with pytest.raises(ValueError) as msg:
        Foo()
    msg = str(msg.value).lower()
    assert 'mmas' in msg
    assert 'mass' in msg
