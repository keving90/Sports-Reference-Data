import requests
import bs4
import numpy as np
import pandas as pd


class ProRefScraper(object):
    def __init__(self):
        self._tables = ['rushing', 'passing', 'receiving', 'kicking', 'returns', 'scoring', 'fantasy', 'defense']
        self._possible_cols_for_all_seasons = None
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

    @property
    def tables(self):
        """getter: Returns a list of the possible table types to scrape from."""
        return self._tables

    """
    check table type
    check years
    
    if start == end:
        get single season
    else:
        get multiple seasons
        
    get_single_season:
        keep as is, but should not worry about columns for multiple seasons
        
    get multiple seasons:
        uses get_single_season, but keeps track of cols for all seasons (outside of get_single_season)
        can use logic from current get_data function
    """

    def get_data(self, start_year, end_year, table_type, remove_pro_bowl=True, remove_all_pro=True):
        """
        Gets a data frame of NFL player stats for one for more seasons.

        :param start_year: First season to scrape data from (string or int)
        :param end_year: Final season (inclusive) to scrape data from (string or int)
        :param table_type: Stat category to scrape
        :param remove_pro_bowl:
        :param remove_all_pro:

        :return: Data frame of one or more seasons of data for a given stat.
        """
        self._check_table_type(table_type)
        start_year, end_year = self._check_start_and_end_years(start_year, end_year)

        if start_year == end_year:
            df = self._get_single_season(start_year, table_type)
        else:
            df = self._get_multiple_seasons(start_year, end_year, table_type)

        df.set_index('player_url', inplace=True)

        # Change data from string to numeric, where applicable.
        df = df.apply(pd.to_numeric, errors='ignore')

        if remove_pro_bowl or remove_all_pro:
            self._remove_player_accolades(df, remove_pro_bowl, remove_all_pro)

        # Rename some columns so field goal distance is obvious.
        if table_type.lower() == 'kicking':
            df = df.rename(index=str, columns=self._kicking_cols_to_rename)

        return df

    def _get_multiple_seasons(self, start_year, end_year, table_type):
        # Get seasons to iterate through.
        year_range = self._get_year_range(start_year, end_year)

        data_frames = []

        # Get individual df for each season.
        for year in year_range:
            single_season_df = self._get_single_season(year, table_type)
            data_frames.append(single_season_df)
            self._add_possible_cols_for_all_seasons(list(single_season_df.columns))

        # Combine all seasons into one large df.
        # sort = False prevents FutureWarning when concatenating data frames with different number of columns (1/18/19)
        big_df = pd.concat(data_frames, sort=False)

        # if self._possible_cols_for_all_seasons[-1] != 'year':
        #     self._possible_cols_for_all_seasons.remove('year')
        #     self._possible_cols_for_all_seasons.append('year')
        #     # Reorder columns. Need to create a deep copy in order to prevent a SettingWithCopy warning.
        #     big_df = big_df[self._possible_cols_for_all_seasons].copy()

        return big_df

    def _get_year_range(self, start_year, end_year):
        """
        Uses a start_year and end_year to build a range iterator.

        :param start_year: Year to begin iterator at.
        :param end_year: Year to end iterator at.

        :return: A range iterator.
        """
        # Build range iterator depending on how start_year and end_year are related.
        if start_year > end_year:
            year_range = range(start_year, end_year - 1, -1)
        else:
            year_range = range(start_year, end_year + 1)

        return year_range

    def _check_start_and_end_years(self, start_year, end_year):
        # Convert years to int, if needed.
        if not isinstance(start_year, int):
            try:
                start_year = int(start_year)
            except ValueError:
                raise ValueError('Must input number as type string or int for start_year.')
        if not isinstance(end_year, int):
            try:
                end_year = int(end_year)
            except ValueError:
                raise ValueError('Must input number as type string or int for end_year.')

        return start_year, end_year

    def _get_single_season(self, year, table_type):
        """
        Scrapes a table from Pro Football Reference based on the table_type and puts it into a Pandas data frame.

        :param year: Season's year.
        :param table_type: String representing the type of table to be scraped.

        :return: A data frame of the scraped table for a single season.
        """

        table_rows = self._get_table(year, table_type)
        header_row = self._get_table_headers(table_rows)
        df_cols = self._get_df_columns(header_row, table_type)
        player_elements = self._get_player_elements(table_rows)
        season_data = self._get_player_stats(player_elements)

        # final data frame for single season
        return self._make_df(year, season_data, df_cols, table_type)

    def _get_table(self, year, table_type):
        """
        PROVIDE

        :return: PROVIDE
        """
        # Send a GET request to Pro-Football Reference
        url = 'https://www.pro-football-reference.com/years/' + str(year) + '/' + table_type + '.htm'
        response = requests.get(url)
        response.raise_for_status()

        # Create a BeautifulSoup object.
        soup = bs4.BeautifulSoup(response.text, 'lxml')

        table = soup.find('table', id=table_type)

        if table is None:
            raise AttributeError("Table for '" + table_type + "' stats not found for year " + str(year) + ".")

        # Return the table containing the data.
        return table

    def _get_table_headers(self, table_element):
        """

        :param table_element:
        :return:
        """
        # 'thead' contains the table's header row
        head = table_element.find('thead')

        # 'tr' refers to a table row
        col_names = head.find_all('tr')[-1]

        # 'th' is a table header cell
        return col_names.find_all('th')

    def _get_df_columns(self, header_elements, table_type):
        """

        :param header_elements:
        :return:
        """
        cols_for_single_season = [header_cell['data-stat'] for header_cell in header_elements[1:]]
        cols_for_single_season.insert(1, 'player_url')

        return cols_for_single_season

    def _add_possible_cols_for_all_seasons(self, single_season_cols):
        """

        :param single_season_cols:
        :return:
        """
        if not self._possible_cols_for_all_seasons:
            self._possible_cols_for_all_seasons = single_season_cols
        else:
            new_cols = list(set(single_season_cols) - set(self._possible_cols_for_all_seasons))
            self._possible_cols_for_all_seasons += new_cols

    def _get_table_rows(self, table_element):
        """

        :param table_element:
        :return:
        """
        # tbody is the table's body
        # Get the body of the table
        body = table_element.find('tbody')

        # tr refers to a table row
        # Each element in player_list has data for a single player.
        # This will also collect descriptions of each column found in the web page's table, which
        # is filtered out in create_player_objects().
        return body.find_all('tr')

    def _get_player_elements(self, table_element):
        # tbody is the table's body
        # Get the body of the table
        body = table_element.find('tbody')

        # tr refers to a table row
        # Each element in player_list has data for a single player.
        # This will also collect descriptions of each column found in the web page's table, which
        # is filtered out in create_player_objects().
        return body.find_all('tr')

    def _get_player_stats(self, player_row_elements):
        """

        :param player_row_elements:
        :return:
        """
        # This list holds a dictionary of each object's attributes.
        # Each dictionary is made from the object's __dict__ attribute.
        league_stats = []

        # Get each player's stats, create a Player object, and append the object
        # and the instance's __dict__ to their own list.
        for player in player_row_elements:
            # The <td> tag defines a standard cell in an HTML table.
            # Get a list of cells. This raw web page data represents one player.
            stats = player.find_all('td')

            # If raw_stat_list has data, then we will extract the desired information from the elements.
            # info_list will be empty if the current 'player' in the player_list is actually other
            # irrelevant information we're not interested in (such as a column description).
            if stats:
                # Create a Player object and append the __dict__ attribute to a list.
                # This list is used for the data in our data frame.
                clean_stats = self._get_clean_stats(stats)
                league_stats.append(clean_stats)

        return league_stats

    def _get_clean_stats(self, stat_row):
        """
        Gets clean text stats from a list of BeautifulSoup4 element tags.

        :param raw_stat_list: List of BeautifulSoup4 element ResultSets. Inside of each ResultSet is a stat.

        :return: List of the player's stats as strings.
        """
        clean_player_stats = []
        for stat_cell in stat_row:
            clean_player_stats.append(stat_cell.text)

            # Every tag has an attribute.
            # If the tag's data-stat attribute is 'player', then we get the player's URL.
            if stat_cell['data-stat'] == 'player':
                url = self._get_player_url(stat_cell)
                clean_player_stats.append(url)

        return clean_player_stats

    def _get_player_url(self, player_cell):
        """

        :param player:
        :return:
        """
        # href specifies the URL of the page the link goes to.
        href = player_cell.find_all('a', href=True)

        # Return URL string
        return href[0]['href']

    def _make_df(self, year, league_stats, column_headers, table_type):
        """
        Makes a data frame using a dictionary's keys as column names and list of player_object.__dict__'s as data. The
        player's unique URL is used as the data frame's index.

        :param year: Season's year used to create a unique index for the player's season in the data set.
        :param player_dicts: List of player_object.__dict__'s.
        :param table_type: String to get column names for data frame.

        :return: A data frame.
        """
        # Get data frame's columns from a relevant table dict's keys.
        # df_columns = list(self._tables_dict[table_type]['all_columns'].keys())

        df = pd.DataFrame(data=league_stats, columns=column_headers)
        df.insert(loc=3, column='year', value=year)
        # df['year'] = year

        # Combined player_url + year acts as a unique identifier for a player's season of data.
        df['player_url'] = df['player_url'].apply(lambda x: x + str(year))

        return df

    def _remove_player_accolades(self, df, remove_pro_bowl, remove_all_pro):
        """

        :param remove_pro_bowl:
        :param remove_all_pro:
        :return:
        """
        if remove_pro_bowl and not remove_all_pro:
            df['player'] = df['player'].apply(lambda x: ''.join(x.split('*')))
        elif remove_all_pro and not remove_pro_bowl:
            df['player'] = df['player'].apply(lambda x: ''.join(x.split('+')))
        else:
            df['player'] = df['player'].apply(lambda x: x[:-2])

    def _check_table_type(self, table_type):
        # Only scrapes from tables in self._tables.
        if table_type.lower() not in self._tables:
            raise KeyError("Error, make sure to specify table_type. "
                           + "Can only currently handle the following table names: "
                           + str(self._tables))

# NEED FUNCTIONS TO GET RID OF PRO BOWL AND ALL PRO (*+). MAKE IT OPTIONAL.

ref = ProRefScraper()
# df = ref.get_data(2018, 2018, 'passing')
df = ref.get_data('2005', '2006', 'passing')
df.to_csv('passing05-06.csv')