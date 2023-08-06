"""
Class CustomWave

2020, September 5
"""

import numpy as np
import copy

import scipy.interpolate


def isincreasing(arr):
    """Helper function. Returns True if array strictly increasing, False otherwise."""
    return len(arr) < 2 or all([arr[i + 1] > arr[i] for i in range(len(arr) - 1)])


class Custom:
    """
    Custom wave

    The argument for wave_array should be a 2D-indexable array-like object
    (List, Tuple, numpy.ndarray, etc.)
    and contain the time values and the corresponding output values.
    One dimension should have size two.
    The function is transpose-agnostic.

    The argument for time_notation can be 'absolute' or 'relative'.
    In case of relative, each time value is relative
    to the one before it.

    The default argument 'previous' for 'kind'
    results in a rectangular wave (zero-order interpolation).
    The interpolation is handled using the Scipy method
    ``scipy.interpolate.interp1d``
    and the available interpolation kinds
    therefore are those supported by this Scipy method.
    For a complete reference,
    see https://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html.
    From above site (copied 2020, September 5):

      Specifies the kind of interpolation as a string
      (‘linear’, ‘nearest’, ‘zero’, ‘slinear’, ‘quadratic’, ‘cubic’, ‘previous’, ‘next’,
      where ‘zero’, ‘slinear’, ‘quadratic’ and ‘cubic’ refer to a spline interpolation
      of zeroth, first, second or third order;
      ‘previous’ and ‘next’ simply return the previous or next value of the point)
      or as an integer specifying the order of the spline interpolator to use.

    To readout the value (and therefore call the interpolation function),
    call the created object.

    Example:

    .. code-block:: python

       import fonsim

       # Create Custom wave object
       # times: 0.0, 1.0, 1.5 and values: 12, 18, 15
       wave_array = [[0.0, 12], [1.0, 18], [1.5, 15]]
       mywave = fonsim.wave.custom.Custom(wave_array, time_notation='absolute', kind='previous')

       # Read it out by calling the object
       y = mywave(1.2)  # y = array(18.)

    :param wave_array: indexable object, shape 2 x N or N x 2
    :param time_notation: 'absolute' or 'relative'
    :param kind: interpolation kind
    """
    def __init__(self, wave_array, time_notation='absolute', kind='previous'):
        # Take copy of input to avoid modifying input
        wave_array = copy.deepcopy(wave_array)

        # Convert to numpy array if it isn't yet one
        if not isinstance(wave_array, np.ndarray):
            wave_array = np.array(wave_array)

        # Take transpose by default
        wave_array = wave_array.T

        # Look at shape of given wave series and transpose as necessary
        if np.shape(wave_array)[0] != 2:
            wave_array = wave_array.T
        if np.shape(wave_array)[0] != 2:
            msg = 'Error: wave_series shape does not seem to be compatible: ' +\
                  'at least one dimension should have length two.'
            raise ValueError(msg)

        # Put in separate variable to ease handling
        times = wave_array[0, :]
        values = wave_array[1, :]

        # If absolute, check that the time series is increasing
        # and if not, raise exception
        if time_notation == 'absolute' and not np.all(np.diff(times) >= 0):
            msg = 'Given timeseries in wave_array is not increasing.'
            raise ValueError(msg)

        # If relative, check that all relative time values strictly positive
        if time_notation == 'relative' and not np.all(times >= 0):
            msg = 'Given relative timeseries in wave_array is not strictly positive.'
            raise ValueError(msg)

        # Convert given time series to absolute if relative
        if time_notation == 'relative':
            np.cumsum(times, out=times)

        # Preprocessing finished
        self.times = times
        self.values = values
        self.kind = kind

        # Interpolation function
        self.f = None
        self._update_interpolation_function()

    def _update_interpolation_function(self):
        """
        Update interpolation function

        :return: None
        """
        self.f = scipy.interpolate.interp1d(
            self.times, self.values, kind=self.kind,
            bounds_error=False, fill_value=(self.values[0], self.values[-1]))

    def __call__(self, time):
        """
        Overload call operator to allow calling the object (using ())
        to read out the value.

        :param time: elapsed time, in s
        :return: interpolated value
        """
        return self.f(time)

    def __add__(self, other):
        """
        Add offset on y-values.

        :param other: y offset, float
        :return: modified object
        """
        # Update values
        self.values += other
        # Update interpolation function
        self._update_interpolation_function()
        return self

    def __mul__(self, other):
        """
        Multiply y-values

        :param other: y multiplier, float
        :return: modified object
        """
        # Update values
        self.values *= other
        # Update interpolation function
        self._update_interpolation_function()
        return self
