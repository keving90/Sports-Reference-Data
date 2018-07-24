#!/usr/bin/env python3

"""
This module contains a FbDbScraper class used to scrape NFL data from www.footballdb.com for a given season. It then
places the data into a Pandas data frame. Users can scrape a table for a single stat category. They can also scrape
comprehensive data for several stat categories. This will include a calculation of each player's fantasy point total
for the season based on provided fantasy settings. Multiple seasons of data can be scraped at once.

Note: This module was built using Python 3.6.1, so dictionaries are ordered.
"""

import requests
import bs4
import pandas as pd
from player import Player


class FbDbScraper(object):
    """

    Scrapes data from www.footballdb.com and places it into a Pandas data frame. It can scrape an individual table
    using the get_specific_df() method. It can also scrape several tables, join them together, and calculate each
    player's fantasy point total using the get_fantasy_df() method. Each method returns a data frame. The data frames
    are created using the __dict__ form of Player objects.

    The methods will scrape data from different tables based on a table_type variable.

    Valid table_type values include:

    'all_purpose': All purpose yardage data. Has data for all NFL players.
    'passing': Passing data.
    'rushing': Rushing data.
    'receiving': Receiving data.
    'scoring': Scoring data.
    'fumbles': Fumble data.
    'kick_returns': Kick return data.
    'punt_returns': Punt return data.
    'kicking': Field goal and point after touchdown data.
    'fantasy_offense': QB, RB, WR, and TE data with www.footballdb.com's custom fantasy settings data.

    Attributes:
        _tables_dict (dict): Dictionary whose keys are the type of table to scrape from. The value is
            another dictionary. The nested dictionary contains keys whose values are used for building the URL to the
            table. Another key within the nested dict has a dict as a value to store the column names and their data
            type. The values for the 'fantasy_offense' key has a unique layout because its URL is different from other
            tables.

            Example:
                ex = {
                    'table_type': {
                        'mode_id_for_table_type': 'url_letter_id',
                        'column_to_sort_on': 'url_column_name',
                        'columns_to_grab_from_table': {
                            'column_name': data_type_of_column
                        }
                    }
                }

        _fantasy_settings_dict (dict): Dictionary stores the name of each fantasy stat as keys and their point value
        as values. A property allows setting custom fantasy settings using a valid dictionary. Originally represents a
        standard Yahoo! 0PPR league.

            Users can calculate fantasy points with a custom fantasy settings dictionary:

            fb_db_obj.fantasy_settings = a_dictionary

            A valid dictionary must be used.

            Example of valid dict (these are the default fantasy settings):

                default_settings = {
                    'pass_yards': 1 / 25,  # 25 yards = 1 point
                    'pass_td': 4,
                    'interceptions': -1,
                    'rush_yards': 1 / 10,  # 10 yards = 1 point
                    'rush_td': 6,
                    'rec_yards': 1 / 10,  # 10 yards = 1 point
                    'receptions': 0,
                    'rec_td': 6,
                    'two_pt_conversions': 2,
                    'fumbles_lost': -2,
                    'offensive_fumble_return_td': 6,
                    'return_yards': 1 / 25,  # 25 yards = 1 point
                    'return_td': 6,
                    'pat_made': 1,
                    '0-19_made': 3,
                    '20-29_made': 3,
                    '30-39_made': 3,
                    '40-49_made': 4,
                    '50_plus_made': 5,
                }

        _valid_fantasy_keys (dict_keys): Dictionary view object records initial keys in _fantasy_settings_dict to check
            for invalid keys when setting a custom fantasy settings dictionary.

    """
    def __init__(self):
        """Initialize FbDbScraper object."""
        self._tables_dict = {
            'all_purpose': {
                'mode': 'A',
                'sort': 'apyds',
                'all_columns': {
                    'name': str,
                    'player_url': str,
                    'team': str,
                    'position': str,
                    'all_purpose_yards': int,
                    'rush_yards': int,
                    'rec_yards': int,
                    'kick_return_yards': int,
                    'punt_return_yards': int,
                    'int_return_yards': int,
                    'fum_return_yards': int
                }
            },
            'passing': {
                'mode': 'P',
                'sort': 'passyds',
                'all_columns': {
                    'name': str,
                    'player_url': str,
                    'team': str,
                    'pass_attempts': int,
                    'pass_completions': int,
                    'completion_pct': float,
                    'pass_yards': int,
                    'yards_per_pass_attempt': float,
                    'pass_td': int,
                    'pass_td_pct': float,
                    'interceptions': int,
                    'int_pct': float,
                    'longest_pass': str,
                    'sacked': int,
                    'sack_yards_lost': int,
                    'qb_rating': float
                }
            },
            'rushing': {
                'mode': 'R',
                'sort': 'rushyds',
                'all_columns': {
                    'name': str,
                    'player_url': str,
                    'team': str,
                    'games_played': int,
                    'rush_attempts': int,
                    'rush_yards': int,
                    'yards_per_rush': float,
                    'rush_yards_per_game': float,
                    'longest_rush': str,
                    'rush_td': int,
                    'rush_first_downs': int
                }
            },
            'receiving': {
                'mode': 'C',
                'sort': 'recyds',
                'all_columns': {
                    'name': str,
                    'player_url': str,
                    'team': str,
                    'games_played': int,
                    'receptions': int,
                    'receiving_yards': int,
                    'yards_per_reception': float,
                    'rec_yards_per_game': float,
                    'longest_reception': str,
                    'rec_td': int,
                    'rec_first_downs': int,
                    'targets': int,
                    'yards_after_catch': int
                }
            },
            'scoring': {
                'mode': 'S',
                'sort': 'totconv',
                'all_columns': {
                    'name': str,
                    'player_url': str,
                    'team': str,
                    'points': int,
                    'total_td': int,
                    'rush_td': int,
                    'rec_td': int,
                    'kick_return_td': int,
                    'punt_return_td': int,
                    'int_return_td': int,
                    'fumble_return_td': int,
                    'blocked_fg_td': int,
                    'blocked_punt_td': int,
                    'missed_fg_td': int,
                    'pat': str,
                    'field_goals': str,
                    'rush_rec_2pt': int,
                    'safeties': int
                }
            },
            'fumbles': {
                'mode': 'M',
                'sort': 'fumlost',
                'all_columns': {
                    'name': str,
                    'player_url': str,
                    'team': str,
                    'fumbles': int,
                    'fumbles_lost': int,
                    'forced_fumbles': int,
                    'own_fum_recovery': int,
                    'opp_fumble_recovery': int,
                    'total_recoveries': int,
                    'fumble_return_yards': int,
                    'fumble_return_td': int
                }
            },
            'kick_returns': {
                'mode': 'KR',
                'sort': 'kryds',
                'all_columns': {
                    'name': str,
                    'player_url': str,
                    'team': str,
                    'kick_returns': int,
                    'kr_yards': int,
                    'kr_avg': float,
                    'kr_fair_catches': int,
                    'longest_kr': str,
                    'kr_td': int
                }
            },
            'punt_returns': {
                'mode': 'PR',
                'sort': 'pryds',
                'all_columns': {
                    'name': str,
                    'player_url': str,
                    'team': str,
                    'punt_returns': int,
                    'pr_yards': int,
                    'pr_avg': float,
                    'pr_fair_catches': int,
                    'longest_pr': str,
                    'pr_td': int
                }
            },
            'kicking': {
                'mode': 'K',
                'sort': 'kickpts',
                'all_columns': {
                    'name': str,
                    'player_url': str,
                    'team': str,
                    'pat': str,
                    'fg_pct': str,
                    '0-19': str,
                    '20-29': str,
                    '30-39': str,
                    '40-49': str,
                    '50_plus': str,
                    'longest_fg': int,
                    'fg_points': int
                }
            },
            'fantasy_offense': {
                'url1': 'https://www.footballdb.com/fantasy-football/index.html?pos=QB%2CRB%2CWR%2CTE&yr=',
                'url2': '&wk=all&rules=1&sort=passconv',
                'all_columns': {
                    'name': str,
                    'player_url': str,
                    'bye': int,
                    'fantasy_points': float,
                    'pass_attempts': int,
                    'pass_completions': int,
                    'pass_yards': int,
                    'pass_td': int,
                    'interceptions': int,
                    'pass_2pt': int,
                    'rush_attempts': int,
                    'rush_yards': int,
                    'rush_td': int,
                    'rush_2pt': int,
                    'receptions': int,
                    'receiving_yards': int,
                    'rec_td': int,
                    'rec_2pt': int,
                    'fumbles_lost': int,
                    'fumble_return_td': int
                }
            }
        }

        # Default settings for calculating fantasy points in self.get_fantasy_df().
        # Can be modified with fantasy_settings property.
        self._fantasy_settings_dict = {
            'pass_yards': 1 / 25,  # 25 yards = 1 point
            'pass_td': 4,
            'interceptions': -1,
            'rush_yards': 1 / 10,  # 10 yards = 1 point
            'rush_td': 6,
            'rec_yards': 1 / 10,  # 10 yards = 1 point
            'receptions': 0,
            'rec_td': 6,
            'two_pt_conversions': 2,
            'fumbles_lost': -2,
            'offensive_fumble_return_td': 6,
            'return_yards': 1 / 25,  # 25 yards = 1 point
            'return_td': 6,
            'pat_made': 1,
            '0-19_made': 3,
            '20-29_made': 3,
            '30-39_made': 3,
            '40-49_made': 4,
            '50_plus_made': 5,
        }

        # Helps check for invalid keys when using a custom fantasy settings dictionary.
        self._valid_fantasy_keys = self._fantasy_settings_dict.keys()

    @property
    def fantasy_settings(self):
        """
        getter: Return the current fantasy settings dictionary.

        setter: Set _fantasy_settings_dict to a custom fantasy settings dictionary.
        """
        return self._fantasy_settings_dict

    @fantasy_settings.setter
    def fantasy_settings(self, settings_dict):
        """_fantasy_settings_dict can only be set to a dictionary with the same keys as original attribute."""
        # Fantasy settings must be a dictionary.
        if not isinstance(settings_dict, dict):
            raise ValueError("Fantasy settings must be a dictionary.")

        # Check for valid number of keys in new fantasy settings dictionary.
        dict_len = len(self._valid_fantasy_keys)
        message = "keys in new fantasy settings dict. " + str(dict_len) + " keys required."
        if len(settings_dict) > dict_len:
            raise KeyError("Too many " + message)
        elif len(settings_dict) < dict_len:
            raise KeyError("Too few " + message)

        # Check for valid keys and value types in new fantasy settings dictionary.
        for key, value in settings_dict.items():
            if key not in self._valid_fantasy_keys:
                raise KeyError("Invalid key in new fantasy settings dict. "
                               + "Valid keys include: " + str(list(self._valid_fantasy_keys)))
            if type(value) not in [float, int]:
                raise ValueError("Invalid value in new fantasy settings dict. Must be type int or float.")

        self._fantasy_settings_dict = settings_dict

    def get_fantasy_df(self, start_year, end_year):
        """
        Returns a large data frame containing comprehensive player stats and their fantasy points total. Filters data
        frame so only quarterbacks, wide receivers, running backs, tight ends, and kickers remain. A single season is
        scraped if start_year == end_year. It does not matter which year is start_year or end_year. This will only
        affect the order the data is scraped.

        :param start_year: Year to start scraping from.
        :param end_year: Final year to scrape from.

        :return: Data frame containing all players and their fantasy points total for the season.
        """
        # Loop through dictionary keys, scraping a table and joining it to the "main data frame" each iteration. The
        # dictionary is ordered, so the 'all_purpose' key (for the All Purpose Yardage table) will always come first.
        # The 'all_purpose' data frame is used as the "main data frame" because it has the highest number of NFL
        # players.
        for table in self._tables_dict.keys():
            # Scrape a given table from www.footballdb.com and create a data frame.
            df = self.get_specific_df(start_year, end_year, table)

            if table == 'all_purpose':
                # The 'all_purpose' table will act as the "main data frame" since it has players of all positions.
                main_df = df
            else:
                # All other data frames will be joined to main_df.
                # The only columns in df we're interested in are the ones not in main_df.
                relevant_cols = [col for col in df.columns if col not in main_df.columns]
                df = df[relevant_cols]

                # Join main_df and df using the unique player_url index.
                main_df = main_df.join(df, how='left')

        # Rearrange column order and calculate each player's fantasy point total.
        main_df = self._prepare_for_fantasy_calc(main_df)
        main_df = self._calculate_fantasy_points(main_df)

        # Only interested in offense positions.
        main_df = main_df[(main_df['position'] == 'QB')
                          | (main_df['position'] == 'WR')
                          | (main_df['position'] == 'RB')
                          | (main_df['position'] == 'TE')
                          | (main_df['position'] == 'K')]

        return main_df

    def get_specific_df(self, start_year, end_year, table_type):
        """
        Gets a data frame of one or more seasons of data for a given table_type. A single season is scraped if
        start_year == end_year. It does not matter which year is start_year or end_year. This will only affect the
        order the data is scraped.

        :param start_year: Year to start scraping from.
        :param end_year: Final year to scrape from.
        :param table_type: String representing the type of table to be scraped.

        :return: Big data frame of several data frames concatenated together.
        """
        # Get year range for iteration.
        year_range = self._get_year_range(start_year, end_year)

        # Get a data frame for each season.
        df_list = [self._get_season(year, table_type) for year in year_range]

        # Concatenate all seasons into one big data frame.
        big_df = pd.concat(df_list)

        return big_df

    def _get_season(self, year, table_type):
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
        url = self._make_url(year, table_type)
        player_list = self._get_player_result_set(url)
        player_dicts = self._get_player_stats(player_list, table_type)
        df = self._make_df(year, player_dicts, table_type)

        # The 'scoring' and 'kicking' tables have field goal stats as a 'made/attempts' string.
        # Split these stats into two integer columns.
        if table_type in ['scoring', 'kicking']:
            df = self._handle_field_goals(df, table_type)

        return df

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
        Creates a URL string used to send a GET request to www.footballdb.com to scrape a table.

        :param year: Season year needed to go to the correct season of data.
        :param table_type: Indicates which table to scrape from.

        :return: URL string used to send GET request.
        """
        # Build the URL.
        # The 'fantasy_offense' table has a different URL than all other tables.
        if table_type == 'fantasy_offense':
            url = (self._tables_dict[table_type]['url1']
                   + str(year)
                   + self._tables_dict[table_type]['url2'])
        else:
            url = ('https://www.footballdb.com/stats/stats.html?lg=NFL&yr='
                   + str(year)
                   + '&type=reg&mode='
                   + self._tables_dict[table_type]['mode']
                   + '&conf=&limit=all&sort='
                   + self._tables_dict[table_type]['sort'])

        return url

    def _get_player_result_set(self, url):
        """
        Sends a GET request and use BeautifulSoup4 to scrape a ResultSet from a www.footballdb.com table.

        :param url: String URL built by self._make_url().

        :return: A list - BeautifulSoup4 ResultSet of player data.
        """
        # Required for successful request. 403 error when not provided.
        # Taken from: https://stackoverflow.com/questions/38489386/python-requests-403-forbidden
        req_header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36'
                                    + '(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

        # Send a GET request to gather the data.
        r = requests.get(url, headers=req_header)
        r.raise_for_status()

        # Create a BeautifulSoup object.
        soup = bs4.BeautifulSoup(r.text, 'lxml')

        # Find the first table with tag 'table' and class 'statistics scrollable'
        table = soup.find('table', class_='statistics scrollable')

        # tbody is the table's body
        # Get the body of the table
        body = table.find('tbody')

        # tr refers to a table row
        # Each row in player_list has data for a single player.
        player_list = body.find_all('tr')

        return player_list

    def _get_player_stats(self, player_list, table_type):
        """
        Iterates through a BeautifulSoup4 ResultSet to get a player stat data. Uses a list of player stats to create a
        Player object for each player. The object's attributes are based on the table_type.

        :param player_list: List of BeautifulSoup4 ResultSet player data.
        :param table_type: String used to access self._tables_dict key data for creating Player objects.

        :return: List of player_object.__dict__'s for building a data frame.
        """
        # This list holds a dictionary of each object's attributes.
        # Each dictionary is made from the object's __dict__ attribute.
        list_of_player_dicts = []

        # Get each player's stats and create a Player object.
        # Create a list containing each player object's __dict__.
        for player in player_list:
            # The <td> tag defines a standard cell in an HTML table.
            # Get a list of cells. This raw web page data represents one player.
            raw_stat_list = player.find_all('td')

            # player_stats = self.__get_player_stats(raw_stat_list)
            name = raw_stat_list[0].find('span', class_='hidden-xs').text

            # Get href, which specifies the URL of the page the link goes to when you click on the player's name
            # in the footballdb.com table.
            href = raw_stat_list[0].find_all('a', href=True)

            # Player's unique URL. Will be used as a primary key to handle players with the same name.
            player_url = href[0]['href']  # Get the URL string

            stats_no_name = [stat.text for stat in raw_stat_list[1:]]
            player_stats = [name, player_url] + stats_no_name

            # Create a Player object and append the __dict__ attribute to a list.
            # This list is used for the data in our data frame.
            obj = Player(player_stats, self._tables_dict[table_type]['all_columns'])
            list_of_player_dicts.append(obj.__dict__)

        return list_of_player_dicts

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

    def _handle_field_goals(self, df, table_type):
        """
        Handles a kicker's field goal stats. Splits 'made/attempts' string, creates separate made and attempts integer
        columns, and drops original columns. Handles point after touchdown and field goals of all ranges in 'scoring'
        and 'kicking' tables.

        Example 'kicking' table whose PAT and FG columns would be modified (similar for 'scoring' table):
        https://www.footballdb.com/stats/stats.html?mode=K&yr=2017&lg=NFL

        :param df: Data frame to be modified.
        :param table_type: Type of table to be modified. Columns to modify vary based on table type.

        :return: Modified data frame.
        """
        # Handle different columns based on table type.
        if table_type == 'scoring':
            kicking_cols = ['pat', 'field_goals']
        elif table_type == 'kicking':
            kicking_cols = ['fg_pct', 'pat', '0-19', '20-29', '30-39', '40-49', '50_plus']

        # Split 'made/attempts' string column into two different integer columns.
        for col in kicking_cols:
            # Rename new integer columns based on stat.
            if col == 'fg_pct':
                col_names = ('fg_made', 'fg_att')
            else:
                col_names = (col + '_made', col + '_att')

            # Add new integer columns.
            df[col_names[0]] = df[col].apply(lambda x: int(x.split('/')[0]))
            df[col_names[1]] = df[col].apply(lambda x: int(x.split('/')[1]))

        # Drop the original 'made/attempts' string columns.
        [df.drop(col, axis=1, inplace=True) for col in kicking_cols]

        return df

    def _prepare_for_fantasy_calc(self, df):
        """
        Grabs only the relevant columns in df and rearranges their order. Replaces all numpy.NaN values with 0. Inserts
        'return_yards', 'return_td', and 'two_pt_conversions' columns for fantasy points calculation.

        :param df: Data frame to be prepared.

        :return: A data frame prepared for fantasy points calculation.
        """
        # Replace all numpy.NaN values with 0.
        [df[column].fillna(0, inplace=True) for column in df[3:]]

        # Add 'return_yards' and 'return_td' columns for fantasy points calculation.
        df['return_yards'] = df['punt_return_yards'] + df['kick_return_yards']
        df['return_td'] = df['kick_return_td'] + df['punt_return_td']
        df['two_pt_conversions'] = df['rush_rec_2pt'] + df['pass_2pt']

        # Desired columns and their order.
        col_order = ['name', 'team', 'position', 'year', 'rush_attempts', 'rush_yards', 'yards_per_rush',
                     'rush_td', 'targets', 'receptions', 'rec_yards', 'rec_td', 'pass_attempts', 'pass_completions',
                     'completion_pct', 'pass_yards', 'pass_td', 'interceptions', 'sacked', 'return_yards', 'return_td',
                     'two_pt_conversions', 'fumbles_lost', 'pat_made', 'pat_att', '0-19_made', '0-19_att',
                     '20-29_made', '20-29_att', '30-39_made', '30-39_att', '40-49_made', '40-49_att', '50_plus_made',
                     '50_plus_att']

        # Reorder the columns, and drop the unnecessary ones.
        # Need to create a deep copy in order to prevent a SettingWithCopy warning.
        reordered_df = df[col_order].copy()

        return reordered_df

    def _calculate_fantasy_points(self, df):
        """
        Inserts the fantasy_points column and calculates each player's fantasy point total.

        :param df: Data frame to have fantasy_points column inserted into.

        :return: A data frame with a fantasy_points column.
        """
        # Insert the fantasy_points column.
        df['fantasy_points'] = 0

        # Calculate each player's fantasy point total.
        for stat, value in self._fantasy_settings_dict.items():
            if stat in df.columns:
                # Round to two decimal places because of float arithmetic.
                df['fantasy_points'] += round(df[stat] * value, 2)
                # df['fantasy_points'] += df[stat] * value

        # df['fantasy_points'].apply(lambda x: round(x, 2))

        return df


if __name__ == '__main__':
    # Usage example.

    # Create object.
    fb_db = FbDbScraper()

    # Create custom fantasy settings dictionary.
    custom_settings = {
        'pass_yards': 1 / 25,
        'pass_td': 4,
        'interceptions': -1,
        'rush_yards': 1 / 10,
        'rush_td': 6,
        'rec_yards': 1 / 10,
        'receptions': 1,  # receptions: 0 -> receptions: 1
        'rec_td': 6,
        'two_pt_conversions': 2,
        'fumbles_lost': -2,
        'offensive_fumble_return_td': 6,
        'return_yards': 1 / 25,
        'return_td': 6,
        'pat_made': 1,
        '0-19_made': 3,
        '20-29_made': 3,
        '30-39_made': 3,
        '40-49_made': 4,
        '50_plus_made': 5
    }

    # Use custom fantasy settings instead of default settings (optional).
    fb_db.fantasy_settings = custom_settings

    # Scrape data for the 2017 NFL season.
    fantasy_df = fb_db.get_fantasy_df(start_year=2017, end_year=2017)

    print(fantasy_df)

    fantasy_df.to_csv('fbdb_fantasy.csv')

"""
Sample output:

                                                           name team position  \
player_url                                                                      
/players/todd-gurley-gurleto022017                  Todd Gurley   LA       RB   
/players/leveon-bell-bellle022017                  Le'Veon Bell  PIT       RB   
/players/alvin-kamara-kamaral012017                Alvin Kamara   NO       RB   
/players/tyler-lockett-lockety012017              Tyler Lockett  SEA       WR   
/players/kareem-hunt-huntka012017                   Kareem Hunt   KC       RB   
/players/dion-lewis-lewisdi012017                    Dion Lewis   NE       RB   
/players/antonio-brown-brownan052017              Antonio Brown  PIT       WR   
/players/lesean-mccoy-mccoyle022017                LeSean McCoy  BUF       RB   
/players/melvin-gordon-gordome012017              Melvin Gordon  LAC       RB   
/players/tarik-cohen-cohenta012017                  Tarik Cohen  CHI       RB   
/players/mark-ingram-ingrama022017                  Mark Ingram   NO       RB   
/players/keenan-allen-allenke032017                Keenan Allen  LAC       WR   
/players/julio-jones-jonesju052017                  Julio Jones  ATL       WR   
/players/tyreek-hill-hillty022017                   Tyreek Hill   KC       WR   
/players/pharoh-cooper-coopeph012017              Pharoh Cooper   LA       WR   
/players/deandre-hopkins-hopkide012017          DeAndre Hopkins  HOU       WR   
/players/leonard-fournette-fournle012017      Leonard Fournette  JAX       RB   
/players/christian-mccaffrey-mccafch012017  Christian McCaffrey  CAR       RB   
/players/jerick-mckinnon-mckinje022017          Jerick McKinnon  MIN       RB   
/players/carlos-hyde-hydeca012017                   Carlos Hyde   SF       RB   
/players/adam-thielen-thielad012017                Adam Thielen  MIN       WR   
/players/ezekiel-elliott-ellioez012017          Ezekiel Elliott  DAL       RB   
/players/jordan-howard-howarjo022017              Jordan Howard  CHI       RB   
/players/michael-thomas-thomami052017            Michael Thomas   NO       WR   
/players/cj-anderson-andercj012017                C.J. Anderson  DEN       RB   
/players/lamar-miller-millela032017                Lamar Miller  HOU       RB   
/players/alex-collins-collial012017                Alex Collins  BAL       RB   
/players/frank-gore-gorefr012017                     Frank Gore  IND       RB   
/players/devonta-freeman-freemde012017          Devonta Freeman  ATL       RB   
/players/juju-smithschuster-smithju032017   JuJu Smith-Schuster  PIT       WR   
...                                                         ...  ...      ...   
/players/shane-smith-smithsh102017                  Shane Smith  NYG       RB   
/players/cj-spiller-spillcj022017                  C.J. Spiller   KC       RB   
/players/caleb-sturgis-sturgca012017              Caleb Sturgis  PHI        K   
/players/ryan-succop-succory012017                  Ryan Succop  TEN        K   
/players/giorgio-tavecchio-tavecgi012017      Giorgio Tavecchio  OAK        K   
/players/justin-tucker-tuckeju012017              Justin Tucker  BAL        K   
/players/jason-vander-laan-vandeja032017      Jason Vander Laan  IND       TE   
/players/adam-vinatieri-vinatad012017            Adam Vinatieri  IND        K   
/players/blair-walsh-walshbl012017                  Blair Walsh  SEA        K   
/players/isaac-whitney-whitnis012017              Isaac Whitney  OAK       WR   
/players/marquez-williams-willima262017        Marquez Williams  CLE       RB   
/players/greg-zuerlein-zuerlgr012017              Greg Zuerlein   LA        K   
/players/austin-davis-davisau012017                Austin Davis  SEA       QB   
/players/cody-kessler-kesslco012017                Cody Kessler  CLE       QB   
/players/derek-anderson-anderde012017            Derek Anderson  CAR       QB   
/players/chase-daniel-daniech012017                Chase Daniel   NO       QB   
/players/bronson-hill-hillbr022017                 Bronson Hill  ARI       RB   
/players/sean-mannion-mannise022017                Sean Mannion   LA       QB   
/players/darren-mcfadden-mcfadda012017          Darren McFadden  DAL       RB   
/players/sam-bradford-bradfsa012017                Sam Bradford  MIN       QB   
/players/teddy-bridgewater-bridgte012017      Teddy Bridgewater  MIN       QB   
/players/ryan-mallett-mallery012017                Ryan Mallett  BAL       QB   
/players/tyler-bray-brayty012017                     Tyler Bray   KC       QB   
/players/kellen-clemens-clemeke012017            Kellen Clemens  LAC       QB   
/players/nick-foles-folesni012017                    Nick Foles  PHI       QB   
/players/chad-henne-hennech012017                    Chad Henne  JAX       QB   
/players/brian-hoyer-hoyerbr012017                  Brian Hoyer   NE       QB   
/players/philip-rivers-riverph012017              Philip Rivers  LAC       QB   
/players/krishawn-hogan-hogankr012017            Krishawn Hogan  IND       WR   
/players/landry-jones-jonesla062017                Landry Jones  PIT       QB   

                                            year  rush_attempts  rush_yards  \
player_url                                                                    
/players/todd-gurley-gurleto022017          2017          279.0        1305   
/players/leveon-bell-bellle022017           2017          321.0        1291   
/players/alvin-kamara-kamaral012017         2017          120.0         728   
/players/tyler-lockett-lockety012017        2017           10.0          58   
/players/kareem-hunt-huntka012017           2017          272.0        1327   
/players/dion-lewis-lewisdi012017           2017          180.0         896   
/players/antonio-brown-brownan052017        2017            0.0           0   
/players/lesean-mccoy-mccoyle022017         2017          287.0        1138   
/players/melvin-gordon-gordome012017        2017          284.0        1105   
/players/tarik-cohen-cohenta012017          2017           87.0         370   
/players/mark-ingram-ingrama022017          2017          230.0        1124   
/players/keenan-allen-allenke032017         2017            2.0           9   
/players/julio-jones-jonesju052017          2017            1.0          15   
/players/tyreek-hill-hillty022017           2017           17.0          59   
/players/pharoh-cooper-coopeph012017        2017            1.0           6   
/players/deandre-hopkins-hopkide012017      2017            0.0           0   
/players/leonard-fournette-fournle012017    2017          268.0        1040   
/players/christian-mccaffrey-mccafch012017  2017          117.0         435   
/players/jerick-mckinnon-mckinje022017      2017          150.0         570   
/players/carlos-hyde-hydeca012017           2017          240.0         938   
/players/adam-thielen-thielad012017         2017            1.0          11   
/players/ezekiel-elliott-ellioez012017      2017          242.0         983   
/players/jordan-howard-howarjo022017        2017          276.0        1122   
/players/michael-thomas-thomami052017       2017            0.0           0   
/players/cj-anderson-andercj012017          2017          245.0        1007   
/players/lamar-miller-millela032017         2017          238.0         888   
/players/alex-collins-collial012017         2017          212.0         973   
/players/frank-gore-gorefr012017            2017          261.0         961   
/players/devonta-freeman-freemde012017      2017          196.0         865   
/players/juju-smithschuster-smithju032017   2017            0.0           0   
...                                          ...            ...         ...   
/players/shane-smith-smithsh102017          2017            0.0           0   
/players/cj-spiller-spillcj022017           2017            2.0           0   
/players/caleb-sturgis-sturgca012017        2017            0.0           0   
/players/ryan-succop-succory012017          2017            0.0           0   
/players/giorgio-tavecchio-tavecgi012017    2017            0.0           0   
/players/justin-tucker-tuckeju012017        2017            0.0           0   
/players/jason-vander-laan-vandeja032017    2017            0.0           0   
/players/adam-vinatieri-vinatad012017       2017            0.0           0   
/players/blair-walsh-walshbl012017          2017            0.0           0   
/players/isaac-whitney-whitnis012017        2017            0.0           0   
/players/marquez-williams-willima262017     2017            0.0           0   
/players/greg-zuerlein-zuerlgr012017        2017            0.0           0   
/players/austin-davis-davisau012017         2017            1.0          -1   
/players/cody-kessler-kesslco012017         2017            1.0          -1   
/players/derek-anderson-anderde012017       2017            2.0          -2   
/players/chase-daniel-daniech012017         2017            3.0          -2   
/players/bronson-hill-hillbr022017          2017            1.0          -2   
/players/sean-mannion-mannise022017         2017            9.0          -2   
/players/darren-mcfadden-mcfadda012017      2017            1.0          -2   
/players/sam-bradford-bradfsa012017         2017            2.0          -3   
/players/teddy-bridgewater-bridgte012017    2017            3.0          -3   
/players/ryan-mallett-mallery012017         2017            4.0          -3   
/players/tyler-bray-brayty012017            2017            1.0           0   
/players/kellen-clemens-clemeke012017       2017            5.0          -5   
/players/nick-foles-folesni012017           2017           11.0           3   
/players/chad-henne-hennech012017           2017            5.0          -5   
/players/brian-hoyer-hoyerbr012017          2017            9.0           4   
/players/philip-rivers-riverph012017        2017           18.0          -2   
/players/krishawn-hogan-hogankr012017       2017            0.0           0   
/players/landry-jones-jonesla062017         2017            8.0         -10   

                                            yards_per_rush  rush_td  targets  \
player_url                                                                     
/players/todd-gurley-gurleto022017                    4.68     13.0     87.0   
/players/leveon-bell-bellle022017                     4.02      9.0    106.0   
/players/alvin-kamara-kamaral012017                   6.07      8.0    100.0   
/players/tyler-lockett-lockety012017                  5.80      0.0     71.0   
/players/kareem-hunt-huntka012017                     4.88      8.0     63.0   
/players/dion-lewis-lewisdi012017                     4.98      6.0     35.0   
/players/antonio-brown-brownan052017                  0.00      0.0    163.0   
/players/lesean-mccoy-mccoyle022017                   3.97      6.0     77.0   
/players/melvin-gordon-gordome012017                  3.89      8.0     83.0   
/players/tarik-cohen-cohenta012017                    4.25      2.0     71.0   
/players/mark-ingram-ingrama022017                    4.89     12.0     71.0   
/players/keenan-allen-allenke032017                   4.50      0.0    159.0   
/players/julio-jones-jonesju052017                   15.00      0.0    148.0   
/players/tyreek-hill-hillty022017                     3.47      0.0    105.0   
/players/pharoh-cooper-coopeph012017                  6.00      0.0     19.0   
/players/deandre-hopkins-hopkide012017                0.00      0.0    174.0   
/players/leonard-fournette-fournle012017              3.88      9.0     48.0   
/players/christian-mccaffrey-mccafch012017            3.72      2.0    113.0   
/players/jerick-mckinnon-mckinje022017                3.80      3.0     68.0   
/players/carlos-hyde-hydeca012017                     3.91      8.0     88.0   
/players/adam-thielen-thielad012017                  11.00      0.0    142.0   
/players/ezekiel-elliott-ellioez012017                4.06      7.0     38.0   
/players/jordan-howard-howarjo022017                  4.07      9.0     32.0   
/players/michael-thomas-thomami052017                 0.00      0.0    149.0   
/players/cj-anderson-andercj012017                    4.11      3.0     40.0   
/players/lamar-miller-millela032017                   3.73      3.0     45.0   
/players/alex-collins-collial012017                   4.59      6.0     36.0   
/players/frank-gore-gorefr012017                      3.68      3.0     38.0   
/players/devonta-freeman-freemde012017                4.41      7.0     47.0   
/players/juju-smithschuster-smithju032017             0.00      0.0     79.0   
...                                                    ...      ...      ...   
/players/shane-smith-smithsh102017                    0.00      0.0      0.0   
/players/cj-spiller-spillcj022017                     0.00      0.0      2.0   
/players/caleb-sturgis-sturgca012017                  0.00      0.0      0.0   
/players/ryan-succop-succory012017                    0.00      0.0      0.0   
/players/giorgio-tavecchio-tavecgi012017              0.00      0.0      0.0   
/players/justin-tucker-tuckeju012017                  0.00      0.0      0.0   
/players/jason-vander-laan-vandeja032017              0.00      0.0      0.0   
/players/adam-vinatieri-vinatad012017                 0.00      0.0      0.0   
/players/blair-walsh-walshbl012017                    0.00      0.0      0.0   
/players/isaac-whitney-whitnis012017                  0.00      0.0      1.0   
/players/marquez-williams-willima262017               0.00      0.0      1.0   
/players/greg-zuerlein-zuerlgr012017                  0.00      0.0      0.0   
/players/austin-davis-davisau012017                  -1.00      0.0      0.0   
/players/cody-kessler-kesslco012017                  -1.00      0.0      0.0   
/players/derek-anderson-anderde012017                -1.00      0.0      0.0   
/players/chase-daniel-daniech012017                  -0.67      0.0      0.0   
/players/bronson-hill-hillbr022017                   -2.00      0.0      0.0   
/players/sean-mannion-mannise022017                  -0.22      0.0      0.0   
/players/darren-mcfadden-mcfadda012017               -2.00      0.0      0.0   
/players/sam-bradford-bradfsa012017                  -1.50      0.0      0.0   
/players/teddy-bridgewater-bridgte012017             -1.00      0.0      0.0   
/players/ryan-mallett-mallery012017                  -0.75      0.0      0.0   
/players/tyler-bray-brayty012017                      0.00      0.0      0.0   
/players/kellen-clemens-clemeke012017                -1.00      0.0      0.0   
/players/nick-foles-folesni012017                     0.27      0.0      0.0   
/players/chad-henne-hennech012017                    -1.00      0.0      0.0   
/players/brian-hoyer-hoyerbr012017                    0.44      1.0      0.0   
/players/philip-rivers-riverph012017                 -0.11      0.0      0.0   
/players/krishawn-hogan-hogankr012017                 0.00      0.0      0.0   
/players/landry-jones-jonesla062017                  -1.25      0.0      0.0   

                                            receptions       ...        \
player_url                                                   ...         
/players/todd-gurley-gurleto022017                64.0       ...         
/players/leveon-bell-bellle022017                 85.0       ...         
/players/alvin-kamara-kamaral012017               81.0       ...         
/players/tyler-lockett-lockety012017              45.0       ...         
/players/kareem-hunt-huntka012017                 53.0       ...         
/players/dion-lewis-lewisdi012017                 32.0       ...         
/players/antonio-brown-brownan052017             101.0       ...         
/players/lesean-mccoy-mccoyle022017               59.0       ...         
/players/melvin-gordon-gordome012017              58.0       ...         
/players/tarik-cohen-cohenta012017                53.0       ...         
/players/mark-ingram-ingrama022017                58.0       ...         
/players/keenan-allen-allenke032017              102.0       ...         
/players/julio-jones-jonesju052017                88.0       ...         
/players/tyreek-hill-hillty022017                 75.0       ...         
/players/pharoh-cooper-coopeph012017              11.0       ...         
/players/deandre-hopkins-hopkide012017            96.0       ...         
/players/leonard-fournette-fournle012017          36.0       ...         
/players/christian-mccaffrey-mccafch012017        80.0       ...         
/players/jerick-mckinnon-mckinje022017            51.0       ...         
/players/carlos-hyde-hydeca012017                 59.0       ...         
/players/adam-thielen-thielad012017               91.0       ...         
/players/ezekiel-elliott-ellioez012017            26.0       ...         
/players/jordan-howard-howarjo022017              23.0       ...         
/players/michael-thomas-thomami052017            104.0       ...         
/players/cj-anderson-andercj012017                28.0       ...         
/players/lamar-miller-millela032017               36.0       ...         
/players/alex-collins-collial012017               23.0       ...         
/players/frank-gore-gorefr012017                  29.0       ...         
/players/devonta-freeman-freemde012017            36.0       ...         
/players/juju-smithschuster-smithju032017         58.0       ...         
...                                                ...       ...         
/players/shane-smith-smithsh102017                 0.0       ...         
/players/cj-spiller-spillcj022017                  0.0       ...         
/players/caleb-sturgis-sturgca012017               0.0       ...         
/players/ryan-succop-succory012017                 0.0       ...         
/players/giorgio-tavecchio-tavecgi012017           0.0       ...         
/players/justin-tucker-tuckeju012017               0.0       ...         
/players/jason-vander-laan-vandeja032017           0.0       ...         
/players/adam-vinatieri-vinatad012017              0.0       ...         
/players/blair-walsh-walshbl012017                 0.0       ...         
/players/isaac-whitney-whitnis012017               0.0       ...         
/players/marquez-williams-willima262017            0.0       ...         
/players/greg-zuerlein-zuerlgr012017               0.0       ...         
/players/austin-davis-davisau012017                0.0       ...         
/players/cody-kessler-kesslco012017                0.0       ...         
/players/derek-anderson-anderde012017              0.0       ...         
/players/chase-daniel-daniech012017                0.0       ...         
/players/bronson-hill-hillbr022017                 0.0       ...         
/players/sean-mannion-mannise022017                0.0       ...         
/players/darren-mcfadden-mcfadda012017             0.0       ...         
/players/sam-bradford-bradfsa012017                0.0       ...         
/players/teddy-bridgewater-bridgte012017           0.0       ...         
/players/ryan-mallett-mallery012017                0.0       ...         
/players/tyler-bray-brayty012017                   0.0       ...         
/players/kellen-clemens-clemeke012017              0.0       ...         
/players/nick-foles-folesni012017                  0.0       ...         
/players/chad-henne-hennech012017                  0.0       ...         
/players/brian-hoyer-hoyerbr012017                 0.0       ...         
/players/philip-rivers-riverph012017               0.0       ...         
/players/krishawn-hogan-hogankr012017              0.0       ...         
/players/landry-jones-jonesla062017                0.0       ...         

                                            0-19_att  20-29_made  20-29_att  \
player_url                                                                    
/players/todd-gurley-gurleto022017               0.0         0.0        0.0   
/players/leveon-bell-bellle022017                0.0         0.0        0.0   
/players/alvin-kamara-kamaral012017              0.0         0.0        0.0   
/players/tyler-lockett-lockety012017             0.0         0.0        0.0   
/players/kareem-hunt-huntka012017                0.0         0.0        0.0   
/players/dion-lewis-lewisdi012017                0.0         0.0        0.0   
/players/antonio-brown-brownan052017             0.0         0.0        0.0   
/players/lesean-mccoy-mccoyle022017              0.0         0.0        0.0   
/players/melvin-gordon-gordome012017             0.0         0.0        0.0   
/players/tarik-cohen-cohenta012017               0.0         0.0        0.0   
/players/mark-ingram-ingrama022017               0.0         0.0        0.0   
/players/keenan-allen-allenke032017              0.0         0.0        0.0   
/players/julio-jones-jonesju052017               0.0         0.0        0.0   
/players/tyreek-hill-hillty022017                0.0         0.0        0.0   
/players/pharoh-cooper-coopeph012017             0.0         0.0        0.0   
/players/deandre-hopkins-hopkide012017           0.0         0.0        0.0   
/players/leonard-fournette-fournle012017         0.0         0.0        0.0   
/players/christian-mccaffrey-mccafch012017       0.0         0.0        0.0   
/players/jerick-mckinnon-mckinje022017           0.0         0.0        0.0   
/players/carlos-hyde-hydeca012017                0.0         0.0        0.0   
/players/adam-thielen-thielad012017              0.0         0.0        0.0   
/players/ezekiel-elliott-ellioez012017           0.0         0.0        0.0   
/players/jordan-howard-howarjo022017             0.0         0.0        0.0   
/players/michael-thomas-thomami052017            0.0         0.0        0.0   
/players/cj-anderson-andercj012017               0.0         0.0        0.0   
/players/lamar-miller-millela032017              0.0         0.0        0.0   
/players/alex-collins-collial012017              0.0         0.0        0.0   
/players/frank-gore-gorefr012017                 0.0         0.0        0.0   
/players/devonta-freeman-freemde012017           0.0         0.0        0.0   
/players/juju-smithschuster-smithju032017        0.0         0.0        0.0   
...                                              ...         ...        ...   
/players/shane-smith-smithsh102017               0.0         0.0        0.0   
/players/cj-spiller-spillcj022017                0.0         0.0        0.0   
/players/caleb-sturgis-sturgca012017             0.0         0.0        0.0   
/players/ryan-succop-succory012017               0.0        10.0       10.0   
/players/giorgio-tavecchio-tavecgi012017         0.0         5.0        5.0   
/players/justin-tucker-tuckeju012017             0.0         7.0        7.0   
/players/jason-vander-laan-vandeja032017         0.0         0.0        0.0   
/players/adam-vinatieri-vinatad012017            0.0        11.0       11.0   
/players/blair-walsh-walshbl012017               0.0         6.0        6.0   
/players/isaac-whitney-whitnis012017             0.0         0.0        0.0   
/players/marquez-williams-willima262017          0.0         0.0        0.0   
/players/greg-zuerlein-zuerlgr012017             1.0         8.0        8.0   
/players/austin-davis-davisau012017              0.0         0.0        0.0   
/players/cody-kessler-kesslco012017              0.0         0.0        0.0   
/players/derek-anderson-anderde012017            0.0         0.0        0.0   
/players/chase-daniel-daniech012017              0.0         0.0        0.0   
/players/bronson-hill-hillbr022017               0.0         0.0        0.0   
/players/sean-mannion-mannise022017              0.0         0.0        0.0   
/players/darren-mcfadden-mcfadda012017           0.0         0.0        0.0   
/players/sam-bradford-bradfsa012017              0.0         0.0        0.0   
/players/teddy-bridgewater-bridgte012017         0.0         0.0        0.0   
/players/ryan-mallett-mallery012017              0.0         0.0        0.0   
/players/tyler-bray-brayty012017                 0.0         0.0        0.0   
/players/kellen-clemens-clemeke012017            0.0         0.0        0.0   
/players/nick-foles-folesni012017                0.0         0.0        0.0   
/players/chad-henne-hennech012017                0.0         0.0        0.0   
/players/brian-hoyer-hoyerbr012017               0.0         0.0        0.0   
/players/philip-rivers-riverph012017             0.0         0.0        0.0   
/players/krishawn-hogan-hogankr012017            0.0         0.0        0.0   
/players/landry-jones-jonesla062017              0.0         0.0        0.0   

                                            30-39_made  30-39_att  40-49_made  \
player_url                                                                      
/players/todd-gurley-gurleto022017                 0.0        0.0         0.0   
/players/leveon-bell-bellle022017                  0.0        0.0         0.0   
/players/alvin-kamara-kamaral012017                0.0        0.0         0.0   
/players/tyler-lockett-lockety012017               0.0        0.0         0.0   
/players/kareem-hunt-huntka012017                  0.0        0.0         0.0   
/players/dion-lewis-lewisdi012017                  0.0        0.0         0.0   
/players/antonio-brown-brownan052017               0.0        0.0         0.0   
/players/lesean-mccoy-mccoyle022017                0.0        0.0         0.0   
/players/melvin-gordon-gordome012017               0.0        0.0         0.0   
/players/tarik-cohen-cohenta012017                 0.0        0.0         0.0   
/players/mark-ingram-ingrama022017                 0.0        0.0         0.0   
/players/keenan-allen-allenke032017                0.0        0.0         0.0   
/players/julio-jones-jonesju052017                 0.0        0.0         0.0   
/players/tyreek-hill-hillty022017                  0.0        0.0         0.0   
/players/pharoh-cooper-coopeph012017               0.0        0.0         0.0   
/players/deandre-hopkins-hopkide012017             0.0        0.0         0.0   
/players/leonard-fournette-fournle012017           0.0        0.0         0.0   
/players/christian-mccaffrey-mccafch012017         0.0        0.0         0.0   
/players/jerick-mckinnon-mckinje022017             0.0        0.0         0.0   
/players/carlos-hyde-hydeca012017                  0.0        0.0         0.0   
/players/adam-thielen-thielad012017                0.0        0.0         0.0   
/players/ezekiel-elliott-ellioez012017             0.0        0.0         0.0   
/players/jordan-howard-howarjo022017               0.0        0.0         0.0   
/players/michael-thomas-thomami052017              0.0        0.0         0.0   
/players/cj-anderson-andercj012017                 0.0        0.0         0.0   
/players/lamar-miller-millela032017                0.0        0.0         0.0   
/players/alex-collins-collial012017                0.0        0.0         0.0   
/players/frank-gore-gorefr012017                   0.0        0.0         0.0   
/players/devonta-freeman-freemde012017             0.0        0.0         0.0   
/players/juju-smithschuster-smithju032017          0.0        0.0         0.0   
...                                                ...        ...         ...   
/players/shane-smith-smithsh102017                 0.0        0.0         0.0   
/players/cj-spiller-spillcj022017                  0.0        0.0         0.0   
/players/caleb-sturgis-sturgca012017               1.0        1.0         1.0   
/players/ryan-succop-succory012017                 7.0        7.0        16.0   
/players/giorgio-tavecchio-tavecgi012017           5.0        7.0         3.0   
/players/justin-tucker-tuckeju012017              11.0       11.0        11.0   
/players/jason-vander-laan-vandeja032017           0.0        0.0         0.0   
/players/adam-vinatieri-vinatad012017              7.0       10.0         6.0   
/players/blair-walsh-walshbl012017                 7.0       10.0         8.0   
/players/isaac-whitney-whitnis012017               0.0        0.0         0.0   
/players/marquez-williams-willima262017            0.0        0.0         0.0   
/players/greg-zuerlein-zuerlgr012017              11.0       12.0        12.0   
/players/austin-davis-davisau012017                0.0        0.0         0.0   
/players/cody-kessler-kesslco012017                0.0        0.0         0.0   
/players/derek-anderson-anderde012017              0.0        0.0         0.0   
/players/chase-daniel-daniech012017                0.0        0.0         0.0   
/players/bronson-hill-hillbr022017                 0.0        0.0         0.0   
/players/sean-mannion-mannise022017                0.0        0.0         0.0   
/players/darren-mcfadden-mcfadda012017             0.0        0.0         0.0   
/players/sam-bradford-bradfsa012017                0.0        0.0         0.0   
/players/teddy-bridgewater-bridgte012017           0.0        0.0         0.0   
/players/ryan-mallett-mallery012017                0.0        0.0         0.0   
/players/tyler-bray-brayty012017                   0.0        0.0         0.0   
/players/kellen-clemens-clemeke012017              0.0        0.0         0.0   
/players/nick-foles-folesni012017                  0.0        0.0         0.0   
/players/chad-henne-hennech012017                  0.0        0.0         0.0   
/players/brian-hoyer-hoyerbr012017                 0.0        0.0         0.0   
/players/philip-rivers-riverph012017               0.0        0.0         0.0   
/players/krishawn-hogan-hogankr012017              0.0        0.0         0.0   
/players/landry-jones-jonesla062017                0.0        0.0         0.0   

                                            40-49_att  50_plus_made  \
player_url                                                            
/players/todd-gurley-gurleto022017                0.0           0.0   
/players/leveon-bell-bellle022017                 0.0           0.0   
/players/alvin-kamara-kamaral012017               0.0           0.0   
/players/tyler-lockett-lockety012017              0.0           0.0   
/players/kareem-hunt-huntka012017                 0.0           0.0   
/players/dion-lewis-lewisdi012017                 0.0           0.0   
/players/antonio-brown-brownan052017              0.0           0.0   
/players/lesean-mccoy-mccoyle022017               0.0           0.0   
/players/melvin-gordon-gordome012017              0.0           0.0   
/players/tarik-cohen-cohenta012017                0.0           0.0   
/players/mark-ingram-ingrama022017                0.0           0.0   
/players/keenan-allen-allenke032017               0.0           0.0   
/players/julio-jones-jonesju052017                0.0           0.0   
/players/tyreek-hill-hillty022017                 0.0           0.0   
/players/pharoh-cooper-coopeph012017              0.0           0.0   
/players/deandre-hopkins-hopkide012017            0.0           0.0   
/players/leonard-fournette-fournle012017          0.0           0.0   
/players/christian-mccaffrey-mccafch012017        0.0           0.0   
/players/jerick-mckinnon-mckinje022017            0.0           0.0   
/players/carlos-hyde-hydeca012017                 0.0           0.0   
/players/adam-thielen-thielad012017               0.0           0.0   
/players/ezekiel-elliott-ellioez012017            0.0           0.0   
/players/jordan-howard-howarjo022017              0.0           0.0   
/players/michael-thomas-thomami052017             0.0           0.0   
/players/cj-anderson-andercj012017                0.0           0.0   
/players/lamar-miller-millela032017               0.0           0.0   
/players/alex-collins-collial012017               0.0           0.0   
/players/frank-gore-gorefr012017                  0.0           0.0   
/players/devonta-freeman-freemde012017            0.0           0.0   
/players/juju-smithschuster-smithju032017         0.0           0.0   
...                                               ...           ...   
/players/shane-smith-smithsh102017                0.0           0.0   
/players/cj-spiller-spillcj022017                 0.0           0.0   
/players/caleb-sturgis-sturgca012017              1.0           1.0   
/players/ryan-succop-succory012017               20.0           2.0   
/players/giorgio-tavecchio-tavecgi012017          5.0           3.0   
/players/justin-tucker-tuckeju012017             12.0           5.0   
/players/jason-vander-laan-vandeja032017          0.0           0.0   
/players/adam-vinatieri-vinatad012017             7.0           5.0   
/players/blair-walsh-walshbl012017               12.0           0.0   
/players/isaac-whitney-whitnis012017              0.0           0.0   
/players/marquez-williams-willima262017           0.0           0.0   
/players/greg-zuerlein-zuerlgr012017             12.0           6.0   
/players/austin-davis-davisau012017               0.0           0.0   
/players/cody-kessler-kesslco012017               0.0           0.0   
/players/derek-anderson-anderde012017             0.0           0.0   
/players/chase-daniel-daniech012017               0.0           0.0   
/players/bronson-hill-hillbr022017                0.0           0.0   
/players/sean-mannion-mannise022017               0.0           0.0   
/players/darren-mcfadden-mcfadda012017            0.0           0.0   
/players/sam-bradford-bradfsa012017               0.0           0.0   
/players/teddy-bridgewater-bridgte012017          0.0           0.0   
/players/ryan-mallett-mallery012017               0.0           0.0   
/players/tyler-bray-brayty012017                  0.0           0.0   
/players/kellen-clemens-clemeke012017             0.0           0.0   
/players/nick-foles-folesni012017                 0.0           0.0   
/players/chad-henne-hennech012017                 0.0           0.0   
/players/brian-hoyer-hoyerbr012017                0.0           0.0   
/players/philip-rivers-riverph012017              0.0           0.0   
/players/krishawn-hogan-hogankr012017             0.0           0.0   
/players/landry-jones-jonesla062017               0.0           0.0   

                                            50_plus_att  fantasy_points  
player_url                                                               
/players/todd-gurley-gurleto022017                  0.0          383.30  
/players/leveon-bell-bellle022017                   0.0          341.60  
/players/alvin-kamara-kamaral012017                 0.0          334.28  
/players/tyler-lockett-lockety012017                0.0          171.74  
/players/kareem-hunt-huntka012017                   0.0          295.20  
/players/dion-lewis-lewisdi012017                   0.0          225.80  
/players/antonio-brown-brownan052017                0.0          312.74  
/players/lesean-mccoy-mccoyle022017                 0.0          263.60  
/players/melvin-gordon-gordome012017                0.0          288.10  
/players/tarik-cohen-cohenta012017                  0.0          184.34  
/players/mark-ingram-ingrama022017                  0.0          278.00  
/players/keenan-allen-allenke032017                 0.0          278.20  
/players/julio-jones-jonesju052017                  0.0          251.90  
/players/tyreek-hill-hillty022017                   0.0          254.36  
/players/pharoh-cooper-coopeph012017                0.0           77.24  
/players/deandre-hopkins-hopkide012017              0.0          309.80  
/players/leonard-fournette-fournle012017            0.0          230.20  
/players/christian-mccaffrey-mccafch012017          0.0          237.40  
/players/jerick-mckinnon-mckinje022017              0.0          190.58  
/players/carlos-hyde-hydeca012017                   0.0          233.80  
/players/adam-thielen-thielad012017                 0.0          239.70  
/players/ezekiel-elliott-ellioez012017              0.0          203.20  
/players/jordan-howard-howarjo022017                0.0          199.70  
/players/michael-thomas-thomami052017               0.0          258.50  
/players/cj-anderson-andercj012017                  0.0          175.10  
/players/lamar-miller-millela032017                 0.0          193.50  
/players/alex-collins-collial012017                 0.0          173.00  
/players/frank-gore-gorefr012017                    0.0          173.60  
/players/devonta-freeman-freemde012017              0.0          200.20  
/players/juju-smithschuster-smithju032017           0.0          207.30  
...                                                 ...             ...  
/players/shane-smith-smithsh102017                  0.0            0.00  
/players/cj-spiller-spillcj022017                   0.0            0.00  
/players/caleb-sturgis-sturgca012017                1.0           13.00  
/players/ryan-succop-succory012017                  5.0          156.00  
/players/giorgio-tavecchio-tavecgi012017            4.0           90.00  
/players/justin-tucker-tuckeju012017                7.0          162.00  
/players/jason-vander-laan-vandeja032017            0.0            0.00  
/players/adam-vinatieri-vinatad012017               6.0          125.00  
/players/blair-walsh-walshbl012017                  1.0          108.00  
/players/isaac-whitney-whitnis012017                0.0            0.00  
/players/marquez-williams-willima262017             0.0            0.00  
/players/greg-zuerlein-zuerlgr012017                7.0          182.00  
/players/austin-davis-davisau012017                 0.0           -0.10  
/players/cody-kessler-kesslco012017                 0.0            3.94  
/players/derek-anderson-anderde012017               0.0            0.48  
/players/chase-daniel-daniech012017                 0.0           -0.20  
/players/bronson-hill-hillbr022017                  0.0           -0.20  
/players/sean-mannion-mannise022017                 0.0            5.20  
/players/darren-mcfadden-mcfadda012017              0.0           -0.20  
/players/sam-bradford-bradfsa012017                 0.0           26.98  
/players/teddy-bridgewater-bridgte012017            0.0           -1.30  
/players/ryan-mallett-mallery012017                 0.0            9.94  
/players/tyler-bray-brayty012017                    0.0           -2.00  
/players/kellen-clemens-clemeke012017               0.0           -0.06  
/players/nick-foles-folesni012017                   0.0           35.78  
/players/chad-henne-hennech012017                   0.0           -0.50  
/players/brian-hoyer-hoyerbr012017                  0.0           67.88  
/players/philip-rivers-riverph012017                0.0          280.40  
/players/krishawn-hogan-hogankr012017               0.0           -0.32  
/players/landry-jones-jonesla062017                 0.0            9.56  

[613 rows x 36 columns]
"""
