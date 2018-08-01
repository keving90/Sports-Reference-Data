#!/usr/bin/env python3

"""
This module contains a ProFbRefScraper class used to scrape NFL data from www.pro-football-reference.com. It then
places the data into a Pandas data frame. Users can scrape data from the following data tables: rushing, receiving,
passing, kicking, returns, scoring, fantasy, and defense. Multiple years of data can be scraped and placed into the
same data frame.

Note: This module was built using Python 3.6.1, so dictionaries are ordered.
"""


import requests
import bs4
import pandas as pd
from player import Player
from datetime import datetime


class ProFbRefScraper(object):
    """

    Scrapes NFL data from www.pro-football-reference.com and places it into a Pandas data frame. Multiple years of data
    can be scraped and placed into a single data frame for the same statistical category. Users can scrape data for
    the following stats: rushing, receiving, passing, kicking, returns, scoring, fantasy, and defense. The get_data()
    method is used to scrape the data. The user must specify a table type, start year, and end year.

    Valid table_type values include:

    'all_purpose': All purpose yardage data. Has data for all NFL players.

    'rushing': Rushing data.
    'passing': Passing data.
    'receiving': Receiving data.
    'kicking': Field goal, point after touchdown, and punt data.
    'returns': Punt and kick return data.
    'scoring': All types of scoring data, such as touchdowns (defense/offense), two point conversions, kicking, etc.
    'fantasy': Rushing, receiving, and passing stats, along with fantasy point totals from various leagues.
    'defense': Defensive player stats.

    Attributes:
        _tables_dict (dict): Dictionary whose keys are the type of table to scrape from. The value is
            another dictionary. The nested dictionary contains a key whose value is used for building the URL to the
            table. Another key within the nested dict has a dict as a value to store the column names and their data
            type.

            Example:
                ex = {
                    'table_type': {
                        'table_type_id': 'url_table_type_id',
                        'columns_to_grab_from_table': {
                            'column_name': data_type_of_column,
                            .
                            .
                            .
                            'column_name': data_type_of_column
                        }
                    }
                }

        _logs_dict (dict): Similar to _tables_dict, except it scrapes and individual player's game log for a given
            season. (this feature is under construction)

    """
    def __init__(self):
        # Used to create a Player object. Keys are attributed and values are their data type.
        # Also used to create columns in a data frame.
        self._tables_dict = {
            'rushing': {
                'table_id': 'rushing_and_receiving',
                'all_columns': {
                    'name': str,
                    'player_url': str,
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
                    'fumbles': int  # all fumbles (not just fumbles lost)
                }
            },
            'passing': {
                'table_id': 'passing',
                'all_columns': {
                    'name': str,
                    'player_url': str,
                    'team': str,
                    'age': int,
                    'position': str,
                    'games_played': int,
                    'games_started': int,
                    'qb_record': str,
                    'pass_completions': int,
                    'pass_attempts': int,
                    'comp_pct': float,
                    'pass_yards': int,
                    'pass_td': int,
                    'pass_td_pct': float,
                    'interceptions': int,
                    'int_pct': float,
                    'longest_pass': int,
                    'pass_yards_per_att': float,
                    'adj_yards_per_att': float,
                    'pass_yards_per_comp': float,
                    'pass_yards_per_game': float,
                    'qb_rating': float,
                    'total_qbr': float,
                    'sacked': int,
                    'sack_yards': int,
                    'net_yards_per_att': float,
                    'adj_net_yards_per_att': float,
                    'sack_pct': float,
                    'Q4_comebacks': int,
                    'game_winning_drives': int
                }
            },
            'receiving': {
                'table_id': 'receiving',
                'all_columns': {
                    'name': str,
                    'player_url': str,
                    'team': str,
                    'age': int,
                    'position': str,
                    'games_played': int,
                    'games_started': int,
                    'targets': int,
                    'receptions': int,
                    'catch_pct': float,
                    'rec_yards': int,
                    'yards_per_rec': float,
                    'rec_td': int,
                    'longest_rec': int,
                    'rec_per_game': float,
                    'rec_yards_per_game': float,
                    'fumbles': int
                }
            },
            'kicking': {
                'table_id': 'kicking',
                'all_columns': {
                    'name': str,
                    'player_url': str,
                    'team': str,
                    'age': int,
                    'position': str,
                    'games_played': int,
                    'games_started': int,
                    '0-19_made': int,
                    '0-19_att': int,
                    '20-29_made': int,
                    '20-29_att': int,
                    '30-39_made': int,
                    '30-39_att': int,
                    '40-49_made': int,
                    '40-49_att': int,
                    '50_plus_made': int,
                    '50_plus_att': int,
                    'fg_made': int,
                    'fg_att': int,
                    'fg_pct': float,
                    'extra_pt_att': int,
                    'extra_pt_made': int,
                    'extra_pt_pct': float,
                    'punts': int,
                    'punt_yards': int,
                    'longest_punt': int,
                    'blocked_punts': int,
                    'yards_per_punt': float

                }
            },
            'returns': {
                'table_id':'returns',
                'all_columns': {
                    'name': str,
                    'player_url': str,
                    'team': str,
                    'age': int,
                    'position': str,
                    'games_played': int,
                    'games_started': int,
                    'punt_returns': int,
                    'punt_return_yards': int,
                    'punt_return_td': int,
                    'lng_punt_return': int,
                    'yards_per_punt_return': float,
                    'kick_returns': int,
                    'kick_return_yards': int,
                    'kick_return_td': int,
                    'lng_kick_return': int,
                    'yards_per_kick_return': float,
                    'all_purpose_yards': int

                }
            },
            'scoring': {
                'table_id': 'scoring',
                'all_columns': {
                    'name': str,
                    'player_url': str,
                    'team': str,
                    'age': int,
                    'position': str,
                    'games_played': int,
                    'games_started': int,
                    'rush_td': int,
                    'rec_td': int,
                    'punt_return_td': int,
                    'kick_return_td': int,
                    'fum_return_td': int,
                    'int_return_td': int,
                    'other_td': int,  # Blocked kicks or missed field goals.
                    'all_td': int,
                    'two_pt_made': int,
                    'two_pt_att': int,
                    'extra_point_made': int,
                    'extra_point_att': int,
                    'fg_made': int,
                    'fg_att': int,
                    'safeties': int,
                    'points': int,
                    'points_per_game': float
                }
            },
            'fantasy': {
                'table_id': 'fantasy',
                'all_columns': {
                    'name': str,
                    'player_url': str,
                    'team': str,
                    'position': str,
                    'age': int,
                    'games_played': int,
                    'games_started': int,
                    'pass_completions': int,
                    'pass_attempts': int,
                    'pass_yards': int,
                    'pass_td': int,
                    'interceptions': int,
                    'rush_attempts': int,
                    'rush_yards': int,
                    'yards_per_rush': float,
                    'rush_td': int,
                    'targets': int,
                    'receptions': int,
                    'rec_yards': int,
                    'yards_per_rec': float,
                    'rec_td': int,
                    'fan_points': int,  # Standard scoring. (football_db_scraper.py default settings)
                    'fan_points_ppr': float,  # 1 point per reception.
                    'draft_kings': float,
                    'fan_duel': float,
                    'vbd': int,  # Player's fantasy points minus fantasy points of the baseline player.
                    'position_rank': int,
                    'overall_rank': int
                }
            },
            'defense': {
                'table_id': 'defense',
                'all_columns': {
                    'name': str,
                    'player_url': str,
                    'team': str,
                    'age': int,
                    'position': str,
                    'games_played': int,
                    'games_started': int,
                    'interceptions': int,
                    'int_yards': int,
                    'int_td': int,
                    'lng_int': int,
                    'passes_def': int,
                    'forced_fumbles': int,
                    'fumbles': int,
                    'fum_recovered': int,
                    'fum_ret_yards': int,
                    'fum_ret_td': int,
                    'sacks': float,
                    'tackles': int,
                    'tackle_asst': int,
                    'safeties': int
                }
            }
        }

        self._logs_dict = {
            'rush_rec_log': {
                'table_id': 'stats',
                'all_columns': {
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
            },
            'pass_rush_rec_log': {
                'table_id': 'stats',
                'all_columns': {
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
            }
        }

    def get_data(self, start_year, end_year, table_type):
        """
        Gets a data frame of NFL player stats for one for more seasons based on the desired stat table.

        :param start_year:
        :param end_year:
        :param table_type:
        :return:
        """
        # Only scrapes from tables in self._tables_dict.keys().
        if table_type.lower() not in self._tables_dict.keys():
            raise KeyError("Error, make sure to specify table_type. "
                           + "Can only currently handle the following table names: "
                           + str(list(self._tables_dict.keys())))

        # Get seasons to iterate through.
        year_range = self._get_year_range(start_year, end_year)

        # Scrape data for each season.
        df_list = [self._get_single_season(year, table_type) for year in year_range]

        # Concatenate all seasons into one big data frame.
        big_df = pd.concat(df_list)

        big_df = self._replace_nan(big_df, table_type)

        return big_df

    def _get_year_range(self, start_year, end_year):
        """
        Uses a start_year and end_year to build a range iterator.

        :param start_year: Year to begin iterator at.
        :param end_year: Year to end iterator at.

        :return: A range iterator.
        """
        # Build range iterator depending on how start_year and end_year are related.
        if int(start_year) > int(end_year):
            year_range = range(start_year, end_year - 1, -1)
        elif int(start_year) <= int(end_year):
            year_range = range(start_year, end_year + 1)

        return year_range

    def _get_single_season(self, year, table_type):
        """
        Scrapes a table from www.footballdb.com based on the table_type and puts it into a Pandas data frame.

        :param year: Season's year.
        :param table_type: String representing the type of table to be scraped.

        :return: A data frame of the scraped table for a single season.
        """
        # Only scrapes from tables in self._tables_dict.keys().
        if table_type.lower() not in self._tables_dict.keys():
            raise KeyError("Error, make sure to specify table_type. "
                           + "Can only currently handle the following table names: "
                           + str(list(self._tables_dict.keys())))

        # Scrape a given table from www.footballdb.com and create a data frame.
        player_list = self._get_player_result_set(year, table_type)
        player_dicts = self._get_player_stats(player_list, table_type)
        df = self._make_df(year, player_dicts, table_type)

        return df

    def _get_player_result_set(self, year, table_type):
        """
        Scrapes a table from pro-football-reference.com based on provided table type.

        :return: List of BeautifulSoup4 element ResultSets. Each item in list is a row in the table.
        """
        # Send a GET request to Pro Football Reference's Rushing & Receiving page to gather the data.
        url = 'https://www.pro-football-reference.com/years/' + str(year) + '/' + table_type + '.htm'
        r = requests.get(url)
        r.raise_for_status()

        # Create a BeautifulSoup object.
        soup = bs4.BeautifulSoup(r.text, 'lxml')

        # Find the first table with tag 'table' and id 'rushing_and_receiving.
        table = soup.find('table', id=self._tables_dict[table_type]['table_id'])

        # tbody is the table's body
        # Get the body of the table
        body = table.find('tbody')

        # tr refers to a table row
        # Each element in player_list has data for a single player.
        # This will also collect descriptions of each column found in the web page's table, which
        # is filtered out in create_player_objects().
        player_list = body.find_all('tr')

        return player_list

    def _get_player_stats(self, player_list, table_type):
        """
        Iterates through a BeautifulSoup4 ResultSet to get a player stat data. Uses a list of player stats to create a
        Player object for each player. The object's attributes are based on the table_type.

        :param player_list: List of BeautifulSoup4 element ResultSets. Each item in list is a row in the table.

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
                # Create a Player object and append the __dict__ attribute to a list.
                # This list is used for the data in our data frame.
                player_stats = self._get_clean_data(raw_stat_list)
                obj = Player(player_stats, self._tables_dict[table_type]['all_columns'])
                list_of_player_dicts.append(obj.__dict__)

        return list_of_player_dicts

    def _get_clean_data(self, raw_stat_list):
        """
        Gets clean text stats from a list of BeautifulSoup4 element tags.

        :param raw_stat_list: List of BeautifulSoup4 element ResultSets. Inside of each ResultSet is a stat.

        :return: List of the player's stats in text form.
        """
        clean_player_stats = []
        for stat in raw_stat_list:
            # Grab the text representing the given stat.
            clean_player_stats.append(stat.text)

            # Every tag has an attribute.
            # If the tag's data-stat attribute is 'player', then we get the player's URL.
            if stat['data-stat'] == 'player':
                # Get href, which specifies the URL of the page the link goes to.
                href = stat.find_all('a', href=True)

                # Get the URL string
                url = href[0]['href']
                clean_player_stats.append(url)

        return clean_player_stats

    def _make_df(self, year, player_dicts, table_type):
        """
        Makes a data frame using a dictionary's keys as column names and list of player_object.__dict__'s as data. The
        player's unique URL is used as the data frame's index.

        :param year: Season's year used to create a unique index for the player's season in the data set.
        :param player_dicts: List of player_object.__dict__'s.
        :param table_type: String to get column names for data frame.

        :return: A data frame.
        """
        # Get data frame's columns from a relevant table dict's keys.
        df_columns = list(self._tables_dict[table_type]['all_columns'].keys())

        # Create the data frame.
        df = pd.DataFrame(data=player_dicts, columns=df_columns)

        # Add year column.
        df['year'] = year

        # Combine player_url and year into one column. With this, a player's season can be uniquely identified when
        # they have records for multiple seasons in a single data set. It will prevent issues when joining two data
        # sets that each have multiple seasons of data for a single player.
        df['player_url'] = df['player_url'].apply(lambda x: x + str(year))

        # Make the new 'player_url' the data frame's index.
        df.set_index('player_url', inplace=True)

        return df

    def _replace_nan(self, df, table_type):
        """
        Replaces numpy.NaN values with 0 in a data frame for numerical categories only.

        :param df: Data frame to be modified.
        :param table_type: Type of table scraped to be modified.

        :return: The modified data frame.
        """
        if table_type.lower() == 'passing':
            [df[column].fillna(0, inplace=True) for column in df[8:]]
        else:
            [df[column].fillna(0, inplace=True) for column in df[7:]]

        return df


    # Work in progress:

    # def scrape_game_log(self, player_url, year):
    #     """
    #     Scrapes regular season stats from a player's game log for a specific year.
    #
    #     :param player_url: String representing player's unique URL found in the "Rushing and Receiving" table.
    #     :param year: Season's year for the game log.
    #
    #     :return: Data frame where each row is the stats for a game.
    #     """
    #     # Remove the '.htm' part of the player's url if necessary.
    #     if player_url.endswith('.htm'):
    #         player_url = player_url[:-4]
    #
    #     # Build the URL to the player's game log page
    #     url = 'https://www.pro-football-reference.com' + player_url + '/gamelog/' + str(year) + '/'
    #
    #     # ID used to identify the regular season stats table.
    #     table_id = 'stats'
    #
    #     # Get the data from the game log page.
    #     data = self.__scrape_table(url, table_id)
    #
    #     # Use the appropriate header dictionary based on the number of elements in data list.
    #     if not data[0]:
    #         raise ValueError("Error, no data was scraped from the game log.")
    #     elif len(data[0]) == 33:
    #         header = self._log_rush_rec_pass_header
    #     elif len(data[0]) == 21:
    #         header = self._log_rush_rec_header
    #     else:
    #         raise ValueError("Error, can only currently handle logs with rushing and receiving data (21 columns), "
    #                          + "or with rushing, receiving, and passing data (33 columns).")
    #
    #     list_of_log_dicts = self.__create_player_objects(data, header)
    #     df = self.__make_data_frame(list_of_log_dicts, year)
    #
    #     return df


if __name__ == '__main__':
    # Usage example.
    fb_ref = ProFbRefScraper()

    rush_rec_df = fb_ref.get_data(start_year=2017, end_year=2017, table_type='rushing')

    print(rush_rec_df)

    rush_rec_df.to_csv('rushing.csv')
