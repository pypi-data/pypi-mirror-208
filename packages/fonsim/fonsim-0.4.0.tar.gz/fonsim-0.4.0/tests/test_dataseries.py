"""
Test dataseries.py

2022, April 28
"""

import numpy as np
import pathlib
import pytest
from pytest import approx

from fonsim.data.dataseries import DataSeries


# Filepaths of CSV files to use for testing
path_of_this_file = str(pathlib.Path(__file__).parent.absolute()) + '/'
print('path of this file:', path_of_this_file)
resource_dir = path_of_this_file + 'resources/'
file_01 = resource_dir + 'test_dataseries_01.csv'
file_02 = resource_dir + 'test_dataseries_02.csv'
file_03 = resource_dir + 'test_dataseries_03.csv'
file_04 = resource_dir + 'test_dataseries_04.csv'
file_05 = resource_dir + 'test_dataseries_05.csv'
file_06 = resource_dir + 'test_dataseries_06.csv'
file_07 = resource_dir + 'test_dataseries_07.csv'
#file_08
file_09 = resource_dir + 'test_dataseries_09.csv'
file_10 = resource_dir + 'test_dataseries_10.csv'


def test_O1():
    """
    One row, three columns.
    """
    ds = DataSeries(file_01)

    assert ds.array == approx(np.array([[1.10, 2.8, 3.2]]))
    assert ds.labels == ['Time', 'Volume', 'Pressure']
    assert ds.units == ['s', 'ml', 'mbar']


def test_02():
    """
    Two rows, three columns.
    """
    ds = DataSeries(file_02)

    assert ds.array == approx(np.array([[1.10, 2.8, 3.2], [1.12, 2.9, 3.1]]))


def test_03(capsys):
    """
    Two rows, three columns.
    Less labels than values -> desire warning thrown.
    """
    with pytest.warns(UserWarning, match=r'label'):
        ds = DataSeries(file_03)


def test_04(capsys):
    """
    Two rows, three columns.
    Less units than values -> desire warning thrown.
    """
    with pytest.warns(UserWarning, match=r'unit'):
        ds = DataSeries(file_04)


def test_05():
    """
    Two rows, three columns, no topline.
    """
    ds = DataSeries(file_05)

    assert ds.array == approx(np.array([[1.10, 2.8, 3.2], [1.12, 2.9, 3.1]]))
    assert ds.labels == ['Time', 'Volume', 'Pressure']
    assert ds.units == ['s', 'ml', 'mbar']


def test_06():
    """
    Two rows, three columns, no topline and no labels.
    """
    with pytest.warns(UserWarning, match=r'label'):
        ds = DataSeries(file_06)

    assert ds.array == approx(np.array([[1.10, 2.8, 3.2], [1.12, 2.9, 3.1]]))
    assert ds.labels == ['0', '1', '2']
    assert ds.units == ['s', 'ml', 'mbar']


def test_07():
    """
    Two rows, three columns, no topline, no labels and no units.
    """
    with pytest.warns(UserWarning):
        ds = DataSeries(file_07)

    assert ds.array == approx(np.array([[1.10, 2.8, 3.2], [1.12, 2.9, 3.1]]))
    assert ds.labels == ['0', '1', '2']
    assert ds.units == [None, None, None]


def test_08():
    """
    Unsupported file format
    """
    with pytest.raises(ValueError) as msg:
        ds = DataSeries('nonexisting_file.json')

    msg = str(msg.value).lower()
    assert 'file' in msg
    assert 'supported' in msg
    assert 'csv' in msg


# Value rows in CSV file do not all have the same length
@pytest.mark.parametrize('test_input', [
    file_09,    # one or more values too much
    file_10,    # one or more values missing
])
def test_09(test_input):
    with pytest.raises(ValueError) as msg:
        ds = DataSeries(file_09)

    msg = str(msg.value).lower()
    assert 'homogeneous' in msg
