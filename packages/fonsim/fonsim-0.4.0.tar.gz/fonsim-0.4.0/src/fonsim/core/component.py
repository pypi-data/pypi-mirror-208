"""
Class Component

2020, July 21
"""

import numpy as np
import inspect
import copy
import warnings

from fonsim.conversion import indexmatch


class Component:
    """Components to build a system with

    This base class provides a starting ground
    to build components usable in a FONSim system.
    Several examples are found in the FONSim standard library
    (see the :py:mod:`fonsim.components` package).
    Also, be sure to check out the
    :doc:`tutorial on custom components</tutorials/custom_components>`.

    **Interaction with other components**
    The component terminals (instances of :py:class:`.Terminal`)
    specify the possibilities for interaction with other components.
    They are added using the method :py:meth:`.Component.set_terminals`.
    Example of adding two fluidic terminals with labels 'a' and 'b':

    .. code-block:: python

       self.set_terminals(Terminal('a', terminal_fluidic, {'pressure': 'p0', 'massflow': 'mf0'}),
                          Terminal('b', terminal_fluidic, {'pressure': 'p1', 'massflow': 'mf1'}))

    The list ``terminal_fluidic`` contains two :py:class:`.Variable` instances,
    one for pressure and one for massflow.
    It is defined in
    :repo:`components/terminals.py<src/fonsim/components/terminals.py>`.
    If the :py:meth:`.Component.auto` and :py:meth:`.Component.auto_state`
    methods are used to define  methods :py:meth:`.Component.evaluate`
    and :py:meth:`.Component.update_state`,
    then the variable labels 'p0', 'mf0' etc. will be used further on
    (for an example, please see the tutorial linked to earlier on).
    The lists of terminals and of the terminal variables are respectively
    kept in the member variables ``terminals`` and ``arguments``.

    **States**
    State variables are added using the :py:meth:`.Component.set_states`
    method. These variables are considered to be *local*
    because they are not accessible to other components.
    Example of adding a single state with label 'mass':

    .. code-block:: python

       self.set_states(Variable('mass', 'local', label='m', initial_value=5e-3))

    The state variables are subsequently available as a list
    in the member variable ``states``.

    **Internal behavior**
    The two methods :py:meth:`.Component.evaluate`
    and :py:meth:`.Component.update_state` govern the internal behaviour.
    The former specifies a relation between the terminal and state variables
    that should be respected at each discrete timestep
    and the latter expresses how the state variables change over a timestep
    given a previous state and the terminal variables.

    There are **two ways** to define these methods.
    By far the easiest is to use the :py:meth:`.Component.auto`
    and :py:meth:`.Component.auto_state` methods,
    as a method or as a decorator, because this allows
    to refer to the terminal and state variables by their label.
    The documentation of these two methods discusses how to do so.
    This is also the approach discussed
    in the custom component tutorial mentioned earlier.

    The second way is to conform to form of the :py:meth:`.Component.evaluate`
    :py:meth:`.Component.update_state` methods.
    This requires variables to be referred to by their index
    in the passed arrays, making this method prone to errors if done manually.
    Knowing the indices to use requires either searching the terminal variables
    in the member variable ``arguments``
    or putting the variables in that member variable in a particular order,
    preferably using :py:meth:`.Component.set_arguments`.
    Note that :py:meth:`.Component.set_terminals` modifies ``arguments``.

    **Storage of the state and terminal variable values**
    The state data (e.g. amount of fluid inside actuator)
    is saved as 2D-array in the components themselves
    (and the solver always refers to these)
    while the argument data (e.g. pressure, flow in/out)
    is saved as a list of _references_
    to nameless 1D-arrays created by the solver.
    The component object provides functionality for the solver
    to allocate memory for the states,
    but not for allocating the variables.
    The solver takes care of calling these functions necessary.
    The object property ``state_history`` holds the 2D-array
    and object property ``argument_history`` holds a list
    with references to the 1D-arrays.

    :param label: Component name.
    """
    def __init__(self, label):
        # component name
        self.label = label

        # terminals of component
        self.terminals = []
        # variables for the evaluation of the left-hand side of the residual
        # and for the state update equation
        self.arguments = []
        # other variables that are updated based on the solutions for the arguments
        self.states = []
        # Initial values for the state
        self.state_initial = []
        # number of evaluation equations
        self.nb_equations = 0
        # maximum step change of arguments for iterative stepping
        # Note: It appears this variable is not used anywhere?
        self.arguments_stepsize = []

        # References to calculated values
        # Will hold 2D Numpy array
        self.state_history = None
        # Will hold 2D Numpy array
        self.argument_history = None

        # Autocall
        # Two lists below are filled by the respective two autocall decorators
        self.arg_indices = []
        self.arg_indices_state = []

    def evaluate(self, values, jacobian_state, jacobian_arguments, state, arguments, elapsed_time):
        """
        Evaluates the component internal equations.
        **This method should be static**.

        Note: only evaluate left-hand side (LH) of equation, equation should be structured such that RH is always zero.

        :param values: array where the equation residuals will be stored.
        :param jacobian_state: array where the jacobian to the state will be stored.
        :param jacobian_arguments: array where the jacobian to the arguments will be stored.
        :param state: numerical values belonging to the state Variables.
        :param arguments: numerical values belonging to the Variables.
        :param elapsed_time: ? TODO.
        :return: None
        """
        # Empty here, as this method is to be overriden by child class definition.
        # For usage examples, please see the standard components in ``src/fonsim/components/``.
        pass

    def update_state(self, state_new, jacobian, state, arguments, dt):
        """
        Evaluates the update to the component state.
        **This method should be static**.

        :param state_new: array where the new state values will be stored.
        :param jacobian: array where the jacobian to the arguments will be stored.
        :param state: numerical values belonging to the state Variables.
        :param arguments: numerical values belonging to the Variables.
        :param dt: time discretization timestep.
        :return: None
        """
        # Empty here, as this method is to be overriden by child class definition.
        # For usage examples, please see the standard components in ``src/fonsim/components/``.
        pass

    def set_terminals(self, *terminals):
        """
        Overwrite component terminals list with the provided Terminal
        objects and attach those terminals to the component.

        :param terminals: one or more Terminal objects
        :return: None
        """
        self.terminals = list(terminals)
        for t in self.terminals:
            t.component = self
        # Set arguments
        args = []
        for t in self.terminals:
            args.extend(t.get_variables())
        self.set_arguments(*args)

    def set_arguments(self, *arguments):
        """
        Overwrite component arguments list with the provided Variable
        objects.

        :param arguments: one or more Variable objects
        :return: None
        """
        self.arguments = list(arguments)

    def set_states(self, *states):
        """
        Overwrite component states list with the provided Variable
        objects.

        :param states: one or more Variable objects
        :return: None
        """
        self.states = list(states)

    def _cache_argumentfetcher(self, f, extra_args=[]):
        """
        :param f: function that takes labels of function args as arguments,
                  together with the other arguments `required_args`.
        :return: list mapping argument and state indices to function arguments
        """
        extra_args = list(extra_args)
        var_labels = [v.label for v in self.arguments + self.states]
        func_args = list(inspect.signature(f).parameters.keys())
        # build a list with for every argument in the function signature the
        # index of the corresponding variable in var_labels
        arg_indices = []
        for func_arg in func_args:
            for j, var in enumerate(var_labels + extra_args):
                if func_arg == var:
                    arg_indices.append(j)
                    break

        # check that extra arguments are not found in variables
        extra_args_in_variables = set(extra_args) & set(var_labels)
        if extra_args_in_variables:
            msg = f'Name collision: extra argument(s) ' \
                  f'`{"`, `".join(extra_args_in_variables)}` ' \
                  f'found in argument and/or state variables ' \
                  f'of component {self.label}.'
            raise ValueError(msg)
        # check if every argument in the signature is matched to a variable
        unresolved_labels = set(func_args) - set(var_labels + extra_args)
        if unresolved_labels:
            terminal_labels = set(a.label for a in self.arguments)
            state_labels = set(a.label for a in self.states)
            msg = f'Suspect error in Variable labels of ' \
                  f'component `{self.label}`: function {f.__name__} ' \
                  f'references argument(s) `{"`, `".join(unresolved_labels)}`, ' \
                  f'but no variables with those labels were found among ' \
                  f'the terminal variables (`{"`, `".join(terminal_labels)}`)'
            if state_labels:
                msg += f' or state variables (`{"`, `".join(state_labels)}`)'
            if extra_args:
                msg += f' or the extra arguments (`{"`, `".join(extra_args)}`)'
            msg += '.'
            raise ValueError(msg)

        return arg_indices

    def _finite_diff_residuals(self, jac_args, jac_state, t,
                    args, state, y, f, d_rel=1e-4, d_min=1e-12):
        """
        :param jac_args: numpy array where derivatives WILL BE WRITTEN
        :param jac_state: numpy array where derivatives WILL BE WRITTEN
        :param t: elapsed time
        :param i: argument index to calculate derivatives to
        :param args: arguments array
        :param state: states array
        :param y: residual array
        :param f: evaluate residuals function
        :param d_rel: (maximum) relative FD disturbance
        :param d_min: minimum absolute FD disturbance
        """
        # TODO improve this so this method has less arguments?
        # loop over all arguments that have an influence on the residual
        nb_args = len(self.arguments)
        for i in filter(lambda a: a < nb_args, self.arg_indices):
            x = np.concatenate((args, state))
            disturbance = max(abs(x[i]) * d_rel, d_min)
            if x[i] < 0: disturbance *= -1
            x[i] += disturbance
            x = np.append(x, t)
            y_mod = f(*x[self.arg_indices])
            jac = (y_mod - y) / disturbance
            if i < nb_args:
                jac_args[:, i] = jac
            else:
                jac_state[:, i - nb_args] = jac

    def _finitediff_state(self, jacobian, dt,
                         args, state, y, f, d_rel=1e-4, d_min=1e-12):
        """
        :param jacobian: numpy array where derivatives WILL BE WRITTEN
        :param dt: timestep, required to call f
        :param i: argument index to calculate derivatives to
        :param args: arguments array
        :param state: states array
        :param y: new state array
        :param f: state update function
        :param d_rel: (maximum) relative FD disturbance
        :param d_min: minimum absolute FD disturbance
        """
        # TODO improve this so this method has less arguments?
        # loop over all arguments that have an influence on the residual
        nb_args = len(self.arguments)
        for i in filter(lambda a: a < nb_args, self.arg_indices):
            x = np.concatenate((args, state))
            disturbance = max(abs(x[i]) * d_rel, d_min)
            if x[i] < 0: disturbance *= -1
            x[i] += disturbance
            x = np.append(x, dt)
            y_acc = f(*x[self.arg_indices_state])
            y_mod = np.array([y_acc[s.label] for s in self.states])
            jacobian[:, i] = (y_mod - y) / disturbance

    def auto(self, func):
        """Wrapper for Component.evaluate
        Wrapper that converts a function taking as arguments
        terminal and state variable labels to a function taking arrays
        and conforming to the :py:meth:`.Component.evaluate` signature.
        Often used as a decorator.

        If the given function ``func`` returns a Numpy array and a list,
        then it is assumed that the former is the array of residuals
        and the latter the component jacobian.
        Else, if it returns one Numpy array,
        it is assumed that that is the array of residuals,
        and FONSim will automatically estimate the jacobian
        using finite differences.

        The following example demonstrates
        the creation of a residual and a jacobian.
        The third and the fourth line specify the derivatives
        of the first residual (with array index 0)
        respectively to the variables *mf0* and *mf1*.

        .. code-block:: python

           values, jacobian = np.zeros(1, dtype=float), [{},]
           values[0] = mf0 + mf1
           jacobian[0]['mf0'] = 1
           jacobian[0]['mf1'] = 1
           return values, jacobian

        :param func: ``simplified update_state`` function
        :return: new ``update_state`` function
        """
        nb_args = len(self.arguments)

        # Cache argument fetcher
        self.arg_indices = self._cache_argumentfetcher(func, extra_args=['t',])
        # Cache manual jacobian writer
        # label -> variable index of np.concatenate((arguments  states))
        var_indices_by_label = dict((var.label, i) for i, var in enumerate(self.arguments + self.states))
        # Register number of equations
        init_vals = [v.initial_value for v in self.arguments + self.states] \
            + [0, ] * (max(self.arg_indices) + 1 - len(self.arguments + self.states)) \
            if self.arg_indices else []     # `max()` with empty list or array errors out
        ret = func(*np.array(init_vals)[self.arg_indices])
        if ret is None:
            msg = f"The function {str(func)} of component {str(self)} " \
                  f"returned None, however residual values and optionally " \
                  f"their derivatives were expected. " \
                  f"Perhaps the 'return' statement is missing or incomplete?"
            raise RuntimeError(msg)
        self.nb_equations = len(ret[0] if isinstance(ret, tuple) else ret)

        # The new method, which will be returned
        def evaluate_new(values, jacobian_state, jacobian_arguments, state, arguments, elapsed_time):
            # Fetch args
            args = np.concatenate((arguments, state, [elapsed_time,]))[self.arg_indices]
            # Evaluation of equation residuals
            ret = func(*args)
            # Read in function return value
            jacobian_given = isinstance(ret, tuple)
            if jacobian_given:
                values[:], jac = ret
            else:
                values[:] = ret
            # Handle derivatives, manually specified or finite differences
            if jacobian_given:
                # ! not specified indices are not set to zero !
                for i in range(self.nb_equations):
                    for key, value in jac[i].items():
                        j = var_indices_by_label[key]
                        if j < nb_args:
                            jacobian_arguments[i, j] = value
                        else:
                            jacobian_state[i, j-nb_args] = value
            else:
                self._finite_diff_residuals(jacobian_arguments, jacobian_state,
                                            elapsed_time, arguments, state, values, func)
        return evaluate_new

    def auto_state(self, func):
        """Wrapper for ``Component.update_state``
        Wrapper that converts a function having as parameters
        terminal and state variable labels to a function taking arrays
        and conforming to the :py:meth:`.Component.update_state` signature.
        Often used as a decorator.

        If the given function ``func`` returns two dictionaries,
        then it is assumed that the former contains the updated states
        and the latter the component jacobian.
        Else, if it returns only one dictionary,
        it is assumed that it contains the updated states,
        and FONSim will automatically estimate the jacobian
        using finite differences.

        The following example demonstrates
        the creation of an updated state and a jacobian.
        The third and the fourth line specify the derivatives
        of the state *m*
        respectively to the variables *p* and *mf*.

        .. code-block:: python

           jacobian = {}
           m_new = m + dt * mf
           jacobian['m/p'] = 0
           jacobian['m/mf'] = dt
           return {'m': m_new}, jacobian

        :param func: ``simplified update_state`` function
        :return: new ``update_state`` function
        """
        nb_args = len(self.arguments)
        nb_states = len(self.states)

        # Cache argument fetcher
        self.arg_indices_state = self._cache_argumentfetcher(func, extra_args=['dt',])

        # The new method, which will be returned
        def update_state_new(state_new, jacobian, state, arguments, dt):
            # Fetch args
            args = np.concatenate((arguments, state, [dt,]))[self.arg_indices_state]
            # Evaluation of equation residuals
            ret = func(*args)
            if ret is None:
                msg = f"The function {str(func)} of component {str(self)} " \
                      f"returned None, however state values and optionally " \
                      f"their derivatives were expected. " \
                      f"Perhaps the 'return' statement is missing or incomplete?"
                raise RuntimeError(msg)
            jacobian_given = isinstance(ret, tuple)
            if jacobian_given:
                vs, jac = ret
            else:
                vs = ret
            # Write out new state
            # ! the returned dictionary should contain values for all states !
            state_new[:] = [vs[s.label] for s in self.states]
            # Jacobian: manually specified or using finite differences
            if jacobian_given:
                # Transform back to numpy arrays
                for j in range(nb_states):
                    for i in range(nb_args):
                        key = self.states[j].label + '/' + self.arguments[i].label
                        jacobian[j, i] = jac[key] if key in jac else 0
            else:
                self._finitediff_state(jacobian,
                                       dt, arguments, state, state_new, func)
        return update_state_new

    def get_terminal(self, terminallabel=None):
        """
        Returns Terminal object.
        If no label given,
        returns the first unconnected terminal.
        If label given,
        returns terminal with that label.
        If no terminal found, returns None.

        :param terminallabel: Label of terminal
        :return: Terminal object
        """
        if terminallabel is None:
            for terminal in self.terminals:
                if terminal.isconnected is False:
                    return terminal
            return self.terminals[0]
        else:
            for terminal in self.terminals:
                if terminal.label == terminallabel:
                    return terminal
        return None

    def get_state(self, label):
        """
        Get simulation results.
        Supports 'smart matching' by comparing string distances.

        :param label: state label, e.g. 'volume'
        :return: Numpy ndarray object
        """
        labels = [state.key for state in self.states]
        state_index = indexmatch.get_index_of_best_match(label, labels)
        return self.state_history[:, state_index]

    def get_all(self, variable_key, terminal_label=None):
        """
        Get simulation results.
        Supports 'smart matching' by comparing string distances.

        :param variable_key: key of variable, e.g. 'pressure'
        :param terminal_label: label of terminal, e.g. 'a'
        :return: Numpy ndarray object and Terminal object
        """
        # Similarity scores for variable keys
        sim_var = np.array([indexmatch.similar(variable_key, a.key) for a in self.arguments])
        # Similarity scores for terminal labels, with the terminals belonging to the variables
        sim_tmn = np.array([indexmatch.similar(terminal_label, a.terminal.label) for a in self.arguments])\
            if terminal_label is not None else np.ones(len(self.arguments))
        # Combined similarity scores using element-by-element multiplication
        sim_com = np.multiply(sim_var, sim_tmn)
        # Index of variable with highest combined similarity score
        i = np.argmax(sim_com)
        # Retrieve that variable and the terminal belonging to it
        variable = self.arguments[i]
        term = variable.terminal
        # Return simulation data (1D Numpy array) and Terminal object
        return self.argument_history[:, i], term

    def get(self, variable_key, terminal_label=None):
        """
        Same as method ``self.get_all``, but returns only the first return value.
        """
        a, b = self.get_all(variable_key, terminal_label)
        return a
