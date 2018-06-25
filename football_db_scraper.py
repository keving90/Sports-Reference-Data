#!/usr/bin/env python3

"""
This module contains a FbDbScraper class used to scrape NFL data from www.footballdb.com for a given season. It then
places the data into a Pandas data frame. Users can scrape a single table, or they can scrape comprehensive data, which
will include a calculation of each player's fantasy point total for the season based on provided fantasy settings.

Note: This module was built using Python 3.6.1, so dictionaries are ordered.

Issues:
    Currently, www.footballdb.com has no data for passing two point conversions. Therefore, fantasy calculations
    for quarterbacks will be slightly off. Rushing and receiving two point conversions are still recorded (even
    from a QB).
"""

import requests
import bs4
import pandas as pd
from player import Player


class FbDbScraper(object):
    """

    Scrapes data from www.footballdb.com and places it into a Pandas data frame. It can scrape an individual table
    using the get_df() method, or it can scrape several tables, join them together, and calculate each player's fantasy
    point total using the get_fantasy_df() method. Each method returns a data frame. The data frames are created using
    the __dict__ form of Player objects.

    Attributes:
        _fbdb_tables_dict (dict): Dictionary whose keys are the type of table to scrape from. The value is
            another dictionary. The nested dictionary contains keys whose values are used for building the URL to the
            table. Another key within the nested dict has a dict as values to store the column names and their data
            type.

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

        _fantasy_settings_dict (dict): Dictionary stores the name of the fantasy stat as keys and their point value as
            values. A property allows setting custom fantasy settings using a valid dictionary. Originally represents a
            standard Yahoo! 0PPR league.

            Example of valid dict:
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
                    'return_td': 6
                }

        _valid_fantasy_keys (dict_keys): Dictionary view object records initial keys in _fantasy_settings_dict to check
            for invalid keys when setting a custom fantasy settings dictionary.

    """
    def __init__(self):
        """Initialize FbDbScraper object."""
        self._fbdb_tables_dict = {
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
                    'point_after_td': str,
                    'field_goals': str,
                    'two_pt_conversions': int,
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
                    'point_after_td': str,
                    'fg_pct': str,
                    '0-19': str,
                    '20-29': str,
                    '30-39': str,
                    '40-49': str,
                    '50+': str,
                    'longest_fg': int,
                    'fg_points': int
                }
            }
        }

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
            'return_td': 6
        }

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
            """
            _fantasy_settings_dict can only be set to a dictionary with the same keys as original attribute.
            """
            # Fantasy settings must be a dictionary.
            if not isinstance(settings_dict, dict):
                raise ValueError("Fantasy settings must be a dictionary.")

            # Check for valid number of keys in new fantasy settings dictionary.
            dict_len = len(self._valid_fantasy_keys)
            if len(settings_dict) > dict_len:
                raise KeyError("Too many keys in new fantasy settings dict. "
                               + str(dict_len) + " keys required.")
            elif len(settings_dict) < dict_len:
                raise KeyError("Too few keys in new fantasy settings dict. "
                               + str(dict_len) + " keys required.")

            # Check for valid keys and value types in new fantasy settings dictionary.
            for key, value in settings_dict.items():
                if key not in self._valid_fantasy_keys:
                    raise KeyError("Invalid key in new fantasy settings dict. "
                                   + "Valid keys include: " + str(list(self._valid_fantasy_keys)))
                if type(value) not in [float, int]:
                    raise ValueError("Invalid value in new fantasy settings dict. Must be type int or float.")

            self._fantasy_settings_dict = settings_dict

    def get_fantasy_df(self, year):
        """
        Return a large data frame containing comprehensive players stats and their fantasy point total.

        :param year: Season's year.

        :return: Data frame containing all players and their fantasy points total for the season.
        """
        # Loop through dictionary keys, scraping a table and joining it to the "main data frame" each iteration. The
        # dictionary is an OrderedDict, so the 'all_purpose' key (for the All Purpose Yardage table) will always come
        # first. This data frame is used as the "main data frame" because it has the highest number of NFL players.
        for table in self._fbdb_tables_dict.keys():
            # Data set will not include kickers.
            if table == 'kicking':
                continue

            # Scrape a given table from footballdb.com and create a data frame.
            df = self.get_single_df(year, table, add_year_col=False)

            if table == 'all_purpose':
                # The 'all_purpose' table will act as the "main data frame".
                main_df = df
                main_df['year'] = year
            else:
                # All other data frames will be joined to main_df.
                # The only columns in df we're interested in are the ones not in main_df.
                relevant_cols = [col for col in df.columns if col not in main_df.columns]
                df = df[relevant_cols]

                # Join main_df and df using the unique player_url index.
                main_df = main_df.join(df, how='left')

        # Rearrange column order and calculate each player's fantasy point total.
        main_df = self._prepare_for_fantasy_points(main_df)
        main_df = self._insert_fantasy_points_column(main_df)

        return main_df

    def get_single_df(self, year, table_type, add_year_col=True):
        """
        Scrape a table from footballdb.com based on the table_type and put it into a data frame.

        :param year: Season's year.
        :param table_type: String representing the type of table to be scraped.

        :return: A data frame of the scraped table.
        """
        # Only scrapes from tables in self._fbdb_tables_dict.keys().
        if table_type.lower() not in self._fbdb_tables_dict.keys():
            raise KeyError("Error, make sure to specify table_type. "
                           + "Can only currently handle the following table names: "
                           + str(list(self._fbdb_tables_dict.keys())))

        # Scrape a given table from footballdb.com and create a data frame.
        url = self._make_url(year, table_type)
        player_list = self._get_player_result_set(url)
        player_dicts = self._get_player_stats(player_list, table_type)
        df = self._make_df(player_dicts, table_type)

        # Add year column if specified.
        if add_year_col:
            df['year'] = year

        return df

    def _make_url(self, year, table_type):
        """
        Create a URL string used to send a GET request to footballdb.com to scrape a table.

        :param year: Season year needed to go to the correct season of data.
        :param table_type: Indicates which table to scrape from.

        :return: URL string used to send GET request.
        """
        # Build the URL.
        url = ('https://www.footballdb.com/stats/stats.html?lg=NFL&yr='
               + str(year)
               + '&type=reg&mode='
               + self._fbdb_tables_dict[table_type]['mode']
               + '&conf=&limit=all&sort='
               + self._fbdb_tables_dict[table_type]['sort'])

        return url

    def _get_player_result_set(self, url):
        """
        Send a GET request and use BeautifulSoup4 to scrape a ResultSet from a footballdb.com table.

        :param url: String URL built by self._make_url().

        :return: A list - BeautifulSoup4 ResultSet of player data.
        """
        # Required for successful request. 403 error when not provided.
        # Taken from: https://stackoverflow.com/questions/38489386/python-requests-403-forbidden
        req_header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36'
                                    + '(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

        # Send a GET request to Pro Football Reference's Rushing & Receiving page to gather the data.
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
        # Each row in player_list has data for a single player
        # This will also collect descriptions of each column found in the web page's table, which
        # is filtered out in create_player_objects().
        player_list = body.find_all('tr')

        return player_list

    def _get_player_stats(self, player_list, table_type):
        """
        Iterate through a BeautifulSoup4 ResultSet to get a player stat data. Use list to create a Player object for
        each player.

        :param player_list: List of BeautifulSoup4 ResultSet player data.
        :param table_type: String used to access self._fbdb_tables_dict key data for creating Player objects.

        :return: List of player_object.__dict__'s for building a data frame.
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
            obj = Player(player_stats, self._fbdb_tables_dict[table_type]['all_columns'])
            list_of_player_dicts.append(obj.__dict__)

        return list_of_player_dicts

    def _make_df(self, player_dicts, table_type):
        """
        Make a data frame using a dictionary's keys as column names and list of player_object.__dict__'s as data.

        :param player_dicts: List of player_object.__dict__'s.
        :param table_type: String to get self._fbdb_tables_dict[table_type]['all_columns'].keys() for column names.

        :return: A data frame.
        """
        # Get dict's keys for df's column names.
        df_columns = list(self._fbdb_tables_dict[table_type]['all_columns'].keys())
        df = pd.DataFrame(data=player_dicts, columns=df_columns)  # Create the data frame.
        df.set_index('player_url', inplace=True)                        # Make 'name' the data frame's index

        return df

    def _prepare_for_fantasy_points(self, df):
        """
        Grab only the relevant columns in df and rearrange their order. Replace all numpy.NaN values with 0. Insert
        'return_yards' and 'return_td' columns for fantasy points calculation.

        :param df: Data frame to be prepared.

        :return: A data frame prepared for fantasy point calculation.
        """
        col_order = ['name', 'team', 'position', 'year', 'rush_attempts', 'rush_yards', 'yards_per_rush',
                     'rush_td', 'targets', 'receptions', 'rec_yards', 'rec_td', 'pass_attempts', 'pass_completions',
                     'completion_pct', 'pass_yards', 'pass_td', 'interceptions', 'sacked', 'kick_return_yards',
                     'kick_return_td', 'punt_return_yards', 'punt_return_td', 'two_pt_conversions', 'fumbles_lost']

        # Need to create a deep copy in order to prevent a SettingWithCopy warning.
        reordered_df = df[col_order].copy()

        # Replace all numpy.NaN values with 0.
        [reordered_df[column].fillna(0, inplace=True) for column in col_order[4:]]

        # Add 'return_yards' and 'return_td' columns for fantasy points calculation.
        reordered_df['return_yards'] = reordered_df['punt_return_yards'] + reordered_df['kick_return_yards']
        reordered_df['return_td'] = reordered_df['kick_return_td'] + reordered_df['punt_return_td']

        return reordered_df

    def _insert_fantasy_points_column(self, df):
        """
        Insert the fantasy_points column and calculate each player's fantasy point total.

        :param df: Data frame to have fantasy_points column inserted into.

        :return: A data frame with a fantasy_points column.
        """
        df['fantasy_points'] = 0
        for stat, value in self._fantasy_settings_dict.items():
            if stat in df.columns:
                df['fantasy_points'] += df[stat] * value

        return df


if __name__ == '__main__':
    # Usage example. Gets all NFL players from footballdb.com's "All Purpose Yards" and their data.
    # Also scrapes other tables to get each player's total fantasy points for the season.
    fb_db = FbDbScraper()
    fantasy_df = fb_db.get_fantasy_df(2017)
    print(fantasy_df)
    fantasy_df.to_csv('fbdb_fantasy.csv')

"""
Sample output:

                                                       name team position  \
player_url                                                                  
/players/todd-gurley-gurleto02                  Todd Gurley   LA       RB   
/players/leveon-bell-bellle02                  Le'Veon Bell  PIT       RB   
/players/alvin-kamara-kamaral01                Alvin Kamara   NO       RB   
/players/tyler-lockett-lockety01              Tyler Lockett  SEA       WR   
/players/kareem-hunt-huntka01                   Kareem Hunt   KC       RB   
/players/dion-lewis-lewisdi01                    Dion Lewis   NE       RB   
/players/antonio-brown-brownan05              Antonio Brown  PIT       WR   
/players/lesean-mccoy-mccoyle02                LeSean McCoy  BUF       RB   
/players/melvin-gordon-gordome01              Melvin Gordon  LAC       RB   
/players/tarik-cohen-cohenta01                  Tarik Cohen  CHI       RB   
/players/mark-ingram-ingrama02                  Mark Ingram   NO       RB   
/players/keenan-allen-allenke03                Keenan Allen  LAC       WR   
/players/julio-jones-jonesju05                  Julio Jones  ATL       WR   
/players/tyreek-hill-hillty02                   Tyreek Hill   KC       WR   
/players/pharoh-cooper-coopeph01              Pharoh Cooper   LA       WR   
/players/deandre-hopkins-hopkide01          DeAndre Hopkins  HOU       WR   
/players/leonard-fournette-fournle01      Leonard Fournette  JAX       RB   
/players/christian-mccaffrey-mccafch01  Christian McCaffrey  CAR       RB   
/players/jerick-mckinnon-mckinje02          Jerick McKinnon  MIN       RB   
/players/carlos-hyde-hydeca01                   Carlos Hyde   SF       RB   
/players/adam-thielen-thielad01                Adam Thielen  MIN       WR   
/players/ezekiel-elliott-ellioez01          Ezekiel Elliott  DAL       RB   
/players/jordan-howard-howarjo02              Jordan Howard  CHI       RB   
/players/michael-thomas-thomami05            Michael Thomas   NO       WR   
/players/cj-anderson-andercj01                C.J. Anderson  DEN       RB   
/players/lamar-miller-millela03                Lamar Miller  HOU       RB   
/players/alex-collins-collial01                Alex Collins  BAL       RB   
/players/frank-gore-gorefr01                     Frank Gore  IND       RB   
/players/devonta-freeman-freemde01          Devonta Freeman  ATL       RB   
/players/juju-smithschuster-smithju03   JuJu Smith-Schuster  PIT       WR   
...                                                     ...  ...      ...   
/players/brent-qvale-qvalebr01                  Brent Qvale  NYJ       OT   
/players/derron-smith-smithde12                Derron Smith  CIN       DB   
/players/sam-bradford-bradfsa01                Sam Bradford  MIN       QB   
/players/teddy-bridgewater-bridgte01      Teddy Bridgewater  MIN       QB   
/players/chris-jones-jonesch15                  Chris Jones   KC       DT   
/players/ryan-mallett-mallery01                Ryan Mallett  BAL       QB   
/players/tyler-bray-brayty01                     Tyler Bray   KC       QB   
/players/brian-mihalik-mihalbr01              Brian Mihalik  DET       DE   
/players/mike-pouncey-pouncmi01                Mike Pouncey  MIA        C   
/players/kevin-zeitler-zeitlke01              Kevin Zeitler  CLE       OG   
/players/kellen-clemens-clemeke01            Kellen Clemens  LAC       QB   
/players/nick-foles-folesni01                    Nick Foles  PHI       QB   
/players/chad-henne-hennech01                    Chad Henne  JAX       QB   
/players/brian-hoyer-hoyerbr01                  Brian Hoyer   NE       QB   
/players/matt-paradis-paradma01                Matt Paradis  DEN        C   
/players/josh-harris-harrijo12                  Josh Harris  ATL       LB   
/players/corey-linsley-linslco01              Corey Linsley   GB        C   
/players/philip-rivers-riverph01              Philip Rivers  LAC       QB   
/players/rodney-hudson-hudsoro01              Rodney Hudson  OAK        C   
/players/krishawn-hogan-hogankr01            Krishawn Hogan  IND       WR   
/players/zach-fulton-fultoza01                  Zach Fulton   KC       OG   
/players/evan-smith-dietrev01                    Evan Smith   TB       OG   
/players/landry-jones-jonesla06                Landry Jones  PIT       QB   
/players/jordan-devey-deveyjo01                Jordan Devey   KC       OT   
/players/ryan-jensen-jensery01                  Ryan Jensen  BAL       OT   
/players/marquette-king-kingma02             Marquette King  OAK        P   
/players/jc-tretter-trettjc01                  J.C. Tretter  CLE       OT   
/players/max-unger-ungerma01                      Max Unger   NO        C   
/players/spencer-pulley-pullesp01            Spencer Pulley  LAC        C   
/players/chris-hubbard-hubbach01              Chris Hubbard  PIT       OG   

                                        year  rush_attempts  rush_yards  \
player_url                                                                
/players/todd-gurley-gurleto02          2017          279.0        1305   
/players/leveon-bell-bellle02           2017          321.0        1291   
/players/alvin-kamara-kamaral01         2017          120.0         728   
/players/tyler-lockett-lockety01        2017           10.0          58   
/players/kareem-hunt-huntka01           2017          272.0        1327   
/players/dion-lewis-lewisdi01           2017          180.0         896   
/players/antonio-brown-brownan05        2017            0.0           0   
/players/lesean-mccoy-mccoyle02         2017          287.0        1138   
/players/melvin-gordon-gordome01        2017          284.0        1105   
/players/tarik-cohen-cohenta01          2017           87.0         370   
/players/mark-ingram-ingrama02          2017          230.0        1124   
/players/keenan-allen-allenke03         2017            2.0           9   
/players/julio-jones-jonesju05          2017            1.0          15   
/players/tyreek-hill-hillty02           2017           17.0          59   
/players/pharoh-cooper-coopeph01        2017            1.0           6   
/players/deandre-hopkins-hopkide01      2017            0.0           0   
/players/leonard-fournette-fournle01    2017          268.0        1040   
/players/christian-mccaffrey-mccafch01  2017          117.0         435   
/players/jerick-mckinnon-mckinje02      2017          150.0         570   
/players/carlos-hyde-hydeca01           2017          240.0         938   
/players/adam-thielen-thielad01         2017            1.0          11   
/players/ezekiel-elliott-ellioez01      2017          242.0         983   
/players/jordan-howard-howarjo02        2017          276.0        1122   
/players/michael-thomas-thomami05       2017            0.0           0   
/players/cj-anderson-andercj01          2017          245.0        1007   
/players/lamar-miller-millela03         2017          238.0         888   
/players/alex-collins-collial01         2017          212.0         973   
/players/frank-gore-gorefr01            2017          261.0         961   
/players/devonta-freeman-freemde01      2017          196.0         865   
/players/juju-smithschuster-smithju03   2017            0.0           0   
...                                      ...            ...         ...   
/players/brent-qvale-qvalebr01          2017            0.0           0   
/players/derron-smith-smithde12         2017            0.0           0   
/players/sam-bradford-bradfsa01         2017            2.0          -3   
/players/teddy-bridgewater-bridgte01    2017            3.0          -3   
/players/chris-jones-jonesch15          2017            0.0           0   
/players/ryan-mallett-mallery01         2017            4.0          -3   
/players/tyler-bray-brayty01            2017            1.0           0   
/players/brian-mihalik-mihalbr01        2017            0.0           0   
/players/mike-pouncey-pouncmi01         2017            0.0           0   
/players/kevin-zeitler-zeitlke01        2017            0.0           0   
/players/kellen-clemens-clemeke01       2017            5.0          -5   
/players/nick-foles-folesni01           2017           11.0           3   
/players/chad-henne-hennech01           2017            5.0          -5   
/players/brian-hoyer-hoyerbr01          2017            9.0           4   
/players/matt-paradis-paradma01         2017            0.0           0   
/players/josh-harris-harrijo12          2017            0.0           0   
/players/corey-linsley-linslco01        2017            0.0           0   
/players/philip-rivers-riverph01        2017           18.0          -2   
/players/rodney-hudson-hudsoro01        2017            0.0           0   
/players/krishawn-hogan-hogankr01       2017            0.0           0   
/players/zach-fulton-fultoza01          2017            0.0           0   
/players/evan-smith-dietrev01           2017            0.0           0   
/players/landry-jones-jonesla06         2017            8.0         -10   
/players/jordan-devey-deveyjo01         2017            0.0           0   
/players/ryan-jensen-jensery01          2017            0.0           0   
/players/marquette-king-kingma02        2017            2.0         -14   
/players/jc-tretter-trettjc01           2017            0.0           0   
/players/max-unger-ungerma01            2017            0.0           0   
/players/spencer-pulley-pullesp01       2017            0.0           0   
/players/chris-hubbard-hubbach01        2017            0.0           0   

                                        yards_per_rush  rush_td  targets  \
player_url                                                                 
/players/todd-gurley-gurleto02                    4.68     13.0     87.0   
/players/leveon-bell-bellle02                     4.02      9.0    106.0   
/players/alvin-kamara-kamaral01                   6.07      8.0    100.0   
/players/tyler-lockett-lockety01                  5.80      0.0     71.0   
/players/kareem-hunt-huntka01                     4.88      8.0     63.0   
/players/dion-lewis-lewisdi01                     4.98      6.0     35.0   
/players/antonio-brown-brownan05                  0.00      0.0    163.0   
/players/lesean-mccoy-mccoyle02                   3.97      6.0     77.0   
/players/melvin-gordon-gordome01                  3.89      8.0     83.0   
/players/tarik-cohen-cohenta01                    4.25      2.0     71.0   
/players/mark-ingram-ingrama02                    4.89     12.0     71.0   
/players/keenan-allen-allenke03                   4.50      0.0    159.0   
/players/julio-jones-jonesju05                   15.00      0.0    148.0   
/players/tyreek-hill-hillty02                     3.47      0.0    105.0   
/players/pharoh-cooper-coopeph01                  6.00      0.0     19.0   
/players/deandre-hopkins-hopkide01                0.00      0.0    174.0   
/players/leonard-fournette-fournle01              3.88      9.0     48.0   
/players/christian-mccaffrey-mccafch01            3.72      2.0    113.0   
/players/jerick-mckinnon-mckinje02                3.80      3.0     68.0   
/players/carlos-hyde-hydeca01                     3.91      8.0     88.0   
/players/adam-thielen-thielad01                  11.00      0.0    142.0   
/players/ezekiel-elliott-ellioez01                4.06      7.0     38.0   
/players/jordan-howard-howarjo02                  4.07      9.0     32.0   
/players/michael-thomas-thomami05                 0.00      0.0    149.0   
/players/cj-anderson-andercj01                    4.11      3.0     40.0   
/players/lamar-miller-millela03                   3.73      3.0     45.0   
/players/alex-collins-collial01                   4.59      6.0     36.0   
/players/frank-gore-gorefr01                      3.68      3.0     38.0   
/players/devonta-freeman-freemde01                4.41      7.0     47.0   
/players/juju-smithschuster-smithju03             0.00      0.0     79.0   
...                                                ...      ...      ...   
/players/brent-qvale-qvalebr01                    0.00      0.0      0.0   
/players/derron-smith-smithde12                   0.00      0.0      0.0   
/players/sam-bradford-bradfsa01                  -1.50      0.0      0.0   
/players/teddy-bridgewater-bridgte01             -1.00      0.0      0.0   
/players/chris-jones-jonesch15                    0.00      0.0      0.0   
/players/ryan-mallett-mallery01                  -0.75      0.0      0.0   
/players/tyler-bray-brayty01                      0.00      0.0      0.0   
/players/brian-mihalik-mihalbr01                  0.00      0.0      1.0   
/players/mike-pouncey-pouncmi01                   0.00      0.0      0.0   
/players/kevin-zeitler-zeitlke01                  0.00      0.0      1.0   
/players/kellen-clemens-clemeke01                -1.00      0.0      0.0   
/players/nick-foles-folesni01                     0.27      0.0      0.0   
/players/chad-henne-hennech01                    -1.00      0.0      0.0   
/players/brian-hoyer-hoyerbr01                    0.44      1.0      0.0   
/players/matt-paradis-paradma01                   0.00      0.0      0.0   
/players/josh-harris-harrijo12                    0.00      0.0      0.0   
/players/corey-linsley-linslco01                  0.00      0.0      0.0   
/players/philip-rivers-riverph01                 -0.11      0.0      0.0   
/players/rodney-hudson-hudsoro01                  0.00      0.0      0.0   
/players/krishawn-hogan-hogankr01                 0.00      0.0      0.0   
/players/zach-fulton-fultoza01                    0.00      0.0      0.0   
/players/evan-smith-dietrev01                     0.00      0.0      0.0   
/players/landry-jones-jonesla06                  -1.25      0.0      0.0   
/players/jordan-devey-deveyjo01                   0.00      0.0      0.0   
/players/ryan-jensen-jensery01                    0.00      0.0      0.0   
/players/marquette-king-kingma02                 -7.00      0.0      0.0   
/players/jc-tretter-trettjc01                     0.00      0.0      0.0   
/players/max-unger-ungerma01                      0.00      0.0      0.0   
/players/spencer-pulley-pullesp01                 0.00      0.0      0.0   
/players/chris-hubbard-hubbach01                  0.00      0.0      0.0   

                                        receptions       ...        sacked  \
player_url                                               ...                 
/players/todd-gurley-gurleto02                64.0       ...           0.0   
/players/leveon-bell-bellle02                 85.0       ...           0.0   
/players/alvin-kamara-kamaral01               81.0       ...           0.0   
/players/tyler-lockett-lockety01              45.0       ...           0.0   
/players/kareem-hunt-huntka01                 53.0       ...           0.0   
/players/dion-lewis-lewisdi01                 32.0       ...           0.0   
/players/antonio-brown-brownan05             101.0       ...           0.0   
/players/lesean-mccoy-mccoyle02               59.0       ...           0.0   
/players/melvin-gordon-gordome01              58.0       ...           0.0   
/players/tarik-cohen-cohenta01                53.0       ...           0.0   
/players/mark-ingram-ingrama02                58.0       ...           0.0   
/players/keenan-allen-allenke03              102.0       ...           0.0   
/players/julio-jones-jonesju05                88.0       ...           0.0   
/players/tyreek-hill-hillty02                 75.0       ...           0.0   
/players/pharoh-cooper-coopeph01              11.0       ...           0.0   
/players/deandre-hopkins-hopkide01            96.0       ...           0.0   
/players/leonard-fournette-fournle01          36.0       ...           0.0   
/players/christian-mccaffrey-mccafch01        80.0       ...           0.0   
/players/jerick-mckinnon-mckinje02            51.0       ...           0.0   
/players/carlos-hyde-hydeca01                 59.0       ...           0.0   
/players/adam-thielen-thielad01               91.0       ...           0.0   
/players/ezekiel-elliott-ellioez01            26.0       ...           0.0   
/players/jordan-howard-howarjo02              23.0       ...           0.0   
/players/michael-thomas-thomami05            104.0       ...           0.0   
/players/cj-anderson-andercj01                28.0       ...           0.0   
/players/lamar-miller-millela03               36.0       ...           0.0   
/players/alex-collins-collial01               23.0       ...           0.0   
/players/frank-gore-gorefr01                  29.0       ...           0.0   
/players/devonta-freeman-freemde01            36.0       ...           0.0   
/players/juju-smithschuster-smithju03         58.0       ...           0.0   
...                                            ...       ...           ...   
/players/brent-qvale-qvalebr01                 0.0       ...           0.0   
/players/derron-smith-smithde12                0.0       ...           0.0   
/players/sam-bradford-bradfsa01                0.0       ...           5.0   
/players/teddy-bridgewater-bridgte01           0.0       ...           0.0   
/players/chris-jones-jonesch15                 0.0       ...           0.0   
/players/ryan-mallett-mallery01                0.0       ...           0.0   
/players/tyler-bray-brayty01                   0.0       ...           0.0   
/players/brian-mihalik-mihalbr01               1.0       ...           0.0   
/players/mike-pouncey-pouncmi01                0.0       ...           0.0   
/players/kevin-zeitler-zeitlke01               1.0       ...           0.0   
/players/kellen-clemens-clemeke01              0.0       ...           0.0   
/players/nick-foles-folesni01                  0.0       ...           5.0   
/players/chad-henne-hennech01                  0.0       ...           0.0   
/players/brian-hoyer-hoyerbr01                 0.0       ...          16.0   
/players/matt-paradis-paradma01                0.0       ...           0.0   
/players/josh-harris-harrijo12                 0.0       ...           0.0   
/players/corey-linsley-linslco01               0.0       ...           0.0   
/players/philip-rivers-riverph01               0.0       ...          18.0   
/players/rodney-hudson-hudsoro01               0.0       ...           0.0   
/players/krishawn-hogan-hogankr01              0.0       ...           0.0   
/players/zach-fulton-fultoza01                 0.0       ...           0.0   
/players/evan-smith-dietrev01                  0.0       ...           0.0   
/players/landry-jones-jonesla06                0.0       ...           3.0   
/players/jordan-devey-deveyjo01                0.0       ...           0.0   
/players/ryan-jensen-jensery01                 0.0       ...           0.0   
/players/marquette-king-kingma02               0.0       ...           0.0   
/players/jc-tretter-trettjc01                  0.0       ...           0.0   
/players/max-unger-ungerma01                   0.0       ...           0.0   
/players/spencer-pulley-pullesp01              0.0       ...           0.0   
/players/chris-hubbard-hubbach01               0.0       ...           0.0   

                                        kick_return_yards  kick_return_td  \
player_url                                                                  
/players/todd-gurley-gurleto02                          0             0.0   
/players/leveon-bell-bellle02                           0             0.0   
/players/alvin-kamara-kamaral01                       347             1.0   
/players/tyler-lockett-lockety01                      949             1.0   
/players/kareem-hunt-huntka01                           0             0.0   
/players/dion-lewis-lewisdi01                         570             1.0   
/players/antonio-brown-brownan05                        0             0.0   
/players/lesean-mccoy-mccoyle02                         0             0.0   
/players/melvin-gordon-gordome01                        0             0.0   
/players/tarik-cohen-cohenta01                        583             0.0   
/players/mark-ingram-ingrama02                          0             0.0   
/players/keenan-allen-allenke03                         0             0.0   
/players/julio-jones-jonesju05                          0             0.0   
/players/tyreek-hill-hillty02                           0             0.0   
/players/pharoh-cooper-coopeph01                      932             1.0   
/players/deandre-hopkins-hopkide01                      0             0.0   
/players/leonard-fournette-fournle01                    0             0.0   
/players/christian-mccaffrey-mccafch01                 58             0.0   
/players/jerick-mckinnon-mckinje02                    312             0.0   
/players/carlos-hyde-hydeca01                           0             0.0   
/players/adam-thielen-thielad01                         0             0.0   
/players/ezekiel-elliott-ellioez01                      0             0.0   
/players/jordan-howard-howarjo02                        0             0.0   
/players/michael-thomas-thomami05                       0             0.0   
/players/cj-anderson-andercj01                          0             0.0   
/players/lamar-miller-millela03                         0             0.0   
/players/alex-collins-collial01                        50             0.0   
/players/frank-gore-gorefr01                            0             0.0   
/players/devonta-freeman-freemde01                      0             0.0   
/players/juju-smithschuster-smithju03                 240             1.0   
...                                                   ...             ...   
/players/brent-qvale-qvalebr01                          0             0.0   
/players/derron-smith-smithde12                         0             0.0   
/players/sam-bradford-bradfsa01                         0             0.0   
/players/teddy-bridgewater-bridgte01                    0             0.0   
/players/chris-jones-jonesch15                          0             0.0   
/players/ryan-mallett-mallery01                         0             0.0   
/players/tyler-bray-brayty01                            0             0.0   
/players/brian-mihalik-mihalbr01                        0             0.0   
/players/mike-pouncey-pouncmi01                         0             0.0   
/players/kevin-zeitler-zeitlke01                        0             0.0   
/players/kellen-clemens-clemeke01                       0             0.0   
/players/nick-foles-folesni01                           0             0.0   
/players/chad-henne-hennech01                           0             0.0   
/players/brian-hoyer-hoyerbr01                          0             0.0   
/players/matt-paradis-paradma01                         0             0.0   
/players/josh-harris-harrijo12                          0             0.0   
/players/corey-linsley-linslco01                        0             0.0   
/players/philip-rivers-riverph01                        0             0.0   
/players/rodney-hudson-hudsoro01                        0             0.0   
/players/krishawn-hogan-hogankr01                       0             0.0   
/players/zach-fulton-fultoza01                          0             0.0   
/players/evan-smith-dietrev01                           0             0.0   
/players/landry-jones-jonesla06                         0             0.0   
/players/jordan-devey-deveyjo01                         0             0.0   
/players/ryan-jensen-jensery01                          0             0.0   
/players/marquette-king-kingma02                        0             0.0   
/players/jc-tretter-trettjc01                           0             0.0   
/players/max-unger-ungerma01                            0             0.0   
/players/spencer-pulley-pullesp01                       0             0.0   
/players/chris-hubbard-hubbach01                        0             0.0   

                                        punt_return_yards  punt_return_td  \
player_url                                                                  
/players/todd-gurley-gurleto02                          0             0.0   
/players/leveon-bell-bellle02                           0             0.0   
/players/alvin-kamara-kamaral01                         0             0.0   
/players/tyler-lockett-lockety01                      237             0.0   
/players/kareem-hunt-huntka01                           0             0.0   
/players/dion-lewis-lewisdi01                           0             0.0   
/players/antonio-brown-brownan05                       61             0.0   
/players/lesean-mccoy-mccoyle02                         0             0.0   
/players/melvin-gordon-gordome01                        0             0.0   
/players/tarik-cohen-cohenta01                        272             1.0   
/players/mark-ingram-ingrama02                          0             0.0   
/players/keenan-allen-allenke03                         0             0.0   
/players/julio-jones-jonesju05                          0             0.0   
/players/tyreek-hill-hillty02                         204             1.0   
/players/pharoh-cooper-coopeph01                      399             0.0   
/players/deandre-hopkins-hopkide01                      0             0.0   
/players/leonard-fournette-fournle01                    0             0.0   
/players/christian-mccaffrey-mccafch01                162             0.0   
/players/jerick-mckinnon-mckinje02                      0             0.0   
/players/carlos-hyde-hydeca01                           0             0.0   
/players/adam-thielen-thielad01                         0             0.0   
/players/ezekiel-elliott-ellioez01                      0             0.0   
/players/jordan-howard-howarjo02                        0             0.0   
/players/michael-thomas-thomami05                       0             0.0   
/players/cj-anderson-andercj01                          0             0.0   
/players/lamar-miller-millela03                         0             0.0   
/players/alex-collins-collial01                         0             0.0   
/players/frank-gore-gorefr01                            0             0.0   
/players/devonta-freeman-freemde01                      0             0.0   
/players/juju-smithschuster-smithju03                   0             0.0   
...                                                   ...             ...   
/players/brent-qvale-qvalebr01                          0             0.0   
/players/derron-smith-smithde12                         0             0.0   
/players/sam-bradford-bradfsa01                         0             0.0   
/players/teddy-bridgewater-bridgte01                    0             0.0   
/players/chris-jones-jonesch15                          0             0.0   
/players/ryan-mallett-mallery01                         0             0.0   
/players/tyler-bray-brayty01                            0             0.0   
/players/brian-mihalik-mihalbr01                        0             0.0   
/players/mike-pouncey-pouncmi01                         0             0.0   
/players/kevin-zeitler-zeitlke01                        0             0.0   
/players/kellen-clemens-clemeke01                       0             0.0   
/players/nick-foles-folesni01                           0             0.0   
/players/chad-henne-hennech01                           0             0.0   
/players/brian-hoyer-hoyerbr01                          0             0.0   
/players/matt-paradis-paradma01                         0             0.0   
/players/josh-harris-harrijo12                          0             0.0   
/players/corey-linsley-linslco01                        0             0.0   
/players/philip-rivers-riverph01                        0             0.0   
/players/rodney-hudson-hudsoro01                        0             0.0   
/players/krishawn-hogan-hogankr01                      -8             0.0   
/players/zach-fulton-fultoza01                          0             0.0   
/players/evan-smith-dietrev01                           0             0.0   
/players/landry-jones-jonesla06                         0             0.0   
/players/jordan-devey-deveyjo01                         0             0.0   
/players/ryan-jensen-jensery01                          0             0.0   
/players/marquette-king-kingma02                        0             0.0   
/players/jc-tretter-trettjc01                           0             0.0   
/players/max-unger-ungerma01                            0             0.0   
/players/spencer-pulley-pullesp01                       0             0.0   
/players/chris-hubbard-hubbach01                        0             0.0   

                                        two_pt_conversions  fumbles_lost  \
player_url                                                                 
/players/todd-gurley-gurleto02                         0.0           2.0   
/players/leveon-bell-bellle02                          0.0           2.0   
/players/alvin-kamara-kamaral01                        1.0           1.0   
/players/tyler-lockett-lockety01                       0.0           0.0   
/players/kareem-hunt-huntka01                          0.0           1.0   
/players/dion-lewis-lewisdi01                          0.0           0.0   
/players/antonio-brown-brownan05                       1.0           0.0   
/players/lesean-mccoy-mccoyle02                        0.0           1.0   
/players/melvin-gordon-gordome01                       0.0           0.0   
/players/tarik-cohen-cohenta01                         0.0           2.0   
/players/mark-ingram-ingrama02                         0.0           3.0   
/players/keenan-allen-allenke03                        0.0           0.0   
/players/julio-jones-jonesju05                         0.0           0.0   
/players/tyreek-hill-hillty02                          0.0           0.0   
/players/pharoh-cooper-coopeph01                       0.0           1.0   
/players/deandre-hopkins-hopkide01                     0.0           1.0   
/players/leonard-fournette-fournle01                   0.0           0.0   
/players/christian-mccaffrey-mccafch01                 0.0           1.0   
/players/jerick-mckinnon-mckinje02                     1.0           2.0   
/players/carlos-hyde-hydeca01                          0.0           1.0   
/players/adam-thielen-thielad01                        0.0           2.0   
/players/ezekiel-elliott-ellioez01                     0.0           1.0   
/players/jordan-howard-howarjo02                       0.0           1.0   
/players/michael-thomas-thomami05                      0.0           0.0   
/players/cj-anderson-andercj01                         1.0           1.0   
/players/lamar-miller-millela03                        0.0           0.0   
/players/alex-collins-collial01                        0.0           2.0   
/players/frank-gore-gorefr01                           0.0           0.0   
/players/devonta-freeman-freemde01                     0.0           1.0   
/players/juju-smithschuster-smithju03                  0.0           0.0   
...                                                    ...           ...   
/players/brent-qvale-qvalebr01                         0.0           0.0   
/players/derron-smith-smithde12                        0.0           0.0   
/players/sam-bradford-bradfsa01                        0.0           0.0   
/players/teddy-bridgewater-bridgte01                   0.0           0.0   
/players/chris-jones-jonesch15                         0.0           0.0   
/players/ryan-mallett-mallery01                        0.0           0.0   
/players/tyler-bray-brayty01                           0.0           1.0   
/players/brian-mihalik-mihalbr01                       0.0           0.0   
/players/mike-pouncey-pouncmi01                        0.0           0.0   
/players/kevin-zeitler-zeitlke01                       0.0           0.0   
/players/kellen-clemens-clemeke01                      0.0           0.0   
/players/nick-foles-folesni01                          0.0           2.0   
/players/chad-henne-hennech01                          0.0           0.0   
/players/brian-hoyer-hoyerbr01                         0.0           1.0   
/players/matt-paradis-paradma01                        0.0           0.0   
/players/josh-harris-harrijo12                         0.0           0.0   
/players/corey-linsley-linslco01                       0.0           0.0   
/players/philip-rivers-riverph01                       0.0           1.0   
/players/rodney-hudson-hudsoro01                       0.0           0.0   
/players/krishawn-hogan-hogankr01                      0.0           0.0   
/players/zach-fulton-fultoza01                         0.0           0.0   
/players/evan-smith-dietrev01                          0.0           0.0   
/players/landry-jones-jonesla06                        0.0           1.0   
/players/jordan-devey-deveyjo01                        0.0           0.0   
/players/ryan-jensen-jensery01                         0.0           0.0   
/players/marquette-king-kingma02                       0.0           0.0   
/players/jc-tretter-trettjc01                          0.0           0.0   
/players/max-unger-ungerma01                           0.0           0.0   
/players/spencer-pulley-pullesp01                      0.0           0.0   
/players/chris-hubbard-hubbach01                       0.0           0.0   

                                        return_yards  return_td  \
player_url                                                        
/players/todd-gurley-gurleto02                     0        0.0   
/players/leveon-bell-bellle02                      0        0.0   
/players/alvin-kamara-kamaral01                  347        1.0   
/players/tyler-lockett-lockety01                1186        1.0   
/players/kareem-hunt-huntka01                      0        0.0   
/players/dion-lewis-lewisdi01                    570        1.0   
/players/antonio-brown-brownan05                  61        0.0   
/players/lesean-mccoy-mccoyle02                    0        0.0   
/players/melvin-gordon-gordome01                   0        0.0   
/players/tarik-cohen-cohenta01                   855        1.0   
/players/mark-ingram-ingrama02                     0        0.0   
/players/keenan-allen-allenke03                    0        0.0   
/players/julio-jones-jonesju05                     0        0.0   
/players/tyreek-hill-hillty02                    204        1.0   
/players/pharoh-cooper-coopeph01                1331        1.0   
/players/deandre-hopkins-hopkide01                 0        0.0   
/players/leonard-fournette-fournle01               0        0.0   
/players/christian-mccaffrey-mccafch01           220        0.0   
/players/jerick-mckinnon-mckinje02               312        0.0   
/players/carlos-hyde-hydeca01                      0        0.0   
/players/adam-thielen-thielad01                    0        0.0   
/players/ezekiel-elliott-ellioez01                 0        0.0   
/players/jordan-howard-howarjo02                   0        0.0   
/players/michael-thomas-thomami05                  0        0.0   
/players/cj-anderson-andercj01                     0        0.0   
/players/lamar-miller-millela03                    0        0.0   
/players/alex-collins-collial01                   50        0.0   
/players/frank-gore-gorefr01                       0        0.0   
/players/devonta-freeman-freemde01                 0        0.0   
/players/juju-smithschuster-smithju03            240        1.0   
...                                              ...        ...   
/players/brent-qvale-qvalebr01                     0        0.0   
/players/derron-smith-smithde12                    0        0.0   
/players/sam-bradford-bradfsa01                    0        0.0   
/players/teddy-bridgewater-bridgte01               0        0.0   
/players/chris-jones-jonesch15                     0        0.0   
/players/ryan-mallett-mallery01                    0        0.0   
/players/tyler-bray-brayty01                       0        0.0   
/players/brian-mihalik-mihalbr01                   0        0.0   
/players/mike-pouncey-pouncmi01                    0        0.0   
/players/kevin-zeitler-zeitlke01                   0        0.0   
/players/kellen-clemens-clemeke01                  0        0.0   
/players/nick-foles-folesni01                      0        0.0   
/players/chad-henne-hennech01                      0        0.0   
/players/brian-hoyer-hoyerbr01                     0        0.0   
/players/matt-paradis-paradma01                    0        0.0   
/players/josh-harris-harrijo12                     0        0.0   
/players/corey-linsley-linslco01                   0        0.0   
/players/philip-rivers-riverph01                   0        0.0   
/players/rodney-hudson-hudsoro01                   0        0.0   
/players/krishawn-hogan-hogankr01                 -8        0.0   
/players/zach-fulton-fultoza01                     0        0.0   
/players/evan-smith-dietrev01                      0        0.0   
/players/landry-jones-jonesla06                    0        0.0   
/players/jordan-devey-deveyjo01                    0        0.0   
/players/ryan-jensen-jensery01                     0        0.0   
/players/marquette-king-kingma02                   0        0.0   
/players/jc-tretter-trettjc01                      0        0.0   
/players/max-unger-ungerma01                       0        0.0   
/players/spencer-pulley-pullesp01                  0        0.0   
/players/chris-hubbard-hubbach01                   0        0.0   

                                        fantasy_points  
player_url                                              
/players/todd-gurley-gurleto02                  319.30  
/players/leveon-bell-bellle02                   256.60  
/players/alvin-kamara-kamaral01                 253.28  
/players/tyler-lockett-lockety01                126.74  
/players/kareem-hunt-huntka01                   242.20  
/players/dion-lewis-lewisdi01                   193.80  
/players/antonio-brown-brownan05                211.74  
/players/lesean-mccoy-mccoyle02                 204.60  
/players/melvin-gordon-gordome01                230.10  
/players/tarik-cohen-cohenta01                  131.34  
/players/mark-ingram-ingrama02                  220.00  
/players/keenan-allen-allenke03                 176.20  
/players/julio-jones-jonesju05                  163.90  
/players/tyreek-hill-hillty02                   179.36  
/players/pharoh-cooper-coopeph01                 66.24  
/players/deandre-hopkins-hopkide01              213.80  
/players/leonard-fournette-fournle01            194.20  
/players/christian-mccaffrey-mccafch01          157.40  
/players/jerick-mckinnon-mckinje02              139.58  
/players/carlos-hyde-hydeca01                   174.80  
/players/adam-thielen-thielad01                 148.70  
/players/ezekiel-elliott-ellioez01              177.20  
/players/jordan-howard-howarjo02                176.70  
/players/michael-thomas-thomami05               154.50  
/players/cj-anderson-andercj01                  147.10  
/players/lamar-miller-millela03                 157.50  
/players/alex-collins-collial01                 150.00  
/players/frank-gore-gorefr01                    144.60  
/players/devonta-freeman-freemde01              164.20  
/players/juju-smithschuster-smithju03           149.30  
...                                                ...  
/players/brent-qvale-qvalebr01                   -0.20  
/players/derron-smith-smithde12                   0.00  
/players/sam-bradford-bradfsa01                  26.98  
/players/teddy-bridgewater-bridgte01             -1.30  
/players/chris-jones-jonesch15                    0.00  
/players/ryan-mallett-mallery01                   9.94  
/players/tyler-bray-brayty01                     -2.00  
/players/brian-mihalik-mihalbr01                 -0.40  
/players/mike-pouncey-pouncmi01                   0.00  
/players/kevin-zeitler-zeitlke01                 -0.40  
/players/kellen-clemens-clemeke01                -0.06  
/players/nick-foles-folesni01                    35.78  
/players/chad-henne-hennech01                    -0.50  
/players/brian-hoyer-hoyerbr01                   67.88  
/players/matt-paradis-paradma01                   0.00  
/players/josh-harris-harrijo12                    0.00  
/players/corey-linsley-linslco01                  0.00  
/players/philip-rivers-riverph01                280.40  
/players/rodney-hudson-hudsoro01                  0.00  
/players/krishawn-hogan-hogankr01                -0.32  
/players/zach-fulton-fultoza01                    0.00  
/players/evan-smith-dietrev01                     0.00  
/players/landry-jones-jonesla06                   9.56  
/players/jordan-devey-deveyjo01                   0.00  
/players/ryan-jensen-jensery01                    0.00  
/players/marquette-king-kingma02                 -1.40  
/players/jc-tretter-trettjc01                     0.00  
/players/max-unger-ungerma01                      0.00  
/players/spencer-pulley-pullesp01                 0.00  
/players/chris-hubbard-hubbach01                  0.00  

[1745 rows x 28 columns]
"""
