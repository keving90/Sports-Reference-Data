#!/usr/bin/env python3

"""
This module contains a Player class used to represent an NFL player. Its attributes are various statistics.
"""

import numpy as np
from datetime import datetime


class Player(object):
    """

    Represent a record in the data set. Uses a dictionary to assign attributes and give them appropriate data
    types. The dictionary's keys will be class attributes. The dictionary's value will be attribute data types.

    """
    def __init__(self, data, header):
        # Loop through the header dictionary keys and values. An enumeration is used to grab data from a specific
        # column in the row. Use the keys and values in header to assign attributes and data types for
        # the attributes.
        for i, (attr, data_type) in enumerate(header.items()):
            # In a player's game log table, if '@' is in the row, then it was an away game.
            # Otherwise, it was a home game.
            if attr == 'location':
                if data[i] == '@':
                    setattr(self, attr, 'away')
                else:
                    setattr(self, attr, 'home')
                continue

            # If data type is datetime, then convert data to type datetime.
            if data_type == datetime:
                date = datetime.strptime(data[i], '%Y-%m-%d').date()
                setattr(self, attr, date)
                continue

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
                # Row's cell has missing data.
                if data_type == str:
                    # Data type is string; leave blank.
                    setattr(self, attr, '')
                else:
                    # Data type is not string; use NaN.
                    setattr(self, attr, np.NaN)
            else:
                # Row has no missing data. Use header dict's value as data type.
                if ',' in data[i]:
                    # Get rid of the comma in the row's cell.
                    no_comma = ''.join(data[i].split(','))
                    setattr(self, attr, data_type(no_comma))
                else:
                    setattr(self, attr, data_type(data[i]))
