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


# Dictionary used in make_url() to build a URL to a footballdb.com table. Keys are the table type to be scraped. Values
# are another dictionary. The nested dictionary's keys and values build the URL so the correct table is found and
# sorted by the desired stat to be scraped.
url_dict = {
    'fumble': {
        'mode': 'M',
        'sort': 'fumlost'
    },
    'kick return': {
        'mode': 'KR',
        'sort': 'kryds'
    },
    'punt return': {
        'mode': 'PR',
        'sort': 'pryds'
    },
    'conversion': {
        'mode': 'S',
        'sort': 'totconv'
    }
}


def get_df(year, table_type, drop_year=True):
    """
    Scrapes a table from footballdb.com based on the table_type and puts it into a data frame.

    :param year: Season's year.
    :param table_type: String representing the type of table to be scraped. Currently only handles 'fumble', 'return',
                       and conversion.
    :param drop_year: Specify whether to drop the year column in the data frame.

    :return: A data frame of the scraped table.
    """
    player_list = scrape_football_db(year, table_type)
    df = make_df(player_list, table_type, year)

    if drop_year:
        df.drop('year', axis=1, inplace=True)  # Drop year column if specified

    return df


def make_url(year, table_type):
    """
    Creates a URL string used in scrape_football_db() to send a GET request to footballdb.com in order to scrape a
    table.

    :param year: Season year needed to go to the correct season of data.
    :param table_type: Indicates which table to scrape from. Currently only accepts 'fumble' (for fumbles lost),
                       'return' (for kickoff and punt returns), and 'conversion' (for two point conversions).

    :return: URL string used to send GET request.
    """
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
    Sends a GET request and uses BeautifulSoup4 to scrape data from a footballdb.com table.

    :param year: Season's year.
    :param table_type: String used to identify the table to scrape from. Used in make_url() to create the correct url.

    :return: List of BeautifulSoup4 elements.
    """
    # Currently only scrapes from three different tables.
    if table_type.lower() not in url_dict.keys():
        print("Error in scrape_football_db(). Make sure to specify table_type.")
        print("Can only currently handle 'fumble', 'return', and 'conversion'.")
        exit(1)

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


def make_df(player_list, table_type, year):
    """
    Creates a data frame based on the specified table type.

    :param player_list: List of BeautifulSoup4 elements. Each item represents a player.
    :param table_type: String used to identify the type of table scraped.
    :param year: Season's year.

    :return: Data frame of table scraped from footballdb.com.
    """
    list_of_player_dicts, attr_dict = get_stats(player_list, table_type)  # Scrape stats from given table.

    df_columns = list(attr_dict.keys())                                   # Get dict's keys for df's column names.
    df = pd.DataFrame(data=list_of_player_dicts, columns=df_columns)      # Create the data frame.
    df['year'] = year                                                     # Add a 'year' column.
    df.set_index('name', inplace=True)                                    # Make 'name' the data frame's index

    return df


def get_stats(player_list, table_type):
    # This list holds a dictionary of each object's attributes.
    # Each dictionary is made from the object's __dict__ attribute.
    player_obj_list = []

    # Get each player's stats, create a Player object, and append the object
    # and the instance's __dict__ to their own list
    for player in player_list:
        # The <td> tag defines a standard cell in an HTML table.
        # Get a list of cells. This raw web page data represents one player.
        raw_stat_list = player.find_all('td')

        # Scrape stats from table based on table_type.
        if table_type.lower() == 'fumble':
            stats, attr_dict, stop = get_fumbles_lost(raw_stat_list)
        elif table_type.lower() in ['kick return', 'punt return']:
            stats, attr_dict, stop = get_return_stats(raw_stat_list, table_type.lower())
        elif table_type.lower() == 'conversion':
            stats, attr_dict, stop = get_two_pt_conversions(raw_stat_list)
        else:
            print("Error in scrape_football_db(). Make sure to specify table_type.")
            print("Can only currently handle 'fumble', 'return', and 'conversion'.")
            exit(1)

        # Stop is True when remaining data in a table doesn't need to be scraped.
        # Examples of this situation include when a table is sorted by fumbles lost or two point conversions.
        if stop:
            break

        obj = Player(stats, attr_dict)
        player_obj_list.append(obj.__dict__)

    return player_obj_list, attr_dict


def get_two_pt_conversions(raw_stat_list):
    name = raw_stat_list[0].find('span', class_='hidden-xs').text  # Get player's name
    two_pt_conversions = raw_stat_list[15].text                    # Get number of 2 point conversions

    # The web page's 2pt conversion table is sorted, so we can stop at first appearance of 0.
    # The number of two point conversions can never be below 0.
    if int(two_pt_conversions) == 0:
        stop = True
    else:
        stop = False

    conversion_stats = [name, two_pt_conversions]
    conversion_dict = {'name': str, 'two_pt_conversions': int}

    return conversion_stats, conversion_dict, stop


def get_fumbles_lost(raw_stat_list):
    name = raw_stat_list[0].find('span', class_='hidden-xs').text  # Get player's name.
    fumbles_lost = raw_stat_list[3].text                           # Get number of fumbles lost.

    # The web page's fumbles table is sorted by fumbles lost, so we can stop at first appearance of 0.
    # The number of fumbles lost can never be below 0.
    if int(fumbles_lost) == 0:
        stop = True
    else:
        stop = False

    fumble_stats = [name, fumbles_lost]
    fumbles_lost_dict = {'name': str, 'fumbles_lost': int}

    return fumble_stats, fumbles_lost_dict, stop


def get_return_stats(raw_stat_list, table_type):
    name = raw_stat_list[0].find('span', class_='hidden-xs').text  # Get player's name.
    return_yards = raw_stat_list[3].text                           # Get total return yards.
    return_td = raw_stat_list[7].text                              # Get total return touchdowns.

    return_stats = [name, return_yards, return_td]

    if table_type.lower() == 'kick return':
        return_dict = {'name': str, 'kick_return_yards': int, 'kick_return_td': int}
    elif table_type.lower() == 'punt return':
        return_dict = {'name': str, 'punt_return_yards': int, 'punt_return_td': int}

    return return_stats, return_dict, False


if __name__ == '__main__':
    """Usage example."""
    season_year = 2017
    table = 'punt return'
    punt_return_df = get_df(season_year, table, drop_year=False)
    print(punt_return_df)
    punt_return_df.to_csv('punt_return.csv')


"""
Sample output:

                     punt_return_yards  punt_return_td  year
name                                                        
Jamal Agnew                        447               2  2017
Pharoh Cooper                      399               0  2017
Marcus Sherels                     372               0  2017
Michael Campanaro                  291               1  2017
Adoree' Jackson                    290               0  2017
Trevor Davis                       289               0  2017
Jaydon Mickens                     287               1  2017
Trent Taylor                       281               0  2017
Alex Erickson                      278               0  2017
Tarik Cohen                        272               1  2017
Travis Benjamin                    257               1  2017
Ryan Switzer                       256               1  2017
Kenjon Barner                      240               0  2017
Tyler Lockett                      237               0  2017
Danny Amendola                     231               0  2017
Tyreek Hill                        204               1  2017
Andre Roberts                      201               0  2017
Brandon Tate                       193               0  2017
Jakeem Grant                       190               0  2017
Isaiah McKenzie                    183               0  2017
Jabrill Peppers                    180               0  2017
Bernard Reedy                      175               0  2017
Jamison Crowder                    171               0  2017
Christian McCaffrey                162               0  2017
Jalen Richard                      155               0  2017
Kaelin Clay                        149               1  2017
Eli Rogers                         146               0  2017
Kerwynn Williams                   137               0  2017
Will Fuller                        135               0  2017
Adam Jones                         131               0  2017
...                                ...             ...   ...
Damiere Byrd                         9               0  2017
Torrey Smith                         9               0  2017
DeAngelo Hall                        7               0  2017
Lardarius Webb                       7               0  2017
Corey Grant                          6               0  2017
Bennie Fowler                        6               0  2017
Trumaine Johnson                     6               0  2017
Brendan Langley                      6               0  2017
Eddie Jackson                        6               0  2017
DeAndrew White                       3               0  2017
Desmond King                         2               0  2017
Griff Whalen                         2               0  2017
T.J. Carrie                          0               0  2017
Keelan Cole                          0               0  2017
Stacy Coley                          0               0  2017
Maurice Harris                       0               0  2017
Cooper Kupp                          0               0  2017
Geronimo Allison                     0               0  2017
Donatello Brown                      0               0  2017
Patrick Chung                        0               0  2017
Darqueze Dennard                     0               0  2017
Johnny Holton                        0               0  2017
William Jackson                      0               0  2017
Max McCaffrey                        0               0  2017
Willie Snead                         0               0  2017
Daniel Sorensen                      0               0  2017
Jermaine Whitehead                   0               0  2017
Emmanuel Sanders                    -2               0  2017
Demarcus Robinson                   -4               0  2017
Krishawn Hogan                      -8               0  2017

[96 rows x 3 columns]
"""
