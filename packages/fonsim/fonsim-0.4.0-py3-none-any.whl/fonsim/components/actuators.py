"""
2020, July 21
"""

import collections
import pkgutil

from ..core.component import *
from .terminals import terminal_fluidic
from ..core.terminal import *
from ..core.variable import *
from fonsim.data import pvcurve
from fonsim.data import dataseries
import fonsim.fluid.fluid as fd

import fonsim.constants.physical as cphy
import fonsim.constants.norm as cnorm


# Named it 'free' because the actuator cannot drive anything (in the simulation)
class FreeActuator(Component):
    """
    An actuator with a custom pressure-volume relationship
    specified as a pressure-volume curve or pv-curve.
    It is named 'free' because the actuator cannot drive anything,
    at least in this simulation.
    It has two terminals 'a' and 'b'.
    It has one state 'mass' that represents the mass of fluid
    inside the actuator.

    The argument fluid should be one of the fluids defined in the module ``fluids``.

    The argument curve should point to a pressure-volume curve (pv-curve)
    that describes the pressure-volume relationship of the actuator.
    It can be:

     - a filename of a CSV file
     - a PVCurve object
     - an object that behaves sufficiently like a PVCurve object

    Concerning the latter option, the object should provide the following methods:

     - ``get_initial_volume(p0)``
     - ``fdf_volume(volume)``

    :param label: label
    :param fluid: fluid
    :param curve: pressure-volume curve (pv-curve)
    """
    def __init__(self, label=None, fluid=None, curve=None,
                 initial_volume=None):
        Component.__init__(self, label)

        self.set_terminals(Terminal('a', terminal_fluidic, {'pressure': 'p0', 'massflow': 'mf0'}),
                           Terminal('b', terminal_fluidic, {'pressure': 'p1', 'massflow': 'mf1'}))
        self.set_states(Variable('mass', 'local', label='mass'))

        # Custom functionality
        self.fluid = fluid
        interpolation_opts = dict(extrapolate=False, extrapolate_derivative=True)
        if curve is None:
            filepath = 'resources/Measurement_60mm_balloon_actuator_01.csv'
            bs = pkgutil.get_data('fonsim', filepath)
            ds = dataseries.DataSeries(filename='.csv', bytestring=bs)
            self.pvcurve = pvcurve.PVCurve(ds, autocorrect=True, **interpolation_opts)
        elif isinstance(curve, (str, bytes)):
            filename = curve
            self.pvcurve = pvcurve.PVCurve(filename, autocorrect=True, **interpolation_opts)
        else:
            self.pvcurve = curve

        # Continue init based on fluid
        # Compatible fluids
        initfunction_by_compatible_fluids = collections.OrderedDict([
            (fd.IdealCompressible, freeactuator_compressible),
            (fd.IdealIncompressible, freeactuator_incompressible),
        ])
        # Continue init based on fluid
        self.fluid.select_object_by_fluid(initfunction_by_compatible_fluids)(self)

        # initialize state
        if initial_volume is None or initial_volume == 'auto':
            p0 = sum([t('pressure').initial_value for t in self.terminals]) / len(self.terminals)
            V0 = self.pvcurve.get_initial_volume(p0)
        elif initial_volume == 'minimum':
            V0 = np.min(self.pvcurve.v)
        else:
            V0 = initial_volume
        self.states[0].initial_value = V0*self.density

        @self.auto_state
        def update_state(dt, mass, mf0, mf1):
            jac = {}
            mass_new = mass + dt * (mf0 + mf1) \
                if mass >= 0 or (mf0 + mf1) >= 0 \
                else mass
            jac['mass/mf0'] = dt
            jac['mass/mf1'] = dt
            return {'mass': mass_new}, jac
        self.update_state = update_state


def freeactuator_compressible(self: FreeActuator):
    """
    Init function, part specifically for compressible fluids.

    :param self: FreeActuator object
    :return: None
    """
    @self.auto
    def evaluate(t, p0, p1, mass):
        residual, jac = np.zeros(2, dtype=float), [{}, {}]
        # Evaluate pv-curve
        normalvolume = mass/self.fluid.rho_stp
        volume = normalvolume * cnorm.pressure_atmospheric / p0
        # f, df: interpolation functionality, volume -> pressure
        f, df = self.pvcurve.fdf_volume(volume)
        residual[0] = f - p0
        # both terminals have the same pressure
        residual[1] = p1 - p0
        jac[0]['mass'] = df * cnorm.pressure_atmospheric / (p0 * self.fluid.rho_stp)
        jac[0]['p0'] = -df * volume / p0 - 1
        jac[1]['p1'] = 1
        jac[1]['p0'] = -1
        return residual, jac
    self.evaluate = evaluate

    p0 = sum([t('pressure').initial_value for t in self.terminals]) / len(self.terminals)
    self.density = p0 / cnorm.pressure_atmospheric * self.fluid.rho_stp

def freeactuator_incompressible(self: FreeActuator):
    """
    Init function, part specifically for incompressible fluids.

    :param self: FreeActuator object
    :return: None
    """
    @self.auto
    def evaluate(t, p0, p1, mass):
        residual, jac = np.zeros(2, dtype=float), [{}, {}]
        # Evaluate pv-curve
        volume = mass/self.fluid.rho
        # f, df: interpolation functionality, volume -> pressure
        f, df = self.pvcurve.fdf_volume(volume)
        residual[0] = f - p0
        # both terminals have the same pressure
        residual[1] = p1 - p0
        jac[0]['mass'] = df/self.fluid.rho
        jac[0]['p0'] = -1
        jac[1]['p1'] = 1
        jac[1]['p0'] = -1
        return residual, jac
    self.evaluate = evaluate

    self.density = self.fluid.rho

