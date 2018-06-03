#!/usr/bin/env python3

"""
This Python file contains constant dictionaries used for creating Player objects, creating data frame columns, and
calculating fantasy point totals.
"""

# This dictionary is used for creating columns in the data frame and assigning a data type for each column.
# It's also used for creating attributes for Player object's. The keys are the attribute, and the values are the
# attribute's data type.
HEADER = {
    'name': str,
    'url': str,
    'team': str,
    'age': int,
    'position': str,
    'games_played': int,
    'games_started': int,
    'rush_attempts': int,
    'rush_yards': int,
    'rush_touchdowns': int,
    'longest_run': int,
    'yards_per_rush': float,
    'yards_per_game': float,
    'attempts_per_game': float,
    'targets': int,
    'receptions': int,
    'rec_yards': int,
    'yards_per_rec': float,
    'rec_touchdowns': int,
    'longest_rec': int,
    'rec_per_game': float,
    'rec_yards_per_game': float,
    'catch_percentage': float,
    'scrimmage_yards': int,
    'rush_rec_touchdowns': int,
    'fumbles': int
}

# This dictionary holds the stat name as keys and their fantasy points worth as values.
FANTASY_SETTINGS_DICT = {
    'pass_yard': 1 / 25,  # 25 yards = 1 point
    'pass_td': 4,
    'interception': -1,
    'rush_yard': 1 / 10,  # 10 yards = 1 point
    'rush_td': 6,
    'rec_yard': 1 / 10,  # 10 yards = 1 point
    'reception': 0,
    'receiving_td': 6,
    'two_pt_conversion': 2,
    'fumble_lost': -2,
    'offensive_fumble_return_td': 6,
    'return_yard': 1 / 25  # 25 yards = 1 point
}