"""
2020, July 21
"""

import collections

from ..core.component import *
from .terminals import terminal_fluidic
from ..core.terminal import *
from ..core.variable import *
import fonsim.fluid.fluid as fd

import fonsim.constants.physical as cphy
import fonsim.constants.norm as cnorm


class PressureSource(Component):
    """Ideal pressure source

    The pressure exactly equals the desired pressure
    and the flow is unlimited.
    It has one terminal 'a' and is stateless.

    The argument 'pressure' should be either a constant value
    or a callable method that takes a single argument,
    the argument being the elapsed time since the simulation start.

    The argument fluid should be one of the fluids defined in the module ``fluids``.

    :param label: label
    :param fluid: fluid
    :param pressure: desired pressure
    """
    def __init__(self, label=None, fluid=None, pressure=None):
        Component.__init__(self, label)

        terminal0 = Terminal('a', terminal_fluidic)
        self.set_terminals(terminal0)
        self.set_arguments(terminal0('pressure'), terminal0('massflow'))
        self.nb_equations = 1

        # Custom functionality
        self.pressure = pressure

    def evaluate(self, values, jacobian_state, jacobian_arguments, state, arguments, elapsed_time):
        if callable(self.pressure):
            values[0] = arguments[0] - self.pressure(elapsed_time)
        else:
            values[0] = arguments[0] - self.pressure
        jacobian_arguments[0, 0] = 1


class Sink(PressureSource):
    """Ideal pressure sink at atmospheric pressure

    Wrapper of a :py:class:`.PressureSource`
    set to atmospheric pressure (1013 mBar).

    :param label: label
    :param pressure: desired pressure
    """
    def __init__(self, label=None, pressure=cnorm.pressure_atmospheric):
        super().__init__(self, label, pressure=pressure)


class MassflowSource(Component):
    """Ideal massflow source

    The massflow exactly equals the desired massflow.
    A **positive* flow value means that fluid **exits** the source.
    It has one terminal 'a' and is stateless.

    The argument 'massflow' should be either a constant value
    or a callable method that takes a single argument,
    the argument being the elapsed time since the simulation start.

    The argument fluid should be one of the fluids defined in the module ``fluids``.

    :param label: label
    :param fluid: fluid
    :param massflow: desired massflow
    """
    def __init__(self, label=None, fluid=None, massflow=None):
        Component.__init__(self, label)

        terminal0 = Terminal('a', terminal_fluidic)
        self.set_terminals(terminal0)
        self.set_arguments(terminal0('massflow'), terminal0('pressure'))
        self.nb_equations = 1

        # Custom functionality
        self.massflow = massflow

    def evaluate(self, values, jacobian_state, jacobian_arguments, state, arguments, elapsed_time):
        if callable(self.massflow):
            values[0] = arguments[0] + self.massflow(elapsed_time)
        else:
            values[0] = arguments[0] + self.massflow
        jacobian_arguments[0, 0] = 1


class VolumeflowSource(Component):
    """Ideal volumeflow source

    The volumeflow exactly equals the desired volume flow.
    A **positive* flow value means that fluid **exits** the source
    It has one terminal 'a' and is stateless.

    The value 'volumeflow' should be either a constant value
    or a callable method that takes a single argument,
    the argument being the elapsed time since the simulation start.

    The fluid should be one of the fluids defined in the module ``fluids``.

    :param label: label
    :param fluid: fluid
    :param volumeflow: desired volumeflow
    """
    def __init__(self, label=None, fluid=None, volumeflow=None):
        Component.__init__(self, label)

        terminal0 = Terminal('a', terminal_fluidic)
        self.set_terminals(terminal0)
        self.set_arguments(terminal0('pressure'), terminal0('massflow'))
        self.nb_equations = 1

        # Custom functionality
        self.fluid = fluid
        self.volumeflow = volumeflow

        # Continue init based on fluid
        # Compatible fluids
        initfunction_by_compatible_fluids = collections.OrderedDict([
            (fd.IdealCompressible, volumeflowsource_compressible),
            (fd.IdealIncompressible, volumeflowsource_incompressible),
        ])
        # Continue init based on fluid
        self.fluid.select_object_by_fluid(initfunction_by_compatible_fluids)(self)


def volumeflowsource_incompressible(self: VolumeflowSource):
    """Init function, part specifically for incompressible fluids

    :param self: VolumeflowSource object
    :return: None
    """
    def evaluate(values, jacobian_state, jacobian_arguments, state, arguments, elapsed_time):
        vf = self.volumeflow(elapsed_time) if callable(self.volumeflow) else self.volumeflow
        values[0] = arguments[1] + vf*self.fluid.rho
        jacobian_arguments[0, 1] = 1
    self.evaluate = evaluate


def volumeflowsource_compressible(self: VolumeflowSource):
    """Init function, part specifically for compressible fluids

    :param self: VolumeflowSource object
    :return: None
    """
    def evaluate(values, jacobian_state, jacobian_arguments, state, arguments, elapsed_time):
        vf = self.volumeflow(elapsed_time) if callable(self.volumeflow) else self.volumeflow
        a = self.fluid.rho_stp/cnorm.pressure_atmospheric
        values[0] = arguments[1] + a*vf*arguments[0]
        jacobian_arguments[0, 0] = a*vf
        jacobian_arguments[0, 1] = a*arguments[0]
    self.evaluate = evaluate
