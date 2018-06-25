#!/usr/bin/env python3

"""
This module contains a Player class used to represent an NFL player. Its attributes are various statistics.

Note: This module was built using Python 3.6.1, so dictionaries are ordered.
"""

import numpy as np
from datetime import datetime


class Player(object):
    """

    Represents a record in the data set.

    Attributes:
        Uses a dictionary to assign attributes and give them appropriate data types. The dictionary's keys will be
        class attributes. The dictionary's value will be attribute data types.

    """
    def __init__(self, data, header):
        """
        Initialize Player object.

        Args:
            data (list): List of player stats. Order of stats must match order of keys in header dict.

            header (dict): Dictionary whose keys are the stats name and values are a data type. The keys will be used
                as attribute names, and the values will be the data type of the attribute. The elements in the data
                list will be the values of each attribute.
        """
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
            # These qualities are found when scraping from www.pro-football-reference.com.
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
                setattr(self, attr, np.NaN)
            else:
                if ',' in data[i]:
                    no_comma = ''.join(data[i].split(','))
                    setattr(self, attr, data_type(no_comma))
                else:
                    setattr(self, attr, data_type(data[i]))
