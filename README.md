# NFL-Data-Python
This repository contains Python programs capable of scraping data from [The Football Database](https://www.footballdb.com/) and [Pro Football Reference](https://www.pro-football-reference.com/).

#### For scraping NFL data, there is is football_db_scraper.py and pro_football_ref_scraper package. Which is better?

Personally, I think the `football_db_scraper` module is better. It scrapes data from a single source (The Football Database). This single source has enough data to get comprehensive data for accurately calculating fantasy points. The module can also scrape a single, specific table if needed. In my opinion, the biggest drawbacks are player ages and number of games played are not provided. These are not needed for calculating fantasy points, but they are useful for analysis of future performance.

The `pro_football_ref_scraper` package, on the other hand, needs to scrape data from multiple sources (both The Football Database and Pro Football Reference). It uses Pro Football Reference's "Rushing and Receiving " as the primary source of data, and fills in the gaps by scraping missing fumbles lost and two point conversion data from The Football Database. Pro Football Reference also has missing position data. Its benefits are it includes player ages and games played/started. This package was the first program I made, and I figured if I need to scrape from a second source (The Football Database) to fill in missing data, then I may as well try to get all of the data from that second source instead. Thus, I created the `football_db_scraper` module.

#### What have been some difficulties along the way?
First, I wanted to scrape data from Pro Football Reference. Then, I decided I want to be able to calculate accurate pantasy point data. The first issues were that fumbles lost and two point conversion data cannot be found.  I filled in these gaps by scraping additional data from The Football Database, and joining the two data sets. The next issue was players with the same name (Chris Thompson). This leads to difficulties when using player names as the index to join two data frames on. I realized I could use a player's unique URL, which is what you find when you click on a player's name in a table. However, the same player will have a different URL on different websites. Finally, I decided to just make a program capable of getting all data from The Football Database. It still uses the player's URL as an index, and joining data frames are not a problem. The only drawbacks are the games played and age stats are missing, which Pro Football Reference has.

## football_db_scraper.py
Scrapes data from footballdb.com. It can create a comprehensive data set containing players of all positions and calculate their fantasy point total for the season. It can also scrape an individual stat table (rushing only, receiving only, etc.) It is more accurate than the `pro_football_ref_scraper` package.

The `FbDbScraper` class will scrape the data. Just create an object.


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
        'receptions': 1,  # receptions: 0 -> receptions: 1
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
        '50+_made': 5,
    }

    # Use custom fantasy settings.
    # Skipping this step uses default settings from class.
    fb_db.fantasy_settings = custom_settings

    # Get fantasy data frame.
    fantasy_df = fb_db.get_fantasy_df(2017)

## rb_carries package
The `rb_carries` package contains a module called `rb_carries.py` which uses `football_db_scraper.py` to get data from www.footballdb.com. It then filters the data out so the only remaining players are running backs with 50 or more carries in each of the last `n` seasons. It also saves the data frame into a `csv` file. There is also a Jupyter Notebook version that shows the data set, its characteristics, visualizations, and analysis.

## pro_football_ref_scraper package
Scrapes the Rushing and Receiving table from pro-football-reference.com for a given season. It can also calculate each player's fantasy point total. It needs to scrape some data from footballdb.com to account for missing fields.

## player.py
This module contains a class representing a single player object. The class takes a list of data and a dictionary as input. The dictionary's keys are a given stat category and values are the data type of the stat.
