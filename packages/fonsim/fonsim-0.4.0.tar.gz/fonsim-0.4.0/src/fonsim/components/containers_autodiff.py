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


class Container_autodiff(Component):
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
            m_new = m + mf * dt
            return {'m': m_new}
        self.update_state = update_state


# Type hinting: mention Container class in arguments
def container_incompressible(self: Container_autodiff):
    """
    Init function, part specifically for incompressible fluids.

    :param self: Container object
    :return: None
    """
    @self.auto
    def evaluate_incompressible(t, mf):
        residual = mf
        return np.array([residual], dtype=float)
    self.evaluate = evaluate_incompressible

    self.density = self.fluid.rho


def container_compressible(self: Container_autodiff):
    """
    Init function, part specifically for compressible fluids.

    :param self: Container object
    :return: None
    """
    self.mass_stp = self.volume * self.fluid.rho_stp

    @self.auto
    def evaluate_compressible(t, p, m):
        residual = m * cnorm.pressure_atmospheric - self.mass_stp * p
        return np.array([residual], dtype=float)
    self.evaluate = evaluate_compressible

    p0 = sum([t('pressure').initial_value for t in self.terminals]) / len(self.terminals)
    self.density = p0 / cnorm.pressure_atmospheric * self.fluid.rho_stp
