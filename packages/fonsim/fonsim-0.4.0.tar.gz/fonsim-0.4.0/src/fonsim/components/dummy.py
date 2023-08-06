"""
Dummy component for testing.
Has one terminal such that system connectivity can be tested.
2022, May 06
"""

from ..core.component import *
from ..core.terminal import *
from ..core.variable import *

import fonsim.constants.norm as cnorm

terminal_fluidic = [Variable('pressure', 'across', cnorm.pressure_atmospheric),
                    Variable('massflow', 'through')]


class Dummy(Component):
    def __init__(self, label=None):
        Component.__init__(self, label)

        terminal0 = Terminal('a', terminal_fluidic)
        terminal1 = Terminal('b', terminal_fluidic)
        self.set_terminals(terminal0, terminal1)
        self.set_arguments(terminal0('pressure'), terminal0('massflow'),
                           terminal1('pressure'), terminal1('massflow'))
        self.nb_equations = 2

    def evaluate(self, values, jacobian_state, jacobian_arguments, state, arguments, elapsed_time):
        pass
