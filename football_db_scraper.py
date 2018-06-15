#!/usr/bin/env python3

"""
This module contains functions for scraping data from footballdb.com tables. Certain tables on
pro-football-reference.com, such as the Rushing and Receiving table, have missing stats for calculating a player's
total fantasy points for a season. These include fumbles lost, return yards, return touchdowns, and two point
conversions. This module scrapes those missing stats from various tables so fantasy point totals can be accurately
calculated.
"""

import requests
import bs4
import pandas as pd
from player import Player
import constants
import pro_football_ref_scraper as proref


def get_df(year, table_type):
    """
    Scrapes a table from footballdb.com based on the table_type and puts it into a data frame.
    :param year: Season year
    :param table_type: String representing the type of table to be scraped. Currently only handles 'fumble', 'return',
                       and conversion.
    :return: A data frame of the scraped table.
    """
    player_list = scrape_football_db(year, table_type)
    df = make_df(player_list, table_type)

    return df


def make_url(year, table_type):
    """
    Creates a URL for sending a GET request to footballdb.com in order to scrape a table. A dictionary called url_dict
    has keys that are the table type to be scraped. The values are another dictionary. This nested dictionary's keys
    build the URL so the correct table is found and sorted by the desired stat to be scraped.

    :param year: Season year needed to go to the correct season of data.
    :param table_type: Indicates which table to scrape from. Currently only accepts 'fumble' (for fumbles lost),
                       'return' (for kickoff and punt returns), and 'conversion' (for two point conversions).
    :return:
    """
    url_dict = {
        'fumble': {
            'mode': 'M',
            'sort': 'fumlost'
        },
        'return': {
            'mode': 'KR',
            'sort': 'kryds'
        },
        'conversion': {
            'mode': 'S',
            'sort': 'totconv'
        }
    }

    # Currently only scrapes from three different tables.
    if table_type.lower() not in url_dict.keys():
        print("Error in make_url(). Make sure to specify table_type.")
        print("Can only currently handle 'fumble', 'return', and 'conversion'.")
        exit(1)

    str_year = str(year)

    # Build the URL.
    url = ('https://www.footballdb.com/stats/stats.html?lg=NFL&yr='
           + str_year
           + '&type=reg&mode='
           + url_dict[table_type]['mode']
           + '&conf=&limit=all&sort='
           + url_dict[table_type]['sort'])

    return url


def scrape_football_db(year, table_type):
    """
    Scrapes data from a footballdb.com table.
    :param year:
    :param table_type:
    :return:
    """
    url = make_url(year, table_type)

    # Required for successful request. 403 error when not provided.
    # Taken from: https://stackoverflow.com/questions/38489386/python-requests-403-forbidden.
    req_header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36'
                             + '(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    # Send a GET request to Pro Football Reference's Rushing & Receiving page to gather the data.
    r = requests.get(url, headers=req_header)
    r.raise_for_status()

    # Create a BeautifulSoup object.
    soup = bs4.BeautifulSoup(r.text, 'lxml')

    # Find the first table with tag 'table' and id 'rushing_and_receiving
    table = soup.find('table', class_='statistics scrollable')

    # tbody is the table's body
    # Get the body of the table
    body = table.find('tbody')

    # tr refers to a table row
    # Each row in player_list has data for a single player
    # This will also collect descriptions of each column found in the web page's table, which
    # is filtered out in create_player_objects().
    player_list = body.find_all('tr')

    return player_list


def make_df(player_list, table_type):
    if table_type.lower() == 'fumble':
        column_dict = {'name': str, 'fumbles_lost': int}
        list_of_player_dicts = get_fumbles_lost(player_list, column_dict)
    elif table_type.lower() == 'return':
        column_dict = {'name': str, 'return_yards': int, 'return_td': int}
        list_of_player_dicts = get_return_stats(player_list, column_dict)
    elif table_type.lower() == 'conversion':
        column_dict = {'name': str, 'two_pt_conversions': int}
        list_of_player_dicts = get_two_pt_conversions(player_list, column_dict)

    df_columns = list(column_dict.keys())                             # Get dict's keys for df's column names.
    df = pd.DataFrame(data=list_of_player_dicts, columns=df_columns)  # Create the data frame.
    # df['year'] = year                                               # Add a 'year' column.
    df.set_index('name', inplace=True)                                # Make 'name' the data frame's index

    return df


def get_two_pt_conversions(player_list, conversion_dict):
    # This list holds a dictionary of each object's attributes.
    # Each dictionary is made from the object's __dict__ attribute.
    conversion_objs = []

    # Get each player's stats, create a Player object, and append the object
    # and the instance's __dict__ to their own list
    for player in player_list:
        # The <td> tag defines a standard cell in an HTML table.
        # Get a list of cells. This raw web page data represents one player.
        raw_stat_list = player.find_all('td')

        name = raw_stat_list[0].find('span', class_='hidden-xs').text     # Get player's name
        two_pt_conversions = raw_stat_list[15].text                       # Get number of 2 point conversions

        # The web page's 2pt conversion table is sorted, so we can stop at first appearance of 0.
        if int(two_pt_conversions) == 0:
            break

        conversion_stats = [name, two_pt_conversions]
        obj = Player(conversion_stats, conversion_dict)
        conversion_objs.append(obj.__dict__)

    return conversion_objs


def get_fumbles_lost(player_list, fumbles_lost_dict):
    # This list holds a dictionary of each object's attributes.
    # Each dictionary is made from the object's __dict__ attribute.
    fumbles_lost_objs = []

    # Get each player's stats, create a Player object, and append the object
    # and the instance's __dict__ to their own list
    for player in player_list:
        # The <td> tag defines a standard cell in an HTML table.
        # Get a list of cells. This raw web page data represents one player.
        raw_stat_list = player.find_all('td')

        name = raw_stat_list[0].find('span', class_='hidden-xs').text  # Get player's name.
        fumbles_lost = raw_stat_list[3].text                           # Get number of fumbles lost.

        # The web page's fumbles table is sorted by fumbles lost, so we can stop at first appearance of 0.
        if int(fumbles_lost) == 0:
            break

        fumble_stats = [name, fumbles_lost]
        obj = Player(fumble_stats, fumbles_lost_dict)
        fumbles_lost_objs.append(obj.__dict__)

    return fumbles_lost_objs


def get_return_stats(player_list, return_dict):
    # This list holds a dictionary of each object's attributes.
    # Each dictionary is made from the object's __dict__ attribute.
    return_objs = []

    # Get each player's stats, create a Player object, and append the object
    # and the instance's __dict__ to their own list
    for player in player_list:
        # The <td> tag defines a standard cell in an HTML table.
        # Get a list of cells. This raw web page data represents one player.
        raw_stat_list = player.find_all('td')

        name = raw_stat_list[0].find('span', class_='hidden-xs').text  # Get player's name.
        return_yards = raw_stat_list[3].text  # Get total return yards.
        return_td = raw_stat_list[7].text  # Get total return touchdowns.

        return_stats = [name, return_yards, return_td]
        obj = Player(return_stats, return_dict)
        return_objs.append(obj.__dict__)

    return return_objs


if __name__ == '__main__':
    year = 2017

    # Create url for given season.
    url = 'https://www.pro-football-reference.com/years/' + str(year) + '/rushing.htm'

    # Identify the table ID to get scrape from the correct table.
    table_id = 'rushing_and_receiving'

    # Scrape the data to get each player's web page elements.
    player_list = proref.scrape_table(url, table_id)

    # Use the elements to create Player objects.
    list_of_player_dicts = proref.create_player_objects(player_list, constants.SEASON_RUSH_REC_HEADER)

    # Create a data frame for the season
    df = proref.make_data_frame(list_of_player_dicts, year, constants.SEASON_RUSH_REC_HEADER, fantasy=True)

    return_df = scrape_football_db(2017, 'return')

    return_df.drop('year', inplace=True, axis=1)
    new_df = df.join(return_df, on='name', how='left')

    # new_df['two_pt_conversions'].fillna(0, inplace=True)

    new_df['return_yards'].fillna(0, inplace=True)
    new_df['return_td'].fillna(0, inplace=True)

    # Set the player's name and the season's year as the indexes.
    new_df.set_index(['name', 'year'], inplace=True)

    # print(new_df)

    new_df.to_csv('returns.csv')
