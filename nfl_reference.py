"""
This module contains a NflStatistics class used to scrape NFL data from www.pro-football-reference.com. It places
the data into a Pandas data frame, which can be saved as a CSV file. Built using Python 3.7.0.
"""

import requests
import bs4
import pandas as pd
from sports_reference import SportsReference


class NflReference(SportsReference):
    """
    Scrapes NFL data from www.pro-football-reference.com and places it into a Pandas data frame. Multiple years of data
    can be scraped and placed into a single data frame for the same statistical category. Each category is referred to
    as a 'stat type'. Possible stat types include:

    'rushing': Rushing data.
    'passing': Passing data.
    'receiving': Receiving data.
    'kicking': Field goal, point after touchdown, and punt data.
    'returns': Punt and kick return data.
    'scoring': All types of scoring data, such as touchdowns (defense/offense), two point conversions, kicking, etc.
    'fantasy': Rushing, receiving, and passing stats, along with fantasy point totals from various leagues.
    'defense': Defensive player stats.

    Each player on Pro Football Reference has their own unique URL. This URL, combined with the year for the player's
    specific season of data, is used as a unique identifier for each row in the data frame. It is used as the data
    frame's index.

    Instance Attributes:
        _stat_types: List of strings representing each possible statistical category. Not to be modified.

        _kicking_cols_to_rename: Dictionary helps rename field goal distance column names. Not to be modified.

        _oldest_years: Dictionary where keys are stat types and values are the oldest year with data on
                       Pro-Football Reference.
    """
    def __init__(self):
        super(NflReference, self).__init__()
        self.__stat_types = ['rushing', 'passing', 'receiving', 'kicking', 'returns', 'scoring', 'fantasy', 'defense']
        self.__kicking_cols_to_rename = {
            'fga1': 'att_0-19',
            'fgm1': 'made_0-19',
            'fga2': 'att_20-29',
            'fgm2': 'made_20-29',
            'fga3': 'att_30-39',
            'fgm3': 'made_30-39',
            'fga4': 'att_40-49',
            'fgm4': 'made_40-49',
            'fga5': 'att_50_plus',
            'fgm5': 'made_50_plus'
        }

        # Dict of oldest year available for each stat type.
        self.__oldest_years = {
            'rushing': 1932,
            'passing': 1932,
            'receiving': 1932,
            'kicking': 1938,
            'returns': 1941,
            'scoring': 1922,
            'fantasy': 1970,
            'defense': 1940
        }

    @property
    def stat_types(self):
        """getter: Returns a list of the possible stat types to scrape from."""
        return self.__stat_types

    def get_stats(self, year=None, years=None, stat_type=None):
        """
        Overrides SportsReference superclass' get_stats method. This new calls the
        :param year:
        :param years:
        :param stat_type:
        :return:
        """
        df = super(NflReference, self).get_stats(year, years, stat_type)

        # Create columns for Pro Bowl and All-Pro appearances, and remove the symbols from each player's name.
        df = self.__create_accolade_columns(df)
        df['player'] = df['player'].apply(self.__remove_chars)

        if stat_type.lower() == 'kicking':
            # For kicking data, rename some columns so field goal distance is obvious.
            df = df.rename(index=str, columns=self.__kicking_cols_to_rename)

        return df

    def __create_accolade_columns(self, df):
        """
        Creates pro_bowl and all_pro columns for each player.

        :param df: DataFrame of NFL players.
        :return: New DataFrame containing accolade columns.
        """
        df['pro_bowl'] = df['player'].apply(lambda x: True if '*' in x else False)
        df['all_pro'] = df['player'].apply(lambda x: True if '+' in x else False)

        return df

    def __remove_chars(self, string):
        """
        Removes any combination of a single '*' and '+' from the end of a string.
        :param string: String to remove characters from.
        :return: Modified string.
        """
        if string.endswith('*+'):
            string = string[:-2]
        elif string.endswith('*') or string.endswith('+'):
            string = string[:-1]

        return string

    def get_passing_stats(self, year=None, years=None):
        return self.get_stats(year=year, years=years, stat_type='passing')

    def get_rushing_stats(self, year=None, years=None):
        return self.get_stats(year=year, years=years, stat_type='rushing')

    def get_receiving_stats(self, year=None, years=None):
        return self.get_stats(year=year, years=years, stat_type='receiving')

    def get_kicking_stats(self, year=None, years=None):
        return self.get_stats(year=year, years=years, stat_type='kicking')

    def get_return_stats(self, year=None, years=None):
        return self.get_stats(year=year, years=years, stat_type='returns')

    def get_scoring_stats(self, year=None, years=None):
        return self.get_stats(year=year, years=years, stat_type='scoring')

    def get_fantasy_stats(self, year=None, years=None):
        return self.get_stats(year=year, years=years, stat_type='fantasy')

    def get_defensive_player_stats(self, year=None, years=None):
        return self.get_stats(year=year, years=years, stat_type='defense')

    def _create_url(self, year, stat_type):
        return 'https://www.pro-football-reference.com/years/' + str(year) + '/' + stat_type + '.htm'


if __name__ == '__main__':
    nfl_stats = NflReference()

    df = nfl_stats.get_stats(year=2019, stat_type='passing')

    print(df)

    # dfs = []
    # dfs.append(nfl_stats.get_passing_stats(year=2018))
    # dfs.append(nfl_stats.get_receiving_stats(year=2018))
    # dfs.append(nfl_stats.get_rushing_stats(year=2018))
    # dfs.append(nfl_stats.get_kicking_stats(year=2018))
    # dfs.append(nfl_stats.get_scoring_stats(year=2018))
    # dfs.append(nfl_stats.get_return_stats(year=2018))
    # dfs.append(nfl_stats.get_fantasy_stats(year=2018))
    # dfs.append(nfl_stats.get_defensive_player_stats(year=2018))

    # for i, single_df in enumerate(dfs):
    #     name = "sample_data%d.csv" % i
    #     single_df.to_csv(name)

    df.to_csv('sample_data.csv')

