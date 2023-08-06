"""
Class PVCurve

2020, September 4
"""

import numpy as np
import warnings
import stringunitconverter as suc
import inspect

from . import curve
from . import interpolate
from fonsim.conversion import indexmatch
import fonsim.constants.norm as cnorm


class PVCurve(curve.Curve):
    """
    Class to ease working with pv-curves

    Warning: original data in DataSeries object may be modified by this function.
    Take a deepcopy if modification undesirable.

    The autocorrect functionality provides a little tool
    to correct measurement data.
    Parameter ``autocorrect`` should be a tuple of length two
    (respectively volume and pressure)
    or a scalar.
    The elements of this tuple, or the scalar, can be:

    - False: No correction applied.
    - True: Default correction applied.
      For volume, the volume at index 0 will equal zero.
      For pressure,
      the pressure at index 0 will equal standard atmospheric pressure.
    - A scalar value: Default correction is applied
      whereafter an offset with the given value is applied.
      Units are m^3 for volume and Pa for pressure.
    - A function: The function is applied to the value series.
      The function should take the value series as argument
      and should return the new value series.

    Note: the pressure_reference parameter looses its effect
    when autocorrect is applied to pressure.

    Note: The volume data sequence should be increasing or decreasing,
    otherwise the interpolation function will not work.

    Example:

    .. code-block:: python

       import fonsim

       # Create PVCurve object
       curve = fonsim.data.pvcurve.PVCurve('mypvcurvefile.csv',
                       pressure_reference='relative', autocorrect=True)

       # Readout the absolute pressure and its derivative to volume
       # at volume 3.8e-6 m^3 (= 3.8 ml)
       p, dp_dv = PVCurve.fdf_volume(3.8e-6)

    TODO Discuss format of CSV file.

    :param data: filepath to CSV file or DataSeries-like object
    :param pressure_reference: "relative" or "absolute"
    :param autocorrect: see description
    :param interpolation_opts: kwargs for interpolation function
    """
    def __init__(self, data, pressure_reference="relative", autocorrect=False,
                 **interpolation_opts):
        super().__init__(data,
                         key_x='volume', key_f='pressure',
                         convert_to_base_si=True,
                         autocorrect=False,
                         **interpolation_opts)
        # Map p and v to f and x
        self.v = self.x
        self.p = self.f

        # To absolute pressure
        if pressure_reference == "relative":
            self.p += cnorm.pressure_atmospheric
        elif pressure_reference == "absolute":
            pass
        else:
            msg = 'Pressure reference not recognized. ' +\
                  "Expected 'relative' or 'absolute' but received '" + pressure_reference + "'."
            warnings.warn(msg, UserWarning, stacklevel=2)

        # Autocorrect
        # TODO use instead autocorrect function in class Curve
        '''
        if autocorrect:
            self.autocorrect(autocorrect)
        '''
        if autocorrect:
            # If single function specified, warn user of the effect his has
            if callable(autocorrect):
                msg = 'Parameter autocorrect received as argument a single function. ' +\
                      'This given function will be applied sequentially to both volume and pressure data.'
                warnings.warn(msg, UserWarning, stacklevel=2)
            # Unwrap
            if not isinstance(autocorrect, (tuple, list)):
                autocorrect = [autocorrect, autocorrect]
            # Two helper functions
            def isfalse(a):
                return isinstance(a, bool) and a is False
            def convert_from_boolean(a):
                return 0 if isinstance(a, bool) and a is True else a
            # Process both
            if callable(autocorrect[0]):
                self.v = autocorrect[0](self.v)
            elif not isfalse(autocorrect[0]):
                a = convert_from_boolean(autocorrect[0])
                self.v = self.v - self.v[0] + a
            if callable(autocorrect[1]):
                self.p = autocorrect[1](self.p)
            elif not isfalse(autocorrect[1]):
                a = convert_from_boolean(autocorrect[1])
                self.p = self.p - self.p[0] + cnorm.pressure_atmospheric + a

    def get_initial_volume(self, p0):
        """
        Get the volume of the first datapoint on the curve that
        approaches the provided pressure value the closest

        TODO what is this function used for?

        :param p0: pressure at which to find the first matching volume
        :return: first closest matching volume
        """
        i0 = 0
        for i in range(len(self.p)-1):
            # check if p0 is crossed
            if self.p[i] <= p0 <= self.p[i+1] or \
               self.p[i] >= p0 >= self.p[i+1]:
                # linear interpolation
                slope = (self.v[i+1]-self.v[i]) / (self.p[i+1]-self.p[i])
                return self.v[i] + slope*(p0-self.p[i])
            # keep a record of the index that approaced p0 the closest in
            # case no crossing with p0 is found
            if abs(p0-self.p[i]) < abs(p0-self.p[i0]):
                i0 = i
        return self.v[i0]

    def fdf_volume(self, volume):
        """
        Readout the pressure for a given volume

        :param volume: volume in [m3]
        :return: f, df
        """
        return self.fdf(volume)

    def __str__(self):
        #txt = "PCurve object"
        txt = self.__repr__()
        txt += "\n  Number of datapoints:             " + str(len(self.v))
        txt += "\n  Maximum relative pressure [bar]:  " + str((max(self.p)-cnorm.pressure_atmospheric)/suc.get_factor("bar"))
        txt += "\n  Maximum volume [ml]:              " + str(max(self.v)/suc.get_factor("ml"))
        txt += "\n  Maximum normalvolume [ml]:        " + str(max(self.nv)/suc.get_factor("ml"))
        txt += "\n  Minimum relative pressure [bar]:  " + str((min(self.p)-cnorm.pressure_atmospheric)/suc.get_factor("bar"))
        txt += "\n  Minimum volume [ml]:              " + str(min(self.v)/suc.get_factor("ml"))
        txt += "\n  Minimum normalvolume [ml]:        " + str(min(self.nv)/suc.get_factor("ml"))
        return txt
