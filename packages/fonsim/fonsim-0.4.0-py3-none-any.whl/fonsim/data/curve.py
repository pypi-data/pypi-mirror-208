"""
Class Curve

2020, September 1
"""

import stringunitconverter as suc
import warnings

from . import dataseries
from . import interpolate
from fonsim.conversion import indexmatch
import inspect


class Curve:
    """
    Class to ease working with pv- and pn-curves
    and similar curves
    
    :param data: filepath to CSV file or DataSeries-like object
    """
    def __init__(self, data, key_x, key_f, convert_to_base_si=False,
                 autocorrect=False,
                 **interpolation_opts):
        # Allow passing filepaths
        if isinstance(data, str):
            ds = dataseries.DataSeries(data)
        elif isinstance(data, bytes):
            msg = 'Support for the type bytes for the argument data ' + \
                  'will be removed in the future. It was introduced ' + \
                  'because pkgutil was used, but pkgutil was replaced ' + \
                  'with importlib_resources.'
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            ds = dataseries.DataSeries(filename='.csv', bytestring=data)
        else:
            ds = data

        # Warn if given interpolation_opts
        # are appropriate for the interpolation function.
        keys_allowed = set(inspect.signature(interpolate.interpolate_fdf).parameters.keys())
        keys_given = set(interpolation_opts.keys())
        keys_not_allowed = keys_given - keys_allowed
        if len(keys_not_allowed):
            msg = 'The following argument keys were given but are not supported ' + \
                  'by the interpolation function: ' + str(*keys_not_allowed) + '.'
            warnings.warn(msg, UserWarning, stacklevel=2)

        self.interpolation_opts = interpolation_opts

        # Get indices of desired x and f
        i_x = indexmatch.get_index_of_best_match(key_x, ds.labels)
        i_f = indexmatch.get_index_of_best_match(key_f, ds.labels)

        # Extract x and f
        self.x = ds.array[:, i_x]
        self.f = ds.array[:, i_f]

        # Convert to base SI
        # ! to be replaced with better unit conversion method
        if convert_to_base_si:
            self.x *= suc.get_factor(ds.units[i_x])
            self.f *= suc.get_factor(ds.units[i_f])

        # Autocorrect
        if autocorrect:
            self.autocorrect(autocorrect)

    def autocorrect(self, arg):
        """
        TODO implement autocorrect here
        I made this a separate function
        such that child classes can modify the data as they want
        before they use the autocorrect functionality.

        :return None:
        """
        pass

    def fdf(self, x):
        """
        Readout f(x)

        :param x: x
        :return: f, df
        """
        return interpolate.interpolate_fdf(x, self.x, self.f,
                                           **self.interpolation_opts)

    def __str__(self):
        #txt = "Curve object"
        txt = self.__repr__()
        txt += "\n  Number of datapoints:             " + str(len(self.x))
        txt += "\n  Maximum x:                        " + str((max(self.x)))
        txt += "\n  Minimum x:                        " + str((min(self.x)))
        txt += "\n  Maximum f(x):                     " + str((max(self.f)))
        txt += "\n  Minimum f(x):                     " + str((min(self.f)))
        return txt
