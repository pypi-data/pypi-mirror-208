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


class Container(Component):
    """
    A Container object is a (by default, empty) container or tank.
    It has one terminal named 'a'.
    It has one state named 'mass',
    which represents the mass of the fluid inside the container.

    The fluid should be one of the fluids defined in the module ``fluids``.
    A Container object is mostly useful with compressible fluids.

    :param label: label
    :param fluid: fluid
    :param volume: volume of the container in m^3.
    """
    def __init__(self, label=None, fluid=None, volume=None):
        super().__init__(label)

        self.set_terminals(
            Terminal('a', terminal_fluidic, {'pressure': 'p', 'massflow': 'mf'}))
        self.set_states(Variable('mass', 'local', label='m'))

        # Custom functionality
        self.volume = volume
        self.fluid = fluid

        # Continue init based on fluid
        # Compatible fluids
        initfunction_by_compatible_fluids = collections.OrderedDict([
            (fd.IdealCompressible, container_compressible),
            (fd.IdealIncompressible, container_incompressible),
        ])
        # Continue init based on fluid
        self.fluid.select_object_by_fluid(initfunction_by_compatible_fluids)(self)
        self.states[0].initial_value = volume*self.density

        @self.auto_state
        def update_state(dt, mf, m):
            jacobian = {}
            m_new = m + dt * mf
            jacobian['m/p'] = 0
            jacobian['m/mf'] = dt
            return {'m': m_new}, jacobian
        self.update_state = update_state


# Type hinting: mention Container class in arguments
def container_incompressible(self: Container):
    """
    Init function, part specifically for incompressible fluids.

    :param self: Container object
    :return: None
    """
    @self.auto
    def evaluate_incompressible(t, mf):
        values, jacobian = np.zeros(1, dtype=float), [{}]
        values[0] = mf
        jacobian[0]['mf'] = 1
        return values, jacobian
    self.evaluate = evaluate_incompressible

    self.density = self.fluid.rho


def container_compressible(self: Container):
    """
    Init function, part specifically for compressible fluids.

    :param self: Container object
    :return: None
    """
    self.mass_stp = self.volume * self.fluid.rho_stp

    @self.auto
    def evaluate_compressible(t, p, m):
        values, jacobian = np.zeros([1], dtype=float), [{}]
        values[0] = m * cnorm.pressure_atmospheric - self.mass_stp * p
        jacobian[0]['m'] = cnorm.pressure_atmospheric
        jacobian[0]['p'] = -self.mass_stp
        return values, jacobian
    self.evaluate = evaluate_compressible

    p0 = sum([t('pressure').initial_value for t in self.terminals]) / len(self.terminals)
    self.density = p0 / cnorm.pressure_atmospheric * self.fluid.rho_stp


class LinearAccumulator(Component):
    """
    A LinearAccumulator object is a flexible reservoir
    of which the pressure varies linearly with its volume.
    It has one terminal named 'a'.
    It has one state named 'mass',
    which represents the mass of the fluid inside the accumulator.

    The pressure *p* relates to the volume *v* as follows:
    ``p = k * (v - v0) + p0``.

    This component does not (yet) pose limits
    on the volume and the pressure having to be positive
    (doing so requires describing additional behaviour to handle these cases),
    so this should be checked manually in the simulation results.

    The fluid should be one of the fluids defined in the module ``fluids``.
    This component works well both with compressible and incompressible fluids.

    :param label: label
    :param fluid: fluid
    :param k: spring constant, expressed in Pa/m^3
    :param p0: pressure offset
    :param v0: volume offset
    """
    def __init__(self, label=None, fluid=None, k=None,
                 p0=cnorm.pressure_atmospheric, v0=0):
        super().__init__(label)

        self.set_terminals(
            Terminal('a', terminal_fluidic, {'pressure': 'p', 'massflow': 'mf'}))
        self.set_states(Variable('mass', 'local', label='m'))

        # Custom functionality
        self.k = k
        self.p0 = p0
        self.v0 = v0
        self.fluid = fluid

        # Continue init based on fluid
        # Compatible fluids
        initfunction_by_compatible_fluids = collections.OrderedDict([
            (fd.IdealCompressible, accumulator_compressible),
            (fd.IdealIncompressible, accumulator_incompressible),
        ])
        # Continue init based on fluid
        self.fluid.select_object_by_fluid(initfunction_by_compatible_fluids)(self)
        self.states[0].initial_value = v0 * self.density

        @self.auto_state
        def update_state(dt, mf, m):
            jacobian = {}
            m_new = m + dt * mf
            jacobian['m/p'] = 0
            jacobian['m/mf'] = dt
            return {'m': m_new}, jacobian
        self.update_state = update_state


def accumulator_incompressible(self: LinearAccumulator):
    """Init function, part specifically for incompressible fluids"""
    @self.auto
    def evaluate_incompressible(t, p, m):
        values, jacobian = np.zeros(1, dtype=float), [{}]
        v = m / self.fluid.rho
        p_int = self.k * (v - self.v0) + self.p0
        values[0] = p_int - p
        jacobian[0]['p'] = -1
        jacobian[0]['m'] = self.k / self.fluid.rho
        return values, jacobian
    self.evaluate = evaluate_incompressible

    self.density = self.fluid.rho


def accumulator_compressible(self: LinearAccumulator):
    """Init function, part specifically for compressible fluids"""
    @self.auto
    def evaluate_compressible(t, p, m):
        values, jacobian = np.zeros([1], dtype=float), [{}]
        v = m / self.fluid.rho_stp * cnorm.pressure_atmospheric / p
        p_int = self.k * (v - self.v0) + self.p0
        values[0] = p_int - p
        jacobian[0]['p'] = -1/p**2 * (self.k * m / self.fluid.rho_stp * cnorm.pressure_atmospheric) - 1
        jacobian[0]['m'] = self.k * cnorm.pressure_atmospheric / (p * self.fluid.rho_stp)
        return values, jacobian
    self.evaluate = evaluate_compressible

    p0 = self.terminals[0]('pressure').initial_value
    self.density = p0 / cnorm.pressure_atmospheric * self.fluid.rho_stp
