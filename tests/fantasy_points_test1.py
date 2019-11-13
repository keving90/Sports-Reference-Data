#!/usr/bin/env python3

import requests
import bs4
import pandas as pd
import datetime

# Putting '..' on sys.path because Player import was causing an error when scraper.py is imported from
# another module (such as 5_seasons_50_carries.py).
import sys
import os

# os.path.split() splits the head and tail of the path for the file.
# This line of code grabs the head, joins it with '..', and inserts the path into the first element of sys.path.
sys.path.insert(0, os.path.join(os.path.split(__file__)[0], '..'))

import pro_football_ref_scraper as pfbr
from player import Player


pfbr_fantasy_table = {
    'name': str,
    'fantasy_points': int
}


def get_fantasy_table(year):
    str_year = str(year)
    url = 'https://www.pro-football-reference.com/years/' + str_year + '/fantasy.htm'
    table_id = 'fantasy'
    player_list = scrape_table(url, table_id)
    list_of_player_dicts = create_player_objects(player_list, pfbr_fantasy_table)
    fantasy_df = make_data_frame(list_of_player_dicts, year)

    return fantasy_df


def scrape_table(url, table_id):
    """
    Scrape a table from pro-football-reference.com based on provided table ID.

    :param url: Websites URL.
    :param table_id: Identifier for the table. Found when used "inspect element" on web page.

    :return: List of BeautifulSoup4 element ResultSets. Each item in list is a row in the table.
    """
    # Send a GET request to Pro Football Reference's Rushing & Receiving page to gather the data.
    r = requests.get(url)
    r.raise_for_status()

    # Create a BeautifulSoup object.
    soup = bs4.BeautifulSoup(r.text, 'lxml')

    # Find the first table with tag 'table' and id 'rushing_and_receiving.
    table = soup.find('table', id=table_id)

    # tbody is the table's body
    # Get the body of the table
    body = table.find('tbody')

    # tr refers to a table row
    # Each element in player_list has data for a single player.
    # This will also collect descriptions of each column found in the web page's table, which
    # is filtered out in create_player_objects().
    player_list = body.find_all('tr')

    return player_list

# name = 0
# fp = 20

def create_player_objects(player_list, header):
    """
    Create an object for each player using the player_list created by scrape_data().

    :param player_list: List of BeautifulSoup4 element ResultSets. Each item in list is a row in the table.
    :param header: Dictionary where keys are the name of the stat and values are the data type.

    :return: List of dictionary representations of Player objects (object.__dict__).
    """
    # This list holds a dictionary of each object's attributes.
    # Each dictionary is made from the object's __dict__ attribute.
    list_of_player_dicts = []

    # Get each player's stats, create a Player object, and append the object
    # and the instance's __dict__ to their own list.
    for player in player_list:
        # The <td> tag defines a standard cell in an HTML table.
        # Get a list of cells. This raw web page data represents one player.
        raw_stat_list = player.find_all('td')

        # If info_list has data, then we will extract the desired information from the elements.
        # info_list will be empty if the current 'player' in the player_list is actually other
        # irrelevant information we're not interested in (such as a column description).
        if raw_stat_list:
            player_stats = get_player_stats(raw_stat_list)
            # Create a Player object and append the __dict__ attribute to a list.
            # This list is used for the data in our data frame.
            obj = Player(player_stats, header)
            list_of_player_dicts.append(obj.__dict__)

    return list_of_player_dicts


def get_player_stats(raw_stat_list):
    """
    Get text data from from a BeautifulSoup4 element tag. Also gets a URL to the player's personal career stat
    page. Used in create_player_objects().

    :param raw_stat_list: List of BeautifulSoup4 element ResultSets. Inside of each ResultSet is a stat.

    :return: List of the player's stats in text form.
    """
    name = raw_stat_list[0].text
    fantasy_points = raw_stat_list[20].text

    return [name, fantasy_points]


def make_data_frame(player_dict_list, year):
    """
    Create a new data frame and return it.

    :param player_dict_list: List of unique Player.__dict__'s.
    :param year: NFL season's year.
    :param fantasy: When true, add a column for player's total fantasy points for the season.

    :return: Data frame of stats.
    """
    df_columns = list(pfbr_fantasy_table.keys())  # Get header dict's keys for df's column names.
    df = pd.DataFrame(data=player_dict_list, columns=df_columns)  # Create the data frame.
    df['year'] = year  # Add a 'year' column.
    df.set_index('name', inplace=True)  # Make 'name' the data frame's index

    for stat in df_columns[5:]:
        df[stat].fillna(0, inplace=True)  # Fill missing stats with 0.

    return df

if __name__ == '__main__':
    fb_ref = pfbr.ProFbRefScraper()
    rush_rec_df = fb_ref.get_rushing_receiving_data(2017, fantasy=True)
    fantasy_df = get_fantasy_table(2017)
    print(fantasy_df)
    rush_rec_df.to_csv('rush_rec.csv')
    fantasy_df.to_csv('fantasy.csv')
