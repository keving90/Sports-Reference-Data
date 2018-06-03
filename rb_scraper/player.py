import numpy as np

class Player(object):
    """
    The Player class is used to represent a record in the data set. The player's 'name' and 'year' attributes will be
    used in the data frame as a multi-hierarchical index. The class uses the HEADER dictionary to assign attributes
    and use the appropriate datatype.
    """
    def __init__(self, data, header):
        """
        Initialize the Player object. This method will use the keys and values in HEADER to assign attributes and
        data types for the attributes.
        """
        # Loop through the HEADER dictionary keys and values. An enumeration is also used to grab data from a specific
        # column in the row.
        for i, (attr, data_type) in enumerate(header.items()):
            # Remove unwanted characters in data.
            # '*' in the player's name indicates a Pro Bowl appearance.
            # '+' in the player's name indicates a First-Team All-Pro award.
            # '%' is included in the catch percentage stat on pro-football reference
            if data[i].endswith('*+'):
                data[i] = data[i][:-2]
            elif data[i].endswith('%') or data[i].endswith('*') or data[i].endswith('+'):
                data[i] = data[i][:-1]

            # Set the class attribute. If the data is empty then we will assign a NumPy NaN value to the attribute.
            # Otherwise, we set the attribute as usual.
            if not data[i]:
                setattr(self, type(data[i])(np.NaN), str(data[i]))
            else:
                setattr(self, attr, data_type(data[i]))