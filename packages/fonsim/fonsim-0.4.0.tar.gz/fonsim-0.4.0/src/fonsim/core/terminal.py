"""
Class Terminal

2020, July 22
"""

import warnings

from . import variable


class Terminal:
    """
    Component connection point with local through and across variables.

    Note: In any particular Terminal object,
    there cannot be more than one variable with the same key.

    :param label: Label to refer to the Terminal later on. Free to choose.
    :param variables: Variable objects that will belong to the Terminal.
    """
    def __init__(self, label, variables, variable_labels={}):
        # Check input
        all_keys = [var.key for var in variables]
        if len(all_keys) > len(set(all_keys)):
            msg = 'In a single Terminal, all Variables must have a different key, ' + \
                  'however, encountered the following keys: ' + str(all_keys) + '.'
            raise ValueError(msg)

        # Assign arguments to properties
        self.label = label

        # The Variable objects are stored in two dictionaries
        # depending on their orientation.
        self.variables_across = {}
        self.variables_through = {}
        for variable in variables:
            local_variable = variable.copy_and_attach(self)
            if variable.orientation == 'across':
                self.variables_across[variable.key] = local_variable
            elif variable.orientation == 'through':
                self.variables_through[variable.key] = local_variable
            else:
                msg = 'Terminals can only have "across" or "through" Variables, ' +\
                      'but encountered a Variable object ' +\
                      'with orientation "' + variable.orientation + '".'
                warnings.warn(msg, UserWarning, stacklevel=2)

        # Apply variable labels
        for key in variable_labels:
            if key in self.variables_across:
                self.variables_across[key].label = variable_labels[key]
            elif key in self.variables_through:
                self.variables_through[key].label = variable_labels[key]
            else:
                a = list(self.variables_across.keys()) + list(self.variables_through.keys())
                s = "', '"
                msg = f"Key '{key}' not found in the available variables " \
                      f"'{s.join(a)}'."
                raise ValueError(msg)

        # Component the Terminal belongs to
        self.component = None
        # Whether the Terminal is connected to another Terminal
        self.isconnected = False

    def get_variables(self, orientation=None):
        """
        Get list of all terminal variables with the given orientation.
        The orientation can be either "through" or "across". If not
        provided or None, all variables regardless of orientation are
        returned

        :param orientation: optional string specifying desired
                            variable orientation
        :return: list of Variable objects
        """
        if orientation == 'through':
            return list(self.variables_through.values())
        elif orientation == 'across':
            return list(self.variables_across.values())
        elif orientation is None:
            return self.get_variables('through') + \
                   self.get_variables('across')
        else:
            return []

    def get_variable(self, key):
        """
        Return the variable object attached to the terminal with the
        provided key, for example 'pressure'.
        If there is no variable with the requested key,
        None is returned.

        :param key: key of the variable to return
        :return variable: attached variable with the matching key
        """
        if key in self.variables_across.keys():
            return self.variables_across[key]
        if key in self.variables_through.keys():
            return self.variables_through[key]

    def __call__(self, arg):
        """
        Same as method ``self.get_variable()``.
        """
        return self.get_variable(arg)
