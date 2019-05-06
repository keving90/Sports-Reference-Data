"""
This module contains a NflStatistics class used to scrape NFL data from www.pro-football-reference.com. It places
the data into a Pandas data frame, which can be saved as a CSV file. Built using Python 3.7.0.
"""

import requests
import bs4
import pandas as pd


class NflStatistics(object):
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
    """
    def __init__(self):
        self._stat_types = ['rushing', 'passing', 'receiving', 'kicking', 'returns', 'scoring', 'fantasy', 'defense']
        self._kicking_cols_to_rename = {
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
        self._oldest_years = dict(zip(self._stat_types, [1932, 1932, 1932, 1938, 1941, 1922, 1970, 1932]))

    @property
    def stat_types(self):
        """getter: Returns a list of the possible stat types to scrape from."""
        return self._stat_types

    def get_stats(self, year=None, years=None, stat_type=None):
        if (year is None) == (years is None):
            raise RuntimeError("Need to have an argument for either 'year' or 'years', but not both.")
        elif year:
            df = self._get_single_season(year, stat_type)
        else:
            df = self._get_multiple_seasons(years, stat_type)

        # Unique identifier for each player's season of data.
        df.set_index('player_url', inplace=True)

        # Change data from string to numeric, where applicable.
        df = df.apply(pd.to_numeric, errors='ignore')

        # Create columns for Pro Bowl and All-Pro appearances, and remove the symbols from each player's name.
        df = self.create_accolade_columns(df)
        df['player'] = df['player'].apply(self._remove_chars)

        if stat_type.lower() == 'kicking':
            # For kicking data, rename some columns so field goal distance is obvious.
            df = df.rename(index=str, columns=self._kicking_cols_to_rename)

        return df

    def _get_multiple_seasons(self, years, stat_type):
        """
        Scrapes multiple seasons of data from Pro Football Reference and puts it into a Pandas data frame.
        :param start_year: First season to scrape data from (string or int)
        :param end_year: Final season (inclusive) to scrape data from (string or int)
        :param stat_type: Stat category to scrape
        :return: Data frame with multiple seasons of data for a given stat category.
        """
        # Get seasons to iterate through.
        # year_range = self._get_year_range(start_year, end_year)

        # Get a data frame of each season.
        seasons = [self._get_single_season(year, stat_type) for year in years]

        # Combine all seasons into one large df.
        # sort = False prevents FutureWarning when concatenating data frames with different number of columns (1/18/19)
        big_df = pd.concat(seasons, sort=False)

        return big_df

    def _get_single_season(self, year, stat_type):
        """
        Scrapes a single stat table from Pro Football Reference and puts it into a Pandas data frame.
        :param year: Season's year.
        :param stat_type: String representing the type of stats to be scraped.
        :return: A data frame of the scraped stats for a single season.
        """
        # self._check_year(year, stat_type)

        table = self._get_table(year, stat_type)
        header_row = self._get_table_headers(table)
        df_cols = self._get_df_columns(header_row)
        player_elements = self._get_player_rows(table)

        if not player_elements:
            # Table found, but it doesn't have data.
            raise RuntimeError(stat_type.capitalize() + " stats table found for year " + str(year)
                               + ", but it does not contain data."
                               + " Oldest year with data is " + str(self._oldest_years[stat_type]) + ".")

        season_data = self._get_player_stats(player_elements)

        # Final data frame for single season
        return self._make_df(year, season_data, df_cols)

    def _get_table(self, year, stat_type):
        """
        Sends a GET request to Pro-Football Reference and uses BeautifulSoup to find the HTML table.
        :param year: Season's year.
        :param stat_type: String representing the type of table to be scraped.
        :return: BeautifulSoup table element.
        """
        # Send a GET request to Pro-Football Reference
        url = 'https://www.pro-football-reference.com/years/' + str(year) + '/' + stat_type + '.htm'
        response = requests.get(url)
        response.raise_for_status()

        # Create a BeautifulSoup object.
        soup = bs4.BeautifulSoup(response.text, 'lxml')

        table = soup.find('table', id=stat_type)

        if table is None:
            # No table found
            raise RuntimeError(stat_type.capitalize() + " stats table not found for year " + str(year) + "."
                               + " Oldest year with data is " + str(self._oldest_years[stat_type]) + ".")

        # Return the table containing the data.
        return table

    def _get_table_headers(self, table_element):
        """
        Extracts the top row of a BeautifulSoup table element.
        :param table_element: BeautifulSoup table element.
        :return: List of header cells from a table.
        """
        # 'thead' contains the table's header row
        head = table_element.find('thead')

        # 'tr' refers to a table row
        col_names = head.find_all('tr')[-1]

        # 'th' is a table header cell
        return col_names.find_all('th')

    def _get_df_columns(self, header_elements):
        """
        Extracts stat names from column header cells.
        :param header_elements: List of header cells
        :return: List of stat names.
        """
        cols_for_single_season = [header_cell['data-stat'] for header_cell in header_elements[1:]]
        cols_for_single_season.insert(1, 'player_url')

        return cols_for_single_season

    def _get_player_rows(self, table_element):
        """
        Gets a list of rows from an HTML table.
        :param table_element: HTML table.
        :return: A list of table row elements.
        """
        # 'tbody' is the table's body
        body = table_element.find('tbody')

        # 'tr' refers to a table row
        return body.find_all('tr')

    def _get_player_stats(self, player_row_elements):
        """
        Gets stats for each player in a table for a season.
        :param player_row_elements: List of table rows where each row is a player's season stat line.
        :return: List where each element is a list containing a player's data for the season.
        """
        season_stats = []
        for player in player_row_elements:
            # 'td' is an HTML table cell
            player_stats = player.find_all('td')

            # Some rows do not contain player data.
            if player_stats:
                clean_stats = self._get_clean_stats(player_stats)
                season_stats.append(clean_stats)

        return season_stats

    def _get_clean_stats(self, stat_row):
        """
        Gets clean text stats for a player's season.
        :param stat_row: List of table cells representing a player's stat line for a season.
        :return: List of strings representing a player's season stat line.
        """
        clean_player_stats = []
        for stat_cell in stat_row:
            clean_player_stats.append(stat_cell.text)

            # Also grab the player's URL so they have a unique identifier when combined with the season's year.
            if stat_cell['data-stat'] == 'player':
                url = self._get_player_url(stat_cell)
                clean_player_stats.append(url)

        return clean_player_stats

    def _get_player_url(self, player_cell):
        """
        Get's a player's unique URL.
        :param player_cell: HTML table cell.
        :return: String - player's unique URL.
        """
        # 'href' is the URL of the page the link goes to.
        href = player_cell.find_all('a', href=True)

        # Return URL string
        return href[0]['href']

    def _make_df(self, year, league_stats, column_names):
        """
        :param year: Season's year.
        :param league_stats: List where each element is a list of stats for a single player.
        :param column_names: List used for data frame's column names.
        :return: A data frame.
        """
        df = pd.DataFrame(data=league_stats, columns=column_names)
        df.insert(loc=3, column='year', value=year)  # Column for current year.

        # Combined player_url + year acts as a unique identifier for a player's season of data.
        df['player_url'] = df['player_url'].apply(lambda x: x + str(year))

        return df

    def create_accolade_columns(self, df):
        """
        Creates pro_bowl and all_pro columns for each player.

        :param df: DataFrame of NFL players.
        :return: New DataFrame containing accolade columns.
        """
        df['pro_bowl'] = df['player'].apply(lambda x: True if '*' in x else False)
        df['all_pro'] = df['player'].apply(lambda x: True if '+' in x else False)

        return df

    def _remove_chars(self, string):
        """
        Removes any combination of a single '*' and '+' from the end of a string.
        :param string: String
        :return: String
        """
        if string.endswith('*+'):
            string = string[:-2]
        elif string.endswith('*') or string.endswith('+'):
            string = string[:-1]

        return string
    

if __name__ == '__main__':
    nfl_stats = NflStatistics()
    # df = nfl_stats.get_data(start_year=2017, end_year=2018, stat_type='passing')
    df = nfl_stats.get_stats(year=2000, stat_type='passing')
    df.to_csv('sample_data.csv')
