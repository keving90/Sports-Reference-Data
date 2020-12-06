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

        _oldest_years: Dictionary where keys are stat types and values are the oldest year with data on
                       Pro-Football Reference.
    """
    def __init__(self):
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
        Gets a DataFrame of NFL statistics from Pro-Football Reference for given season years and a given stat type.

        :param year: Integer or string representing season's year to get data for.
        :param years: Iterable of integers or strings for each season's year.
        :param stat_type: String representing what stat type to get.
        :return: DataFrame of NFL statistics.

        """
        if (year is None) == (years is None):
            raise RuntimeError("Need to have an argument for either 'year' or 'years', but not both.")
        elif year:
            df = self.__get_single_season(year, stat_type)
        else:
            df = self.__get_multiple_seasons(years, stat_type)

        # try:
        #     # Assume years is an iterable.
        #     df = self.__get_multiple_seasons(years, stat_type)
        # except TypeError:
        #     # Exception occurs when treating type int as an iterable.
        #     df = self.__get_single_season(years, stat_type)

        # Unique identifier for each player's season of data.
        df.set_index('player_url', inplace=True)

        # Change data from string to numeric, where applicable.
        df = df.apply(pd.to_numeric, errors='ignore')

        # Create columns for Pro Bowl and All-Pro appearances, and remove the symbols from each player's name.
        df = self.__create_accolade_columns(df)
        df['player'] = df['player'].apply(self.__remove_chars)

        if stat_type.lower() == 'kicking':
            # For kicking data, rename some columns so field goal distance is obvious.
            df = df.rename(index=str, columns=self.__kicking_cols_to_rename)

        return df

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

    def __get_multiple_seasons(self, years, stat_type):
        """
        Scrapes multiple seasons of data from Pro Football Reference and puts it into a Pandas data frame.
        :param years: Iterable containing years to get data for.
        :param stat_type: Stat category to get data for.
        :return: Data frame with multiple seasons of data for a given stat category.
        """

        # Get a data frame of each season.
        seasons = [self.__get_single_season(year, stat_type) for year in years]

        # Combine all seasons into one large df.
        # sort = False prevents FutureWarning when concatenating data frames with different number of columns (1/18/19)
        big_df = pd.concat(seasons, sort=False)

        return big_df

    def __get_single_season(self, year, stat_type):
        """
        Scrapes a single stat table from Pro Football Reference and puts it into a Pandas data frame.
        :param year: Season's year.
        :param stat_type: String representing the type of stats to be scraped.
        :return: A data frame of the scraped stats for a single season.
        """

        # get the HTML stat table from from Pro-Football Reference
        table = self.__get_table(year, stat_type)

        # get the header row of the HTML table
        header_row = self.__get_table_headers(table)

        # store each header name in a list (to be used as column names for each stat)
        df_cols = self.__get_df_columns(header_row)

        # get all remaining rows of the HTML table (player stats)
        player_elements = self.__get_player_rows(table)

        # extract each player's stats from the HTML table
        season_data = self.__get_player_stats(player_elements)

        # Final data frame for single season
        return self.__make_df(year, season_data, df_cols)

    def __get_table(self, year, stat_type):
        """
        Sends a GET request to Pro-Football Reference and uses BeautifulSoup to find the HTML table.
        :param year: Season's year.
        :param stat_type: String representing the type of table to be scraped.
        :return: BeautifulSoup table element.
        """
        # Send a GET request to Pro-Football Reference
        url = 'https://www.pro-football-reference.com/years/' + str(year) + '/' + stat_type + '.htm'
        response = requests.get(url)

        # check the GET response
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as HTTPError:
            error_message = "%s - Is %s a valid year?" % (str(HTTPError), year)
            raise requests.exceptions.HTTPError(error_message)

        # Create a BeautifulSoup object.
        soup = bs4.BeautifulSoup(response.text, 'lxml')

        table = soup.find('table', id=stat_type)

        if table is None:
            # No table found
            raise ValueError("No table was found for %s %s at URL: %s" % (year, stat_type, url))

        # Return the table containing the data.
        return table

    def __get_table_headers(self, table_element):
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

    def __get_df_columns(self, header_elements):
        """
        Extracts stat names from column header cells.
        :param header_elements: List of header cells
        :return: List of stat names.
        """
        cols_for_single_season = [header_cell['data-stat'] for header_cell in header_elements[1:]]
        cols_for_single_season.insert(1, 'player_url')

        return cols_for_single_season

    def __get_player_rows(self, table_element):
        """
        Gets a list of rows from an HTML table.
        :param table_element: HTML table.
        :return: A list of table row elements.
        """
        # 'tbody' is the table's body
        body = table_element.find('tbody')

        # 'tr' refers to a table row
        return body.find_all('tr')

    def __get_player_stats(self, player_row_elements):
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
                clean_stats = self.__get_clean_stats(player_stats)
                season_stats.append(clean_stats)

        return season_stats

    def __get_clean_stats(self, stat_row):
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
                url = self.__get_player_url(stat_cell)
                clean_player_stats.append(url)

        return clean_player_stats

    def __get_player_url(self, player_cell):
        """
        Get's a player's unique URL.
        :param player_cell: HTML table cell.
        :return: String - player's unique URL.
        """
        # 'href' is the URL of the page the link goes to.
        href = player_cell.find_all('a', href=True)

        # Return URL string
        return href[0]['href']

    def __make_df(self, year, league_stats, column_names):
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


if __name__ == '__main__':
    nfl_stats = NflStatistics()

    df = nfl_stats.get_stats(year='2021', stat_type='passing')

    # dfs = []
    # dfs.append(nfl_stats.get_passing_stats(year=2018))
    # dfs.append(nfl_stats.get_receiving_stats(year=2018))
    # dfs.append(nfl_stats.get_rushing_stats(year=2018))
    # dfs.append(nfl_stats.get_kicking_stats(year=2018))
    # dfs.append(nfl_stats.get_scoring_stats(year=2018))
    # dfs.append(nfl_stats.get_return_stats(year=2018))
    # dfs.append(nfl_stats.get_fantasy_stats(year=2018))
    # dfs.append(nfl_stats.get_defensive_player_stats(year=2018))

    print(df)

    df.to_csv('sample_data.csv')

    # for i, single_df in enumerate(dfs):
    #     name = "sample_data%d.csv" % i
    #     single_df.to_csv(name)
