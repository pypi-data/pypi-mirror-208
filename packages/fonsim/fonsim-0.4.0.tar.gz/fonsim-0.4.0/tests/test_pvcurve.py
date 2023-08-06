"""
Test pvcurve.py

2022, April 28
"""

import numpy as np
import pathlib
import pytest
from pytest import approx

from fonsim.data.pvcurve import PVCurve


# Filepaths of CSV files to use for testing
path_of_this_file = str(pathlib.Path(__file__).parent.absolute()) + '/'
print('path of this file:', path_of_this_file)
resource_dir = path_of_this_file + 'resources/'
file_01 = resource_dir + 'test_pvcurve_01.csv'


@pytest.mark.parametrize("test_input, expected", [
    # Reference absolute, autocorrect off
    ((file_01, 'absolute', False), (
            np.array([0.51, 0.93, 1.25, 1.58]) * 1e-6,
            np.array([100, 103, 112, 123]) * 1e2,
    )),
    # Reference absolute, autocorrect off but written differently
    ((file_01, 'absolute', (False, False)), (
            np.array([0.51, 0.93, 1.25, 1.58]) * 1e-6,
            np.array([100, 103, 112, 123]) * 1e2,
    )),
    # Reference relative, autocorrect off
    ((file_01, 'relative', False), (
            np.array([0.51, 0.93, 1.25, 1.58]) * 1e-6,
            np.array([100, 103, 112, 123]) * 1e2 + 101300,
    )),
    # Reference absolute, autocorrect on
    ((file_01, 'absolute', True), (
            (np.array([0.51, 0.93, 1.25, 1.58]) - 0.51) * 1e-6,
            (np.array([100, 103, 112, 123]) - 100 + 1013) * 1e2,
    )),
    # Reference absolute, autocorrect on but written differently
    ((file_01, 'absolute', (True, True)), (
            (np.array([0.51, 0.93, 1.25, 1.58]) - 0.51) * 1e-6,
            (np.array([100, 103, 112, 123]) - 100 + 1013) * 1e2,
    )),
    # Reference relative, autocorrect on
    ((file_01, 'relative', True), (
            (np.array([0.51, 0.93, 1.25, 1.58]) - 0.51) * 1e-6,
            (np.array([100, 103, 112, 123]) - 100 + 1013) * 1e2,
    )),
    # Reference absolute, autocorrect to defaults
    ((file_01, 'absolute', (0, 0)), (
            (np.array([0.51, 0.93, 1.25, 1.58]) - 0.51) * 1e-6,
            (np.array([100, 103, 112, 123]) - 100 + 1013) * 1e2,
    )),
    # Reference absolute, autocorrect to defaults + offset
    ((file_01, 'absolute', (0.1234, 5678)), (
            (np.array([0.51, 0.93, 1.25, 1.58]) - 0.51) * 1e-6 + 0.1234,
            (np.array([100, 103, 112, 123]) - 100 + 1013) * 1e2 + 5678,
    )),
    # Reference absolute, autocorrect using lambdas
    ((file_01, 'absolute', (lambda x: x * 2.5, lambda x: x * 1.8)), (
            np.array([0.51, 0.93, 1.25, 1.58]) * 2.5 * 1e-6,
            np.array([100, 103, 112, 123]) * 1.8 * 1e2,
    )),
])
def test_01(test_input, expected):
    filepath, pressure_reference, autocorrect = test_input
    curve = PVCurve(filepath, pressure_reference=pressure_reference, autocorrect=autocorrect)

    v, p = expected
    assert curve.v == approx(v)
    assert curve.p == approx(p)


def test_warning_autocorrect_single_function():
    with pytest.warns(UserWarning):
        curve = PVCurve(file_01, pressure_reference='absolute', autocorrect=lambda x: x + 5)


def test_warning_incorrect_argument_key():
    # 'pressure_referenc' instead of 'pressure_reference'
    with pytest.warns(UserWarning, match=r'pressure_referenc'):
        curve = PVCurve(file_01, pressure_referenc='absolute', autocorrect=lambda x: x + 5)
