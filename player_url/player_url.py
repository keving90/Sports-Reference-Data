import requests
import bs4
import pandas as pd
import numpy as np
import datetime

# Get the current date to help figure out which year to start gathering data from.
now = datetime.datetime.now()

# Number of years of data.
num_years = 1

# Starting with last year since it's a full season of data.
start_year = now.year - 1

# Get the final year to gather data from.
end_year = start_year - num_years

# This dictionary is used for creating columns in the dataframe and assigning a datatype for each column.
HEADER = {
    'name': str,
    'team': str,
    'age': int,
    'position': str,
    'games_played': int,
    'games_started': int,
    'rush_attempts': int,
    'rush_yards': int,
    'rush_touchdowns': int,
    'longest_run': int,
    'yards_per_rush': float,
    'yards_per_game': float,
    'attempts_per_game': float,
    'targets': int,
    'receptions': int,
    'rec_yards': int,
    'yards_per_rec': float,
    'rec_touchdowns': int,
    'longest_rec': int,
    'rec_per_game': float,
    'rec_yards_per_game': float,
    'catch_percentage': float,
    'scrimmage_yards': int,
    'rush_rec_touchdowns': int,
    'fumbles': int,
    'url': str
}


class Player(object):
    """
    The Player class is used to represent a record in the dataset. The player's 'name' and 'year' attributes will be 
    used in the dataframe as a multi-hierarchical index. The class uses the HEADER dictionary to assign attributes 
    and use the appropriate datatype.
    """

    def __init__(self, data):
        """
        Initialize the Player object. This method will use the keys and values in HEADER to assign attributes and 
        data types for the attributes.
        """
        # Loop through the HEADER dictionary keys and values. An enumeration is also used to grab data from a specific
        # column in the row.
        for i, (attr, data_type) in enumerate(HEADER.items()):
            # Remove unwanted characters in data.
            # '*' in the player's name indicates a Pro Bowl appearance.
            # '+' in the player's name indicates a First-Team All-Pro award.
            # '%' is included in the catch percentage stat on pro-football reference
            if data[i].endswith('*+'):
                data[i] = data[i][:-2]
            elif data[i].endswith('%') or data[i].endswith('*') or data[i].endswith('+'):
                data[i] = data[i][:-1]

            # Set the class attribute. If the data is empty then we will assign a NumPy NaN value to the attribute.
            # Otherwise, we set the attribute as usual.
            if not data[i]:
                setattr(self, type(data[i])(np.NaN), str(data[i]))
            else:
                setattr(self, attr, data_type(data[i]))


# Holds each dataframe scraped from pro-football reference.
# Keys are the years, values are the dataframe.
dataframe_dict = {}

# Iterate through each year of data and create a dataframe for each one.
for year in range(start_year, end_year, -1):
    # Send a GET request to Pro Football Reference's Rushing & Receiving page to gather the data.
    r = requests.get('https://www.pro-football-reference.com/years/' + str(year) + '/rushing.htm')
    r.raise_for_status()

    # Greate a BeautifulSoup object.
    soup = bs4.BeautifulSoup(r.text, 'lxml')

    # Find the first table with tag 'table' and id 'rushing_and_receiving
    table = soup.find('table', id='rushing_and_receiving')

    # tbody is the table's body
    # Get the body of the table
    body = table.find('tbody')

    # tr refers to a table row
    # Each row in player_list has data for a player
    player_list = body.find_all('tr')

    # This list holds a dictionary of each object's attributes.
    # The dictionary is made from the object's __dict__ attribute.
    player_dict_list = []

    # Get each player's stats, create a Player object, and append the object
    # and the instance's __dict__ to their own list
    for player in player_list:
        info_list = player.find_all('td')

        # The href is used to get the URL for the player's specific stat page.
        # It is a list containing all elements with a link to another page/
        # The href attribute specifies the URL of the page the link goes to.
        href = player.find_all('a', href=True)

        if not href:
            continue

        print('href: ')
        print(href)
        print()

        print('player: ')
        print(player)
        print()

        # The first element in the list has the URL we're interested in, but there is
        # some extra information in here that we don't need.
        print('href[0]: ')
        print(href[0])
        print()

        # This will get the actual link we're interested in
        print("href[0]['href']: ")
        print(href[0]['href'])
        print()
        player_url = href[0]['href']

        print('\n'*2)
        if len(info_list) == 25:
            player_info = []
            for i, stat in enumerate(info_list):
                print(i, stat)
                # Get text part of each stat and append
                player_info.append(stat.text)
            # Create single Player object based on text stats in info list
            player_info.append(player_url)
            obj = Player(player_info)
            # Append a dict of Player object attributes
            # Used for data in dataframe
            player_dict_list.append(obj.__dict__)
        else:
            print('Error: Missing data for player')

    df = pd.DataFrame(data=player_dict_list)
    header_list = list(HEADER.keys())
    df = df[header_list]
    df['year'] = year
    print(df)

    # dataframe_dict[year] = df