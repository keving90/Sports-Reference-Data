"""
This module contains an abstract class used to scrape sports data from www.sports-reference.com. It stores the data in
a Pandas data frame, which can be saved as a .csv file. Classes that inherit from the abstract class can get data from
sites such as pro-football-reference.com and basketball-reference.com, among others.
"""

import requests
import bs4
import pandas as pd
import sports_reference.custom_exceptions as ce
from datetime import datetime


class SportsReference(object):
    """
    Abstract class for scraping data from sports-reference.com websites.
    """
    def __init__(self):
        pass

    @property
    def stat_types(self):
        raise NotImplementedError("A subclass must implement this property.")

    @property
    def oldest_years(self):
        raise NotImplementedError("A subclass must implement this property.")

    def __check_args(self, year, years, stat_type, stat_types):
        # year and years are mutually exclusive.
        # stat_type and stat_types are mutually exclusive.
        for arg1, arg2, arg1_name, arg2_name in ((year, years, 'year', 'years'),
                                                 (stat_type, stat_types, 'stat_type', 'stat_types')):
            self.__ensure_mutually_exclusive_args(arg1, arg2, arg1_name, arg2_name)

        # Check for empty values given to args such as '', 0, and [].
        for arg, arg_name in zip(list(locals().values())[1:], ['year', 'years', 'stat_type', 'stat_types']):
            self.__check_for_empty_value_arg(arg, arg_name)

        # Check that years and stat_types args can be iterated over.
        for arg, arg_name in zip((years, stat_types), ('years', 'stat_types')):
            if arg is not None:
                self.__check_for_iterable_arg(arg, arg_name)

        # Check for empty values in iterable args, such as [''] and [0].
        for arg, arg_name in zip((years, stat_types), ('years', 'stat_types')):
            if arg is not None:
                self.__check_for_empty_values_in_iterable_arg(arg, arg_name)

        # Check for stat types that don't exist.
        if stat_type:
            self.__check_for_invalid_stat_type(stat_type)
        elif stat_types:
            for stat in stat_types:
                self.__check_for_invalid_stat_type(stat)

        if year and stat_type:
            if year < self.oldest_years[stat_type]:
                raise ValueError(f"{year} is not a valid year for {stat_type}. Oldest year is "
                                 f"{self.oldest_years[stat_type]}")
        if year and stat_types:
            for stat in stat_types:
                if year < self.oldest_years[stat]:
                    raise ValueError(f"{year} is not a valid year for {stat}. Oldest year is "
                                     f"{self.oldest_years[stat]}")
        if years and stat_type:
            for yr in years:
                if yr < self.oldest_years[stat_type]:
                    raise ValueError(f"{yr} is not a valid year for {stat_type}. Oldest year is "
                                     f"{self.oldest_years[stat_type]}")
        if years and stat_types:
            for yr in years:
                for stat in stat_types:
                    if yr < self.oldest_years[stat]:
                        raise ValueError(f"{yr} is not a valid year for {stat}. Oldest year is "
                                         f"{self.oldest_years[stat]}")

        current_year = datetime.now().year
        if year:
            if year > current_year:
                raise ValueError(f"year value of {year} is greater than current year ({current_year}).")
            stat_arg = None
            if stat_type:
                stat_arg = [stat_type]
            elif stat_types:
                stat_arg = stat_types

        elif years:
            pass

        year_arg = self.__get_mutually_exclusive_arg(year, years)
        stat_arg = self.__get_mutually_exclusive_arg(stat_type, stat_types)

        for stat in stat_arg:
            for yr in year_arg:
                if yr < self.oldest_years[stat]:
                    raise ValueError(f"{yr} is not a valid year for {stat}. Oldest year for {stat} is "
                                     f"{self.oldest_years[stat]}")

    def __get_mutually_exclusive_arg(self, value_arg, iterable_arg):
        mutually_exclusive_arg = None
        if value_arg:
            mutually_exclusive_arg = [value_arg]
        elif iterable_arg:
            mutually_exclusive_arg = iterable_arg
        return mutually_exclusive_arg

    def __check_for_iterable_arg(self, arg, arg_name):
        try:
            [i for i in arg]
        except TypeError as e:
            raise ce.NotIterableError(f"Cannot iterate over years args. Received {arg_name}")

    def __ensure_mutually_exclusive_args(self, arg1, arg2, arg1_name, arg2_name):
        if (arg1 is not None) == (arg2 is not None):
            raise ce.MutuallyExclusiveArgsError(f"Need to provide an argument for either '{arg1_name}' or "
                                                f"'{arg2_name}', but not both.")

    def __check_for_empty_value_arg(self, arg, arg_name):
        if (not arg) and (arg is not None):
            raise ce.EmptyValueError(f"{arg_name} arg must be non-zero or not be empty. Received {arg}")

    def __check_for_empty_values_in_iterable_arg(self, arg, arg_name):
        for item in arg:
            if not item:
                raise ce.EmptyValueError(f"'{arg_name}' arg contains a non-zero or empty value: {item}")

    def __check_for_invalid_stat_type(self, stat_type):
        if stat_type not in self.stat_types:
            raise ce.InvalidStatTypeError(f"Invalid stat_type of: {stat_type}.  "
                                          f"Valid stat types include: {self.stat_types}")

    def get_season_player_stats(self, year=None, years=None, stat_type=None, stat_types=None):
        """
        Gets a DataFrame of statistics for specified stats over a given amount of seasons.
        :param year: Integer or string representing season's year to get data for.
        :param years: Iterable of integers or strings for each season's year.
        :param stat_type: String representing what stat type to get.
        :param stat_types: List of strings for gathering multiple tables and joining them
        :return: DataFrame of statistics.
        """
        self.__check_args(year, years, stat_type, stat_types)
        df = None
        if stat_type:
            # Get one or more years of data for just one stat type.
            df = self.__get_stat_data_for_all_years(year=year, years=years, stat_type=stat_type)
        elif stat_types:
            # Get one or more years of data for multiple stats types.
            sports_data_tables = self.__get_data_for_all_stat_types(year=year, years=years, stat_types=stat_types)
            if len(sports_data_tables) > 1:
                df = self.__merge_data_frames(sports_data_tables, stat_types)
            elif len(sports_data_tables) == 1:
                df = sports_data_tables[0]

        # Change data from string to numeric, where applicable.
        df = df.apply(pd.to_numeric, errors='ignore')

        return df

    def __get_data_for_all_stat_types(self, year=None, years=None, stat_types=None):
        """
        Gets one or more years of data for one or more different stat types. One year's worth of data for one stat type
        is stored in its own data frame.
        :param year: Single year.
        :param years: List of years.
        :param stat_types: List of stat types.
        :return: List of data frames.
        """
        stat_data_frames = []
        for stat in stat_types:
            if not stat:
                raise ce.NoStatTypeError(f"No value given for stat_type. Received: '{stat}'")
            df = self.__get_stat_data_for_all_years(year=year, years=years, stat_type=stat)
            stat_data_frames.append(df)

        return stat_data_frames

    def __get_stat_data_for_all_years(self, year=None, years=None, stat_type=None):
        """
        Returns a data frame of a specific stat type for all years provided.
        :param year: Single year
        :param years: List of years
        :param stat_type: String representing stat type
        :return: Data frame, all of a specific stat type over a specified number of years.
        """
        df = None
        if year:
            df = self.__get_single_season(year, stat_type)
        elif years:
            df = self.__get_multiple_seasons(years, stat_type)
        df.set_index('player_url', inplace=True)

        return df

    def __merge_data_frames(self, data_frames, stat_types):
        """
        Merges a list of data frames.
        :param data_frames: List of data frames.
        :param stat_types: List of stat types.
        :return: Single, merged data frame.
        """
        df = None
        # Merge first two data frames together, if needed.
        if len(data_frames) >= 2:
            df = data_frames[0].merge(data_frames[1], on='player_url', how='outer', suffixes=('', '_' + stat_types[1]))
        # Merge remaining data frames to the main data frame, if necessary.
        if len(data_frames) > 2:
            for stat, table in zip(stat_types[2:], data_frames[2:]):
                df = df.merge(table, on='player_url', how='outer', suffixes=('', '_' + stat))

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
        raise NotImplementedError("A subclass must implement this method.")

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
        self._create_player_url_column(df, year)

        return df

    def _create_player_url_column(self, df, year):
        """Abstract method for creating player_url column to use as an index."""
        raise NotImplementedError("A subclass must implement this method.")
