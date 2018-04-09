"""
This notebook scrapes data from https://www.pro-football-reference.com/'s Rushing and Receiving data table and 
places it into a data frame (sample table: https://www.pro-football-reference.com/years/2017/rushing.htm). The notebook uses the `Requests` 
and `Beautiful Soup 4` modules to gather the web page data. A `Player` class is used to create objects representing a single player. The 
program loops through the 5 most recent NFL seasons and gathers data for each season. A column for the player's fantasy points for the season 
is added to each data frame. The points total is based on a standard Yahoo! league (0 PPR). The scoring can be changed in the 
`FANTASY_SETTINGS_DICT` dictionary. A data frame for each season is placed in a list, and this list is concatenated into one big data frame. 
Then, various manipulations are made to the data frame to find all runningbacks who have had 50 or more rushing attempts in each of the last 5 
years. The final data frame is saved as a `.csv` file.

Note: This dataset does not include 2 point conversions. This will affect the fantasy point total for some players. Luckily, few runningbacks 
get many 2 point conversions (9 RB's in 2017 each had only 1 conversion; the rest had 0)  This will only have a small affect on the point 
total for some of the runningbacks.
"""

import requests
import bs4
import pandas as pd
import numpy as np
import datetime


class Player(object):
    """
    The Player class is used to represent a record in the dataset. The player's 'name' and 'year' attributes will be
    used in the data frame as a multi-hierarchical index. The class uses the HEADER dictionary to assign attributes
    and use the appropriate datatype.
    """
    def __init__(self, data, header):
        """
        Initialize the Player object. This method will use the keys and values in HEADER to assign attributes and
        data types for the attributes.
        """
        # Loop through the HEADER dictionary keys and values. An enumeration is also used to grab data from a specific
        # column in the row.
        for i, (attr, data_type) in enumerate(header.items()):
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
                setattr(self, type(data[i])(np.NaN), str(data[i]))
            else:
                setattr(self, attr, data_type(data[i]))


def scrape_data(dataframe_list, stat_year, end_year, current_year, header):
    """
    This function goes to pro-football-reference.com 'Rushing and Receiving' page for the
    given season and scrapes the data from the webpage. A Player object is used to represent
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
    # Each row in player_list has data for a player
    # This will also collect descriptions of each column found in the web page's table.
    # We will filter this out in the for loop below.
    player_list = body.find_all('tr')

    # This list holds a dictionary of each object's attributes.
    # The dictionary is made from the object's __dict__ attribute.
    player_dict_list = []

    # Get each player's stats, create a Player object, and append the object
    # and the instance's __dict__ to their own list
    for player in player_list:
        # The <td> tag defines a standard cell in an HTML table.
        # Get a list of cells. This data represents one player
        info_list = player.find_all('td')

        # If info_list has data, then we will extract the desired information from the elements.
        # info_list will be empty if the current 'player' in the player_list is actually other
        # irrelevant information we're not interested in (such as a column description).
        if info_list:
            # Collect the relevant info from the cells and place them in player_info
            player_info = []
            for stat in info_list:
                player_info.append(stat.text)

            # Create a Player object and append the __dict__ attribute to a list.
            # This list is used for the data in our data frame.
            obj = Player(player_info, header)
            player_dict_list.append(obj.__dict__)

    return player_dict_list


def make_dataframe(dataframe_list, player_dict_list, year, header):
    """
    Creates a new data frame and inserts the the data frame into data frame_list. A 'year' and a
    'fantasy_points' column is added to the data frame. The 'year' column indicates the year of
    the season, and the 'fantasy_points' column calculates how many fantasy points the player
    would have learned that season (excluding 2 point conversions).
    """

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

    # Create the data frame, add column headers, and add a 'year' column for the current season.
    df = pd.DataFrame(data=player_dict_list)
    header_list = list(header.keys())
    df = df[header_list]
    df['year'] = year
    df['fantasy_points'] = df['rush_yards'] * FANTASY_SETTINGS_DICT['rush_yard'] + \
                           df['rush_touchdowns'] * FANTASY_SETTINGS_DICT['rush_td'] + \
                           df['rush_touchdowns'] * FANTASY_SETTINGS_DICT['rush_td'] + \
                           df['receptions'] * FANTASY_SETTINGS_DICT['reception']

    # Add the data frame to the data frame list.
    dataframe_list.append(df)


def modify_data(dataframe_list, NUM_YEARS):
    """
    This function takes a list of data frames as input. It concatenates the data frames together
    to create one large data frame. It then modifies the data to get the runningbacks with 50 or
    more carries in each of the past NUM_YEARS season. The modified data frame is returned.
    """
    # Concatenate the data frames to create one large data frame that has data for each season.
    big_df = pd.concat(dataframe_list)

    # The concatenation creates duplicate indexes, so we will reset the index
    big_df.reset_index(inplace=True, drop=True)

    # Eliminate players with fewer than 50 rush attempts.
    big_df = big_df[big_df['rush_attempts'] >= 50]

    # Some players have a NaN value their position. Any player with 50 or more rush attempts
    # but no position is likely a running back.
    big_df['position'] = big_df['position'].fillna('RB')

    # Some runningbacks have their position description in lowercase letters.
    # Use a lambda function to fix this inconsistency.
    big_df['position'] = big_df['position'].apply(lambda x: 'RB' if 'rb' in x else x)

    # Only interested in runningbacks
    big_df = big_df[big_df['position'] == 'RB']

    # Set the player's name and the season's year as the indexes.
    big_df = big_df.set_index(['name', 'year'])

    # Sort the data frame by the player's name
    big_df.sort_index(level='name', inplace=True)

    # Get each player's name
    names = big_df.index.get_level_values('name').unique()

    # Loop through each player. If they don't have NUM_YEARS season's worth of data, then we
    # drop them from the dataset.
    for name in names:
        if len(big_df.loc[name]) != NUM_YEARS:
            big_df.drop(name, inplace=True)

    return big_df


def main():
    """The main function."""
    # Get the current date to help figure out which year to start gathering data from.
    now = datetime.datetime.now()

    # Number of years of data.
    NUM_YEARS = 5

    # Starting with last year since it's a full season of data.
    # Regular season football ends in late December or early January, so if the current
    # date is late December, and the season has already ended, then unfortunately the
    # newly created season will not be included in the dataset.
    # Football season starts the week after Labor Day weekend. Labor Day is always on
    # the first Monday of September, and the NFL regular season is 17 weeks long
    # (16 games + bye week for a team). From my initial calculations, if September 1 is
    # Labor Day, then the NFL regular season ends on December 28.
    start_year = now.year - 1

    # Get the final year to gather data from.
    end_year = start_year - NUM_YEARS

    # This dictionary is used for creating columns in the data frame and assigning a datatype for each column.
    HEADER = {
        'name': str,
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
        'pass_yard': 1/25, # 25 yards = 1 point
        'pass_td': 4,
        'interception': -1,
        'rush_yard': 1/10, # 10 yards = 1 point
        'rush_td': 6,
        'rec_yard': 1/10, # 10 yards = 1 point
        'reception': 0,
        'receiving_td': 6,
        'two_pt_conversion': 2,
        'fumble_lost': -2,
        'offensive_fumble_return_td': 6,
        'return_yard': 1/25 # 25 yards = 1 point
    }

    # First, we need to scrape the data from Pro-Football Reference.

    # Holds each data frame scraped from Pro-Football Reference.
    # Each data frame has data for a single season.
    dataframe_list = []

    # Iterate through each year of data and create a data frame for each one.
    for year in range(start_year, end_year, -1):
        player_dict_list = scrape_data(dataframe_list, start_year, end_year, year, HEADER)
        make_dataframe(dataframe_list, player_dict_list, year, HEADER)

    # The data has been scraped. We will now concatenate the data frames and clean the data.
    big_df = modify_data(dataframe_list, NUM_YEARS)

    # Write the data frame to a csv file and save it in the current working directory.
    big_df.to_csv('rb_data.csv')


if __name__ == '__main__':
    main()