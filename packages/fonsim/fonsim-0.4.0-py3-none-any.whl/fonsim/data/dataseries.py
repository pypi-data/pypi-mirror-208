"""
Class DataSeries

2020, September 1
"""

import numpy as np
import csv
import warnings


class DataSeries:
    """
    Class to load and hold tabular data from CSV file.
    Numerical data is stored in numpy arrays as floats.
    Labels and units are stored in Python lists

    :param filename: path to file to read or, if bytestring given, filetype
    :param bytestring: bytestring with file data
    """
    def __init__(self, filename, bytestring=None):
        self.labels = []
        self.units = []
        self.array = np.array(0)

        # Load data from file into labels, units and data
        self.load_data(filename, bytestring)

    def load_data(self, filename, bytestring=None):
        """
        Load in data. Provide a filename or byte string.
        If providing a byte string, provide the filetype extension (e.g. .csv)
        to the filename argument such that the formatting of the bytestring can be determined.

        :param filename: path to file to read or, if bytestring given, filetype
        :param bytestring: bytestring with file data
        :return: None
        """
        # Check whether CSV file (.csv)
        if '.csv' in filename:
            # CSV files cannot store numbers directly:
            # they can only store strings of characters,
            # typically representing numbers in decimal format.
            # Thus, we'll first load in the strings in a 2D Python list structure
            # and then convert those strings to floats.

            # Get file contents
            if bytestring is not None:
                csvfile = bytestring.decode('utf-8')
            else:
                f = open(filename, 'r', newline='')
                csvfile = f.read()
                f.close()
            csvfile = csvfile.splitlines()

            # CSV file contents to Python lists
            data = []
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            i_all_floats = -1
            i = 0
            for row in reader:
                # Only add non-empty rows
                if len(row) > 0:
                    data.append(row)
                if i_all_floats == -1:
                    try:
                        [float(x) for x in row]
                        i_all_floats = i
                    except ValueError:
                        pass
                    i += 1

            # Data shape
            width = len(data[i_all_floats])

            # Labels and units
            # No top labels -> this can get difficult!
            if i_all_floats == 0:
                msg = 'No labels and no units detected! Applied automatic labeling.'
                warnings.warn(msg, UserWarning, stacklevel=2)
                self.labels = [str(x) for x in range(width)]
                self.units = [None] * width
            elif i_all_floats == 1:
                msg = 'No labels detected! Applied automatic labeling.'
                warnings.warn(msg, UserWarning, stacklevel=2)
                self.labels = [str(x) for x in range(width)]
                self.units = data[0]
            else:
                self.labels = data[i_all_floats-2]
                self.units = data[i_all_floats-1]

            # Check whether number of labels and units
            # matches number of columns in data
            if len(self.labels) != width:
                msg = 'Found ' + str(len(self.labels)) + ' labels ' +\
                      'but expected ' + str(width) + ' labels.'
                warnings.warn(msg, UserWarning, stacklevel=2)
            if len(self.units) != width:
                msg = 'Found ' + str(len(self.units)) + ' units ' +\
                      'but expected ' + str(width) + ' units.'
                warnings.warn(msg, UserWarning, stacklevel=2)

            # Check whether the shape of data is homogeneous
            for i in range(i_all_floats, len(data)):
                if len(data[i]) != width:
                    msg = 'Data shape is not homogeneous, ' +\
                          'aka not all rows have the same number of columns.'
                    raise ValueError(msg)

            # Convert to Numpy array floats
            self.array = np.array(data[i_all_floats:], dtype=np.float32)

        else:
            msg = "The given filename '" + filename + "' is not recognized as a readable file. " +\
                  "Only .csv files are currently supported."
            raise ValueError(msg)
