# NFL-Data-Python
This repository contains a Python program capable of scraping data from [The Football Database](https://www.footballdb.com/) and [Pro Football Reference](https://www.pro-football-reference.com/).

## football_db_scraper.py
Scrapes data from footballdb.com. It can create a comprehensive data set containing players of all positions and calculate their fantasy point total for the season. It can also scrape an individual stat table (rushing only, receiving only, etc.) It is more accurate than the `pro_football_ref_scraper` package.

## rb_carries package
The `rb_carries` package contains a module called `rb_carries.py` which uses `football_db_scraper.py` to get data from www.footballdb.com. It then filters the data out so the only remaining players are running backs with 50 or more carries in each of the last `n` seasons. It also saves the data frame into a `csv` file. There is also a Jupyter Notebook version that shows the data set, its characteristics, visualizations, and analysis.

## pro_football_ref_scraper package
Scrapes the Rushing and Receiving table from pro-football-reference.com for a given season. It can also calculate each player's fantasy point total. It needs to scrape some data from footballdb.com to account for missing fields.

## player.py
This module contains a class representing a single player object. The class takes a list of data and a dictionary as input. The dictionary's keys are a given stat category and values are the data type of the stat.
