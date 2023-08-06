"""
Class System

2020, July 22
"""

import warnings

from . import component as cmp
from . import terminal as tmn
from . import node


class System:
    """
    A System is a collection of interconnected components.
    It contains the Component objects
    and keeps track of how they are connected to each other.
    A System with components is created
    by first creating the System object,
    then adding components to this object
    and finally connecting these components to each other.

    :param label: Label of the system, optional and currently not important.
    """
    def __init__(self, label=None):
        # Label
        self.label = label
        # List with objects of all the components in the system
        self.components = []
        # Dict to get an object pointer from its label property
        self.components_by_label = {}
        # Dict with as keys the components and as values integers
        # identifying the part of the network the component is connected
        # to. In case all components are connected together, all
        # dict values are the same, but they can be different if there
        # are two or more subsystems that are not connected to each other
        self.component_system = {}
        # List with nodes where two or more terminals connect together
        self.nodes = []

    def add(self, *components):
        """
        Add components to the system.

        :param components: Component object(s) to be added to the system
        :return: None
        """
        for component in components:
            if component.label not in self.components_by_label.keys():
                # Add component to the system
                self.components.append(component)
                self.components_by_label[component.label] = component
                # Create separate subsystem for the component
                # TODO document what 'subsystem' exactly implies
                if len(self.component_system) <= 0:
                    system_id = 0
                else:
                    system_id = max(self.component_system.values()) + 1
                self.component_system[component] = system_id
                # Create separate node for every component terminal
                for terminal in component.terminals:
                    self.nodes.append(node.Node(terminal))
            else:
                msg = 'Component labels need to be unique ' +\
                      'but {} already'.format(component.label) +\
                      'exists in system {}'.format(self.label) + '.'
                raise ValueError(msg)

    def __iadd__(self, component):
        """"
        Add components to the system.
        Also see: method ``Component.add``.

        :param component: Component object to be added to the system
        """
        self.add(component)
        return self

    def get_component_and_terminal(self, arg):
        """
        Get a pair of a Component and a Terminal
        given an argument ``arg``.
        This argument can be:

        - a string specifying a component label present in the system
        - a Component object
        - a Terminal object
        - a Tuple with first the component label and then the terminal label as strings

        If multiple choices are available, this method
        may make an undefined choice.

        :param arg: see desription
        :return: Component object, Terminal object
        """
        # Do conversion depending on type of arg
        if type(arg) is str:
            component = self.components_by_label[arg]
            terminal = component.get_terminal()
        elif isinstance(arg, cmp.Component):
            component = arg
            terminal = component.get_terminal()
        elif type(arg) is tmn.Terminal:
            component = arg.component
            terminal = arg
        elif type(arg) is tuple:
            component = self.components_by_label[arg[0]]
            terminal = component.get_terminal(arg[1])
        else:
            print("Error: did not recognize {}. Aborting connection".format(arg))
            return

        return component, terminal

    def connect_common(self, *args):
        """
        Connect two or more component terminals together. In case terminals are not
        specified directly, the Component objects decide on which of
        their terminals to connect.
        All Terminals are connected to each other,
        aka to a **common Node**.
        Making the connection is handled with the method ``self.connect_two_terminals``.

        The components and/or terminals to connect should be
        as specified in the method ``System.get_component_and_terminal``.

        For instead making sequential connections, use the method ``System.connect``.

        :param args: component terminals
        :return: None
        """
        terminals = []
        components = []
        # Resolve references
        for arg in args:
            component, terminal = self.get_component_and_terminal(arg)
            components.append(component)
            terminals.append(terminal)

        # Connect terminals
        for i in range(len(terminals)-1):
            self.connect_two_terminals(terminals[i], terminals[i+1])

        # Merge component subsystems
        merged_id = min([self.component_system[c] for c in components])
        for component in components:
            self.component_system[component] = merged_id

    def connect(self, *args):
        """
        Connect two or more components together
        by connecting their terminals.
        In case terminals are not
        specified directly, the Component objects decide on which of
        their terminals to connect.
        The connections are made in sequential pairs
        using the method ``System.connect_two_components``
        which in turn uses the method ``self.connect_two_terminals``.

        The components and/or terminals to connect should be
        as specified in the method ``System.get_component_and_terminal``.

        For instead connecting all components to a common Node,
        use the method ``System.connect_common``.

        :param args: component terminals
        :return: None
        """
        for i in range(len(args)-1):
            self.connect_two_components(args[i], args[i+1])

    def connect_two_components(self, component_a, component_b):
        """
        Connect two Components to each other.
        The connection is made using the method ``self.connect_two_terminals``.

        The component arguments component_a and component_b can be
        as specified in the method ``System.get_component_and_terminal``.

        :param component_a: First component, see description
        :param component_b: Second component, see description
        :return: None
        """
        # Resolve components and terminals
        component_a, terminal_a = self.get_component_and_terminal(component_a)
        component_b, terminal_b = self.get_component_and_terminal(component_b)

        # Connect terminals
        self.connect_two_terminals(terminal_a, terminal_b)

        # Merge component subsystems
        merged_id = min([self.component_system[c] for c in [component_a, component_b]])
        for component in [component_a, component_b]:
            self.component_system[component] = merged_id

    def connect_two_terminals(self, terminal_a, terminal_b):
        """
        Connect two system terminals together in a Node.
        These nodes exist for the workings of the solver
        and have nothing to do with any nodes in the fluidic networks being simulated.

        :param terminal_a: Terminal object
        :param terminal_b: Terminal object
        :return: None
        """
        # Make sure the requested terminals are present in the system
        # Check using component label such that dict can be searched,
        # is lower complexity than iterating through list of components.
        for terminal in (terminal_a, terminal_b):
            if terminal.component.label not in self.components_by_label:
                msg = 'Component <' + str(terminal.component) + '>, ' + \
                      'belonging to terminal <' + str(terminal) + '>, ' + \
                      'is not found in the system. ' + \
                      'Component is now added automatically.'
                warnings.warn(msg, UserWarning, stacklevel=2)
                self.add(terminal.component)

        # Mark the terminals as connected
        terminal_a.isconnected = True
        terminal_b.isconnected = True

        # Find nodes containing the terminals
        # The nodes were created when the components were added to the system.
        # Intially, each terminal had its own node, and connecting two terminals together
        # basically consists of merging two relevant nodes.
        node_a = None
        node_b = None
        for node in self.nodes:
            if node.contains_terminal(terminal_a):
                node_a = node
            if node.contains_terminal(terminal_b):
                node_b = node

        # Merge nodes into one
        # If the two nodes are equal,
        # then the two terminals are already connected.
        if node_a != node_b:
            node_a.merge_node(node_b)
            self.nodes.remove(node_b)

    def get(self, component_label):
        """
        :param component_label: Label of the desired component.
        :return: Component object with the given label.
        """
        return self.components_by_label[component_label]

    def get_connectivity_message(self):
        """
        Get a message describing the connectivity of the system
        in case not every component is connected together.

        :return: message string
        """
        message = ""

        # Check whether all components are connected together or not
        if len(set(self.component_system.values())) > 1:
            # Get dictionary with as keys the subsystem identifiers
            # and as values the components in those subsystems
            system_components = dict([])
            for comp, sys in self.component_system.items():
                if sys not in system_components.keys():
                    system_components[sys] = [comp,]
                else:
                    system_components[sys].append(comp)

            # Check whether any subsystem contains only a single component
            singles = []
            for sys, comps in system_components.items():
                if len(comps) <= 1:
                    singles.append("'{}'".format(comps[0].label))

            # Create message
            if len(singles) >= 1:
                message = "Component{} ".format("s"*(len(singles)>1))
                message += ", ".join(singles[:-1])
                message += " and "*(len(singles)>1) + singles[-1]
                message += " is " if len(singles)==1 else " are "
                message += "not connected to any other components"
            else:
                message = "Not all components are connected together"

        return message
