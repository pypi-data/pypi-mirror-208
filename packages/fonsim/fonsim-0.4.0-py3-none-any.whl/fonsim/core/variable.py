"""
Class Variable

2020, July 21
"""

import numpy as np
import warnings


class Variable:
    """
    A ``Variable`` object is used to denote the presence of a yet unknown numerical value.
    For each Variable object, the solver will search for the optimal numerical values over time.
    The solver does so by solving the system of equations that connect these variables together.
    The variables are connected by each other
    by connecting the Terminal objects that contain the values to each other.

    The parameter 'key' indicates the type label.
    Only Variable objects with the same type label can exchange information.

    The parameter 'orientation' should have value 'across' or 'through' or 'free'.
    'across' indicates that the value of the Variable will be shared
    with the Variable belonging to the other Terminal
    while 'through' indicates that its negative will be shared.
    The former is typically used with nondirectional values,
    such as pressure,
    while the latter is typically used with directional values,
    such as a massflow.
    'local' indicates that it will not be shared (feature WIP).

    :param key: type label, e.g. 'pressure', 'massflow'
    :param orientation: 'across', 'through' or 'free'.
    :param terminal: Terminal object to which Variable object get connected, default: None
    :param label: label, used to refer to a Variable instance later on
    :param initial_value: Initial value, default: 0
    :param range: tuple with min and max of allowed value range
    """
    def __init__(self, key, orientation, terminal=None, label='None',
                 initial_value=0., range=(-np.Inf, np.Inf)):
        # Check input
        if orientation not in ('across', 'through', 'local'):
            msg = 'Parameter "orientation" ' + \
                  'ought to have value "across" or "through" or "local", ' + \
                  'but encountered <' + orientation + '>.'
            warnings.warn(msg, UserWarning, stacklevel=2)
        if not isinstance(range, tuple) or \
                (isinstance(range, tuple) and len(range) != 2):
            msg = "Parameter 'range' must be a tuple of length two."
            raise ValueError(msg)

        # Assign arguments to object properties
        self.key = key
        self.orientation = orientation
        self.terminal = terminal
        self.label = str(label)
        self.initial_value = initial_value
        self.range = range

    def __str__(self):
        """
        Return a description string of the format
        ``Variable <self.key> of component <self.terminal.component.label>``.
        The component description part is only added
        if the variable belongs to the terminal of a component.

        :return: var_str: string with description of variable object
        """
        var_str = "Variable {}".format(self.key)
        if self.terminal is not None:
            var_str += " of component {}".format(self.terminal.component.label)
        return var_str

    def short_str(self, nb_var_chars=1):    # pragma: no cover
        """
        Return a short string describing the variable more as a symbol than in
        words. This string contains the first n letters of the variable name
        as well as (if applicable) the port and component it is attached to.

        :param nb_var_chars: number of characters with which the variable key
                             is abbreviated. Set to 0 to avoid abbreviation.
        :return var_str: short string representing the variable
        """
        var_str = self.key
        if nb_var_chars > 0:
            var_str = var_str[:min(nb_var_chars,len(var_str))]
        if self.terminal is not None:
            var_str += '_{}_{}'.format(self.terminal.label,
                                       self.terminal.component.label)
        return var_str

    def copy_and_attach(self, terminal):
        """
        Return a copy of the variable object attached to a given terminal.
        The returned variable has the same key, orientation and initial value
        but is otherwise unrelated to the Variable object
        it is called upon.

        :param terminal: Terminal object to attach the variable copy to
        :return variable: attached copy of the variable object
        """
        return Variable(self.key, self.orientation,
                        terminal=terminal, label=self.label,
                        initial_value=self.initial_value, range=self.range)
