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
                'table_id': 'rushing',
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
                    'fumbles': int,
                    'fumbles_lost': int,
                    'total_td': int,  # touchdowns of any type
                    'two_pt_conversions_made': int,
                    'two_pt_conversion_passes': int,
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

    @property
    def tables(self):
        """getter: Returns a list of the possible table types to scrape from."""
        return list(self._tables_dict.keys())

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
        # Convert years to string.
        if isinstance(start_year, str):
            start_year = int(start_year)
        if isinstance(end_year, str):
            end_year = int(end_year)

        # Build range iterator depending on how start_year and end_year are related.
        if start_year > end_year:
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

"""
Sample output:

                                           name team  age position  \
player_url                                                           
/players/B/BellLe00.htm2017        Le'Veon Bell  PIT   25       RB   
/players/M/McCoLe01.htm2017        LeSean McCoy  BUF   29       RB   
/players/G/GordMe00.htm2017       Melvin Gordon  LAC   24       RB   
/players/G/GurlTo01.htm2017         Todd Gurley  LAR   23       RB   
/players/H/HowaJo00.htm2017       Jordan Howard  CHI   23       RB   
/players/H/HuntKa00.htm2017         Kareem Hunt  KAN   22       RB   
/players/F/FourLe00.htm2017   Leonard Fournette  JAX   22       RB   
/players/G/GoreFr00.htm2017          Frank Gore  IND   34       RB   
/players/A/AndeC.00.htm2017       C.J. Anderson  DEN   26       RB   
/players/E/ElliEz00.htm2017     Ezekiel Elliott  DAL   22       RB   
/players/H/HydeCa00.htm2017         Carlos Hyde  SFO   27       RB   
/players/M/MillLa01.htm2017        Lamar Miller  HOU   26       RB   
/players/I/IngrMa01.htm2017         Mark Ingram  NOR   28       RB   
/players/M/MurrLa00.htm2017     Latavius Murray  MIN   27       RB   
/players/C/CollAl00.htm2017        Alex Collins  BAL   23       RB   
/players/A/AjayJa00.htm2017           Jay Ajayi  2TM   24        0   
/players/L/LyncMa00.htm2017      Marshawn Lynch  OAK   31       RB   
/players/C/CrowIs00.htm2017      Isaiah Crowell  CLE   24       RB   
/players/S/StewJo00.htm2017    Jonathan Stewart  CAR   30       RB   
/players/F/FreeDe00.htm2017     Devonta Freeman  ATL   25       RB   
/players/M/MurrDe00.htm2017      DeMarco Murray  TEN   29       RB   
/players/L/LewiDi00.htm2017          Dion Lewis  NWE   27       RB   
/players/M/MixoJo00.htm2017           Joe Mixon  CIN   21       rb   
/players/P/PoweBi00.htm2017        Bilal Powell  NYJ   29       RB   
/players/H/HenrDe00.htm2017       Derrick Henry  TEN   23       rb   
/players/P/PeriSa00.htm2017       Samaje Perine  WAS   22       RB   
/players/B/BlouLe00.htm2017   LeGarrette Blount  PHI   31       RB   
/players/D/DarkOr00.htm2017      Orleans Darkwa  NYG   25       RB   
/players/A/AbduAm00.htm2017      Ameer Abdullah  DET   24       RB   
/players/C/ColeTe01.htm2017       Tevin Coleman  ATL   24    fb/rb   
...                                         ...  ...  ...      ...   
/players/H/HillBr01.htm2017        Bronson Hill  ARI   24        0   
/players/H/HillJo02.htm2017           Josh Hill  NOR   27       TE   
/players/H/HollJa03.htm2017     Jacob Hollister  NWE   24       te   
/players/H/HumpAd00.htm2017      Adam Humphries  TAM   24       wr   
/players/J/JoneCh02.htm2017         Chris Jones  DAL   28        P   
/players/J/JoneJu02.htm2017         Julio Jones  ATL   28       WR   
/players/K/KessCo00.htm2017        Cody Kessler  CLE   24        0   
/players/K/KuhnJo00.htm2017           John Kuhn  NOR   35       fb   
/players/L/LandJa00.htm2017       Jarvis Landry  MIA   25       WR   
/players/L/LeexMa00.htm2017         Marqise Lee  JAX   26       WR   
/players/L/LutzWi00.htm2017            Wil Lutz  NOR   23        K   
/players/M/MattRi00.htm2017    Rishard Matthews  TEN   28       WR   
/players/M/McFaDa00.htm2017     Darren McFadden  DAL   30        0   
/players/M/McKeIs00.htm2017     Isaiah McKenzie  DEN   22        0   
/players/M/MillBr03.htm2017      Braxton Miller  HOU   25       wr   
/players/N/NatsJo00.htm2017         Jojo Natson  NYJ   23        0   
/players/N/NjokDa00.htm2017         David Njoku  CLE   21       te   
/players/R/RainBo00.htm2017        Bobby Rainey  BAL   30        0   
/players/R/RaymKa00.htm2017       Kalif Raymond  2TM   23        0   
/players/R/RedfKa00.htm2017       Kasey Redfern  DET   26        p   
/players/R/RossJo00.htm2017           John Ross  CIN   23       wr   
/players/S/SmitTo02.htm2017        Torrey Smith  PHI   28       WR   
/players/S/SudfNa00.htm2017        Nate Sudfeld  PHI   24        0   
/players/T/ThieAd00.htm2017        Adam Thielen  MIN   27       WR   
/players/T/ThomDe05.htm2017   De'Anthony Thomas  KAN   24       wr   
/players/T/TregBr00.htm2017        Bryce Treggs  CLE   23       wr   
/players/W/WallMi00.htm2017        Mike Wallace  BAL   31       WR   
/players/W/WeemEr00.htm2017          Eric Weems  TEN   32        0   
/players/W/WhitJe02.htm2017  Jermaine Whitehead  GNB   24        0   
/players/W/WillKy20.htm2017       Kyle Williams  BUF   34  LDT/rdt   

                             games_played  games_started  rush_attempts  \
player_url                                                                
/players/B/BellLe00.htm2017            15             15            321   
/players/M/McCoLe01.htm2017            16             16            287   
/players/G/GordMe00.htm2017            16             16            284   
/players/G/GurlTo01.htm2017            15             15            279   
/players/H/HowaJo00.htm2017            16             16            276   
/players/H/HuntKa00.htm2017            16             16            272   
/players/F/FourLe00.htm2017            13             13            268   
/players/G/GoreFr00.htm2017            16             16            261   
/players/A/AndeC.00.htm2017            16             16            245   
/players/E/ElliEz00.htm2017            10             10            242   
/players/H/HydeCa00.htm2017            16             16            240   
/players/M/MillLa01.htm2017            16             13            238   
/players/I/IngrMa01.htm2017            16             13            230   
/players/M/MurrLa00.htm2017            16             11            216   
/players/C/CollAl00.htm2017            15             12            212   
/players/A/AjayJa00.htm2017            14              8            208   
/players/L/LyncMa00.htm2017            15             15            207   
/players/C/CrowIs00.htm2017            16             16            206   
/players/S/StewJo00.htm2017            15             10            198   
/players/F/FreeDe00.htm2017            14             14            196   
/players/M/MurrDe00.htm2017            15             15            184   
/players/L/LewiDi00.htm2017            16              8            180   
/players/M/MixoJo00.htm2017            14              7            178   
/players/P/PoweBi00.htm2017            15             10            178   
/players/H/HenrDe00.htm2017            16              2            176   
/players/P/PeriSa00.htm2017            16              8            175   
/players/B/BlouLe00.htm2017            16             11            173   
/players/D/DarkOr00.htm2017            15             11            171   
/players/A/AbduAm00.htm2017            14             11            165   
/players/C/ColeTe01.htm2017            15              3            156   
...                                   ...            ...            ...   
/players/H/HillBr01.htm2017             2              0              1   
/players/H/HillJo02.htm2017            16             11              1   
/players/H/HollJa03.htm2017            15              1              1   
/players/H/HumpAd00.htm2017            16              3              1   
/players/J/JoneCh02.htm2017            16              0              1   
/players/J/JoneJu02.htm2017            16             16              1   
/players/K/KessCo00.htm2017             3              0              1   
/players/K/KuhnJo00.htm2017             2              1              1   
/players/L/LandJa00.htm2017            16             16              1   
/players/L/LeexMa00.htm2017            14             14              1   
/players/L/LutzWi00.htm2017            16              0              1   
/players/M/MattRi00.htm2017            14             11              1   
/players/M/McFaDa00.htm2017             1              0              1   
/players/M/McKeIs00.htm2017            11              0              1   
/players/M/MillBr03.htm2017            11              3              1   
/players/N/NatsJo00.htm2017             7              0              1   
/players/N/NjokDa00.htm2017            16              5              1   
/players/R/RainBo00.htm2017             4              0              1   
/players/R/RaymKa00.htm2017             8              0              1   
/players/R/RedfKa00.htm2017             1              0              1   
/players/R/RossJo00.htm2017             3              1              1   
/players/S/SmitTo02.htm2017            16             14              1   
/players/S/SudfNa00.htm2017             1              0              1   
/players/T/ThieAd00.htm2017            16             16              1   
/players/T/ThomDe05.htm2017            16              2              1   
/players/T/TregBr00.htm2017             6              1              1   
/players/W/WallMi00.htm2017            15             14              1   
/players/W/WeemEr00.htm2017            16              0              1   
/players/W/WhitJe02.htm2017            10              0              1   
/players/W/WillKy20.htm2017            16             16              1   

                             rush_yards  rush_td  longest_run  ...   \
player_url                                                     ...    
/players/B/BellLe00.htm2017        1291        9           27  ...    
/players/M/McCoLe01.htm2017        1138        6           48  ...    
/players/G/GordMe00.htm2017        1105        8           87  ...    
/players/G/GurlTo01.htm2017        1305       13           57  ...    
/players/H/HowaJo00.htm2017        1122        9           53  ...    
/players/H/HuntKa00.htm2017        1327        8           69  ...    
/players/F/FourLe00.htm2017        1040        9           90  ...    
/players/G/GoreFr00.htm2017         961        3           21  ...    
/players/A/AndeC.00.htm2017        1007        3           40  ...    
/players/E/ElliEz00.htm2017         983        7           30  ...    
/players/H/HydeCa00.htm2017         938        8           61  ...    
/players/M/MillLa01.htm2017         888        3           21  ...    
/players/I/IngrMa01.htm2017        1124       12           72  ...    
/players/M/MurrLa00.htm2017         842        8           46  ...    
/players/C/CollAl00.htm2017         973        6           50  ...    
/players/A/AjayJa00.htm2017         873        1           71  ...    
/players/L/LyncMa00.htm2017         891        7           51  ...    
/players/C/CrowIs00.htm2017         853        2           59  ...    
/players/S/StewJo00.htm2017         680        6           60  ...    
/players/F/FreeDe00.htm2017         865        7           44  ...    
/players/M/MurrDe00.htm2017         659        6           75  ...    
/players/L/LewiDi00.htm2017         896        6           44  ...    
/players/M/MixoJo00.htm2017         626        4           25  ...    
/players/P/PoweBi00.htm2017         772        5           75  ...    
/players/H/HenrDe00.htm2017         744        5           75  ...    
/players/P/PeriSa00.htm2017         603        1           30  ...    
/players/B/BlouLe00.htm2017         766        2           68  ...    
/players/D/DarkOr00.htm2017         751        5           75  ...    
/players/A/AbduAm00.htm2017         552        4           34  ...    
/players/C/ColeTe01.htm2017         628        5           52  ...    
...                                 ...      ...          ...  ...    
/players/H/HillBr01.htm2017          -2        0           -2  ...    
/players/H/HillJo02.htm2017          -8        0           -8  ...    
/players/H/HollJa03.htm2017           5        0            5  ...    
/players/H/HumpAd00.htm2017           6        0            6  ...    
/players/J/JoneCh02.htm2017          24        0           24  ...    
/players/J/JoneJu02.htm2017          15        0           15  ...    
/players/K/KessCo00.htm2017          -1        0           -1  ...    
/players/K/KuhnJo00.htm2017           2        0            2  ...    
/players/L/LandJa00.htm2017          -7        0           -7  ...    
/players/L/LeexMa00.htm2017          17        0           17  ...    
/players/L/LutzWi00.htm2017           4        0            4  ...    
/players/M/MattRi00.htm2017          -3        0           -3  ...    
/players/M/McFaDa00.htm2017          -2        0           -2  ...    
/players/M/McKeIs00.htm2017           4        0            4  ...    
/players/M/MillBr03.htm2017           1        0            1  ...    
/players/N/NatsJo00.htm2017          15        0           15  ...    
/players/N/NjokDa00.htm2017           1        0            1  ...    
/players/R/RainBo00.htm2017           2        0            2  ...    
/players/R/RaymKa00.htm2017          -1        0            0  ...    
/players/R/RedfKa00.htm2017          10        0           10  ...    
/players/R/RossJo00.htm2017          12        0           12  ...    
/players/S/SmitTo02.htm2017          -3        0           -3  ...    
/players/S/SudfNa00.htm2017          22        0           22  ...    
/players/T/ThieAd00.htm2017          11        0           11  ...    
/players/T/ThomDe05.htm2017           4        0            4  ...    
/players/T/TregBr00.htm2017           6        0            6  ...    
/players/W/WallMi00.htm2017           4        0            4  ...    
/players/W/WeemEr00.htm2017           0        0            0  ...    
/players/W/WhitJe02.htm2017           7        0            7  ...    
/players/W/WillKy20.htm2017           1        1            1  ...    

                             rec_per_game  rec_yards_per_game  \
player_url                                                      
/players/B/BellLe00.htm2017           5.7                43.7   
/players/M/McCoLe01.htm2017           3.7                28.0   
/players/G/GordMe00.htm2017           3.6                29.8   
/players/G/GurlTo01.htm2017           4.3                52.5   
/players/H/HowaJo00.htm2017           1.4                 7.8   
/players/H/HuntKa00.htm2017           3.3                28.4   
/players/F/FourLe00.htm2017           2.8                23.2   
/players/G/GoreFr00.htm2017           1.8                15.3   
/players/A/AndeC.00.htm2017           1.8                14.0   
/players/E/ElliEz00.htm2017           2.6                26.9   
/players/H/HydeCa00.htm2017           3.7                21.9   
/players/M/MillLa01.htm2017           2.3                20.4   
/players/I/IngrMa01.htm2017           3.6                26.0   
/players/M/MurrLa00.htm2017           0.9                 6.4   
/players/C/CollAl00.htm2017           1.5                12.5   
/players/A/AjayJa00.htm2017           1.7                11.3   
/players/L/LyncMa00.htm2017           1.3                10.1   
/players/C/CrowIs00.htm2017           1.8                11.4   
/players/S/StewJo00.htm2017           0.5                 3.5   
/players/F/FreeDe00.htm2017           2.6                22.6   
/players/M/MurrDe00.htm2017           2.6                17.7   
/players/L/LewiDi00.htm2017           2.0                13.4   
/players/M/MixoJo00.htm2017           2.1                20.5   
/players/P/PoweBi00.htm2017           1.5                11.3   
/players/H/HenrDe00.htm2017           0.7                 8.5   
/players/P/PeriSa00.htm2017           1.4                11.4   
/players/B/BlouLe00.htm2017           0.5                 3.1   
/players/D/DarkOr00.htm2017           1.3                 7.7   
/players/A/AbduAm00.htm2017           1.8                11.6   
/players/C/ColeTe01.htm2017           1.8                19.9   
...                                   ...                 ...   
/players/H/HillBr01.htm2017           0.0                 0.0   
/players/H/HillJo02.htm2017           1.0                 7.8   
/players/H/HollJa03.htm2017           0.3                 2.8   
/players/H/HumpAd00.htm2017           3.8                39.4   
/players/J/JoneCh02.htm2017           0.0                 0.0   
/players/J/JoneJu02.htm2017           5.5                90.3   
/players/K/KessCo00.htm2017           0.0                 0.0   
/players/K/KuhnJo00.htm2017           0.0                 0.0   
/players/L/LandJa00.htm2017           7.0                61.7   
/players/L/LeexMa00.htm2017           4.0                50.1   
/players/L/LutzWi00.htm2017           0.0                 0.0   
/players/M/MattRi00.htm2017           3.8                56.8   
/players/M/McFaDa00.htm2017           0.0                 0.0   
/players/M/McKeIs00.htm2017           0.4                 2.6   
/players/M/MillBr03.htm2017           1.7                14.7   
/players/N/NatsJo00.htm2017           0.3                 2.6   
/players/N/NjokDa00.htm2017           2.0                24.1   
/players/R/RainBo00.htm2017           1.3                 4.5   
/players/R/RaymKa00.htm2017           0.1                 1.5   
/players/R/RedfKa00.htm2017           0.0                 0.0   
/players/R/RossJo00.htm2017           0.0                 0.0   
/players/S/SmitTo02.htm2017           2.3                26.9   
/players/S/SudfNa00.htm2017           0.0                 0.0   
/players/T/ThieAd00.htm2017           5.7                79.8   
/players/T/ThomDe05.htm2017           0.9                 8.9   
/players/T/TregBr00.htm2017           0.8                13.2   
/players/W/WallMi00.htm2017           3.5                49.9   
/players/W/WeemEr00.htm2017           0.1                 0.3   
/players/W/WhitJe02.htm2017           0.0                 0.0   
/players/W/WillKy20.htm2017           0.0                 0.0   

                             catch_percentage  touches  all_purpose_ypg  \
player_url                                                                
/players/B/BellLe00.htm2017              80.2      406             1946   
/players/M/McCoLe01.htm2017              76.6      346             1586   
/players/G/GordMe00.htm2017              69.9      342             1581   
/players/G/GurlTo01.htm2017              73.6      343             2093   
/players/H/HowaJo00.htm2017              71.9      299             1247   
/players/H/HuntKa00.htm2017              84.1      325             1782   
/players/F/FourLe00.htm2017              75.0      304             1342   
/players/G/GoreFr00.htm2017              76.3      290             1198   
/players/A/AndeC.00.htm2017              70.0      273             1231   
/players/E/ElliEz00.htm2017              68.4      268             1252   
/players/H/HydeCa00.htm2017              67.0      299             1282   
/players/M/MillLa01.htm2017              80.0      274             1215   
/players/I/IngrMa01.htm2017              81.7      288             1540   
/players/M/MurrLa00.htm2017              88.2      231              945   
/players/C/CollAl00.htm2017              63.9      237             1210   
/players/A/AjayJa00.htm2017              70.6      232             1031   
/players/L/LyncMa00.htm2017              64.5      227             1042   
/players/C/CrowIs00.htm2017              66.7      234             1035   
/players/S/StewJo00.htm2017              53.3      206              732   
/players/F/FreeDe00.htm2017              76.6      232             1182   
/players/M/MurrDe00.htm2017              83.0      223              925   
/players/L/LewiDi00.htm2017              91.4      235             1680   
/players/M/MixoJo00.htm2017              88.2      208              913   
/players/P/PoweBi00.htm2017              69.7      201              942   
/players/H/HenrDe00.htm2017              64.7      187              880   
/players/P/PeriSa00.htm2017              91.7      199              833   
/players/B/BlouLe00.htm2017             100.0      181              816   
/players/D/DarkOr00.htm2017              67.9      190              867   
/players/A/AbduAm00.htm2017              71.4      198              893   
/players/C/ColeTe01.htm2017              69.2      183              927   
...                                       ...      ...              ...   
/players/H/HillBr01.htm2017               0.0        1               -2   
/players/H/HillJo02.htm2017              72.7       17              117   
/players/H/HollJa03.htm2017              36.4        5               47   
/players/H/HumpAd00.htm2017              73.5       68              686   
/players/J/JoneCh02.htm2017               0.0        1               24   
/players/J/JoneJu02.htm2017              59.5       89             1459   
/players/K/KessCo00.htm2017               0.0        1               -1   
/players/K/KuhnJo00.htm2017               0.0        2               11   
/players/L/LandJa00.htm2017              69.6      125             1056   
/players/L/LeexMa00.htm2017              58.3       62              732   
/players/L/LutzWi00.htm2017               0.0        1                4   
/players/M/MattRi00.htm2017              60.9       54              792   
/players/M/McFaDa00.htm2017               0.0        1               -2   
/players/M/McKeIs00.htm2017              30.8       29              266   
/players/M/MillBr03.htm2017              65.5       23              175   
/players/N/NatsJo00.htm2017              40.0       35              396   
/players/N/NjokDa00.htm2017              53.3       33              387   
/players/R/RainBo00.htm2017              71.4       19              380   
/players/R/RaymKa00.htm2017             100.0       34              381   
/players/R/RedfKa00.htm2017               0.0        1               10   
/players/R/RossJo00.htm2017               0.0        1               12   
/players/S/SmitTo02.htm2017              53.7       38              436   
/players/S/SudfNa00.htm2017               0.0        1               16   
/players/T/ThieAd00.htm2017              64.1       92             1287   
/players/T/ThomDe05.htm2017              87.5       36              468   
/players/T/TregBr00.htm2017              27.8       11              109   
/players/W/WallMi00.htm2017              56.5       53              752   
/players/W/WeemEr00.htm2017              50.0        6               38   
/players/W/WhitJe02.htm2017               0.0        2                7   
/players/W/WillKy20.htm2017               0.0        1                1   

                             ap_yards_per_touch  scrimmage_yards  rush_rec_td  \
player_url                                                                      
/players/B/BellLe00.htm2017                 4.8             1946           11   
/players/M/McCoLe01.htm2017                 4.6             1586            8   
/players/G/GordMe00.htm2017                 4.6             1581           12   
/players/G/GurlTo01.htm2017                 6.1             2093           19   
/players/H/HowaJo00.htm2017                 4.2             1247            9   
/players/H/HuntKa00.htm2017                 5.5             1782           11   
/players/F/FourLe00.htm2017                 4.4             1342           10   
/players/G/GoreFr00.htm2017                 4.1             1206            4   
/players/A/AndeC.00.htm2017                 4.5             1231            4   
/players/E/ElliEz00.htm2017                 4.7             1252            9   
/players/H/HydeCa00.htm2017                 4.3             1288            8   
/players/M/MillLa01.htm2017                 4.4             1215            6   
/players/I/IngrMa01.htm2017                 5.3             1540           12   
/players/M/MurrLa00.htm2017                 4.1              945            8   
/players/C/CollAl00.htm2017                 5.1             1160            6   
/players/A/AjayJa00.htm2017                 4.4             1031            2   
/players/L/LyncMa00.htm2017                 4.6             1042            7   
/players/C/CrowIs00.htm2017                 4.4             1035            2   
/players/S/StewJo00.htm2017                 3.6              732            7   
/players/F/FreeDe00.htm2017                 5.1             1182            8   
/players/M/MurrDe00.htm2017                 4.1              925            7   
/players/L/LewiDi00.htm2017                 7.1             1110            9   
/players/M/MixoJo00.htm2017                 4.4              913            4   
/players/P/PoweBi00.htm2017                 4.7              942            5   
/players/H/HenrDe00.htm2017                 4.7              880            6   
/players/P/PeriSa00.htm2017                 4.2              785            2   
/players/B/BlouLe00.htm2017                 4.5              816            3   
/players/D/DarkOr00.htm2017                 4.6              867            5   
/players/A/AbduAm00.htm2017                 4.5              714            5   
/players/C/ColeTe01.htm2017                 5.1              927            8   
...                                         ...              ...          ...   
/players/H/HillBr01.htm2017                -2.0               -2            0   
/players/H/HillJo02.htm2017                 6.9              117            1   
/players/H/HollJa03.htm2017                 9.4               47            0   
/players/H/HumpAd00.htm2017                10.1              637            1   
/players/J/JoneCh02.htm2017                24.0               24            0   
/players/J/JoneJu02.htm2017                16.4             1459            3   
/players/K/KessCo00.htm2017                -1.0               -1            0   
/players/K/KuhnJo00.htm2017                 5.5                2            0   
/players/L/LandJa00.htm2017                 8.4              980            9   
/players/L/LeexMa00.htm2017                11.8              719            3   
/players/L/LutzWi00.htm2017                 4.0                4            0   
/players/M/MattRi00.htm2017                14.7              792            4   
/players/M/McFaDa00.htm2017                -2.0               -2            0   
/players/M/McKeIs00.htm2017                 9.2               33            0   
/players/M/MillBr03.htm2017                 7.6              163            1   
/players/N/NatsJo00.htm2017                11.3               33            0   
/players/N/NjokDa00.htm2017                11.7              387            4   
/players/R/RainBo00.htm2017                20.0               20            0   
/players/R/RaymKa00.htm2017                11.2               11            0   
/players/R/RedfKa00.htm2017                10.0               10            0   
/players/R/RossJo00.htm2017                12.0               12            0   
/players/S/SmitTo02.htm2017                11.5              427            2   
/players/S/SudfNa00.htm2017                16.0               22            0   
/players/T/ThieAd00.htm2017                14.0             1287            4   
/players/T/ThomDe05.htm2017                13.0              147            2   
/players/T/TregBr00.htm2017                 9.9               85            0   
/players/W/WallMi00.htm2017                14.2              752            4   
/players/W/WeemEr00.htm2017                 6.3                5            0   
/players/W/WhitJe02.htm2017                 3.5                7            0   
/players/W/WillKy20.htm2017                 1.0                1            1   

                             fumbles  year  
player_url                                  
/players/B/BellLe00.htm2017        3  2017  
/players/M/McCoLe01.htm2017        3  2017  
/players/G/GordMe00.htm2017        1  2017  
/players/G/GurlTo01.htm2017        5  2017  
/players/H/HowaJo00.htm2017        1  2017  
/players/H/HuntKa00.htm2017        1  2017  
/players/F/FourLe00.htm2017        2  2017  
/players/G/GoreFr00.htm2017        3  2017  
/players/A/AndeC.00.htm2017        1  2017  
/players/E/ElliEz00.htm2017        1  2017  
/players/H/HydeCa00.htm2017        2  2017  
/players/M/MillLa01.htm2017        1  2017  
/players/I/IngrMa01.htm2017        3  2017  
/players/M/MurrLa00.htm2017        1  2017  
/players/C/CollAl00.htm2017        4  2017  
/players/A/AjayJa00.htm2017        3  2017  
/players/L/LyncMa00.htm2017        1  2017  
/players/C/CrowIs00.htm2017        1  2017  
/players/S/StewJo00.htm2017        3  2017  
/players/F/FreeDe00.htm2017        4  2017  
/players/M/MurrDe00.htm2017        1  2017  
/players/L/LewiDi00.htm2017        0  2017  
/players/M/MixoJo00.htm2017        3  2017  
/players/P/PoweBi00.htm2017        1  2017  
/players/H/HenrDe00.htm2017        1  2017  
/players/P/PeriSa00.htm2017        2  2017  
/players/B/BlouLe00.htm2017        1  2017  
/players/D/DarkOr00.htm2017        1  2017  
/players/A/AbduAm00.htm2017        2  2017  
/players/C/ColeTe01.htm2017        1  2017  
...                              ...   ...  
/players/H/HillBr01.htm2017        0  2017  
/players/H/HillJo02.htm2017        2  2017  
/players/H/HollJa03.htm2017        0  2017  
/players/H/HumpAd00.htm2017        1  2017  
/players/J/JoneCh02.htm2017        0  2017  
/players/J/JoneJu02.htm2017        0  2017  
/players/K/KessCo00.htm2017        0  2017  
/players/K/KuhnJo00.htm2017        0  2017  
/players/L/LandJa00.htm2017        4  2017  
/players/L/LeexMa00.htm2017        1  2017  
/players/L/LutzWi00.htm2017        0  2017  
/players/M/MattRi00.htm2017        0  2017  
/players/M/McFaDa00.htm2017        0  2017  
/players/M/McKeIs00.htm2017        6  2017  
/players/M/MillBr03.htm2017        0  2017  
/players/N/NatsJo00.htm2017        1  2017  
/players/N/NjokDa00.htm2017        0  2017  
/players/R/RainBo00.htm2017        0  2017  
/players/R/RaymKa00.htm2017        5  2017  
/players/R/RedfKa00.htm2017        1  2017  
/players/R/RossJo00.htm2017        1  2017  
/players/S/SmitTo02.htm2017        0  2017  
/players/S/SudfNa00.htm2017        0  2017  
/players/T/ThieAd00.htm2017        3  2017  
/players/T/ThomDe05.htm2017        1  2017  
/players/T/TregBr00.htm2017        1  2017  
/players/W/WallMi00.htm2017        0  2017  
/players/W/WeemEr00.htm2017        0  2017  
/players/W/WhitJe02.htm2017        0  2017  
/players/W/WillKy20.htm2017        0  2017  

[316 rows x 29 columns]
"""
