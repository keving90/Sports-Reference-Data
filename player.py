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
    def __init__(self, data, attr_dict):
        """
        Initialize Player object.

        Args:
            data (list): List of player stats. Order of stats must match order of keys in attr_dict dict. The elements
                in the data list will be the values of each attribute.

            attr_dict (dict): Dictionary whose keys are the stat names and values are a data type. The keys will be
                used as attribute names for the object. The values will be the data type of the attribute.
        """
        # Simultaneously loop through each stat, attribute name, and data type of each attribute.
        # Modify the stat if needed. Assign each attribute using setattr().
        for stat, (attr, data_type) in zip(data, attr_dict.items()):
            # In a player's game log table, if '@' is in the row, then it was an away game.
            # Otherwise, it was a home game.
            # This situation arises when scraping data from www.pro-football-reference.com.
            if attr == 'location':
                if stat == '@':
                    setattr(self, attr, 'away')
                else:
                    setattr(self, attr, 'home')
                continue

            # If data type is datetime, then convert data to type datetime.
            # Dates are present in a www.pro-football-reference.com game log.
            if data_type == datetime:
                date = datetime.strptime(stat, '%Y-%m-%d').date()
                setattr(self, attr, date)
                continue

            # Remove unwanted characters in data.
            # These qualities are found when scraping from www.pro-football-reference.com.
            # '*' in the player's name indicates a Pro Bowl appearance.
            # '+' in the player's name indicates a First-Team All-Pro award.
            # '%' is included in the catch percentage stat on pro-football reference
            if stat.endswith('*+'):
                stat = stat[:-2]
            elif stat.endswith('%') or stat.endswith('*') or stat.endswith('+'):
                stat = stat[:-1]

            # Set the class attribute. If the data is empty then we will assign a NumPy NaN value to the attribute.
            # Otherwise, we set the attribute as usual.
            if not stat:
                setattr(self, attr, np.NaN)
            else:
                if ',' in stat:
                    no_comma = ''.join(stat.split(','))
                    setattr(self, attr, data_type(no_comma))
                else:
                    setattr(self, attr, data_type(stat))
