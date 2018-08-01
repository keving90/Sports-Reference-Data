# NFL-Data-Python
This repository contains Python programs capable of scraping data from [The Football Database](https://www.footballdb.com/) and [Pro Football Reference](https://www.pro-football-reference.com/).

#### Brief Overview

* The `football_db` package contains a module called `football_db_scraper.py` used for scraping comprehensive data and calculating fantasy points. It also contains a module called `yahoo_scraper.py` used to scrape data from a Yahoo fantasy football account. This data is used for confirming the fanatsy point calculations created in `football_db_scraper.py` are accurate. A Jupyter Notebook file is used to confirm these calculations.

* The `pro_football_ref` package contains a module called `pro_football_ref_scraper.py`, which is used for scraping data from www.pro-football-reference.com. It does not include fanatsy point calculations.

* The `player.py` module includes a `Player` class used to represent an individual player and their stats.

* Jupyter Notebook visualizations using `Matplotlib` and `Seaborn` can be found in `rb_carries/rb_carries.ipynb`.

* This project was written using Python 3.6.1.

## football_db/football_db_scraper.py
Scrapes data from www.footballdb.com. It can create a comprehensive data set containing players of all relevant offensive positions and calculate their fantasy point total for the season. It can also scrape an individual stat table (rushing only, receiving only, etc.). Both methods can scrape multiple seasons of data at once. All you need to do is include a `start_year` and `end_year`. It does not matter if `start_year` > `end_year` (or <). This will only affect the order the data is scraped. If `start_year` == `end_year`, then one season is scraped.

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

## rb_carries package
The `rb_carries` package contains a module called `rb_carries.py` which uses `football_db/football_db_scraper.py` to get data from www.footballdb.com. It then filters the data out so the only remaining players are running backs with 50 or more carries in each of the last `n` seasons. It also saves the data frame into a `csv` file. There is also a Jupyter Notebook version that shows the data set, its characteristics, visualizations, and analysis.

## pro_football_ref package (under construction)
Scrapes data from www.pro-football-reference.com (similar to `football_db_scraper.py`). It does not include fantasy calculations.

## player.py
This module contains a class representing a single player object. The class takes a list of data and a dictionary as input. The dictionary's keys are a given stat category and values are the data type of the stat. When initializing the class, the `__init__` method will iterate through the list and dictionary's items. Dictionary keys are used as the object's attribute names. The values are the data type of the attribute, and the items in the list are the value of the attribute.

## More about the modules
#### For scraping NFL data, there is `football_db/football_db_scraper.py` and `pro_football_ref/pro_football_ref_scraper.py`. Which is better?

It depends upon your goal. If you would like to have fantasy points calculations, then I would recommend `football_db/football_db_scraper.py`. If you are only interested in individual tables and player stats, then I would recommend `pro_football_ref/pro_football_ref_scraper.py`. The good thing about the `pro_football_ref_scraper.py` module is it includes each players age and the number of games they played during the season. Unfortunately, there is a bit of a tradeoff between the two modules. Do you want fantasy points calculations with no games played or age statistics, or do you want to include those statistics, but have no fantasy point calculations.

#### Why doesn't `pro_football_ref_scraper.py` include fantasy point calculations?

Unfortunately, www.pro-football-reference.com has missing data, so fantasy point calculations will not be 100% accurate. This includes two point conversion and fumbles lost data.

#### What have been some difficulties along the way?
First, I wanted to scrape data from Pro Football Reference. Then, I decided I want to be able to calculate accurate pantasy point data. The first issues were that fumbles lost and two point conversion data cannot be found.  I filled in these gaps by scraping additional data from The Football Database, and joining the two data sets. The next issue was players with the same name (Chris Thompson). This leads to difficulties when using player names as the index to join two data frames on. I realized I could use a player's unique URL as an index, which is what you find when you click on a player's name in a table. However, the same player will have a different URL on different websites. Finally, I decided to just make a program capable of getting all data from The Football Database. It still uses the player's URL as an index, and joining data frames are not a problem. The only drawbacks are the games played and age stats are missing, which Pro Football Reference has.
