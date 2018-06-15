#!/usr/bin/env python3

"""
This Python file contains constant dictionaries used for creating Player objects, creating data frame columns, and
calculating fantasy point totals.

TOTAL_RUSH_REC_HEADER:

This dictionary is used to represent a player's stats for an entire season. It's used to create Player objects
representing a player's data for a given season The keys are the attribute, and the values are the attribute's data
type. The chosen keys and their order are based on pro-football-reference's Rushing and Receiving table.


FANTASY_SETTINGS_DICT:

This dictionary holds the stat name as keys and their fantasy points worth as values.
"""

from datetime import datetime

SEASON_RUSH_REC_HEADER = {
    'name': str,
    'url': str,
    'team': str,
    'age': int,
    'position': str,
    'games_played': int,
    'games_started': int,
    'rush_attempts': int,
    'rush_yards': int,
    'rush_td': int,
    'longest_run': int,
    'yards_per_rush': float,
    'yards_per_game': float,
    'attempts_per_game': float,
    'targets': int,
    'receptions': int,
    'rec_yards': int,
    'yards_per_rec': float,
    'rec_td': int,
    'longest_rec': int,
    'rec_per_game': float,
    'rec_yards_per_game': float,
    'catch_percentage': float,
    'scrimmage_yards': int,
    'rush_rec_td': int,
    'fumbles': int  # all fumbles
}

FANTASY_SETTINGS_DICT = {
    'pass_yards': 1 / 25,  # 25 yards = 1 point
    'pass_td': 4,
    'interceptions': -1,
    'rush_yards': 1 / 10,  # 10 yards = 1 point
    'rush_td': 6,
    'rec_yards': 1 / 10,  # 10 yards = 1 point
    'receptions': 0,
    'rec_td': 6,
    'two_pt_conversions': 2,
    'fumbles_lost': -2,
    'offensive_fumble_return_td': 6,
    'return_yards': 1 / 25,  # 25 yards = 1 point
    'return_td': 6
}

LOG_RUSH_REC_HEADER = {
    'date': datetime,
    'game_number': int,
    'age': float,
    'team': str,
    'location': str,
    'opponent': str,
    'result': str,
    'rush_attempts': int,
    'rush_yards': int,
    'yards_per_rush': float,
    'rush_td': int,
    'targets': int,
    'receptions': int,
    'rec_yards': int,
    'yards_per_rec': float,
    'rec_td': int,
    'catch_percentage': float,
    'yards_per_target': float,
    'total_td': int,
    'total_points': int
}

LOG_RUSH_REC_PASS_HEADER = {
    'date': datetime,
    'game_number': int,
    'age': float,
    'team': str,
    'location': str,
    'opponent': str,
    'result': str,
    'rush_attempts': int,
    'rush_yards': int,
    'yards_per_rush': float,
    'rush_td': int,
    'targets': int,
    'receptions': int,
    'rec_yards': int,
    'yards_per_rec': float,
    'rec_td': int,
    'catch_percentage': float,
    'yards_per_target': float,
    'pass_completions': int,
    'pass_attempts': int,
    'completion_percentage': float,
    'pass_yards': int,
    'pass_td': int,
    'interceptions': int,
    'qb_rating': float,
    'times_sacked': int,
    'yards_lost_to_sacks': int,
    'yards_per_pass_attempt': float,
    'adjusted_yards_per_pass_attempt': float,
    'pass_2_point_conversions': int,
    'total_td': int,
    'total_points': int
}
