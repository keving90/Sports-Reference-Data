# The football_db Package

## Requirements

This package requires the following Python modules:
* Requests
* BeautifulSoup4
* NumPy
* Pandas
* The `player.py` module found in the repo. It is used for creating Player objects to represent a player and their stats for a season.
* Selenium (optional - if you want to run `yahoo_scraper.py`)

## Overview

* This package was built using Python 3.6.1, so dictionaries are ordered. This information is important because the `get_fantasy_df()` method in `football_db_scraper.py` requires an ordered dictionary. I highly recommend using a version of python that is 3.6 or later.

* The `football_db_scraper.py` scrapes data from www.footballdb.com. It can scrape comprehensive fantasy points data for a given season, or it can scrape an individual table type. Multiple seasons worth of data can be scraped and placed into the same data frame.

* The `yahoo_scraper.py` module scrape data from the Yahoo Fantasy Football Player List. It is used along with the `test_football_db_scraper.ipynb` Jupyter Notebook to verify the fantasy calculations produced by `football_db_scraper.py`. It is only used for verification purposes. The module will not properly run as is because it requires a valid username and password.

## `football_db_scraper.py`

This module scrapes data from www.footballdb.com. It can create a comprehensive data set containing players of all relevant offensive positions and calculate their fantasy point total for the season. It can also scrape an individual stat table (rushing only, receiving only, etc.). Both methods can scrape multiple seasons of data at once. All you need to do is include a `start_year` and `end_year`. It does not matter if `start_year` > `end_year` (or <). This will only affect the order the data is scraped. If `start_year` == `end_year`, then one season is scraped. The actual start years and end years are both included in the data. Users can supply their own custom fantasy settings dictionary to get accurate fantasy point calculations in relation to their favorite league settings. The dictionary's keys must be exactly as seen in the example below (order does not matter).

Valid individual table types include:

* 'all_purpose': All purpose yardage data. Has data for all NFL players.
* 'passing': Passing data.
* 'rushing': Rushing data.
* 'receiving': Receiving data.
* 'scoring': Scoring data.
* 'fumbles': Fumble data.
* 'kick_returns': Kick return data.
* 'punt_returns': Punt return data.
* 'kicking': Field goal and point after touchdown data.
* 'fantasy_offense': QB, RB, WR, and TE data with www.footballdb.com's custom fantasy settings data. Although fantasy settings are included in this table, many players are left out. This table is used in `get_fantasy_df()` to get passing two point conversion data.

The `FbDbScraper` class will scrape the data. Just create an object.

```python
from football_db.football_db_scraper import FbDbScraperfb

# Create object.
fb_db = FbDbScraper()

# Create custom fantasy settings dictionary (optional).
custom_settings = {
    'pass_yards': 1 / 25,
    'pass_td': 4,
    'interceptions': -1,
    'rush_yards': 1 / 10,
    'rush_td': 6,
    'rec_yards': 1 / 10,
    'receptions': 1,  # Default settings have -> receptions: 0
    'rec_td': 6,
    'two_pt_conversions': 2,
    'fumbles_lost': -2,
    'offensive_fumble_return_td': 6,
    'return_yards': 1 / 25,
    'return_td': 6,
    'pat_made': 1,
    '0-19_made': 3,
    '20-29_made': 3,
    '30-39_made': 3,
    '40-49_made': 4,
    '50+_made': 5
}

# Use custom fantasy settings.
# Skipping this step uses default settings from class.
fb_db.fantasy_settings = custom_settings

# Get fantasy data frame. Scrape the 2017 NFL season only.
fantasy_df = fb_db.get_fantasy_df(start_year=2017, end_year=2017)

# Get a data frame of a specific table.
passing_df = fb_db.get_specific_df(start_year=2017, end_year=2017, 'passing')

# Save a data fram to a csv file.
fantasy_df.to_csv('fbdb_fantasy.csv')
```

# yahoo_scraper.py and test_football_db_scraper.ipynb

The `yahoo_scraper.py` module will log into a Yahoo Fantasy Football account and scrape data from the Player List. It was created to test `football_db_scraper.py`'s fantasy point calculations. Since this module is for testing purposes only, it will only scrape the player's name and their fantasy point total. The default fantasy settings for `football_db_scraper.py` reflect the settings for my personal fantasy league, so no scoring modifications are made.

The `test_football_db_scraper.ipynb` Jupyter Notebook is used to verify these calculations. The `yahoo_scraper.py` will not run in its current state because both an invalid username and password are being provided. However, if you would like to give the module a try, then feel to edit lines 16 and 17 in the module to fit your username and password. The module requires `Selenium` and Firefox. Selenium is required instead of Requests because you must log in to an account to access the data. Since Firefox is being used, you will need [geckodriver](https://github.com/mozilla/geckodriver/releases), and you will have to edit line 22 so the path to geckodriver is correct.
