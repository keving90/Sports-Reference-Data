# Which running backs have had 50+ carries in each of the last 5 years?
This folder contains a Python 3 program and a Jupyter Notebook notebook that can scrape data from [Pro Football Reference](https://www.pro-football-reference.com/)'s Rushing and Receiving data table and places it into a data frame ([sample table](https://www.pro-football-reference.com/years/2017/rushing.htm)). The notebook uses the `Requests` and `Beautiful Soup 4` modules to gather the web page data. A `Player` class is used to create objects representing a single player. The program loops through the 5 most recent NFL seasons and gathers data for each season. A column for the player's fantasy points for the season is added to each data frame. The points total is based on a standard Yahoo! league (0 PPR). The scoring can be changed in the `FANTASY_SETTINGS_DICT` dictionary. A data frame for each season is placed in a list, and this list is concatenated into one big data frame. Then, various manipulations are made to the data frame to find all running backs who have had 50 or more rushing attempts in each of the last 5 years. The final data frame is saved as a `.csv` file.

A sample `.csv` output file is included in this repository.

**Note:** This dataset does not include 2 point conversions. This will affect the fantasy point total for some players. Luckily, few running backs get many 2 point conversions (9 RB's in 2017 each had only 1 conversion; the rest had 0)  This will only have a small affect on the point total for some of the running backs.

# Requirements
The following Python 3 libraries are needed to run this program: `Requests`, `Beautiful Soup 4 (bs4)`, `Pandas`, `NumPy`, and `datetime`.

# Usage
To run `rb_scraper.py`, make sure the libraries listed above are included and use the following Terminal command: `python3 rb_scraper.py`

If no problems occur, a `.csv` output file should be saved in `rb_scraper.py`'s current directory. 
