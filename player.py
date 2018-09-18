#!/usr/bin/env python3

"""
This module contains a Player class used to represent an NFL player and their stats. It stores data scraped from
www.pro-football-reference.com or www.footballdb.com.

Note: This module was built using Python 3.6.1, so dictionaries are ordered.
"""

import numpy as np
from datetime import datetime


class Player(object):
    """

    Represents a player and their stats. The data is scraped from www.pro-football-reference.com or www.footballdb.com.

    Attributes:
        Uses a dictionary to assign attributes and give them appropriate data types. The dictionary's keys will be
        class attributes. The dictionary's values will be attribute data types. A list of data is used to give the
        attributes values. Attributes are set using setattr().

        Example:

            attributes_dict = {
                'name': str,
                'team': str,
                'pass_yards': int
            }

            The object will have three attributes with varying data types:

            self.name = str(data[0])
            self.team = str(data[1])
            self.pass_yards = int(data[2])

    """
    def __init__(self, data, attr_dict):
        """
        Initializes a Player object. Loops through attr_dict, and uses setattr() to set attributes.

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
            # '%' is included in the catch percentage stat on pro-football reference.
            if stat.endswith('*+'):
                stat = stat[:-2]
            elif stat.endswith('%') or stat.endswith('*') or stat.endswith('+'):
                stat = stat[:-1]

            # Set the class attribute.
            if not stat:
                # No data exists for this stat in the table. Give the attribute:
                # Empty string if data_type is string, or
                # numpy.NaN if data_type is float or integer.
                if data_type == str:
                    setattr(self, attr, '')
                elif data_type == float or data_type == int:
                    setattr(self, attr, np.NaN)
                else:
                    raise ValueError('Player object can only handle string, float, and integer data types.')
            else:
                # Set the attribute as usual.
                # Get rid of a comma found in numerical stats if needed.
                # This situation arises when scraping from www.footballdb.com.
                if ',' in stat:
                    no_comma = ''.join(stat.split(','))
                    setattr(self, attr, data_type(no_comma))
                else:
                    setattr(self, attr, data_type(stat))
