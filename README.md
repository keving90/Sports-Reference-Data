# NFL-Data-Python
This repository contains Python programs capable of scraping data from [The Football Database](https://www.footballdb.com/) and [Pro Football Reference](https://www.pro-football-reference.com/).

#### Brief Overview

* The `football_db_scraper.py` is the main module used for scraping data.

* The `pro_football_ref_scraper` package is under construction. I am editing it so it will scrape data from www.pro-football-reference.com, but will not include any fantasy calculations. The original version included fantasy calculations, but it is obsolete to `football_db_scraper.py` (and therefore deprecated).

* The `player.py` module includes a `Player` class used to represent an individual player and their stats.

* Jupyter Notebook visualizations using `Matplotlib` and `Seaborn` can be found in `rb_carries/rb_carries.ipynb`.

* This project was written using Python 3.6.1.

## football_db_scraper.py
Scrapes data from www.footballdb.com. It can create a comprehensive data set containing players of all relevant offensive positions and calculate their fantasy point total for the season. It can also scrape an individual stat table (rushing only, receiving only, etc.). Both methods can scrape multiple seasons of data at once. All you need to do is include a `start_year` and `end_year`. It does not matter if `start_year` > `end_year` (or <). This will only affect the order the data is scraped. If `start_year` == `end_year`, then one season is scraped. This module is more accurate than the `pro_football_ref_scraper` package because it does not have missing data.

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
from football_db_scraper import FbDbScraperfb

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
    'receptions': 1,  # Default settings have - receptions: 0
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
The `rb_carries` package contains a module called `rb_carries.py` which uses `football_db_scraper.py` to get data from www.footballdb.com. It then filters the data out so the only remaining players are running backs with 50 or more carries in each of the last `n` seasons. It also saves the data frame into a `csv` file. There is also a Jupyter Notebook version that shows the data set, its characteristics, visualizations, and analysis.

## pro_football_ref_scraper package (under construction)
Will scrape data from www.pro-football-reference.com (similar to `football_db_scraper.py`). It will not include fantasy calculations.

**Note:** This current version is deprecated because it is not as efficient as `football_db_scraper.py`. It needs to scrape data from two sources, and some data is still missing when calculating fantasy points. This current package was my first attempt at creating this entire project.

## player.py
This module contains a class representing a single player object. The class takes a list of data and a dictionary as input. The dictionary's keys are a given stat category and values are the data type of the stat. When initializing the class, the `__init__` method will iterate through the list and dictionary's items. Dictionary keys are used as the object's attribute names. The values are the data type of the attribute, and the items in the list are the value of the attribute.

## More about the modules
#### For scraping NFL data, there is is football_db_scraper.py and pro_football_ref_scraper package. Which is better?

Personally, I think the `football_db_scraper` module is better. It scrapes data from a single source (The Football Database). This single source has enough data to get comprehensive data for accurately calculating fantasy points. The module can also scrape a single, specific table if needed. In my opinion, the biggest drawbacks are player ages and number of games played are not provided. These are not needed for calculating fantasy points, but they are useful for analysis of future performance.

The `pro_football_ref_scraper` package, on the other hand, needs to scrape data from multiple sources (both The Football Database and Pro Football Reference). It uses Pro Football Reference's "Rushing and Receiving " as the primary source of data, and fills in the gaps by scraping missing fumbles lost and two point conversion data from The Football Database. Pro Football Reference also has missing position data. Its benefits are it includes player ages and games played/started. This package was the first program I made, and I figured if I need to scrape from a second source (The Football Database) to fill in missing data, then I may as well try to get all of the data from that second source instead. Thus, I created the `football_db_scraper` module.

#### What have been some difficulties along the way?
First, I wanted to scrape data from Pro Football Reference. Then, I decided I want to be able to calculate accurate pantasy point data. The first issues were that fumbles lost and two point conversion data cannot be found.  I filled in these gaps by scraping additional data from The Football Database, and joining the two data sets. The next issue was players with the same name (Chris Thompson). This leads to difficulties when using player names as the index to join two data frames on. I realized I could use a player's unique URL as an index, which is what you find when you click on a player's name in a table. However, the same player will have a different URL on different websites. Finally, I decided to just make a program capable of getting all data from The Football Database. It still uses the player's URL as an index, and joining data frames are not a problem. The only drawbacks are the games played and age stats are missing, which Pro Football Reference has.
