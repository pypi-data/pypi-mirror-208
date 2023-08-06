"""
! To be superseded by proper unit tests, with asserts etc. !

Do some very basic testing
"""


def test_import():
    import fonsim as fons


def test_wavefunction():
    import fonsim as fons
    waves = [(0, 0.900), (0.50, 0.100)]
    wave_function = fons.wave.Custom(waves) * 1e5 + fons.pressure_atmospheric


def test_systemgeneration():
    import fonsim as fons
    system = fons.System('my_system')


def test_components():
    import fonsim as fons
    c1 = fons.PressureSource('source_00', pressure=1.8e5)
    c2 = fons.Container('container_00', fluid=fons.air, volume=50e-6)
    c3 = fons.CircularTube('tube_00', fluid=fons.air, diameter=2e-3, length=0.60)
    c4 = fons.FlowRestrictor('restrictor_00', fluid=fons.air, diameter=2e-3, k=0.5)
    c5 = fons.FreeActuator('actu_00', fluid=fons.air, curve=None)


def test_networkconstruction():
    import fonsim as fons
    system = fons.System('my_system')
    c1 = fons.PressureSource('source_00', pressure=1.8e5)
    system.add(c1)


def test_connectingcomponents():
    import fonsim as fons
    system = fons.System("my_system")
    c1 = fons.PressureSource("source_00", pressure=1.8e5)
    system.add(c1)
    c2 = fons.Container("container_00", fluid=fons.air, volume=50e-6)
    system.add(c2)
    system.connect("source_00", "container_00")
