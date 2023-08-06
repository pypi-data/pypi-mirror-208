"""
Difficult solver case:
two actuators connected by zero flow resistance

This is a non-physical system (such a configuration
never happens in reality), but nevertheless
the solver should solve it
if put in backward Euler discretization mode.

2023, April 30
"""

import fonsim as fons

import pytest
from pytest import approx


def f_la(label, fluid):
    return fons.LinearAccumulator(label, fluid=fluid, k=1e5/10e-6,
                                  v0=0, p0=fons.cnorm.pressure_atmospheric)


def f_fa(label, fluid):
    return fons.FreeActuator(label, fluid=fluid)


@pytest.mark.parametrize('fluid', [fons.water, fons.air])
@pytest.mark.parametrize('dt', [1, 1e-3, 1e-6, 1e-9])
@pytest.mark.parametrize('fcomp', [f_la, f_fa])
def test_01(dt, fluid, fcomp):
    sys = fons.System()
    # Actuators
    a0 = fcomp('a0', fluid)
    a1 = fcomp('a1', fluid)
    # Initialize the two accumulators with different states
    density = fluid.rho if isinstance(fluid, fons.fluid.IdealIncompressible) \
        else fluid.rho_stp
    a0.states[0].initial_value = 1e-6 * density
    a1.states[0].initial_value = 5e-6 * density
    # Add and connect
    sys.add(a0, a1)
    sys.connect(a0, a1)

    # duration same as timestep e.g. run only a single step
    duration = dt
    sim = fons.Simulation(sys, duration=duration, step=dt, discretization='backward')
    sim.run()

    if False:
        # Plot results
        import matplotlib.pyplot as plt
        from fonsim.visual.plotting import plot, plot_state

        fig, axs = plt.subplots(3, sharex=True, constrained_layout=True)
        plot(axs[0], sim, label='pressure', unit='bar', components=['a0', 'a1'])
        plot_state(axs[1], sim, label='mass', unit='g', components=['a0', 'a1'])
        plot(axs[2], sim, label='massflow', unit='g/s', components=['a0', 'a1'])
        axs[-1].set_xlabel('time [s]')
        plt.show(block=True)

    # Check results
    a0, a1 = [sys.get(a) for a in ('a0', 'a1')]
    mean_mass = 0.5 * (a0.states[0].initial_value + a1.states[0].initial_value)
    reltol = sim.relative_solving_tolerance
    assert a0.get_state('mass')[1] == approx(mean_mass, rel=reltol)
    assert a1.get_state('mass')[1] == approx(mean_mass, rel=reltol)
    assert a0.get('massflow')[1] == approx((mean_mass - a0.states[0].initial_value) / dt, rel=reltol)
    assert a1.get('massflow')[1] == approx((mean_mass - a1.states[0].initial_value) / dt, rel=reltol)


@pytest.mark.parametrize('fluid', [fons.water, fons.air])
@pytest.mark.parametrize('dt', [1, 1e-1])
@pytest.mark.parametrize('fcomp', [f_la, f_fa])
# so `dt` still has quite some influence...
# while it does have no effect mathematically, so it must be numerically
# todo: improve numerical aspects of solver
def test_02(dt, fluid, fcomp):
    sys = fons.System()
    # Source and tube
    dp = 0.2e5
    src = fons.PressureSource('src', pressure=fons.cnorm.pressure_atmospheric+dp)
    tube = fons.CircularTube('tube', fluid, diameter=2e-3, length=0.1)
    # Actuators
    a0 = fcomp('a0', fluid)
    a1 = fcomp('a1', fluid)
    # Initialize the two accumulators with different states
    density = fluid.rho if isinstance(fluid, fons.fluid.IdealIncompressible) \
        else fluid.rho_stp
    a0.states[0].initial_value = 1e-6 * density
    a1.states[0].initial_value = 5e-6 * density
    # Add and connect
    sys.add(src, tube, a0,  a1)
    sys.connect(src, tube)
    sys.connect(a0, tube)
    sys.connect(('a0', 'a'), ('a1', 'a'))

    # run several steps until in quasi equilibrium
    tau = 0.5 if isinstance(fluid, fons.fluid.IdealIncompressible) else 0.05
    duration = max(2*tau, 5*dt)
    sim = fons.Simulation(sys, duration=duration, step=dt,
                          discretization='backward', relative_solving_tolerance=1e-2)
    sim.run()

    if False:
        # Plot results
        import matplotlib.pyplot as plt
        from fonsim.visual.plotting import plot, plot_state

        fig, axs = plt.subplots(3, sharex=True, constrained_layout=True)
        plot(axs[0], sim, label='pressure', unit='bar', components=['a0', 'a1', 'src'])
        plot_state(axs[1], sim, label='mass', unit='g', components=['a0', 'a1'])
        plot(axs[2], sim, label='massflow', unit='g/s', components=['a0', 'a1', 'src'])
        axs[-1].set_xlabel('time [s]')
        plt.show(block=True)

    # Check results
    a0, a1 = [sys.get(a) for a in ('a0', 'a1')]
    p = sys.get('src').pressure
    reltol = sim.relative_solving_tolerance
    assert a0.get('pressure')[-1] == approx(p, abs=2*dp*reltol)
    assert a1.get('pressure')[-1] == approx(p, abs=2*dp*reltol)
