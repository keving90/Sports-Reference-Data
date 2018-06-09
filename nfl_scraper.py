#!/usr/bin/env python3

"""
This module contains functions for scraping data from pro-football-reference.com tables based on a given table ID,
creating Player objects from the data, and saving the data into a data frame.
"""

import requests
import bs4
import pandas as pd

# Putting '..' on sys.path because Player import was causing an error when scraper.py is imported from
# another module (such as 5_seasons_50_carries.py).
import sys
import os

# os.path.split() splits the head and tail of the path for the file.
# This line of code grabs the head, joins it with '..', and inserts the path into the first element of sys.path.
# sys.path.insert(0, os.path.join(os.path.split(__file__)[0], '..'))

from player import Player
from constants import LOG_RUSH_REC_PASS_HEADER, LOG_RUSH_REC_HEADER


def scrape_table(url, table_id):
    """
    Scrape a table from a table in pro-football-reference.com based on provided table ID.

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


def make_data_frame(player_dict_list, year, header, fantasy_settings):
    """
    Creates a new data frame and returns it.

    :param player_dict_list: List of unique Player.__dict__'s.
    :param year: NFL season's year.
    :param header: Dictionary from constants.py used to create data frame columns.
    :param fantasy_settings: Dictionary from constants.py used to calculate player's fantasy points for the season.
    :return: Data frame of stats.
    """
    df = pd.DataFrame(data=player_dict_list)  # Create the data frame.
    header_list = list(header.keys())         # Get header dict's keys for df's column names.
    df = df[header_list]                      # Add column headers.
    df['year'] = year                         # Add a 'year' column.

    # Create fantasy_points column.
    df['fantasy_points'] = (df['rush_yards'] * fantasy_settings['rush_yards']
                            + df['rush_td'] * fantasy_settings['rush_td']
                            + df['receptions'] * fantasy_settings['receptions']
                            + df['rec_yards'] * fantasy_settings['rec_yards']
                            + df['rec_td'] * fantasy_settings['rec_td'])

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
        print('Game log not found for ' + player_url + ' in year ' + str(year) + '.')
        exit(1)
    elif len(data[0]) == 33:
        header = LOG_RUSH_REC_PASS_HEADER
    elif len(data[0]) == 21:
        header = LOG_RUSH_REC_HEADER

    list_of_log_dicts = create_player_objects(data, header)
    df = make_data_frame(list_of_log_dicts, year, header, FANTASY_SETTINGS_DICT)

    return df


if __name__ == '__main__':
    """Usage example."""
    # Necessary imports for running sample script.
    from constants import SEASON_RUSH_REC_HEADER, FANTASY_SETTINGS_DICT

    # Set the year.
    season_year = 2017

    # Create url for given season.
    input_url = 'https://www.pro-football-reference.com/years/' + str(season_year) + '/rushing.htm'

    # Identify the table ID to get scrape from the correct table.
    input_table_id = 'rushing_and_receiving'

    # Scrape the data to get a list of each player's web page elements.
    elem_list = scrape_table(input_url, input_table_id)

    # Use the elements to create Player objects.
    player_dicts = create_player_objects(elem_list, SEASON_RUSH_REC_HEADER)

    # Create a data frame for the season
    output_df = make_data_frame(player_dicts, season_year, SEASON_RUSH_REC_HEADER, FANTASY_SETTINGS_DICT)

    print(output_df)


"""
Sample output:

                   name                      url team  age position  \
0          Le'Veon Bell  /players/B/BellLe00.htm  PIT   25       RB   
1          LeSean McCoy  /players/M/McCoLe01.htm  BUF   29       RB   
2         Melvin Gordon  /players/G/GordMe00.htm  LAC   24       RB   
3           Todd Gurley  /players/G/GurlTo01.htm  LAR   23       RB   
4         Jordan Howard  /players/H/HowaJo00.htm  CHI   23       RB   
5           Kareem Hunt  /players/H/HuntKa00.htm  KAN   22       RB   
6     Leonard Fournette  /players/F/FourLe00.htm  JAX   22       RB   
7            Frank Gore  /players/G/GoreFr00.htm  IND   34       RB   
8         C.J. Anderson  /players/A/AndeC.00.htm  DEN   26       RB   
9       Ezekiel Elliott  /players/E/ElliEz00.htm  DAL   22       RB   
10          Carlos Hyde  /players/H/HydeCa00.htm  SFO   26       RB   
11         Lamar Miller  /players/M/MillLa01.htm  HOU   26       RB   
12          Mark Ingram  /players/I/IngrMa01.htm  NOR   28       RB   
13      Latavius Murray  /players/M/MurrLa00.htm  MIN   27       RB   
14         Alex Collins  /players/C/CollAl00.htm  BAL   23       RB   
15            Jay Ajayi  /players/A/AjayJa00.htm  2TM   24      NaN   
16       Marshawn Lynch  /players/L/LyncMa00.htm  OAK   31       RB   
17       Isaiah Crowell  /players/C/CrowIs00.htm  CLE   24       RB   
18     Jonathan Stewart  /players/S/StewJo00.htm  CAR   30       RB   
19      Devonta Freeman  /players/F/FreeDe00.htm  ATL   25       RB   
20       DeMarco Murray  /players/M/MurrDe00.htm  TEN   29       RB   
21           Dion Lewis  /players/L/LewiDi00.htm  NWE   27       RB   
22            Joe Mixon  /players/M/MixoJo00.htm  CIN   21       rb   
23         Bilal Powell  /players/P/PoweBi00.htm  NYJ   29       RB   
24        Derrick Henry  /players/H/HenrDe00.htm  TEN   23       rb   
25        Samaje Perine  /players/P/PeriSa00.htm  WAS   22       RB   
26    LeGarrette Blount  /players/B/BlouLe00.htm  PHI   31       RB   
27       Orleans Darkwa  /players/D/DarkOr00.htm  NYG   25       RB   
28       Ameer Abdullah  /players/A/AbduAm00.htm  DET   24       RB   
29        Tevin Coleman  /players/C/ColeTe01.htm  ATL   24    fb/rb   
..                  ...                      ...  ...  ...      ...   
286        Bronson Hill  /players/H/HillBr01.htm  ARI   24      NaN   
287           Josh Hill  /players/H/HillJo02.htm  NOR   27       TE   
288     Jacob Hollister  /players/H/HollJa03.htm  NWE   24       te   
289      Adam Humphries  /players/H/HumpAd00.htm  TAM   24       wr   
290         Chris Jones  /players/J/JoneCh02.htm  DAL   28        P   
291         Julio Jones  /players/J/JoneJu02.htm  ATL   28       WR   
292        Cody Kessler  /players/K/KessCo00.htm  CLE   24      NaN   
293           John Kuhn  /players/K/KuhnJo00.htm  NOR   35       fb   
294       Jarvis Landry  /players/L/LandJa00.htm  MIA   25       WR   
295         Marqise Lee  /players/L/LeexMa00.htm  JAX   26       WR   
296            Wil Lutz  /players/L/LutzWi00.htm  NOR   23        K   
297    Rishard Matthews  /players/M/MattRi00.htm  TEN   28       WR   
298     Darren McFadden  /players/M/McFaDa00.htm  DAL   30      NaN   
299     Isaiah McKenzie  /players/M/McKeIs00.htm  DEN   22      NaN   
300      Braxton Miller  /players/M/MillBr03.htm  HOU   25       wr   
301         Jojo Natson  /players/N/NatsJo00.htm  NYJ   23      NaN   
302         David Njoku  /players/N/NjokDa00.htm  CLE   21       te   
303        Bobby Rainey  /players/R/RainBo00.htm  BAL   30      NaN   
304       Kalif Raymond  /players/R/RaymKa00.htm  2TM   23      NaN   
305       Kasey Redfern  /players/R/RedfKa00.htm  DET   26        p   
306           John Ross  /players/R/RossJo00.htm  CIN   23       wr   
307        Torrey Smith  /players/S/SmitTo02.htm  PHI   28       WR   
308        Nate Sudfeld  /players/S/SudfNa00.htm  PHI   24      NaN   
309        Adam Thielen  /players/T/ThieAd00.htm  MIN   27       WR   
310   De'Anthony Thomas  /players/T/ThomDe05.htm  KAN   24       wr   
311        Bryce Treggs  /players/T/TregBr00.htm  CLE   23       wr   
312        Mike Wallace  /players/W/WallMi00.htm  BAL   31       WR   
313          Eric Weems  /players/W/WeemEr00.htm  TEN   32      NaN   
314  Jermaine Whitehead  /players/W/WhitJe02.htm  GNB   24      NaN   
315       Kyle Williams  /players/W/WillKy20.htm  BUF   34  LDT/rdt   

     games_played  games_started  rush_attempts  rush_yards  rush_td  \
0              15             15            321        1291        9   
1              16             16            287        1138        6   
2              16             16            284        1105        8   
3              15             15            279        1305       13   
4              16             16            276        1122        9   
5              16             16            272        1327        8   
6              13             13            268        1040        9   
7              16             16            261         961        3   
8              16             16            245        1007        3   
9              10             10            242         983        7   
10             16             16            240         938        8   
11             16             13            238         888        3   
12             16             13            230        1124       12   
13             16             11            216         842        8   
14             15             12            212         973        6   
15             14              8            208         873        1   
16             15             15            207         891        7   
17             16             16            206         853        2   
18             15             10            198         680        6   
19             14             14            196         865        7   
20             15             15            184         659        6   
21             16              8            180         896        6   
22             14              7            178         626        4   
23             15             10            178         772        5   
24             16              2            176         744        5   
25             16              8            175         603        1   
26             16             11            173         766        2   
27             15             11            171         751        5   
28             14             11            165         552        4   
29             15              3            156         628        5   
..            ...            ...            ...         ...      ...   
286             2              0              1          -2        0   
287            16             11              1          -8        0   
288            15              1              1           5        0   
289            16              3              1           6        0   
290            16              0              1          24        0   
291            16             16              1          15        0   
292             3              0              1          -1        0   
293             2              1              1           2        0   
294            16             16              1          -7        0   
295            14             14              1          17        0   
296            16              0              1           4        0   
297            14             11              1          -3        0   
298             1              0              1          -2        0   
299            11              0              1           4        0   
300            11              3              1           1        0   
301             7              0              1          15        0   
302            16              5              1           1        0   
303             4              0              1           2        0   
304             8              0              1          -1        0   
305             1              0              1          10        0   
306             3              1              1          12        0   
307            16             14              1          -3        0   
308             1              0              1          22        0   
309            16             16              1          11        0   
310            16              2              1           4        0   
311             6              1              1           6        0   
312            15             14              1           4        0   
313            16              0              1           0        0   
314            10              0              1           7        0   
315            16             16              1           1        1   

          ...        rec_td  longest_rec  rec_per_game  rec_yards_per_game  \
0         ...           2.0         42.0           5.7                43.7   
1         ...           2.0         39.0           3.7                28.0   
2         ...           4.0         49.0           3.6                29.8   
3         ...           6.0         80.0           4.3                52.5   
4         ...           0.0         12.0           1.4                 7.8   
5         ...           3.0         78.0           3.3                28.4   
6         ...           1.0         28.0           2.8                23.2   
7         ...           1.0         26.0           1.8                15.3   
8         ...           1.0         25.0           1.8                14.0   
9         ...           2.0         72.0           2.6                26.9   
10        ...           0.0         18.0           3.7                21.9   
11        ...           3.0         32.0           2.3                20.4   
12        ...           0.0         54.0           3.6                26.0   
13        ...           0.0         28.0           0.9                 6.4   
14        ...           0.0         37.0           1.5                12.5   
15        ...           1.0         32.0           1.7                11.3   
16        ...           0.0         26.0           1.3                10.1   
17        ...           0.0         38.0           1.8                11.4   
18        ...           1.0         21.0           0.5                 3.5   
19        ...           1.0         29.0           2.6                22.6   
20        ...           1.0         18.0           2.6                17.7   
21        ...           3.0         20.0           2.0                13.4   
22        ...           0.0         67.0           2.1                20.5   
23        ...           0.0         31.0           1.5                11.3   
24        ...           1.0         66.0           0.7                 8.5   
25        ...           1.0         25.0           1.4                11.4   
26        ...           1.0         20.0           0.5                 3.1   
27        ...           0.0         13.0           1.3                 7.7   
28        ...           1.0         22.0           1.8                11.6   
29        ...           3.0         39.0           1.8                19.9   
..        ...           ...          ...           ...                 ...   
286       ...           NaN          NaN           NaN                 NaN   
287       ...           1.0         22.0           1.0                 7.8   
288       ...           0.0         19.0           0.3                 2.8   
289       ...           1.0         43.0           3.8                39.4   
290       ...           NaN          NaN           NaN                 NaN   
291       ...           3.0         53.0           5.5                90.3   
292       ...           NaN          NaN           NaN                 NaN   
293       ...           NaN          NaN           NaN                 NaN   
294       ...           9.0         49.0           7.0                61.7   
295       ...           3.0         45.0           4.0                50.1   
296       ...           NaN          NaN           NaN                 NaN   
297       ...           4.0         75.0           3.8                56.8   
298       ...           NaN          NaN           NaN                 NaN   
299       ...           0.0         14.0           0.4                 2.6   
300       ...           1.0         57.0           1.7                14.7   
301       ...           0.0         19.0           0.3                 2.6   
302       ...           4.0         34.0           2.0                24.1   
303       ...           0.0         12.0           1.3                 4.5   
304       ...           0.0         12.0           0.1                 1.5   
305       ...           NaN          NaN           NaN                 NaN   
306       ...           0.0          0.0           0.0                 0.0   
307       ...           2.0         59.0           2.3                26.9   
308       ...           NaN          NaN           NaN                 NaN   
309       ...           4.0         65.0           5.7                79.8   
310       ...           2.0         57.0           0.9                 8.9   
311       ...           0.0         20.0           0.8                13.2   
312       ...           4.0         66.0           3.5                49.9   
313       ...           0.0          5.0           0.1                 0.3   
314       ...           NaN          NaN           NaN                 NaN   
315       ...           NaN          NaN           NaN                 NaN   

     catch_percentage  scrimmage_yards  rush_rec_td  fumbles  year  \
0                80.2             1946           11        3  2017   
1                76.6             1586            8        3  2017   
2                69.9             1581           12        1  2017   
3                73.6             2093           19        5  2017   
4                71.9             1247            9        1  2017   
5                84.1             1782           11        1  2017   
6                75.0             1342           10        2  2017   
7                76.3             1206            4        3  2017   
8                70.0             1231            4        1  2017   
9                68.4             1252            9        1  2017   
10               67.0             1288            8        2  2017   
11               80.0             1215            6        1  2017   
12               81.7             1540           12        3  2017   
13               88.2              945            8        1  2017   
14               63.9             1160            6        4  2017   
15               70.6             1031            2        3  2017   
16               64.5             1042            7        1  2017   
17               66.7             1035            2        1  2017   
18               53.3              732            7        3  2017   
19               76.6             1182            8        4  2017   
20               83.0              925            7        1  2017   
21               91.4             1110            9        0  2017   
22               88.2              913            4        3  2017   
23               69.7              942            5        1  2017   
24               64.7              880            6        1  2017   
25               91.7              785            2        2  2017   
26              100.0              816            3        1  2017   
27               67.9              867            5        1  2017   
28               71.4              714            5        2  2017   
29               69.2              927            8        1  2017   
..                ...              ...          ...      ...   ...   
286               NaN               -2            0        0  2017   
287              72.7              117            1        2  2017   
288              36.4               47            0        0  2017   
289              73.5              637            1        1  2017   
290               NaN               24            0        0  2017   
291              59.5             1459            3        0  2017   
292               NaN               -1            0        0  2017   
293               NaN                2            0        0  2017   
294              69.6              980            9        4  2017   
295              58.3              719            3        1  2017   
296               NaN                4            0        0  2017   
297              60.9              792            4        0  2017   
298               NaN               -2            0        0  2017   
299              30.8               33            0        6  2017   
300              65.5              163            1        0  2017   
301              40.0               33            0        1  2017   
302              53.3              387            4        0  2017   
303              71.4               20            0        0  2017   
304             100.0               11            0        5  2017   
305               NaN               10            0        1  2017   
306               0.0               12            0        1  2017   
307              53.7              427            2        0  2017   
308               NaN               22            0        0  2017   
309              64.1             1287            4        3  2017   
310              87.5              147            2        1  2017   
311              27.8               85            0        1  2017   
312              56.5              752            4        0  2017   
313              50.0                5            0        0  2017   
314               NaN                7            0        0  2017   
315               NaN                1            1        0  2017   

     fantasy_points  
0             260.6  
1             206.6  
2             230.1  
3             323.3  
4             178.7  
5             244.2  
6             194.2  
7             144.6  
8             147.1  
9             179.2  
10            176.8  
11            157.5  
12            226.0  
13            142.5  
14            152.0  
15            115.1  
16            146.2  
17            115.5  
18            115.2  
19            166.2  
20            134.5  
21            165.0  
22            115.3  
23            124.2  
24            124.0  
25             90.5  
26             99.6  
27            116.7  
28            101.4  
29            140.7  
..              ...  
286             NaN  
287            17.7  
288             4.7  
289            69.7  
290             NaN  
291           163.9  
292             NaN  
293             NaN  
294           152.0  
295            89.9  
296             NaN  
297           103.2  
298             NaN  
299             3.3  
300            22.3  
301             3.3  
302            62.7  
303             2.0  
304             1.1  
305             NaN  
306             1.2  
307            54.7  
308             NaN  
309           152.7  
310            26.7  
311             8.5  
312            99.2  
313             0.5  
314             NaN  
315             NaN  

[316 rows x 28 columns]
"""
