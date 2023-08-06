"""
2020, July 21
"""

import math
import collections

from ..core.component import *
from .terminals import terminal_fluidic
from ..core.terminal import *
from ..core.variable import *
import fonsim.fluid.fluid as fd

import fonsim.constants.physical as cphy
import fonsim.constants.norm as cnorm


class CircularTube_autodiff(Component):
    """
    Tube modeled as an elongated cylindrical shape.
    The terminal labels are 'a' and 'b'.
    It is stateless (the kinetic energy of the fluid in the tube is neglected).

    The fluid should be one of the fluids defined in the module ``fluids``.

    **TODO:**
     - include kinetic energy of fluid in tube

    :param label: label
    :param fluid: fluid
    :param length: length in m
    :param diameter: internal diameter in m
    :param roughness: wall roughness in m
    """
    def __init__(self, label=None, fluid=None, length=0.60, diameter=0.002, roughness=0.0015e-3):
        Component.__init__(self, label)

        self.set_terminals(Terminal('a', terminal_fluidic, {'pressure': 'p0', 'massflow': 'mf0'}),
                           Terminal('b', terminal_fluidic, {'pressure': 'p1', 'massflow': 'mf1'}))

        # Custom functionality
        self.fluid = fluid
        self.length = length
        self.d = diameter
        self.e = roughness

        # Threshold laminar - turbulent flow
        self.Re_threshold_min = 2300
        self.Re_threshold_max = 4000

        # Continue init based on fluid
        # Compatible fluids
        initfunction_by_compatible_fluids = collections.OrderedDict([
            (fd.IdealCompressible, circulartube_compressible),
            (fd.IdealIncompressible, circulartube_incompressible),
        ])
        # Continue init based on fluid
        self.fluid.select_object_by_fluid(initfunction_by_compatible_fluids)(self)


def circulartube_incompressible(self: CircularTube_autodiff):
    """
    Init function, part specifically for incompressible fluids.

    :param self: CircularTube object
    :return: None
    """
    @self.auto
    def evaluate(t, p0, p1, mf0, mf1):
        # Equation residuals
        values = np.zeros(2, dtype=float)

        # Pressure drop, mass flow
        delta_p = p0 - p1
        mf = abs(mf0)
        # Flow direction
        sign = math.copysign(1, mf0)
        # Calculate Re
        Re = 4 * mf / (math.pi * self.d * self.fluid.mu)
        # Depending on Re, three possibilities:
        # fully laminar, fully turbulent or in transition zone
        # If in transition zone, take weighted average (weight a, 0 <= a <= 1)
        a = (Re - self.Re_threshold_min) / (self.Re_threshold_max - self.Re_threshold_min)
        a = min(1, max(0, a))
        # Flow calculations for both cases
        if a > 0:
            # Turbulent flow
            # Intermediary value
            beta = (self.e/self.d/3.7)**1.11 + 6.9/Re
            # Friction factor (Haaland correlation)
            f = 1/1.8**2 * math.log(beta, 10)**-2
            # Equation
            r = 8/math.pi**2 * self.length/self.d**5
            v_0_turbulent = delta_p - f * r/self.fluid.rho * mf**2 * sign

        if a < 1:
            # Laminar flow
            r = 128/math.pi * self.length/self.d**4 * self.fluid.mu
            v_0_laminar = delta_p - r/self.fluid.rho * mf * sign

        if a == 0:
            # Fully laminar
            values[0] = v_0_laminar
        elif a == 1:
            # Fully turbulent
            values[0] = v_0_turbulent
        else:
            # Merge turbulent and laminar flow
            values[0] = a * v_0_turbulent + (1 - a) * v_0_laminar

        # Continuity: massflow in = massflow out
        values[1] = mf0 + mf1
        
        return values

    self.evaluate = evaluate


def circulartube_compressible(self: CircularTube_autodiff):
    """
    Init function, part specifically for compressible fluids.

    :param self: CircularTube object
    :return: None
    """
    @self.auto
    def evaluate(t, p0, p1, mf0, mf1):
        # Equation residuals
        values = np.zeros(2, dtype=float)

        # Pressure drop, mass flow
        delta_p = p0 - p1
        mf = abs(mf0)
        # Flow direction
        sign = math.copysign(1, mf0)
        # Average density
        p_average = (p0 + p1)/2
        p_average = max(p_average, cnorm.pressure_atmospheric/10)
        rho_average = self.fluid.rho_stp * p_average/cnorm.pressure_atmospheric
        # Calculate Re
        Re = 4 * mf / (math.pi * self.d * self.fluid.mu)
        # Depending on Re, three possibilities:
        # fully laminar, fully turbulent or in transition zone
        # If in transition zone, take weighted average (weight a, 0 <= a <= 1)
        a = (Re - self.Re_threshold_min) / (self.Re_threshold_max - self.Re_threshold_min)
        a = min(1, max(0, a))
        # Flow calculations for both cases
        if a > 0:
            # Turbulent flow
            # Intermediary value
            beta = (self.e/self.d/3.7)**1.11 + 6.9/Re
            # Friction factor (Haaland correlation)
            f = 1 / 1.8**2 * math.log(beta, 10)**-2
            # Equation
            r = 8/math.pi**2 * self.length/self.d**5
            v_0_turbulent = delta_p - f * r/rho_average * mf**2 * sign

        if a < 1:
            # Laminar flow
            r = 128/math.pi * self.length/self.d**4 * self.fluid.mu
            v_0_laminar = delta_p - r/rho_average * mf * sign

        if a == 0:
            # Fully laminar
            values[0] = v_0_laminar
        elif a == 1:
            # Fully turbulent
            values[0] = v_0_turbulent
        else:
            # Merge turbulent and laminar flow
            values[0] = a * v_0_turbulent + (1 - a) * v_0_laminar

        # Continuity: massflow in = massflow out
        values[1] = mf0 + mf1

        return values

    self.evaluate = evaluate
