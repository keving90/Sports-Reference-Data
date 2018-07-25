#!/usr/bin/env python3

"""
This module uses football_db_scraper.py to scrape data from www.footballdb.com and place it into a data frame. The
football_db_scraper.get_fantasy_data() scrapes several seasons worth of data. Then rb_carries.modify_df() performs
various manipulations to find all running backs who have had 50 or more rushing attempts in each of the last
'num_years' seasons. The usage example scrapes 5 seasons of data to find the running backs with 50 or more rushing
attempts in each of the last 5 seasons.

Built using Python 3.6.1
"""

import pandas as pd
import datetime
import sys
import os

# Putting '..' on sys.path so other modules can be imported.
# os.path.split() splits the head and tail of the path for the file.
# This line of code grabs the head, joins it with '..', and inserts the path into the first element of sys.path.
sys.path.insert(0, os.path.join(os.path.split(__file__)[0], '..'))

from football_db.football_db_scraper import FbDbScraper


def modify_df(df, num_years):
    """
    Modify a data frame to get the running backs with 50 or more carries in each of the past num_years seasons.

    :param df: Data frame to be modified.
    :param num_years: Number of seasons of data.

    :return: Data frame of running backs with 50 or more carries in each of the last num_years seasons.
    """
    # Eliminate players with fewer than 50 rush attempts.
    df = df[df['rush_attempts'] >= 50]

    # Only interested in running backs
    df = df[df['position'] == 'RB']

    # Current index is player's unique URL.
    # Make first index the player's name, and the second index the season's year.
    df.set_index('name', inplace=True)
    df.set_index('year', append=True, inplace=True)

    # Sort the data frame by the player's name.
    df.sort_index(level='name', inplace=True)

    # Get each player's name.
    names_list = df.index.get_level_values('name').unique()

    # Drop players in data set who do not have 'num_years' seasons worth of data.
    [df.drop(name, level=0, inplace=True) for name in names_list if len(df.loc[name]) != num_years]

    return df


if __name__ == '__main__':
    # Usage example.

    # Get the 5 most recent years of data.
    fb_db = FbDbScraper()
    five_seasons_df = fb_db.get_fantasy_df(start_year=2017, end_year=2013)

    # Modify data frame so only running backs with 50 or more carries in each of the last 5 seasons remain.
    modified_df = modify_df(five_seasons_df, 5)

    # Write the data frame to a csv file and save it in the current working directory.
    modified_df.to_csv('5_seasons_50_carries.csv')
