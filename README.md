# NFL-Data-Python
This repository contains a Python program capable of scraping data from [Pro Football Reference](https://www.pro-football-reference.com/).

More programs will be added over time.

## 5 Seasons 50 Carries
The `5_seasons_50_carries` package contains a module called `5_seasons_50_carries.py` that uses `nfl_scraper.py` to get data from Pro Football Reference's "Rushing and Receiving" data table. It then filters the data out so the only remaining players are running backs with 50 or more carries in each of the last 5 seasons. It also saves the data frame into a `csv` file. There is also a Jupyter Notebook version that shows the data set, it's shape, and other qualities.

## Game Log
The `game_log` package is a work in progress where the end goal is to be able to scrape an individual player's game log for a given season based on their URL found in the "Rushing and Receiving" data table.

## player.py
This module contains a class representing a single player object. The class takes a list of data, and a dictionary whose keys are a given stat category and values are the data type of the stat.

## constants.py
This module contains dictionary constants used for scraping data, creating data frames, or calculating fantasy football point totals.
