import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
# from pro_football_ref.pro_football_ref_scraper import ProFbRefScraper
# from football_db.football_db_scraper import FbDbScraper
from football_db.fb_db_scraper2 import FbDbScraper
from nfl_reference import NflReference


class TestProReferenceScraper(object):

    @pytest.fixture
    def create_pro_ref_scraper(self):
        return NflReference()

    # Oldest year: 1932
    def test_pro_football_ref_scraper_rushing(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_stats(years=range(1935, 1931, -1), stat_type='rushing')  # Passed on previous run

    # Oldest year: 1932
    def test_pro_football_ref_scraper_passing(self, create_pro_ref_scraper):
        # 2006 has QBR, 2005 does not
        create_pro_ref_scraper.get_stats(years=range(1935, 1931, -1), stat_type='passing')

    # Catch % stat not available before 1992
    # Oldest year: 1932
    def test_pro_football_ref_scraper_receiving(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_stats(years=range(1935, 1931, -1), stat_type='receiving')

    # Oldest year: 1938
    def test_pro_football_ref_scraper_kicking(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_stats(years=range(1941, 1937, -1), stat_type='kicking')

    # Oldest year: 1941
    def test_pro_football_ref_scraper_returns(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_stats(years=range(1943, 1940, -1), stat_type='returns')

    # Oldest year: 1922
    def test_pro_football_ref_scraper_scoring(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_stats(years=range(1926, 1921, -1), stat_type='scoring')

    # Oldest year: 1970
    def test_pro_football_ref_scraper_fantasy(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_stats(years=range(1972, 1969, -1), stat_type='fantasy')

    # Oldest year: 1932
    def test_pro_football_ref_scraper_defense(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_stats(years=range(1943, 1939, -1), stat_type='defense')


"""
class TestFootballDatabaseScraper(object):

    @pytest.fixture
    def create_football_db_scraper(self):
        return FbDbScraper()

    # Passed
    def test_football_database_all_purpose(self, create_football_db_scraper):
        # create_football_db_scraper.get_data(2017, 2018, 'all_purpose')  # Two seasons of data
        # create_football_db_scraper.get_data(2010, 2011, 'all_purpose')  # Data only dates back to 2010
        create_football_db_scraper.get_data(2018, 2010, 'all_purpose')

    # No sack or loss data before 1967.
    def test_football_database_passing(self, create_football_db_scraper):
        # create_football_db_scraper.get_data(2017, 2018, 'passing')
        # create_football_db_scraper.get_data(1941, 1942, 'passing')
        create_football_db_scraper.get_data(2018, 1940, 'passing')

    def test_football_database_rushing(self, create_football_db_scraper):
        # create_football_db_scraper.get_data(2017, 2018, 'rushing')
        # create_football_db_scraper.get_data(1941, 1942, 'rushing')
        create_football_db_scraper.get_data(2018, 1940, 'rushing')

    # Fails because 49t can't be int
    # Differing columns for 2018 and 1941
    def test_football_database_receiving(self, create_football_db_scraper):
        # create_football_db_scraper.get_data(2017, 2018, 'receiving')
        # create_football_db_scraper.get_data(1941, 1942, 'receiving')
        create_football_db_scraper.get_data(2018, 1940, 'receiving')

    # Passed
    def test_football_database_scoring(self, create_football_db_scraper):
        # create_football_db_scraper.get_data(2017, 2018, 'scoring')
        # create_football_db_scraper.get_data(1941, 1942, 'scoring')
        create_football_db_scraper.get_data(2018, 1940, 'scoring')

    # No data for 1940
    def test_football_database_kick_returns(self, create_football_db_scraper):
        # create_football_db_scraper.get_data(2017, 2018, 'kick_returns')
        # create_football_db_scraper.get_data(1941, 1942, 'kick_returns')
        create_football_db_scraper.get_data(2018, 1941, 'kick_returns')

    # No data for 1940
    def test_football_database_punt_returns(self, create_football_db_scraper):
        # create_football_db_scraper.get_data(2017, 2018, 'punt_returns')
        # create_football_db_scraper.get_data(1941, 1942, 'punt_returns')
        create_football_db_scraper.get_data(2018, 1941, 'punt_returns')

    def test_football_database_kicking(self, create_football_db_scraper):
        # create_football_db_scraper.get_data(2017, 2018, 'kicking')
        # create_football_db_scraper.get_data(1941, 1942, 'kicking')
        create_football_db_scraper.get_data(2018, 1940, 'kicking')

    # No data before 2010
    def test_football_database_fumbles(self, create_football_db_scraper):
        create_football_db_scraper.get_data(2018, 2010, 'fumbles')

    # No data before 1970
    def test_football_database_scrimmage(self, create_football_db_scraper):
        create_football_db_scraper.get_data(2018, 1970, 'scrimmage')

    # Fails
    # def test_football_database_fantasy_offense(self, create_football_db_scraper):
    #     create_football_db_scraper.get_data(2017, 2018, 'fantasy_offense')
    #     create_football_db_scraper.get_data(2010, 2011, 'fantasy_offense')  # Data only dates back to 2010

    # Fails (wrong error)
    def test_exception_for_all_purpose_before_2010(self, create_football_db_scraper):
        with pytest.raises(RuntimeError):
            create_football_db_scraper.get_data(2009, 2009, 'all_purpose')

    # Fails (wrong error)
    # def test_exception_for_get_fantasy_df_before_2010(self, create_football_db_scraper):
    #     with pytest.raises(RuntimeError):
    #         create_football_db_scraper.get_fantasy_df(2009, 2009)
"""
