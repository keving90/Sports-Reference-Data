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

import requests
import bs4
import numpy as np
import pandas as pd
import datetime

from player import Player
from constants import HEADER, FANTASY_SETTINGS_DICT


def scrape_data(current_year):
    """
    This function goes to pro-football-reference.com 'Rushing and Receiving' page for the
    given season and scrapes the data from the web page. A Player object is used to represent
    the data for each player. The function uses a list called data frame_list to create a
    data frame for each year of data and append that data frame to the end of the list. The list
    is then returned.
    """
    # Send a GET request to Pro Football Reference's Rushing & Receiving page to gather the data.
    r = requests.get('https://www.pro-football-reference.com/years/' + str(current_year) + '/rushing.htm')
    r.raise_for_status()

    # Create a BeautifulSoup object.
    soup = bs4.BeautifulSoup(r.text, 'lxml')

    # Find the first table with tag 'table' and id 'rushing_and_receiving
    table = soup.find('table', id='rushing_and_receiving')

    # tbody is the table's body
    # Get the body of the table
    body = table.find('tbody')

    # tr refers to a table row
    # Each row in player_list has data for a single player
    # This will also collect descriptions of each column found in the web page's table, which
    # is filtered out in create_player_objects().
    player_list = body.find_all('tr')
    return player_list

    # player_list = body.find_all('tr')


def create_player_objects(player_list, header):
    """
    This function uses the player_list created by scrape_data() to create an object for each player.
    It uses the header dictionary to set each attribute when creating the object. A list is returned.
    Each element in the list is a dictionary representation of each player object.
    """
    # This list holds a dictionary of each object's attributes.
    # Each dictionary is made from the object's __dict__ attribute.
    list_of_player_dicts = []

    # Get each player's stats, create a Player object, and append the object
    # and the instance's __dict__ to their own list
    for player in player_list:
        # The <td> tag defines a standard cell in an HTML table.
        # Get a list of cells. This data represents one player.
        info_list = player.find_all('td')

        # If info_list has data, then we will extract the desired information from the elements.
        # info_list will be empty if the current 'player' in the player_list is actually other
        # irrelevant information we're not interested in (such as a column description).
        if info_list:
            # Collect the relevant info from the cells and place them in player_info
            player_info = []
            for stat in info_list:
                # print(type(stat))
                # print(stat['data-stat'])
                player_info.append(stat.text)
                if stat['data-stat'] == 'player':
                    get_player_url(stat, player_info)

            # Create a Player object and append the __dict__ attribute to a list.
            # This list is used for the data in our data frame.
            obj = Player(player_info, header)
            list_of_player_dicts.append(obj.__dict__)

    return list_of_player_dicts


def get_player_url(stat, player_info):
    """
    Gets the URL to the player's personal career stat page and appends it to player_info list.
    """
    # Every tag has an attribute.
    # If the tag's data-stat attribute is 'player', then we get the player's URL.
    href = stat.find_all('a', href=True)
    url = href[0]['href']
    player_info.append(url)


def make_data_frame(player_dict_list, year, header, fantasy_settings):
    """
    Creates a new data frame and returns it. A 'year' and a 'fantasy_points' column is added to the data frame.
    The 'year' column indicates the year of the season, and the 'fantasy_points' column calculates how many fantasy
    points the player would have earned that season (excluding 2 point conversions).
    """
    df = pd.DataFrame(data=player_dict_list)  # Create the data frame.
    header_list = list(header.keys())         # Get header dict's keys for df's column names.
    df = df[header_list]                      # Add column headers.
    df['year'] = year                         # Add a 'year' column.

    # Create fantasy_points column.
    df['fantasy_points'] = df['rush_yards'] * fantasy_settings['rush_yard'] + \
                           df['rush_touchdowns'] * fantasy_settings['rush_td'] + \
                           df['rush_touchdowns'] * fantasy_settings['rush_td'] + \
                           df['receptions'] * fantasy_settings['reception']

    return df


def modify_data(data_frame_list, num_years, player_url=False):
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
    """The main function."""
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
        # Scrape the data to get each player's web page elements.
        player_list = scrape_data(year)

        # Use the elements to create Player objects.
        list_of_player_dicts = create_player_objects(player_list, HEADER)

        # Create a data frame for the season
        df = make_data_frame(list_of_player_dicts, year, HEADER, FANTASY_SETTINGS_DICT)

        data_frame_list.append(df)

    # Concatenate the data frames and clean the data.
    big_df = modify_data(data_frame_list, num_years, False)

    # Write the data frame to a csv file and save it in the current working directory.
    big_df.to_csv('rb_data.csv')


if __name__ == '__main__':
    main()