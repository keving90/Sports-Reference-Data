#!/usr/bin/env python3

import requests
import bs4
import pandas as pd
# import pro_football_ref_scraper.football_db_utility_scraper as fbdb
from player import Player
from datetime import datetime


class ProFbRefScraper(object):
    """

    Uses Requests and Beautiful Soup 4 to scrape data from www.pro-football-reference.com's Rushing and Receiving table
    for a given season and save it into a data frame. Can calculate fantasy points for the player's season. Extra
    fumbles lost, return yards, return touchdowns, and two point conversions data will need to be scraped from
    www.footballdb.com to get accurate fantasy calculations. This will lead to more overhead.

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
                    'fumbles': int  # all fumbles
                }
            },
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




        # self._season_rush_rec_header = {
        #     'name': str,
        #     'url': str,
        #     'team': str,
        #     'age': int,
        #     'position': str,
        #     'games_played': int,
        #     'games_started': int,
        #     'rush_attempts': int,
        #     'rush_yards': int,
        #     'rush_td': int,
        #     'longest_run': int,
        #     'yards_per_rush': float,
        #     'yards_per_game': float,
        #     'attempts_per_game': float,
        #     'targets': int,
        #     'receptions': int,
        #     'rec_yards': int,
        #     'yards_per_rec': float,
        #     'rec_td': int,
        #     'longest_rec': int,
        #     'rec_per_game': float,
        #     'rec_yards_per_game': float,
        #     'catch_percentage': float,
        #     'scrimmage_yards': int,
        #     'rush_rec_td': int,
        #     'fumbles': int  # all fumbles
        # }

        # Default fantasy settings. Keys are the setting and values are their point value.
        # Can be changed using fantasy_settings property.
        # Represents a standard Yahoo! 0PPR league.
        # self._fantasy_settings_dict = {
        #     'pass_yards': 1 / 25,  # 25 yards = 1 point
        #     'pass_td': 4,
        #     'interceptions': -1,
        #     'rush_yards': 1 / 10,  # 10 yards = 1 point
        #     'rush_td': 6,
        #     'rec_yards': 1 / 10,  # 10 yards = 1 point
        #     'receptions': 0,
        #     'rec_td': 6,
        #     'two_pt_conversions': 2,
        #     'fumbles_lost': -2,
        #     'offensive_fumble_return_td': 6,
        #     'return_yards': 1 / 25,  # 25 yards = 1 point
        #     'return_td': 6
        # }

        # Used in fantasy_settings.setter to make sure new dictionary provided by user is valid.
        # self._valid_fantasy_keys = self._fantasy_settings_dict.keys()

        # Similar to _season_rush_rec_header, but used for scraping a player's game log for a season.
        # Valid only for game log tables containing rushing and receiving data.
    #     self._log_rush_rec_header = {
    #         'date': datetime,
    #         'game_number': int,
    #         'age': float,
    #         'team': str,
    #         'location': str,
    #         'opponent': str,
    #         'result': str,
    #         'rush_attempts': int,
    #         'rush_yards': int,
    #         'yards_per_rush': float,
    #         'rush_td': int,
    #         'targets': int,
    #         'receptions': int,
    #         'rec_yards': int,
    #         'yards_per_rec': float,
    #         'rec_td': int,
    #         'catch_percentage': float,
    #         'yards_per_target': float,
    #         'total_td': int,
    #         'total_points': int
    #     }
    #
    #     # Similar to _log_rush_rec_header. Valid only for game log tables containing rushing, receiving, and passing
    #     # data.
    #     self._log_rush_rec_pass_header = {
    #         'date': datetime,
    #         'game_number': int,
    #         'age': float,
    #         'team': str,
    #         'location': str,
    #         'opponent': str,
    #         'result': str,
    #         'rush_attempts': int,
    #         'rush_yards': int,
    #         'yards_per_rush': float,
    #         'rush_td': int,
    #         'targets': int,
    #         'receptions': int,
    #         'rec_yards': int,
    #         'yards_per_rec': float,
    #         'rec_td': int,
    #         'catch_percentage': float,
    #         'yards_per_target': float,
    #         'pass_completions': int,
    #         'pass_attempts': int,
    #         'completion_percentage': float,
    #         'pass_yards': int,
    #         'pass_td': int,
    #         'interceptions': int,
    #         'qb_rating': float,
    #         'times_sacked': int,
    #         'yards_lost_to_sacks': int,
    #         'yards_per_pass_attempt': float,
    #         'adjusted_yards_per_pass_attempt': float,
    #         'pass_2_point_conversions': int,
    #         'total_td': int,
    #         'total_points': int
    #     }
    #
    # @property
    # def fantasy_settings(self):
    #     return self._fantasy_settings_dict
    #
    # # Let users use their own fantasy settings. Must be a valid dictionary.
    # @fantasy_settings.setter
    # def fantasy_settings(self, settings_dict):
    #     # Fantasy settings must be a dictionary.
    #     if not isinstance(settings_dict, dict):
    #         raise ValueError("Fantasy settings must be a dictionary.")
    #
    #     # Check for valid number of keys in new fantasy settings dictionary.
    #     dict_len = len(self._valid_fantasy_keys)
    #     if len(settings_dict) > dict_len:
    #         raise KeyError("Too many keys in new fantasy settings dict. "
    #                        + str(dict_len) + " keys required.")
    #     elif len(settings_dict) < dict_len:
    #         raise KeyError("Too few keys in new fantasy settings dict. "
    #                        + str(dict_len) + " keys required.")
    #
    #     # Check for valid keys and value types in new fantasy settings dictionary.
    #     for key, value in settings_dict.items():
    #         if key not in self._valid_fantasy_keys:
    #             raise KeyError("Invalid key in new fantasy settings dict. "
    #                            + "Valid keys include: " + str(list(self._valid_fantasy_keys)))
    #         if type(value) not in [float, int]:
    #             raise ValueError("Invalid value in new fantasy settings dict. Must be type int or float.")
    #
    #     self._fantasy_settings_dict = settings_dict





    def get_data(self, start_year, end_year, table_type):
        year_range = self._get_year_range(start_year, end_year)
        df_list = [self._get_single_season(year, table_type) for year in year_range]

        # Concatenate all seasons into one big data frame.
        big_df = pd.concat(df_list)

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

    def _make_url(self, year, table_type):
        """
        Creates a URL string used to send a GET request to www.pro-football-reference.com to scrape a table.

        :param year: Season year needed to go to the correct season of data.
        :param table_type: Indicates which table to scrape from.

        :return: URL string used to send GET request.
        """
        # Build the URL.
        return 'https://www.pro-football-reference.com/years/' + str(year) + '/' + table_type + '.htm'

    def _get_single_season(self, year, table_type):
        """
        Scrapes a table from www.footballdb.com based on the table_type and puts it into a Pandas data frame.

        See documentation under FbDbScraper class for valid table types and their descriptions.

        :param year: Season's year.
        :param table_type: String representing the type of table to be scraped.

        :return: A data frame of the scraped table.
        """
        # Only scrapes from tables in self._tables_dict.keys().
        if table_type.lower() not in self._tables_dict.keys():
            raise KeyError("Error, make sure to specify table_type. "
                           + "Can only currently handle the following table names: "
                           + str(list(self._tables_dict.keys())))

        # Scrape a given table from www.footballdb.com and create a data frame.
        # url = self._make_url(year, table_type)
        # url = 'https://www.pro-football-reference.com/years/' + str(year) + '/' + table_type + '.htm'
        player_list = self._get_player_result_set(year, table_type)
        player_dicts = self._get_player_stats(player_list, table_type)
        df = self._make_df(year, player_dicts, table_type)

        # The 'scoring' and 'kicking' tables have field goal stats as a 'made/attempts' string.
        # Split these stats into two integer columns.
        # if table_type in ['scoring', 'kicking']:
        #     df = self._handle_field_goals(df, table_type)

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
                player_stats = self._get_clean_row(raw_stat_list)
                obj = Player(player_stats, self._tables_dict[table_type]['all_columns'])
                list_of_player_dicts.append(obj.__dict__)

        return list_of_player_dicts

    def _get_clean_row(self, raw_stat_list):
        """
        Get text data from from a BeautifulSoup4 element tag. Also gets a URL to the player's personal career stat
        page. Used in create_player_objects().

        :param raw_stat_list: List of BeautifulSoup4 element ResultSets. Inside of each ResultSet is a stat.

        :return: List of the player's stats in text form.
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

    def _make_df(self, year, player_dicts, table_type):
        """
        Makes a data frame using a dictionary's keys as column names and list of player_object.__dict__'s as data. The
        player's unique URL is used as the data frame's index.

        :param year: Season's year used to create a unique index for the player's season in the data set.
        :param player_dicts: List of player_object.__dict__'s.
        :param table_type: String to get self._tables_dict[table_type]['all_columns'].keys() for column names.

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






    # def get_rushing_receiving_data(self, year, fantasy=False):
    #     """
    #     Scrape data from www.pro-football-reference.com's Rushing and Receiving table.
    #
    #     :param year: Season's year.
    #     :param fantasy: When True, calculate the fantasy point total for each player. Extra fumbles lost, return yards,
    #                     return touchdowns, and two point conversions data will need to be scraped from
    #                     www.footballdb.com to get accurate fantasy calculations. This will lead to more function
    #                     overhead.
    #
    #     :return: Data frame of www.pro-football-reference.com's Rushing and Receiving table.
    #     """
    #     # Create url for given season.
    #     input_url = 'https://www.pro-football-reference.com/years/' + str(year) + '/rushing.htm'
    #
    #     # Identify the table ID to get scrape from the correct table.
    #     input_table_id = 'rushing_and_receiving'
    #
    #     # Scrape the data to get a list of each player's web page elements.
    #     elem_list = self.__scrape_table(input_url, input_table_id)
    #
    #     # Use the elements to create Player objects.
    #     player_dicts = self.__create_player_objects(elem_list, self._season_rush_rec_header)
    #
    #     # Create a data frame for the season.
    #     df = self.__make_data_frame(player_dicts, year, fantasy)
    #
    #     return df

    def scrape_game_log(self, player_url, year):
        """
        Scrape regular season stats from a player's game log for a specific year.

        :param player_url: String representing player's unique URL found in the "Rushing and Receiving" table.
        :param year: Season's year for the game log.

        :return: Data frame where each row is the stats for a game.
        """
        # Remove the '.htm' part of the player's url if necessary.
        if player_url.endswith('.htm'):
            player_url = player_url[:-4]

        # Build the URL to the player's game log page
        url = 'https://www.pro-football-reference.com' + player_url + '/gamelog/' + str(year) + '/'

        # ID used to identify the regular season stats table.
        table_id = 'stats'

        # Get the data from the game log page.
        data = self.__scrape_table(url, table_id)

        # Use the appropriate header dictionary based on the number of elements in data list.
        if not data[0]:
            raise ValueError("Error, no data was scraped from the game log.")
        elif len(data[0]) == 33:
            header = self._log_rush_rec_pass_header
        elif len(data[0]) == 21:
            header = self._log_rush_rec_header
        else:
            raise ValueError("Error, can only currently handle logs with rushing and receiving data (21 columns), "
                             + "or with rushing, receiving, and passing data (33 columns).")

        list_of_log_dicts = self.__create_player_objects(data, header)
        df = self.__make_data_frame(list_of_log_dicts, year)

        return df

    # def __scrape_table(self, url, table_id):
    #     """
    #     Scrape a table from pro-football-reference.com based on provided table ID.
    #
    #     :param url: Websites URL.
    #     :param table_id: Identifier for the table. Found when used "inspect element" on web page.
    #
    #     :return: List of BeautifulSoup4 element ResultSets. Each item in list is a row in the table.
    #     """
    #     # Send a GET request to Pro Football Reference's Rushing & Receiving page to gather the data.
    #     r = requests.get(url)
    #     r.raise_for_status()
    #
    #     # Create a BeautifulSoup object.
    #     soup = bs4.BeautifulSoup(r.text, 'lxml')
    #
    #     # Find the first table with tag 'table' and id 'rushing_and_receiving.
    #     table = soup.find('table', id=table_id)
    #
    #     # tbody is the table's body
    #     # Get the body of the table
    #     body = table.find('tbody')
    #
    #     # tr refers to a table row
    #     # Each element in player_list has data for a single player.
    #     # This will also collect descriptions of each column found in the web page's table, which
    #     # is filtered out in create_player_objects().
    #     player_list = body.find_all('tr')
    #
    #     return player_list
    #
    # def __create_player_objects(self, player_list, header):
    #     """
    #     Create an object for each player using the player_list created by scrape_data().
    #
    #     :param player_list: List of BeautifulSoup4 element ResultSets. Each item in list is a row in the table.
    #     :param header: Dictionary where keys are the name of the stat and values are the data type.
    #
    #     :return: List of dictionary representations of Player objects (object.__dict__).
    #     """
    #     # This list holds a dictionary of each object's attributes.
    #     # Each dictionary is made from the object's __dict__ attribute.
    #     list_of_player_dicts = []
    #
    #     # Get each player's stats, create a Player object, and append the object
    #     # and the instance's __dict__ to their own list.
    #     for player in player_list:
    #         # The <td> tag defines a standard cell in an HTML table.
    #         # Get a list of cells. This raw web page data represents one player.
    #         raw_stat_list = player.find_all('td')
    #
    #         # If info_list has data, then we will extract the desired information from the elements.
    #         # info_list will be empty if the current 'player' in the player_list is actually other
    #         # irrelevant information we're not interested in (such as a column description).
    #         if raw_stat_list:
    #             player_stats = self.__get_player_stats(raw_stat_list)
    #             # Create a Player object and append the __dict__ attribute to a list.
    #             # This list is used for the data in our data frame.
    #             obj = Player(player_stats, header)
    #             list_of_player_dicts.append(obj.__dict__)
    #
    #     return list_of_player_dicts
    #
    # def __get_player_stats(self, raw_stat_list):
    #     """
    #     Get text data from from a BeautifulSoup4 element tag. Also gets a URL to the player's personal career stat
    #     page. Used in create_player_objects().
    #
    #     :param raw_stat_list: List of BeautifulSoup4 element ResultSets. Inside of each ResultSet is a stat.
    #
    #     :return: List of the player's stats in text form.
    #     """
    #     clean_player_stats = []
    #     for stat in raw_stat_list:
    #         clean_player_stats.append(stat.text)  # Grab the text representing the given stat.
    #         if stat['data-stat'] == 'player':
    #             # Every tag has an attribute.
    #             # If the tag's data-stat attribute is 'player', then we get the player's URL.
    #             # get_player_url(stat, player_info)
    #             href = stat.find_all('a', href=True)  # Get href, which specifies the URL of the page the link goes to
    #             url = href[0]['href']  # Get the URL string
    #             clean_player_stats.append(url)
    #
    #     return clean_player_stats
    #
    # def __make_data_frame(self, player_dict_list, year, fantasy=False):
    #     """
    #     Create a new data frame and return it.
    #
    #     :param player_dict_list: List of unique Player.__dict__'s.
    #     :param year: NFL season's year.
    #     :param fantasy: When true, add a column for player's total fantasy points for the season.
    #
    #     :return: Data frame of stats.
    #     """
    #     df_columns = list(self._season_rush_rec_header.keys())        # Get header dict's keys for df's column names.
    #     df = pd.DataFrame(data=player_dict_list, columns=df_columns)  # Create the data frame.
    #     df['year'] = year                                             # Add a 'year' column.
    #     df.set_index('name', inplace=True)                            # Make 'name' the data frame's index
    #
    #     for stat in df_columns[5:]:
    #         df[stat].fillna(0, inplace=True)  # Fill missing stats with 0.
    #
    #     if fantasy:
    #         df = self.__get_fantasy_points(df, year)  # Create fantasy_points column in df.
    #
    #     return df
    #
    # def __get_fantasy_points(self, df, year):
    #     """
    #     Insert 'fumbles_lost', 'two_pt_conversions', 'return_yards', 'return_td', and 'fantasy_points' columns into df.
    #     Calculate fantasy points based on a fantasy settings dictionary. Drop the separate punt return and kick return
    #     columns and replace with consolidated return columns.
    #
    #     :param df: Data frame to be modified.
    #     :param year: Current season.
    #
    #     :return: New data frame with fantasy point calculation.
    #     """
    #     for table_name in ['fumble', 'kick return', 'punt return', 'conversion']:
    #         stat_df = fbdb.get_df(year, table_name)  # Scrape table from footballdb.com and make a data frame.
    #         df = df.join(stat_df, how='left')        # Join stat data frame to main data frame.
    #
    #     # Replace NaN data with 0, otherwise fantasy calculations with have NaN results for players with missing data.
    #     stat_list = ['fumbles_lost', 'two_pt_conversions', 'kick_return_yards', 'kick_return_td',
    #                  'punt_return_yards', 'punt_return_td']
    #     [df[column].fillna(0, inplace=True) for column in stat_list]
    #
    #     df['return_yards'] = df['kick_return_yards'] + df['punt_return_yards']  # Consolidate punt/kick return yards.
    #     df['return_td'] = df['kick_return_td'] + df['punt_return_td']           # Consolidate punt/kick return TDs.
    #
    #     # Drop individual punt/kick return yards and touchdown stats.
    #     dropped_stats = ['kick_return_yards', 'punt_return_yards', 'kick_return_td', 'punt_return_td']
    #     [df.drop(stat, axis=1, inplace=True) for stat in dropped_stats]
    #
    #     # Insert the fantasy_points column and calculate each player's fantasy point total.
    #     df['fantasy_points'] = 0
    #     for stat, value in self._fantasy_settings_dict.items():
    #         if stat in df.columns:
    #             df['fantasy_points'] += df[stat] * value
    #
    #     return df


if __name__ == '__main__':
    # Usage example. Scrapes the following table: https://www.pro-football-reference.com/years/2017/rushing.htm
    fb_ref = ProFbRefScraper()

    # Use custom fantasy settings.
    # Changes: 'receptions': 0 -> 'receptions': 1.
    # new_fantasy_settings_dict = {
    #     'rush_td': 6,
    #     'pass_yards': 1 / 25,  # 25 yards = 1 point
    #     'pass_td': 4,
    #     'rec_td': 6,
    #     'interceptions': -1,
    #     'receptions': 1,
    #     'two_pt_conversions': 2,
    #     'fumbles_lost': -2,
    #     'offensive_fumble_return_td': 6,
    #     'rec_yards': 1 / 10,  # 10 yards = 1 point
    #     'return_yards': 1 / 25,  # 25 yards = 1 point
    #     'return_td': 6,
    #     'rush_yards': 1 / 10  # 10 yards = 1 point
    # }
    #
    # fb_ref.fantasy_settings = new_fantasy_settings_dict
    # rush_rec_df = fb_ref.get_rushing_receiving_data(2017, fantasy=True)
    # print(rush_rec_df)
    # rush_rec_df.to_csv('oop_results.csv')

    rush_rec_df = fb_ref.get_data(start_year=2017, end_year=2015, table_type='rushing')

    rush_rec_df.to_csv('rush_rec.csv')
