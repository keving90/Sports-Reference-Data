#!/usr/bin/env python3

"""
This module uses football_db_scraper.py to scrape data from www.footballdb.com and place it into a data frame. It
scrapes data from the past 'num_years' seasons. Each season is placed into a data frame, and each data frame is placed
into a list. Each data frame in the list is concatenated into one large data frame. Then, various manipulations are
made to the data frame to find all running backs who have had 50 or more rushing attempts in each of the last
'num_years' seasons.

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

from football_db_scraper import FbDbScraper


def get_seasons(num_years):
    """
    Use football_db_scraper.FbDbScraper to scrape 'num_years' seasons worth of data.

    :param num_years: Number of years of data to scrape

    :return: Data frame containing 'num_years' seasons worth of NFL data.
    """
    # Get the current date to help figure out which year to start gathering data from.
    now = datetime.datetime.now()

    # The NFL regular season will end on December 28th at the earliest.
    # If the season has ended and the current date is between 12/28 and 1/1, then unfortunately the newly ended season
    # will not be included.
    start_year = now.year - 1

    # Get the final year to gather data from.
    end_year = start_year - int(num_years)

    # Create object to scrape data.
    fb_db = FbDbScraper()

    # Get a list of data frames, where each data frame if a year of NFL data.
    df_list = [fb_db.get_fantasy_df(year) for year in range(start_year, end_year, -1)]

    # Concatenate the data frames to create one large data frame that has data for each season.
    big_df = pd.concat(df_list)

    return big_df


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
    five_seasons_df = get_seasons(5)

    # Modify data frame so only running backs with 50 or more carries in each of the last 5 seasons remain.
    modified_df = modify_df(five_seasons_df, 5)

    # Write the data frame to a csv file and save it in the current working directory.
    modified_df.to_csv('5_seasons_50_carries.csv')
