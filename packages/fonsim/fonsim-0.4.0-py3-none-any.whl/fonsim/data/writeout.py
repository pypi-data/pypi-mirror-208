"""
Function writeout_simulation

2020, September 9
"""

import time
import socket
import json


def writeout_simulation(filename, simulation):
    """
    Write out simulation data in components to a file.
    Supported formats: JSON.
    Format follows from filename extension.

    :param filename: string with filepath
    :param simulation: Simulation-like object
    :return: None

    ===

    JSON specification::

        {
          "scheme": <string>,
          "general": {
            "date": <timestamp>,
            "hostname": <computer name",
            "version": <version>
          },
          "simulation": {
            "system": {
              "label": <string>,
              "nb components": <integer>
            },
            "solver": {
              "name": <string>,
            },
            "time": <key in "data"
          },
          "components": {
            <component_label>: {
              "terminals": {
                <terminal_label>: {
                  "over": {
                    <over_label>: <key in "data">
                  },
                  through": {
                    <through_label>: <key in "data">
                  }
                },
                ...
              }
              "states": {
                <state_label>: <key in "data">,
                ...
              },
              "time": <key in "data">
            },
            ...
          },
          "data": {
            <key>: <list with numbers>,
            ...
          },
        }
    """

    # Check filename
    if '.' not in filename:
        print("Error: filename does not seem to contain '.'.")
        return None

    # Restructure data to a dictionary - list structure
    # same structure as the one used in the JSON file
    data = dict()

    # bank to hold key - data relations
    bank = Bank()

    # Data formatting scheme
    data['scheme'] = '0.1-alpha'

    # general
    general = dict()
    data['general'] = general
    general['date'] = time.strftime("%Y/%m/%d %H:%M:%S %z", time.gmtime())
    general['hostname'] = socket.gethostname()
    general['version'] = 'none'

    # simulation
    sim = dict()
    data['simulation'] = sim

    # simulation -> system
    system = dict()
    sim['system'] = system
    system['label'] = simulation.system.label
    system['nb_components'] = len(simulation.system.components)
    system['nb_nodes'] = len(simulation.system.nodes)

    # simulation -> solver
    solver = dict()
    sim['solver'] = solver
    # solver['name'] = simulation.solver.name

    # simulation: time
    sim['time'] = bank.add(simulation.times)

    # components
    components = dict()
    data['components'] = components
    for c in simulation.system.components:
        comp = dict()
        components[c.label] = comp

        comp['terminals'] = dict()
        for t in c.terminals:
            terminal = dict()
            comp['terminals'][t.label] = terminal

            # Note: currently support only terminals with one pair of variables!
            terminal['over'] = dict()
            var = list(t.variables_across.values())[0]
            terminal['over'][list(t.variables_across.keys())[0]] = bank.add(c.argument_history[c.arguments.index(var)])

            terminal['through'] = dict()
            var = list(t.variables_through.values())[0]
            terminal['through'][list(t.variables_through.keys())[0]] = bank.add(c.argument_history[c.arguments.index(var)])

        comp['states'] = dict()
        for i in range(len(c.states)):
            comp['states'][c.states[i].key] = bank.add(c.state_history[:, i])

    # numerical data
    data_numerical = dict()
    data['data'] = data_numerical
    for i in bank.indices():
        data_numerical[i] = list(bank.objects[i])

    #print("data:", data)

    # Open file and save dictionary
    with open(filename, 'w') as file:
        extension = filename.split('.')[-1]
        if extension == 'json':
            print("Writing out JSON file...")
            json.dump(data, file, indent=2)
        else:
            print("Error: extension <" + extension + "> not recognized.")
    print("Writing to file <" + filename + "> finished.")


class Bank:
    def __init__(self):
        """
        Class Bank
        Dictionary-like object to keep a set of objects
        and associate each object to an index.
        This index of an object is available
        once that object has been added to the bank.
        """
        self.obj_id_to_index = dict()
        self.objects = []

    def add(self, obj):
        """
        Add an object. Object does not have to be hashable.
        :param obj: object
        :return: index of object, integer
        """
        # Note: rely on id as not all objects are hashable,
        # for example Python lists and Numpy ndarrays.
        if id(obj) in self.obj_id_to_index.keys():
            # Object already known
            index = self.obj_id_to_index[id(obj)]
        else:
            # Object not seen before
            self.objects.append(obj)
            index = len(self.objects) - 1
            self.obj_id_to_index[id(obj)] = index
        return index

    def indices(self):
        """
        Return all indices pointing to objects.
        :return: all indices, Python range
        """
        return range(len(self.objects))
