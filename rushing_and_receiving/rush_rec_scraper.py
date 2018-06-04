#!/usr/bin/env python3

"""
This module contains functions for scraping data from the pro-football-reference.com 'Rushing and Receiving' page
for a given season and creating Player objects from the data.
"""

import requests
import bs4
import pandas as pd

# Putting '..' on sys.path because Player import was causing an error when rush_rec_scraper.py is imported from 
# another module (such as 5_seasons_50_carries.py).
import sys
import os

# os.path.split() splits the head and tail of the path.
# This line of code grabs the head, joins it with '..', and inserts the path into the first element of sys.path.
sys.path.insert(0, os.path.join(os.path.split(__file__)[0], '..'))

from player import Player


def scrape_data(year):
    """
    This function sends a GET request to the pro-football-reference.com 'Rushing and Receiving' page for the
    given season and scrapes the data from the web page using Beautiful Soup 4. It returns a list containing
     each player's row data in the 'Rushing and Receiving' table.
    """
    # Send a GET request to Pro Football Reference's Rushing & Receiving page to gather the data.
    r = requests.get('https://www.pro-football-reference.com/years/' + str(year) + '/rushing.htm')
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


def create_player_objects(player_list, header):
    """
    This function uses the player_list created by scrape_data() to create an object for each player.
    It uses the header dictionary to set each attribute when creating the object. A list is returned.
    Each element in the list is a dictionary representation of each player object. This information is
    used to create a data frame of the Rushing and Receiving table.
    """
    # This list holds a dictionary of each object's attributes.
    # Each dictionary is made from the object's __dict__ attribute.
    list_of_player_dicts = []

    # Get each player's stats, create a Player object, and append the object
    # and the instance's __dict__ to their own list
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
    This function gets the text representation of each stat for a given player. It also gets a URL
    to the player's personal career stat page. It returns a list of the player's stats.
    """
    clean_player_stats = []
    for stat in raw_stat_list:
        clean_player_stats.append(stat.text)  # Grab the text representing the given stat.
        if stat['data-stat'] == 'player':
            # Every tag has an attribute.
            # If the tag's data-stat attribute is 'player', then we get the player's URL.
            # get_player_url(stat, player_info)
            href = stat.find_all('a', href=True)  # Get href, which specifies the URL of the page the link goes to
            url = href[0]['href']  # Get the URL string
            clean_player_stats.append(url)

    return clean_player_stats


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

