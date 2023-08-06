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


class CircularTube(Component):
    """
    Tube modeled as an elongated cylindrical shape.
    The terminal labels are 'a' and 'b'.
    It is stateless (the kinetic energy of the fluid in the tube is neglected).

    The pressure drop is only due to major losses,
    minor losses are neglected.
    In case of compressible flow, the major losses are calculated
    using the mean pressure of the two terminals.
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


def circulartube_incompressible(self: CircularTube):
    """
    Init function, part specifically for incompressible fluids.

    :param self: CircularTube object
    :return: None
    """
    @self.auto
    def evaluate(p0, p1, mf0, mf1):
        values, jacobian = np.zeros(2, dtype=float), [{}, {}]

        # Pressure drop, mass flow
        delta_p = p0 - p1
        mf = abs(mf0)
        # Flow direction
        sign = math.copysign(1, mf0)
        # Calculate Re (same eq. for compressible and incompressible)
        #   cross section surface A = pi d^2 / 4
        #   flow speed u = mf / rho / A
        #   Reynolds number Re = rho u d / mu
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
            df_dRe = 3/1.8**2 * math.log(beta, 10)**-3 * 1/(beta*math.log(10)) * 6.9/Re**2
            dRe_dmf = 4/(math.pi * self.d * self.fluid.mu)
            # Equation
            r = 8/math.pi**2 * self.length/self.d**5
            v_0_turbulent = delta_p - f * r/self.fluid.rho * mf**2 * sign
            ja_0_mf0_turbulent = -r/self.fluid.rho * (f * 2*mf + df_dRe * dRe_dmf * mf**2)

        if a < 1:
            # Laminar flow
            r = 128/math.pi * self.length/self.d**4 * self.fluid.mu
            v_0_laminar = delta_p - r/self.fluid.rho * mf * sign
            ja_0_mf0_laminar = -r/self.fluid.rho

        if a == 0:
            # Fully laminar
            values[0] = v_0_laminar
            jacobian[0]['mf0'] = ja_0_mf0_laminar
        elif a == 1:
            # Fully turbulent
            values[0] = v_0_turbulent
            jacobian[0]['mf0'] = ja_0_mf0_turbulent
        else:
            # Merge turbulent and laminar flow
            values[0] = a * v_0_turbulent + (1 - a) * v_0_laminar
            da_dmf = dRe_dmf / (self.Re_threshold_max - self.Re_threshold_min)
            jacobian[0]['mf0'] = a * ja_0_mf0_turbulent + (1 - a) * ja_0_mf0_laminar\
                                 + da_dmf * (v_0_turbulent - v_0_laminar) * sign

        # Derivatives to pressure: independent of flow regime
        jacobian[0]['p0'] = 1
        jacobian[0]['p1'] = -1

        # Continuity: massflow in = massflow out
        values[1] = mf0 + mf1
        jacobian[1]['mf0'] = 1
        jacobian[1]['mf1'] = 1

        return values, jacobian
    self.evaluate = evaluate


def circulartube_compressible(self: CircularTube):
    """
    Init function, part specifically for compressible fluids.

    :param self: CircularTube object
    :return: None
    """
    @self.auto
    def evaluate(t, p0, p1, mf0, mf1):
        # Allocate equation residual and jacobian
        values, jacobian = np.zeros(2, dtype=float), [{}, {}]

        # Pressure drop, mass flow
        delta_p = p0 - p1
        mf = abs(mf0)
        # Flow direction
        sign = math.copysign(1, mf0)
        # Average density
        p_average = (p0 + p1)/2
        p_average = max(p_average, cnorm.pressure_atmospheric/10)
        rho_average = self.fluid.rho_stp * p_average/cnorm.pressure_atmospheric
        drho_dp = self.fluid.rho_stp / cnorm.pressure_atmospheric / 2
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
            df_dRe = 3/1.8**2 * math.log(beta, 10)**-3 * 1/(beta*math.log(10)) * 6.9/Re**2
            dRe_dmf = 4 / (math.pi * self.d * self.fluid.mu)
            # Equation
            r = 8/math.pi**2 * self.length/self.d**5
            v_0_turbulent = delta_p - f * r/rho_average * mf**2 * sign
            ja_0_mf0_turbulent = -r/rho_average * (f * 2*mf + df_dRe*dRe_dmf * mf**2)
            ja_0_p0_turbulent = 1 + f * r/rho_average**2 * drho_dp * mf**2 * sign
            ja_0_p1_turbulent = -1 + f * r/rho_average**2 * drho_dp * mf**2 * sign

        if a < 1:
            # Laminar flow
            r = 128/math.pi * self.length/self.d**4 * self.fluid.mu
            v_0_laminar = delta_p - r/rho_average * mf * sign
            ja_0_mf0_laminar = -r/rho_average
            ja_0_p0_laminar = 1 + r/rho_average**2 * drho_dp * mf * sign
            ja_0_p1_laminar = -1 + r/rho_average**2 * drho_dp * mf * sign

        if a == 0:
            # Fully laminar
            values[0] = v_0_laminar
            jacobian[0]['mf0'] = ja_0_mf0_laminar
            jacobian[0]['p0'] = ja_0_p0_laminar
            jacobian[0]['p1'] = ja_0_p1_laminar
        elif a == 1:
            # Fully turbulent
            values[0] = v_0_turbulent
            jacobian[0]['mf0'] = ja_0_mf0_turbulent
            jacobian[0]['p0'] = ja_0_p0_turbulent
            jacobian[0]['p1'] = ja_0_p1_turbulent
        else:
            # Merge turbulent and laminar flow
            values[0] = a * v_0_turbulent + (1 - a) * v_0_laminar
            da_dmf = dRe_dmf / (self.Re_threshold_max - self.Re_threshold_min)
            jacobian[0]['mf0'] = a * ja_0_mf0_turbulent + (1 - a) * ja_0_mf0_laminar\
                                           + da_dmf * (v_0_turbulent - v_0_laminar) * sign
            # Note: a depends only on Re and dRe_dp = 0, so da_dp = 0
            jacobian[0]['p0'] = a * ja_0_p0_turbulent + (1 - a) * ja_0_p0_laminar
            jacobian[0]['p1'] = a * ja_0_p1_turbulent + (1 - a) * ja_0_p1_laminar

        # Continuity: massflow in = massflow out
        values[1] = mf0 + mf1
        jacobian[1]['mf0'] = 1
        jacobian[1]['mf1'] = 1
        return values, jacobian
    self.evaluate = evaluate


class FlowRestrictor(Component):
    """
    Flow restrictor modeled as an orifice with a K-factor.
    Terminals are named 'a' and 'b'.
    It is stateless.

    In case of compressible flow, the minor losses are calculated
    using the mean pressure of the two terminals.
    Values for the K-factor (minor loss coefficient) can be found
    `here <https://www.engineeringtoolbox.com/minor-loss-coefficients-pipes-d_626.html>`_.
    The fluid should be one of the fluids defined in the module ``fluids``.

    :param label: label
    :param fluid: fluid
    :param diamter: diameter of orifice
    :param k: K-factor
    """
    def __init__(self, label=None, fluid=None, diameter=0.002, k=0.6):
        Component.__init__(self, label)

        terminal0 = Terminal('a', terminal_fluidic)
        terminal1 = Terminal('b', terminal_fluidic)
        self.set_terminals(terminal0, terminal1)
        self.set_arguments(terminal0('pressure'), terminal0('massflow'), \
                           terminal1('pressure'), terminal1('massflow'))
        self.nb_equations = 2

        # fluid
        self.fluid = fluid
        # diameter, before constriction
        # aka larger one of the two
        self.d = diameter
        # loss value
        self.k = k

        # Continue init based on fluid
        # Compatible fluids
        initfunction_by_compatible_fluids = collections.OrderedDict([
            (fd.IdealCompressible, flowrestrictor_compressible),
            (fd.IdealIncompressible, flowrestrictor_incompressible),
        ])
        # Continue init based on fluid
        self.fluid.select_object_by_fluid(initfunction_by_compatible_fluids)(self)


def flowrestrictor_incompressible(self: FlowRestrictor):
    """
    Init function, part specifically for incompressible fluids.

    :param self: FlowRestrictor object
    :return: None
    """
    def evaluate(values, jacobian_state, jacobian_arguments, state, arguments, elapsed_time):
        # Flow
        delta_p = arguments[0] - arguments[2]
        mf = abs(arguments[1])
        sign = math.copysign(1, arguments[1])
        r = 8/math.pi**2 * self.k/(self.fluid.rho*self.d**4)
        values[0] = delta_p - r * mf**2 * sign
        jacobian_arguments[0][1] = -r * 2*mf
        jacobian_arguments[0][0] = 1
        jacobian_arguments[0][2] = -1

        # matter in = matter out
        values[1] = arguments[1] + arguments[3]
        jacobian_arguments[1][1] = 1
        jacobian_arguments[1][3] = 1
    self.evaluate = evaluate


def flowrestrictor_compressible(self: FlowRestrictor):
    """
    Init function, part specifically for compressible fluids.

    :param self: FlowRestrictor object
    :return: None
    """
    def evaluate(values, jacobian_state, jacobian_arguments, state, arguments, elapsed_time):
        # Flow
        delta_p = arguments[0] - arguments[2]
        mf = abs(arguments[1])
        sign = math.copysign(1, arguments[1])
        # Average density
        p_average = (arguments[0] + arguments[2])/2
        p_average = max(p_average, cnorm.pressure_atmospheric / 10)
        rho_average = self.fluid.rho_stp * p_average/cnorm.pressure_atmospheric
        drho_dp = self.fluid.rho_stp / cnorm.pressure_atmospheric / 2
        # Equation
        r = 8/math.pi**2 * self.k / self.d**4
        values[0] = delta_p - r/rho_average * mf**2 * sign
        jacobian_arguments[0][1] = -r/rho_average * 2 * mf
        jacobian_arguments[0][0] = 1 + r/rho_average**2 * drho_dp * mf**2 * sign
        jacobian_arguments[0][2] = -1 + r/rho_average**2 * drho_dp * mf**2 * sign

        # matter in = matter out
        values[1] = arguments[1] + arguments[3]
        jacobian_arguments[1][1] = 1
        jacobian_arguments[1][3] = 1
    self.evaluate = evaluate
