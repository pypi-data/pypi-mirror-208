"""
2023, April 28
"""

from ..core.component import *
from .terminals import terminal_fluidic
from ..core.terminal import *

import warnings


class CheckValve(Component):
    """Ideal check valve: allows fluid to flow in one direction

    Also called: check valve, non-return valve, reflux valve,
    retention valve, foot valve, or one-way valve

    This check valve has no hysteresis, which makes this component stateless.
    The parameter ``pressure_threshold`` allows to set a maximum pressure drop.
    The valve opens fully when the pressure difference equals this threshold,
    otherwise the valve remains closed and the pressure difference is smaller.

    :param label: label
    :param pressure_threshold: maximum pressure drop over the valve
    """
    def __init__(self, label=None, pressure_threshold=0):
        Component.__init__(self, label)

        self.set_terminals(Terminal('a', terminal_fluidic, {'pressure': 'p0', 'massflow': 'mf0'}),
                           Terminal('b', terminal_fluidic, {'pressure': 'p1', 'massflow': 'mf1'}))

        # Check input
        if pressure_threshold < 0:
            msg = f"The parameter 'pressure_threshold' received the value " + \
                  f"{pressure_threshold}, however a positive value was expected. " + \
                  f"Strictly negative values mean that this CheckValve " + \
                  f"can inject energy into the system, which in turn " + \
                  f"can cause stability and convergence issues."
            warnings.warn(msg, ValueError, stacklevel=2)

        @self.auto
        def evaluate(p0, p1, mf0, mf1):
            values, jacobian = np.zeros(2, dtype=float), [{}, {}]
            # Pressure difference
            dp = p0 - p1 - pressure_threshold
            if mf0 >= 0 and dp >= 0:
                values[0] = dp
                jacobian[0]['p0'] = 1
                jacobian[0]['p1'] = -1
            else:
                values[0] = mf0
                jacobian[0]['mf0'] = 1
            # Mass flow continuity
            values[1] = mf0 + mf1
            jacobian[1]['mf0'] = 1
            jacobian[1]['mf1'] = 1
            return values, jacobian
        self.evaluate = evaluate
