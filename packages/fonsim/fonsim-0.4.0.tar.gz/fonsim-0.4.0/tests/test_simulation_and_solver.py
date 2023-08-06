"""
Test simulation.py and solver.py

Suggestions on how to improve these tests are welcome!

2022, May 16
"""

import pytest
from pytest import approx
import copy


# Basic system
@pytest.fixture(scope='session')
def system_01():
    import fonsim as fons
    waves = [(0, 0.900), (0.50, 0.100)]
    wave_function = fons.wave.Custom(waves) * 1e5 + fons.pressure_atmospheric
    system = fons.System('my_system')
    c1 = fons.PressureSource('source_00', pressure=wave_function)
    system.add(c1)
    c2 = fons.Container('container_00', fluid=fons.air, volume=50e-6)
    system.add(c2)
    c3 = fons.CircularTube("tube_00", fluid=fons.air, diameter=2e-3, length=0.60)
    system.add(c3)
    system.connect('source_00', 'tube_00')
    system.connect('tube_00', 'container_00')

    return system


@pytest.fixture(scope='session')
def sim_constanttimestep_01(system_01):
    import fonsim as fons
    system = system_01
    sim = fons.Simulation(system,
                          duration=1.0,
                          step=1e-3,
                          relative_solving_tolerance=1e-3)
    sim.run()

    return sim


@pytest.fixture(scope='session')
def sim_adaptivetimestep_01(system_01):
    import fonsim as fons
    system = copy.deepcopy(system_01)
    sim = fons.Simulation(system,
                          duration=1.0,
                          step=(1e-3, 1e-1),
                          relative_solving_tolerance=1e-3)
    sim.run()

    return sim


def test_constanttimestep_01(sim_constanttimestep_01):
    """
    Check whether
    (1) simulation runs and
    (2) whether it more or less outputs the expected values
    """
    import fonsim as fons

    sim = copy.deepcopy(sim_constanttimestep_01)

    a1 = sim.times
    a2 = sim.system.get('source_00').get('pressure')
    a3 = sim.system.get('container_00').get('pressure')
    a4 = sim.system.get('container_00').get('massflow')

    # Check lengths of simulation data output arrays
    assert len(a1) == 1001
    assert len(a2) == 1001
    assert len(a3) == 1001
    assert len(a4) == 1001

    # Check values
    assert a1[0] == approx(0, abs=1e-3)
    assert a1[-1] == approx(1, abs=1e-3)
    assert a3[0] == approx(fons.pressure_atmospheric, abs=2e5*1e-3)
    assert a3[-1] == approx(fons.pressure_atmospheric + 0.1e5, abs=2e5*1e-3)
    assert a4[-1] == approx(0, abs=1e-3*1e-2)


def test_adaptivetimestep_01(sim_constanttimestep_01, sim_adaptivetimestep_01):
    """
    Check adaptive timestep by comparing results
    with constant timestep
    """
    import numpy as np

    sim_constant = copy.deepcopy(sim_constanttimestep_01)
    sim_adaptive = copy.deepcopy(sim_adaptivetimestep_01)

    at = sim_constant.times
    a0 = sim_constant.system.get('source_00').get('pressure')
    a1 = sim_constant.system.get('container_00').get('pressure')
    a2 = sim_constant.system.get('container_00').get('massflow')

    bt = sim_adaptive.times
    b0 = sim_adaptive.system.get('source_00').get('pressure')
    b1 = sim_adaptive.system.get('container_00').get('pressure')
    b2 = sim_adaptive.system.get('container_00').get('massflow')

    # Interpolate adaptive up to intermediate timestep
    b0 = np.interp(at, bt, b0)
    b1 = np.interp(at, bt, b1)
    b2 = np.interp(at, bt, b2)

    # Check whether large differences limited to a few places
    err = np.abs(a0 - b0)
    assert sum((-2e5*1e-2 < err) * (err < 2e5*1e-2)) > len(a0) - 2
    err = np.abs(a1 - b1)
    assert sum((-2e5*1e-2 < err) * (err < 2e5*1e-2)) > len(a1) - 2
    err = np.abs(a2 - b2)
    assert sum((-1e-2 < err) * (err < 1e-2)) > len(a2) - 2


# Check whether the four ways to specify simulation step size work
# Also includes selecting constant and adaptive timestep
# But does not check results
@pytest.mark.parametrize('test_input', [
    1e-2,
    (5e-3, 1e-2),
    None,
    (None, None),
    (5e-3, None),
    (None, 1e-2),
])
def test_stepsize_arguments(test_input):
    step = test_input

    import fonsim as fons
    system = fons.System('my_system')
    c1 = fons.PressureSource('source_00', pressure=2e5)
    system.add(c1)

    sim = fons.Simulation(system, duration=0.1, step=step)
    sim.run()


@pytest.mark.parametrize('test_input', [
    400, 497, 498, 499, 500, 501, 502, 503, 900,
])
def test_run_step(sim_constanttimestep_01, test_input):
    """
    Check whether running running method ``run_step``
    when a simulation has already been run
    changes the result (no or minimal changes ought to occur).
    """
    simstep = test_input

    sim = copy.deepcopy(sim_constanttimestep_01)

    # Use deepcopy such that it is impossible
    # that a1 ... a4 get changed by the solver afterwards.
    a1 = copy.deepcopy(sim.times)
    a2 = copy.deepcopy(sim.system.get('source_00').get('pressure'))
    a3 = copy.deepcopy(sim.system.get('container_00').get('pressure'))
    a4 = copy.deepcopy(sim.system.get('container_00').get('massflow'))

    sim.solver.run_step(simstep=simstep)

    a1b = sim.times
    a2b = sim.system.get('source_00').get('pressure')
    a3b = sim.system.get('container_00').get('pressure')
    a4b = sim.system.get('container_00').get('massflow')

    assert a1 == approx(a1b)
    assert a2 == approx(a2b, abs=2e5*1e-3)
    assert a3 == approx(a3b, abs=2e5*1e-3)
    assert a4 == approx(a4b, abs=1e-3*1e-3)
