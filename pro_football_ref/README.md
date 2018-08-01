# The pro_football_ref Package

## Requirements

This package requires the following Python modules:
* Requests
* BeautifulSoup4
* NumPy
* Pandas
* The `player.py` module found in the repo. It is used for creating Player objects to represent a player and their stats for a season.

## Overview

Built using Python 3.6.1.

This package contains a module called `pro_football_ref_scraper.py` that scrapes NFL data from tables found on www.pro-football-reference.com. It can scrape several different types of table data. A `table_type` value must be specified. Valid table types include:

* rushing: Rushing data.
* passing: Passing data.
* receiving: Receiving data.
* kicking: Field goal, point after touchdown, and punt data.
* returns: Punt and kick return data.
* scoring: All types of scoring data, such as touchdowns (defense/offense), two point conversions, kicking, etc.
* fantasy: Rushing, receiving, and passing stats, along with fantasy point totals from various leagues.
* defense: Defensive player stats.

Users can scrape multiple years of data for a single table type. Scraping the data is easy. All you need to do is import the module, create an object, and use the `get_data()` method to scrape the data:

```python
from pro_football_ref.pro_football_ref_scraper import ProFbRefScraper

# Create object.
pro_fb_ref = ProFbRefScraper()

# Get a data frame of a specific table.
passing_df = pro_fb_ref.get_data(start_year=2017, end_year=2017, table_type='passing')

# Save a data fram to a csv file.
passing_df.to_csv('passing2017.csv')
```

If `start_year` == `end_year`, then one season of data will be scraped. Otherwise, multiple years of data will be scraped (including both the start year and the end year). It does not matter which year is the start year and which year is the end year. This will only affect the order in which the data is scraped.

## Future Plans

I plan on adding a feature that will scrape and individual player's game log data for a given season.
