"""
This module contains an abstract class used to scrape sports data from www.sports-reference.com. It places
the data into a Pandas data frame, which can be saved as a CSV file. Classes that inherit from SportsReference
can get data from sites such as pro-football-reference.com and basketball-reference.com. Built using Python 3.7.0.
"""

import requests
import bs4
import pandas as pd


class SportsReference(object):
    """
    Abstract class for scraping data from sports-reference.com websites.
    """
    def __init__(self):
        pass

    def get_stats(self, year=None, years=None, stat_type=None):
        """
        Gets a DataFrame of statistics for a certain stat.

        :param year: Integer or string representing season's year to get data for.
        :param years: Iterable of integers or strings for each season's year.
        :param stat_type: String representing what stat type to get.
        :return: DataFrame of statistics.

        """
        if (year is None) == (years is None):
            raise RuntimeError("Need to have an argument for either 'year' or 'years', but not both.")
        elif year:
            df = self.__get_single_season(year, stat_type)
        else:
            df = self.__get_multiple_seasons(years, stat_type)

        # Unique identifier for each player's season of data.
        df.set_index('player_url', inplace=True)

        # Change data from string to numeric, where applicable.
        df = df.apply(pd.to_numeric, errors='ignore')

        return df

    def __get_multiple_seasons(self, years, stat_type):
        """
        Scrapes multiple seasons of data and puts it into a Pandas data frame.
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
        Scrapes a single stat table and puts it into a Pandas data frame.
        :param year: Season's year.
        :param stat_type: String representing the type of stats to be scraped.
        :return: A data frame of the scraped stats for a single season.
        """

        # get the HTML stat table from website
        table = self.__get_table(year, stat_type)

        # get the header row of the HTML table
        header_row = self.__get_table_headers(table)

        # store each header name in a list (to be used as column names for each stat)
        df_cols = self.__get_table_column_names(header_row)

        # get all remaining rows of the HTML table (player stats)
        player_elements = self.__get_player_rows(table)

        # extract each player's stats from the HTML table
        season_data = self.__get_player_stats(player_elements)

        # Final data frame for single season
        return self.__make_df(year, season_data, df_cols)

    def __get_table(self, year, stat_type):
        """
        Sends a GET request to a Sports-Reference website and uses BeautifulSoup to find the HTML table.
        :param year: Season's year.
        :param stat_type: String representing the type of table to be scraped.
        :return: BeautifulSoup table element.
        """
        # Send a GET request to one of the Sports-Reference websites.
        # url = 'https://www.pro-football-reference.com/years/' + str(year) + '/' + stat_type + '.htm'
        # url = 'https://www.basketball-reference.com/leagues/NBA_' + str(year) + '_per_game.html'
        url = self._create_url(year, stat_type)
        response = requests.get(url)

        # Check the GET response
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as HTTPError:
            error_message = "%s - Is %s a valid year?" % (str(HTTPError), year)
            raise requests.exceptions.HTTPError(error_message)

        # Create a BeautifulSoup object.
        soup = bs4.BeautifulSoup(response.text, 'lxml')

        # Get HTML table for this stat type.
        table = soup.find('table', id=stat_type)

        # Empty table is considered an error.
        if table is None:
            raise ValueError("No table was found for %s %s at URL: %s" % (year, stat_type, url))

        return table

    def _create_url(self, year, stat_type):
        """Abstract method for creating URL to get stats from."""
        raise NotImplementedError()

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

    def __get_table_column_names(self, header_elements):
        """
        Extracts stat names from column header cells.
        :param header_elements: List of header cells
        :return: List of stat names.
        """
        # Use the 'data-stat' attribute for each header cell as the column names for our data sets.
        column_names = [header_cell['data-stat'] for header_cell in header_elements[1:]]

        # Insert out own column name, whose values will be a unique identifier for each row.
        column_names.insert(1, 'player_url')

        return column_names

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
        # 'href' is the URL of a player's personal stat page.
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
