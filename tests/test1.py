#!/usr/bin/env python3

"""Tests for valid fantasy calculation in pro_db_scraper.py."""

# import football_db_scraper as fbdb
# import pro_football_ref_scraper.pro_football_ref_scraper2 as fb_ref

from football_db_scraper import FbDbScraper
from pro_football_ref_scraper.pro_football_ref_scraper2 import ProFbRefScraper
import pandas as pd

def test():
    fbdb = FbDbScraper()
    fb_ref = ProFbRefScraper()

    calc_df = fbdb.get_fantasy_df(start_year=2017, end_year=2017)
    ref_df = fb_ref.get_data(start_year=2017, end_year=2017, stat_type='fantasy')

    print()

    calc_df.sort_values(by='fantasy_points', axis=1, ascending=False)
    ref_df.sort_values(by='fan_points', axis=1, ascending=False)

    print()


if __name__ == '__main__':
    test()
