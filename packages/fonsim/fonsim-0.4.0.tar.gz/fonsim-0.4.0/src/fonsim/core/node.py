"""
Class Node

2021, January 14
"""


class Node:
    """
    Connection between multiple component terminals
    """
    def __init__(self, *terminals):
        self.terminals = list(terminals)

    def contains_terminal(self, terminal):
        """
        Check if the node contains the requested terminal

        :param terminal: Terminal object
        :return: Boolean
        """
        return terminal in self.terminals

    def add_terminals(self, *terminals):
        """
        Connect terminals to the node

        :param terminals: Terminal object. Multiple can be provided
        :return: None
        """
        for terminal in terminals:
            if not self.contains_terminal(terminal):
                self.terminals.append(terminal)

    def merge_node(self, node):
        """
        Connect all terminals from another node to this node

        :param node: Node object
        :return: None
        """
        self.add_terminals(*node.terminals)

    def get_variables(self, orientation=None, key=None):
        """
        Get a list of all variables with the provided orientation and/or
        key associated with the node.

        :param orientation: optional string specifying requested variable
                            orientation
        :param key: optional string specifying requested variable key
        :return: list of Variable objects
        """
        node_variables = []
        for terminal in self.terminals:
            # Get requested variable types from the terminal
            terminal_variables = terminal.get_variables(orientation)
            # Build list of node variables
            if key is not None:
                node_variables += [var for var in terminal_variables \
                                   if var.key==key]
            else:
                node_variables += terminal_variables

        return node_variables
