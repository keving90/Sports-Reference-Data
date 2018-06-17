#!/usr/bin/env python3

"""
This module contains functions for scraping data from pro-football-reference.com tables based on a given table ID,
creating Player objects from the data, and saving the data into a data frame.
"""

import requests
import bs4
import pandas as pd
from player import Player
import constants
import football_db_scraper as fbdb


def scrape_table(url, table_id):
    """
    Scrape a table from pro-football-reference.com based on provided table ID.

    :param url: Websites URL.
    :param table_id: Identifier for the table. Found when used "inspect element" on web page.

    :return: List of BeautifulSoup4 element ResultSets. Each item in list is a row in the table.
    """
    # Send a GET request to Pro Football Reference's Rushing & Receiving page to gather the data.
    r = requests.get(url)
    r.raise_for_status()

    # Create a BeautifulSoup object.
    soup = bs4.BeautifulSoup(r.text, 'lxml')

    # Find the first table with tag 'table' and id 'rushing_and_receiving
    table = soup.find('table', id=table_id)

    # tbody is the table's body
    # Get the body of the table
    body = table.find('tbody')

    # tr refers to a table row
    # Each row in player_list has data for a single player
    # This will also collect descriptions of each column found in the web page's table, which
    # is filtered out in create_player_objects().
    player_list = body.find_all('tr')

    return player_list


def create_player_objects(player_list, header):
    """
    Create an object for each player using the player_list created by scrape_data().

    :param player_list: List of BeautifulSoup4 element ResultSets. Each item in list is a row in the table.
    :param header: Dictionary where keys are the name of the stat and values are the data type.

    :return: List of dictionary representations of Player objects (object.__dict__).
    """
    # This list holds a dictionary of each object's attributes.
    # Each dictionary is made from the object's __dict__ attribute.
    list_of_player_dicts = []

    # Get each player's stats, create a Player object, and append the object
    # and the instance's __dict__ to their own list
    for player in player_list:
        # The <td> tag defines a standard cell in an HTML table.
        # Get a list of cells. This raw web page data represents one player.
        raw_stat_list = player.find_all('td')

        # If info_list has data, then we will extract the desired information from the elements.
        # info_list will be empty if the current 'player' in the player_list is actually other
        # irrelevant information we're not interested in (such as a column description).
        if raw_stat_list:
            player_stats = get_player_stats(raw_stat_list)
            # Create a Player object and append the __dict__ attribute to a list.
            # This list is used for the data in our data frame.
            obj = Player(player_stats, header)
            list_of_player_dicts.append(obj.__dict__)

    return list_of_player_dicts


def get_player_stats(raw_stat_list):
    """
    Used in create_player_objects() to get text data from from a BeautifulSoup4 element tag.
    Also gets a URL to the player's personal career stat page.

    :param raw_stat_list: List of BeautifulSoup4 element ResultSets. Inside of each ResultSet is a stat.

    :return: List of the player's stats in text form.
    """
    clean_player_stats = []
    for stat in raw_stat_list:
        clean_player_stats.append(stat.text)  # Grab the text representing the given stat.
        if stat['data-stat'] == 'player':
            # Every tag has an attribute.
            # If the tag's data-stat attribute is 'player', then we get the player's URL.
            # get_player_url(stat, player_info)
            href = stat.find_all('a', href=True)  # Get href, which specifies the URL of the page the link goes to
            url = href[0]['href']  # Get the URL string
            clean_player_stats.append(url)

    return clean_player_stats


def make_data_frame(player_dict_list, year, header, fantasy=False):
    """
    Create a new data frame and return it.

    :param player_dict_list: List of unique Player.__dict__'s.
    :param year: NFL season's year.
    :param header: Dictionary from constants.py used to create data frame columns.
    :param fantasy: When true, add a column for player's total fantasy points for the season.

    :return: Data frame of stats.
    """
    df_columns = list(header.keys())                              # Get header dict's keys for df's column names.
    df = pd.DataFrame(data=player_dict_list, columns=df_columns)  # Create the data frame.
    df['year'] = year                                             # Add a 'year' column.
    df.set_index('name', inplace=True)                            # Make 'name' the data frame's index

    for stat in df_columns[5:]:
        df[stat].fillna(0, inplace=True)   # Fill missing stats with 0.

    if fantasy:
        df = get_fantasy_points(df, year)  # Create fantasy_points column in df.

    return df


def get_fantasy_points(df, year, fantasy_settings=constants.FANTASY_SETTINGS_DICT):
    """
    Inserts 'fumbles_lost', 'two_pt_conversions', 'return_yards', 'return_td', and 'fantasy_points' columns into df.
    Calculates fantasy points based on a fantasy settings dictionary.

    :param df: Data frame to be modified.
    :param year: Current season.
    :param fantasy_settings: Dictionary where keys are a stat and values are the point value.

    :return: New data frame with fantasy point calculation.
    """
    for table_name in ['fumble', 'kick return', 'punt return', 'conversion']:
        stat_df = fbdb.get_df(year, table_name)  # Scrape table from footballdb.com and make a data frame.
        df = df.join(stat_df, how='left')        # Join stat data frame to main data frame.

    # Replace NaN data with 0, otherwise fantasy calculations with have NaN results for players with missing data.
    stat_list = ['fumbles_lost', 'two_pt_conversions', 'kick_return_yards', 'kick_return_td', 'punt_return_yards',
                 'punt_return_td']
    [df[column].fillna(0, inplace=True) for column in stat_list]

    df['return_yards'] = df['kick_return_yards'] + df['punt_return_yards']  # Calculate total return yards.
    df['return_td'] = df['kick_return_td'] + df['punt_return_td']           # Calculate total return touchdowns.

    # Drop individual return yards and touchdown stats.
    dropped_stats = ['kick_return_yards', 'punt_return_yards', 'kick_return_td', 'punt_return_td']
    [df.drop(stat, axis=1, inplace=True) for stat in dropped_stats]

    # Insert the fantasy_points column and calculate each player's fantasy point total.
    df['fantasy_points'] = 0
    for stat, value in fantasy_settings.items():
        if stat in df.columns:
            df['fantasy_points'] += df[stat] * value

    return df


def scrape_game_log(player_url, year):
    """
    Scrapes regular season stats from a player's game log for a specific year.

    :param player_url: String representing player's unique URL found in the "Rushing and Receiving" table.
    :param year: Season's year for the game log.

    :return: Data frame where each row is the stats for a game.
    """
    # Remove the '.htm' part of the player's url if necessary.
    if player_url.endswith('.htm'):
        player_url = player_url[:-4]

    # Build the URL to the player's game log page
    url = 'https://www.pro-football-reference.com' + player_url + '/gamelog/' + str(year) + '/'

    # ID used to identify the regular season stats table.
    table_id = 'stats'

    # Get the data from the game log page.
    data = scrape_table(url, table_id)

    # Use the appropriate header dictionary based on the number of elements in data list.
    if not data[0]:
        print('Error in game_log_scraper().')
        print('Can only currently handle logs with rush and rec data, or with rush, rec, and pass data.')
        exit(1)
    elif len(data[0]) == 33:
        header = constants.LOG_RUSH_REC_PASS_HEADER
    elif len(data[0]) == 21:
        header = constants.LOG_RUSH_REC_HEADER

    list_of_log_dicts = create_player_objects(data, header)
    df = make_data_frame(list_of_log_dicts, year, header, constants.FANTASY_SETTINGS_DICT)

    return df


if __name__ == '__main__':
    """Usage example."""
    # Set the year.
    season_year = 2017

    # Create url for given season.
    input_url = 'https://www.pro-football-reference.com/years/' + str(season_year) + '/rushing.htm'

    # Identify the table ID to get scrape from the correct table.
    input_table_id = 'rushing_and_receiving'

    # Scrape the data to get a list of each player's web page elements.
    elem_list = scrape_table(input_url, input_table_id)

    # Use the elements to create Player objects.
    player_dicts = create_player_objects(elem_list, constants.SEASON_RUSH_REC_HEADER)

    # Create a data frame for the season.
    output_df = make_data_frame(player_dicts, season_year, constants.SEASON_RUSH_REC_HEADER, fantasy=True)

    print(output_df)
    # output_df.to_csv('results.csv')


"""
Sample output:

                                        url team  age position  games_played  \
name                                                                           
Aaron Jones         /players/J/JoneAa00.htm  GNB   23       rb            12   
Aaron Ripkowski     /players/R/RipkAa00.htm  GNB   25       fb            16   
Aaron Rodgers       /players/R/RodgAa00.htm  GNB   34       qb             7   
Adam Humphries      /players/H/HumpAd00.htm  TAM   24       wr            16   
Adam Thielen        /players/T/ThieAd00.htm  MIN   27       WR            16   
Adoree' Jackson     /players/J/JackAd00.htm  TEN   22       CB            16   
Adrian Peterson     /players/P/PeteAd01.htm  2TM   32      NaN            10   
Akeem Hunt          /players/H/HuntAk01.htm  KAN   24      NaN            15   
Albert Wilson       /players/W/WilsAl02.htm  KAN   25       wr            13   
Alex Collins        /players/C/CollAl00.htm  BAL   23       RB            15   
Alex Erickson       /players/E/EricAl01.htm  CIN   25      NaN            16   
Alex Smith          /players/S/SmitAl03.htm  KAN   33       QB            15   
Alfred Blue         /players/B/BlueAl00.htm  HOU   26      NaN            11   
Alfred Morris       /players/M/MorrAl00.htm  DAL   29       rb            14   
Alvin Kamara        /players/K/KamaAl00.htm  NOR   22    fb/rb            16   
Amari Cooper        /players/C/CoopAm00.htm  OAK   23       WR            14   
Ameer Abdullah      /players/A/AbduAm00.htm  DET   24       RB            14   
Andre Ellington     /players/E/ElliAn00.htm  2TM   28      NaN            12   
Andre Williams      /players/W/WillAn00.htm  LAC   25      NaN             8   
Andy Dalton         /players/D/DaltAn00.htm  CIN   30       QB            16   
Andy Janovich       /players/J/JanoAn00.htm  DEN   24       fb            16   
Anthony Sherman     /players/S/SherAn00.htm  KAN   29       fb            16   
ArDarius Stewart    /players/S/StewAr00.htm  NYJ   24       wr            15   
Austin Davis        /players/D/DaviAu00.htm  SEA   28      NaN             3   
Austin Ekeler       /players/E/EkelAu00.htm  LAC   22      NaN            16   
Ben Roethlisberger  /players/R/RoetBe00.htm  PIT   35       QB            15   
Benny Cunningham    /players/C/CunnBe01.htm  CHI   27      NaN            14   
Bernard Reedy       /players/R/ReedBe01.htm  2TM   26      NaN            11   
Bilal Powell        /players/P/PoweBi00.htm  NYJ   29       RB            15   
Blaine Gabbert      /players/G/GabbBl00.htm  ARI   28       qb             5   
...                                     ...  ...  ...      ...           ...   
Terron Ward         /players/W/WardTe00.htm  ATL   25      NaN            14   
Tevin Coleman       /players/C/ColeTe01.htm  ATL   24    fb/rb            15   
Theo Riddick        /players/R/RiddTh00.htm  DET   26       rb            16   
Thomas Rawls        /players/R/RawlTh00.htm  SEA   24       rb            12   
Tion Green          /players/G/GreeTi00.htm  DET   24      NaN             5   
Todd Gurley         /players/G/GurlTo01.htm  LAR   23       RB            15   
Tom Brady           /players/B/BradTo00.htm  NWE   40       QB            16   
Tom Savage          /players/S/SavaTo00.htm  HOU   27       qb             8   
Tommy Bohanon       /players/B/BohaTo00.htm  JAX   27       FB            16   
Tommylee Lewis      /players/L/LewiTo00.htm  NOR   25      NaN            15   
Torrey Smith        /players/S/SmitTo02.htm  PHI   28       WR            16   
Travaris Cadet      /players/C/CadeTr00.htm  2TM   28      NaN             9   
Travis Benjamin     /players/B/BenjTr00.htm  LAC   28       wr            16   
Travis Kelce        /players/K/KelcTr00.htm  KAN   28       TE            15   
Trevor Davis        /players/D/DaviTr03.htm  GNB   24      NaN            16   
Trevor Siemian      /players/S/SiemTr00.htm  DEN   26       QB            11   
Trey Edmunds        /players/E/EdmuTr00.htm  NOR   23      NaN            16   
Ty Montgomery       /players/M/MontTy01.htm  GNB   24       rb             8   
Tyler Bray          /players/B/BrayTy00.htm  KAN   26      NaN             1   
Tyler Ervin         /players/E/ErviTy00.htm  HOU   24      NaN             4   
Tyler Lockett       /players/L/LockTy00.htm  SEA   25       WR            16   
Tyreek Hill         /players/H/HillTy00.htm  KAN   23       WR            15   
Tyrod Taylor        /players/T/TaylTy00.htm  BUF   28       QB            15   
Vince Mayle         /players/M/MaylVi00.htm  BAL   26      NaN            16   
Wayne Gallman       /players/G/GallWa00.htm  NYG   23       rb            13   
Wendell Smallwood   /players/S/SmalWe00.htm  PHI   23       rb             8   
Wil Lutz            /players/L/LutzWi00.htm  NOR   23        K            16   
Will Fuller         /players/F/FullWi01.htm  HOU   23       WR            10   
Zach Line           /players/L/LineZa01.htm  NOR   27       fb            12   
Zach Zenner         /players/Z/ZennZa00.htm  DET   26      NaN             8   

                    games_started  rush_attempts  rush_yards  rush_td  \
name                                                                    
Aaron Jones                     4             81         448        4   
Aaron Ripkowski                 2              5          13        0   
Aaron Rodgers                   7             24         126        0   
Adam Humphries                  3              1           6        0   
Adam Thielen                   16              1          11        0   
Adoree' Jackson                16              5          55        0   
Adrian Peterson                 7            156         529        2   
Akeem Hunt                      0              8          23        0   
Albert Wilson                   7              3           6        0   
Alex Collins                   12            212         973        6   
Alex Erickson                   0              5          16        0   
Alex Smith                     15             60         355        1   
Alfred Blue                     0             71         262        1   
Alfred Morris                   5            115         547        1   
Alvin Kamara                    3            120         728        8   
Amari Cooper                   12              1           4        0   
Ameer Abdullah                 11            165         552        4   
Andre Ellington                 2             20          55        1   
Andre Williams                  0              9          25        0   
Andy Dalton                    16             38          99        0   
Andy Janovich                   4              6          12        1   
Anthony Sherman                 3             14          40        1   
ArDarius Stewart                2              7          27        0   
Austin Davis                    0              1          -1        0   
Austin Ekeler                   0             47         260        2   
Ben Roethlisberger             15             28          47        0   
Benny Cunningham                0              9          29        0   
Bernard Reedy                   0              3          17        0   
Bilal Powell                   10            178         772        5   
Blaine Gabbert                  5             23          82        0   
...                           ...            ...         ...      ...   
Terron Ward                     0             30         129        0   
Tevin Coleman                   3            156         628        5   
Theo Riddick                    5             84         286        3   
Thomas Rawls                    3             58         157        0   
Tion Green                      0             42         165        2   
Todd Gurley                    15            279        1305       13   
Tom Brady                      16             25          28        0   
Tom Savage                      7              4           2        0   
Tommy Bohanon                  10              5           5        2   
Tommylee Lewis                  0              2          14        0   
Torrey Smith                   14              1          -3        0   
Travaris Cadet                  0             23          96        0   
Travis Benjamin                 3             13          96        0   
Travis Kelce                   15              2           7        0   
Trevor Davis                    0              2          13        0   
Trevor Siemian                 10             31         127        1   
Trey Edmunds                    0              9          48        1   
Ty Montgomery                   5             71         273        3   
Tyler Bray                      0              1           0        0   
Tyler Ervin                     0              4          12        0   
Tyler Lockett                   8             10          58        0   
Tyreek Hill                    13             17          59        0   
Tyrod Taylor                   14             84         427        4   
Vince Mayle                     0              2           2        1   
Wayne Gallman                   1            111         476        0   
Wendell Smallwood               3             47         174        1   
Wil Lutz                        0              1           4        0   
Will Fuller                    10              2           9        0   
Zach Line                       4              7          28        0   
Zach Zenner                     0             14          26        1   

                    longest_run       ...        catch_percentage  \
name                                  ...                           
Aaron Jones                  46       ...                    50.0   
Aaron Ripkowski               4       ...                    70.0   
Aaron Rodgers                18       ...                     0.0   
Adam Humphries                6       ...                    73.5   
Adam Thielen                 11       ...                    64.1   
Adoree' Jackson              20       ...                     0.0   
Adrian Peterson              27       ...                    57.9   
Akeem Hunt                   11       ...                    57.1   
Albert Wilson                 6       ...                    67.7   
Alex Collins                 50       ...                    63.9   
Alex Erickson                14       ...                    75.0   
Alex Smith                   70       ...                     0.0   
Alfred Blue                  48       ...                    77.8   
Alfred Morris                70       ...                    77.8   
Alvin Kamara                 74       ...                    81.0   
Amari Cooper                  4       ...                    50.0   
Ameer Abdullah               34       ...                    71.4   
Andre Ellington              14       ...                    66.1   
Andre Williams                7       ...                     0.0   
Andy Dalton                  25       ...                     0.0   
Andy Janovich                 4       ...                    66.7   
Anthony Sherman               9       ...                    75.0   
ArDarius Stewart             11       ...                    46.2   
Austin Davis                 -1       ...                     0.0   
Austin Ekeler                35       ...                    77.1   
Ben Roethlisberger           14       ...                     0.0   
Benny Cunningham             12       ...                    76.9   
Bernard Reedy                10       ...                   100.0   
Bilal Powell                 75       ...                    69.7   
Blaine Gabbert               12       ...                     0.0   
...                         ...       ...                     ...   
Terron Ward                  17       ...                   100.0   
Tevin Coleman                52       ...                    69.2   
Theo Riddick                 21       ...                    74.6   
Thomas Rawls                 23       ...                    69.2   
Tion Green                   33       ...                   100.0   
Todd Gurley                  57       ...                    73.6   
Tom Brady                     7       ...                     0.0   
Tom Savage                    3       ...                     0.0   
Tommy Bohanon                 3       ...                    54.5   
Tommylee Lewis                8       ...                    71.4   
Torrey Smith                 -3       ...                    53.7   
Travaris Cadet               12       ...                    84.2   
Travis Benjamin              22       ...                    54.8   
Travis Kelce                  4       ...                    68.0   
Trevor Davis                  9       ...                    71.4   
Trevor Siemian               15       ...                     0.0   
Trey Edmunds                 41       ...                     0.0   
Ty Montgomery                37       ...                    74.2   
Tyler Bray                    0       ...                     0.0   
Tyler Ervin                   6       ...                    72.7   
Tyler Lockett                22       ...                    63.4   
Tyreek Hill                  16       ...                    71.4   
Tyrod Taylor                 32       ...                     0.0   
Vince Mayle                   2       ...                     0.0   
Wayne Gallman                24       ...                    70.8   
Wendell Smallwood            26       ...                    72.2   
Wil Lutz                      4       ...                     0.0   
Will Fuller                   5       ...                    56.0   
Zach Line                     9       ...                    40.0   
Zach Zenner                  14       ...                     0.0   

                    scrimmage_yards  rush_rec_td  fumbles  year  fumbles_lost  \
name                                                                            
Aaron Jones                     470            4        0  2017           0.0   
Aaron Ripkowski                  52            0        0  2017           0.0   
Aaron Rodgers                   126            0        1  2017           1.0   
Adam Humphries                  637            1        1  2017           1.0   
Adam Thielen                   1287            4        3  2017           2.0   
Adoree' Jackson                  55            0        1  2017           1.0   
Adrian Peterson                 599            2        3  2017           2.0   
Akeem Hunt                       54            0        0  2017           0.0   
Albert Wilson                   560            3        0  2017           0.0   
Alex Collins                   1160            6        4  2017           2.0   
Alex Erickson                   196            1        6  2017           1.0   
Alex Smith                      355            1        2  2017           1.0   
Alfred Blue                     316            1        0  2017           0.0   
Alfred Morris                   592            1        0  2017           0.0   
Alvin Kamara                   1554           13        1  2017           1.0   
Amari Cooper                    684            7        1  2017           0.0   
Ameer Abdullah                  714            5        2  2017           1.0   
Andre Ellington                 424            1        0  2017           0.0   
Andre Williams                   25            0        0  2017           0.0   
Andy Dalton                      99            0        4  2017           4.0   
Andy Janovich                    47            1        0  2017           0.0   
Anthony Sherman                  87            1        0  2017           0.0   
ArDarius Stewart                109            0        0  2017           0.0   
Austin Davis                     -1            0        0  2017           0.0   
Austin Ekeler                   539            5        2  2017           2.0   
Ben Roethlisberger               47            0        3  2017           1.0   
Benny Cunningham                269            2        1  2017           1.0   
Bernard Reedy                    38            0        1  2017           0.0   
Bilal Powell                    942            5        1  2017           1.0   
Blaine Gabbert                   82            0        7  2017           2.0   
...                             ...          ...      ...   ...           ...   
Terron Ward                     143            0        1  2017           1.0   
Tevin Coleman                   927            8        1  2017           0.0   
Theo Riddick                    730            5        1  2017           1.0   
Thomas Rawls                    251            0        1  2017           1.0   
Tion Green                      179            2        0  2017           0.0   
Todd Gurley                    2093           19        5  2017           2.0   
Tom Brady                        28            0        7  2017           3.0   
Tom Savage                        2            0        8  2017           7.0   
Tommy Bohanon                    48            3        0  2017           0.0   
Tommylee Lewis                  130            1        1  2017           1.0   
Torrey Smith                    427            2        0  2017           0.0   
Travaris Cadet                  215            0        0  2017           0.0   
Travis Benjamin                 663            4        2  2017           0.0   
Travis Kelce                   1045            8        0  2017           0.0   
Trevor Davis                     83            0        0  2017           0.0   
Trevor Siemian                  127            1        5  2017           2.0   
Trey Edmunds                     48            1        0  2017           0.0   
Ty Montgomery                   446            4        0  2017           0.0   
Tyler Bray                        0            0        1  2017           1.0   
Tyler Ervin                      50            0        0  2017           0.0   
Tyler Lockett                   613            2        0  2017           0.0   
Tyreek Hill                    1242            7        2  2017           0.0   
Tyrod Taylor                    427            4        4  2017           2.0   
Vince Mayle                       2            1        0  2017           0.0   
Wayne Gallman                   669            1        3  2017           1.0   
Wendell Smallwood               277            1        0  2017           0.0   
Wil Lutz                          4            0        0  2017           0.0   
Will Fuller                     432            7        0  2017           0.0   
Zach Line                        36            1        0  2017           0.0   
Zach Zenner                      26            1        0  2017           0.0   

                    two_pt_conversions  return_yards  return_td  \
name                                                              
Aaron Jones                        0.0           0.0        0.0   
Aaron Ripkowski                    0.0           0.0        0.0   
Aaron Rodgers                      0.0           0.0        0.0   
Adam Humphries                     0.0          49.0        0.0   
Adam Thielen                       0.0           0.0        0.0   
Adoree' Jackson                    0.0         868.0        0.0   
Adrian Peterson                    0.0           0.0        0.0   
Akeem Hunt                         0.0         611.0        0.0   
Albert Wilson                      0.0          18.0        0.0   
Alex Collins                       0.0          50.0        0.0   
Alex Erickson                      0.0         941.0        0.0   
Alex Smith                         0.0           0.0        0.0   
Alfred Blue                        0.0           0.0        0.0   
Alfred Morris                      0.0           0.0        0.0   
Alvin Kamara                       1.0         347.0        1.0   
Amari Cooper                       0.0           0.0        0.0   
Ameer Abdullah                     0.0         179.0        0.0   
Andre Ellington                    0.0           0.0        0.0   
Andre Williams                     0.0           0.0        0.0   
Andy Dalton                        0.0           0.0        0.0   
Andy Janovich                      0.0          10.0        0.0   
Anthony Sherman                    0.0           7.0        0.0   
ArDarius Stewart                   0.0         173.0        0.0   
Austin Davis                       0.0           0.0        0.0   
Austin Ekeler                      0.0          85.0        0.0   
Ben Roethlisberger                 0.0           0.0        0.0   
Benny Cunningham                   0.0         147.0        0.0   
Bernard Reedy                      0.0         320.0        0.0   
Bilal Powell                       0.0           0.0        0.0   
Blaine Gabbert                     0.0           0.0        0.0   
...                                ...           ...        ...   
Terron Ward                        0.0           0.0        0.0   
Tevin Coleman                      0.0           0.0        0.0   
Theo Riddick                       0.0           0.0        0.0   
Thomas Rawls                       0.0           0.0        0.0   
Tion Green                         0.0           0.0        0.0   
Todd Gurley                        0.0           0.0        0.0   
Tom Brady                          0.0           0.0        0.0   
Tom Savage                         0.0           0.0        0.0   
Tommy Bohanon                      0.0          14.0        0.0   
Tommylee Lewis                     0.0         422.0        0.0   
Torrey Smith                       0.0           9.0        0.0   
Travaris Cadet                     0.0           0.0        0.0   
Travis Benjamin                    0.0         257.0        1.0   
Travis Kelce                       0.0           0.0        0.0   
Trevor Davis                       0.0         996.0        0.0   
Trevor Siemian                     0.0           0.0        0.0   
Trey Edmunds                       0.0          65.0        0.0   
Ty Montgomery                      0.0           0.0        0.0   
Tyler Bray                         0.0           0.0        0.0   
Tyler Ervin                        0.0         153.0        0.0   
Tyler Lockett                      0.0        1186.0        1.0   
Tyreek Hill                        0.0         204.0        1.0   
Tyrod Taylor                       0.0           0.0        0.0   
Vince Mayle                        0.0          43.0        0.0   
Wayne Gallman                      0.0           0.0        0.0   
Wendell Smallwood                  0.0          93.0        0.0   
Wil Lutz                           0.0           0.0        0.0   
Will Fuller                        0.0         135.0        0.0   
Zach Line                          0.0           0.0        0.0   
Zach Zenner                        0.0          62.0        0.0   

                    fantasy_points  
name                                
Aaron Jones                  71.00  
Aaron Ripkowski               5.20  
Aaron Rodgers                10.60  
Adam Humphries               69.66  
Adam Thielen                148.70  
Adoree' Jackson              38.22  
Adrian Peterson              67.90  
Akeem Hunt                   29.84  
Albert Wilson                74.72  
Alex Collins                150.00  
Alex Erickson                61.24  
Alex Smith                   39.50  
Alfred Blue                  37.60  
Alfred Morris                65.20  
Alvin Kamara                253.28  
Amari Cooper                110.40  
Ameer Abdullah              106.56  
Andre Ellington              48.40  
Andre Williams                2.50  
Andy Dalton                   1.90  
Andy Janovich                11.10  
Anthony Sherman              14.98  
ArDarius Stewart             17.82  
Austin Davis                 -0.10  
Austin Ekeler                83.30  
Ben Roethlisberger            2.70  
Benny Cunningham             42.78  
Bernard Reedy                16.60  
Bilal Powell                122.20  
Blaine Gabbert                4.20  
...                            ...  
Terron Ward                  12.30  
Tevin Coleman               140.70  
Theo Riddick                101.00  
Thomas Rawls                 23.10  
Tion Green                   29.90  
Todd Gurley                 319.30  
Tom Brady                    -3.20  
Tom Savage                  -13.80  
Tommy Bohanon                23.36  
Tommylee Lewis               33.88  
Torrey Smith                 55.06  
Travaris Cadet               21.50  
Travis Benjamin             106.58  
Travis Kelce                152.50  
Trevor Davis                 48.14  
Trevor Siemian               14.70  
Trey Edmunds                 13.40  
Ty Montgomery                68.60  
Tyler Bray                   -2.00  
Tyler Ervin                  11.12  
Tyler Lockett               126.74  
Tyreek Hill                 180.36  
Tyrod Taylor                 62.70  
Vince Mayle                   7.92  
Wayne Gallman                70.90  
Wendell Smallwood            37.42  
Wil Lutz                      0.40  
Will Fuller                  90.60  
Zach Line                     9.60  
Zach Zenner                  11.08  

[317 rows x 31 columns]
"""
