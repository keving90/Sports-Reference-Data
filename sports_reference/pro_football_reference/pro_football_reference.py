"""
This module contains a class used to scrape NFL data from www.pro-football-reference.com. It stores the data in a
Pandas data frame, which can be saved as a .csv file.
"""

from sports_reference.sports_reference import SportsReference


class ProFootballReference(SportsReference):
    """
    Scrapes NFL data from www.pro-football-reference.com and stores it in a Pandas data frame. Multiple years of data,
    as well as multiple stat types, can be scraped and stored in a single data frame. Possible stat types include:

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

    Class Attributes:
        __stat_types: List of strings representing each possible statistical category.

        __kicking_cols_to_rename: Dictionary helps rename field goal distance column names.

        __oldest_years: Dictionary where keys are stat types and values are the oldest year with data on
                       Pro-Football Reference.
    """
    __stat_types = ['rushing', 'passing', 'receiving', 'kicking', 'returns', 'scoring', 'fantasy', 'defense']
    __kicking_cols_to_rename = {
        'fga1': 'fga_0-19',
        'fgm1': 'fgm_0-19',
        'fga2': 'fga_20-29',
        'fgm2': 'fgm_20-29',
        'fga3': 'fga_30-39',
        'fgm3': 'fgm_30-39',
        'fga4': 'fga_40-49',
        'fgm4': 'fgm_40-49',
        'fga5': 'fga_50_plus',
        'fgm5': 'fgm_50_plus'
    }

    # Dict of oldest year available for each stat type.
    __oldest_years = {
        'rushing': 1932,
        'passing': 1932,
        'receiving': 1932,
        'kicking': 1938,
        'returns': 1941,
        'scoring': 1922,
        'fantasy': 1970,
        'defense': 1940
    }

    def __init__(self):
        super(ProFootballReference, self).__init__()

    @property
    def stat_types(self):
        """getter: Returns a list of the possible stat types to get data for."""
        return ProFootballReference.__stat_types

    @property
    def oldest_years(self):
        """getter: Returns a list of the possible stat types to get data for."""
        return ProFootballReference.__oldest_years

    def get_season_player_stats(self, year=None, years=None, stat_type=None, stat_types=None):
        """
        Overrides SportsReference superclass' get_season_player_stats method. This method does some extra cleaning such
        as combining repeated columns, creating columns for Pro Bowl and All-Pro accolades, and renaming field goal
        columns.
        :param year: Integer or string representing season's year to get data for.
        :param years: Iterable of integers or strings for each season's year.
        :param stat_type: String representing what stat type to get.
        :param stat_types: List of strings for gathering multiple tables and joining them.
        :return: DataFrame of statistics for each player for a given number of seasons and stat type.
        """
        # Call parent class' get_stats() method, then perform our own extra commands.
        df = super(ProFootballReference, self).get_season_player_stats(year, years, stat_type, stat_types)

        # Fill in missing data for main columns (year, team, etc.) and remove extraneous
        # columns created when merging data frames (such as year_receiving, team_rushing, etc.).
        for column_prefix in ['player_', 'team_', 'year_', 'age_', 'pos_', 'g_', 'gs_']:
            self.__clean_repeated_columns(df, column_prefix)

        # Create columns for Pro Bowl and All-Pro appearances, and remove the symbols from each player's name.
        self.__create_accolade_columns(df)
        df['player'] = df['player'].apply(self.__remove_accolade_chars)

        # If we have kicking data, rename some columns so field goal distance is obvious.
        df = self.__rename_field_goal_columns(df, stat_type, stat_types)

        return df

    def __clean_repeated_columns(self, df, column_type):
        """
        Fills in missing data for a main column from other columns with the same prefix, then removes the non-main
        columns. Cleans data frame in place.
        :param df: Data frame
        :param column_type: Common column name suffix between all similar columns, plus an underscore.
        """
        for column in df.columns:
            if column_type in column.lower():
                # Fill main column with data from "prefix + _" type column names.
                df[column_type[:-1]].fillna(df[column], inplace=True)
                # Drop the "prefix + _" type column names.
                df.drop(column, axis=1, inplace=True)

    def __create_accolade_columns(self, df):
        """
        Creates pro_bowl and all_pro columns for each player.
        :param df: DataFrame of NFL players.
        """
        # Convert player column to string to prevent error while creating accolade columns.
        df['player'] = df.player.astype(str)
        df['pro_bowl'] = df['player'].apply(lambda x: True if '*' in x else False)
        df['all_pro'] = df['player'].apply(lambda x: True if '+' in x else False)

    def __remove_accolade_chars(self, string):
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

    def __rename_field_goal_columns(self, df, stat_type, stat_types):
        """Renames some columns in a data frame with kicking stats to make field goal distance is obvious."""
        if (stat_type and stat_type.lower() == 'kicking') or (stat_types and 'kicking' in stat_types):
            df = df.rename(index=str, columns=ProFootballReference.__kicking_cols_to_rename)

        return df

    def get_passing_stats(self, year=None, years=None):
        return self.get_season_player_stats(year=year, years=years, stat_type='passing')

    def get_rushing_stats(self, year=None, years=None):
        return self.get_season_player_stats(year=year, years=years, stat_type='rushing')

    def get_receiving_stats(self, year=None, years=None):
        return self.get_season_player_stats(year=year, years=years, stat_type='receiving')

    def get_kicking_stats(self, year=None, years=None):
        return self.get_season_player_stats(year=year, years=years, stat_type='kicking')

    def get_return_stats(self, year=None, years=None):
        return self.get_season_player_stats(year=year, years=years, stat_type='returns')

    def get_scoring_stats(self, year=None, years=None):
        return self.get_season_player_stats(year=year, years=years, stat_type='scoring')

    def get_fantasy_stats(self, year=None, years=None):
        return self.get_season_player_stats(year=year, years=years, stat_type='fantasy')

    def get_defensive_player_stats(self, year=None, years=None):
        return self.get_season_player_stats(year=year, years=years, stat_type='defense')

    def _create_url(self, year, stat_type):
        return 'https://www.pro-football-reference.com/years/' + str(year) + '/' + stat_type + '.htm'

    def _create_player_url_column(self, df, year):
        # Combined player_url + year acts as a unique identifier for a player's season of data.
        df['player_url'] = df['player_url'].apply(lambda x: x + str(year))


if __name__ == '__main__':
    nfl_stats = ProFootballReference()
    stat_types = ['passing', 'receiving', 'rushing', 'kicking', 'returns', 'scoring', 'fantasy', 'defense']
    # stat_types = ['passing', 'receiving', 'rushing', 'kicking']
    # df = nfl_stats.get_season_player_stats(years=[2018, 2019, 2020], stat_types=stat_types)
    df = nfl_stats.get_season_player_stats(years=[2000, 0, '0'], stat_types=['passing', 'receiving'])
    df.to_csv('sample_data.csv')


