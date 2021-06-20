"""
This module contains a class used to scrape NBA data from https://www.basketball-reference.com/m. It stores the data in
a Pandas data frame, which can be saved as a .csv file.
"""

from sports_reference import SportsReference
import re


class BasketballReference(SportsReference):
    """
    Scrapes NBA data from https://www.basketball-reference.com/ and stores it in a Pandas data frame. Multiple years of
    data, as well as multiple stat types, can be scraped and stored in a single data frame. Possible stat types include:

    'per_game_stats': Per game stats (points per game, assists per game, etc.)
    'totals_stats': Season total amounts for various categories (points, rebounds, etc.)
    'per_minute_stats': Receiving data.
    'per_poss_stats': Various stat categories adjusted for a per 36 minutes baseline.
    'advanced_stats': Advanced stat categories such as True Shooting Percentage, Player Efficiency Rating, etc.

    Each player on Basketball Reference has their own unique URL. This URL, combined with the player's team and the
    year for the player's specific season of data, is used as a unique identifier for each row in the data frame. It is
    used as the data frame's index.

    Class Attributes:
        __stat_types: List of strings representing each possible statistical category.
    """
    __stat_types = ['per_game_stats', 'totals_stats', 'per_minute_stats', 'per_poss_stats', 'advanced_stats']

    def __init__(self):
        super(BasketballReference, self).__init__()

    @property
    def stat_types(self):
        """getter: Returns a list of the possible stat types to get data for."""
        return BasketballReference.__stat_types

    def get_season_player_stats(self, year=None, years=None, stat_type=None, stat_types=None):
        # Call parent class' get_stats() method, then perform our own extra commands.
        df = super(BasketballReference, self).get_season_player_stats(year, years, stat_type, stat_types)

        return df

    def _create_url(self, year, stat_type):
        # Extract everything in stat_type before the '_stats' suffix.
        stat_type = re.match('(.*)(_stats)', stat_type)[1]
        return 'https://www.basketball-reference.com/leagues/NBA_' + str(year) + '_' + stat_type + '.html'

    def _create_player_url_column(self, df, year):
        # Combined player_url + team + year acts as a unique identifier for a player's season of data.
        df['player_url'] = df['player_url'] + df['team_id'] + df['year'].astype(str)


if __name__ == '__main__':
    nba_stats = BasketballReference()
    stat_types = ['per_game_stats']
    df = nba_stats.get_season_player_stats(years=[2016, 2017, 2018], stat_types=nba_stats.stat_types)
    df.to_csv('nba_sample_data.csv')


