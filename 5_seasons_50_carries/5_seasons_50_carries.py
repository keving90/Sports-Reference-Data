#!/usr/bin/env python3

"""
This module scrapes data from https://www.pro-football-reference.com/'s Rushing and Receiving data table and places
it into a data frame (sample table: https://www.pro-football-reference.com/years/2017/rushing.htm). The module uses
the `Requests` and `Beautiful Soup 4` modules to gather the web page data. A `Player` class is used to create objects
representing a single player. The program loops through the 5 most recent NFL seasons and gathers data for each season.
A column for the player's fantasy points for the season is added to each data frame. The points total is based on a
standard Yahoo! league (0 PPR). The scoring can be changed in the `FANTASY_SETTINGS_DICT` dictionary. A data frame for
each season is placed in a list, and this list is concatenated into one big data frame. Then, various manipulations are
made to the data frame to find all running backs who have had 50 or more rushing attempts in each of the last 5 years.
The final data frame is saved as a `.csv` file.

Note: This data set does not include 2 point conversions. This will affect the fantasy point total for some players.
Luckily, few running backs get many 2 point conversions. Only 9 RB's in 2017 had 1 conversion, while the rest had 0.
This will only have a small affect on the point total for some of the running backs.
"""

import pandas as pd
import datetime

# Putting '..' on sys.path because Player import was causing an error when scraper.py is imported from
# another module (such as 5_seasons_50_carries.py).
import sys
import os

# os.path.split() splits the head and tail of the path for the file.
# This line of code grabs the head, joins it with '..', and inserts the path into the first element of sys.path.
sys.path.insert(0, os.path.join(os.path.split(__file__)[0], '..'))

import nfl_scraper
from constants import SEASON_RUSH_REC_HEADER, FANTASY_SETTINGS_DICT


def modify_data_frame(data_frame_list, num_years, player_url=False):
    """
    This function takes a list of data frames as input. It concatenates the data frames together
    to create one large data frame. It then modifies the data to get the running backs with 50 or
    more carries in each of the past num_years season. The modified data frame is returned.
    """
    # Concatenate the data frames to create one large data frame that has data for each season.
    big_df = pd.concat(data_frame_list)

    # Keep the player_url column in the data frame when player_url=True
    if not player_url:
        big_df.drop('url', axis=1, inplace=True)

    # The concatenation creates duplicate indexes, so we will reset the index
    big_df.reset_index(inplace=True, drop=True)

    # Eliminate players with fewer than 50 rush attempts.
    big_df = big_df[big_df['rush_attempts'] >= 50]

    # Some players have a NaN value their position. Any player with 50 or more rush attempts,
    # but no position is likely a running back.
    big_df['position'] = big_df['position'].fillna('RB')

    # Some running backs have their position description in lowercase letters.
    # Use a lambda function to fix this inconsistency.
    big_df['position'] = big_df['position'].apply(lambda x: 'RB' if 'rb' in x else x)

    # Only interested in running backs
    big_df = big_df[big_df['position'] == 'RB']

    # Set the player's name and the season's year as the indexes.
    big_df = big_df.set_index(['name', 'year'])

    # Sort the data frame by the player's name
    big_df.sort_index(level='name', inplace=True)

    # Get each player's name
    names = big_df.index.get_level_values('name').unique()

    # Loop through each player. If they don't have num_years season's worth of data, then we
    # drop them from the data set.
    for name in names:
        if len(big_df.loc[name]) != num_years:
            big_df.drop(name, inplace=True)

    return big_df


def main():
    """
    The main function.
    """
    # Get the current date to help figure out which year to start gathering data from.
    now = datetime.datetime.now()

    # Number of years of data.
    num_years = 5

    # Starting with last year since it's a full season of data.
    # Regular season football ends in late December or early January, so if the current
    # date is late December, and the season has already ended, then unfortunately the
    # newly created season will not be included in the data set.
    # Football season starts the week after Labor Day weekend. Labor Day is always on
    # the first Monday of September, and the NFL regular season is 17 weeks long
    # (16 games + bye week for a team). From my initial calculations, if September 1 is
    # Labor Day, then the NFL regular season ends on December 28.
    start_year = now.year - 1

    # Get the final year to gather data from.
    end_year = start_year - num_years

    # First, we need to scrape the data from Pro-Football Reference.

    # Holds each data frame scraped from Pro-Football Reference.
    # Each data frame has data for a single season.
    data_frame_list = []

    # Iterate through each year of data and create a data frame for each one.
    for year in range(start_year, end_year, -1):
        # Create url for given season.
        url = 'https://www.pro-football-reference.com/years/' + str(year) + '/rushing.htm'

        # Identify the table ID to get scrape from the correct table.
        table_id = 'rushing_and_receiving'

        # Scrape the data to get each player's web page elements.
        player_list = nfl_scraper.scrape_table(url, table_id)

        # Use the elements to create Player objects.
        list_of_player_dicts = nfl_scraper.create_player_objects(player_list, SEASON_RUSH_REC_HEADER)

        # Create a data frame for the season
        df = nfl_scraper.make_data_frame(list_of_player_dicts, year, SEASON_RUSH_REC_HEADER, FANTASY_SETTINGS_DICT)

        data_frame_list.append(df)

    # Concatenate the data frames and clean the data.
    big_df = modify_data_frame(data_frame_list, num_years, False)

    # Write the data frame to a csv file and save it in the current working directory.
    big_df.to_csv('5_seasons_50_carries.csv')


if __name__ == '__main__':
    main()
