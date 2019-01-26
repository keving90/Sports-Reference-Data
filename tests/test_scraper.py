import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from pro_football_ref.pro_football_ref_scraper import ProFbRefScraper
from football_db.football_db_scraper import FbDbScraper
from pro_football_ref.pro_ref2 import ProRefScraper


class TestProReferenceScraper(object):

    @pytest.fixture
    def create_pro_ref_scraper(self):
        return ProRefScraper()

    # Oldest year: 1932
    def test_pro_football_ref_scraper_rushing(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_data(1941, 1900, 'rushing')    # Passed on previous run
        # create_pro_ref_scraper.get_data(1941, 1942, 'rushing')

    # Oldest year: 1932
    def test_pro_football_ref_scraper_passing(self, create_pro_ref_scraper):
        # 2006 has QBR, 2005 does not
        create_pro_ref_scraper.get_data(1941, 1900, 'passing')    # Failed on previous run
        # create_pro_ref_scraper.get_data(1941, 1942, 'passing')

    # Catch % stat not available before 1992
    def test_pro_football_ref_scraper_receiving(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_data(2018, 1941, 'receiving')
        # create_pro_ref_scraper.get_data(2017, 2018, 'receiving')
        # create_pro_ref_scraper.get_data(1941, 1942, 'receiving')

    def test_pro_football_ref_scraper_kicking(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_data(2018, 1941, 'kicking')

    # No data before 1941 available
    def test_pro_football_ref_scraper_returns(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_data(2018, 1941, 'returns')

    def test_pro_football_ref_scraper_scoring(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_data(2018, 1941, 'scoring')

    # No data before 1970 available
    def test_pro_football_ref_scraper_fantasy(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_data(2018, 1970, 'fantasy')

    def test_pro_football_ref_scraper_defense(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_data(2018, 1941, 'defense')


class TestFootballDatabaseScraper(object):

    @pytest.fixture
    def create_football_db_scraper(self):
        return FbDbScraper()

    def test_football_database_all_purpose(self, create_football_db_scraper):
        create_football_db_scraper.get_specific_df(2017, 2018, 'all_purpose')  # Two seasons of data
        create_football_db_scraper.get_specific_df(2010, 2011, 'all_purpose')  # Data only dates back to 2010

    # No sack or loss data before 1967.
    def test_football_database_passing(self, create_football_db_scraper):
        create_football_db_scraper.get_specific_df(2017, 2018, 'passing')
        create_football_db_scraper.get_specific_df(1941, 1942, 'passing')

    def test_football_database_rushing(self, create_football_db_scraper):
        create_football_db_scraper.get_specific_df(2017, 2018, 'rushing')
        create_football_db_scraper.get_specific_df(1941, 1942, 'rushing')

    def test_football_database_receiving(self, create_football_db_scraper):
        create_football_db_scraper.get_specific_df(2017, 2018, 'receiving')
        create_football_db_scraper.get_specific_df(1941, 1942, 'receiving')

    def test_football_database_scoring(self, create_football_db_scraper):
        create_football_db_scraper.get_specific_df(2017, 2018, 'scoring')
        create_football_db_scraper.get_specific_df(1941, 1942, 'scoring')

    def test_football_database_kick_returns(self, create_football_db_scraper):
        create_football_db_scraper.get_specific_df(2017, 2018, 'kick_returns')
        create_football_db_scraper.get_specific_df(1941, 1942, 'kick_returns')

    def test_football_database_punt_returns(self, create_football_db_scraper):
        create_football_db_scraper.get_specific_df(2017, 2018, 'punt_returns')
        create_football_db_scraper.get_specific_df(1941, 1942, 'punt_returns')

    def test_football_database_kicking(self, create_football_db_scraper):
        create_football_db_scraper.get_specific_df(2017, 2018, 'kicking')
        create_football_db_scraper.get_specific_df(1941, 1942, 'kicking')

    def test_football_database_fantasy_offense(self, create_football_db_scraper):
        create_football_db_scraper.get_specific_df(2017, 2018, 'fantasy_offense')
        create_football_db_scraper.get_specific_df(2010, 2011, 'fantasy_offense')  # Data only dates back to 2010

    def test_exception_for_all_purpose_before_2010(self, create_football_db_scraper):
        with pytest.raises(ValueError):
            create_football_db_scraper.get_specific_df(2009, 2009, 'all_purpose')

    def test_exception_for_get_fantasy_df_before_2010(self, create_football_db_scraper):
        with pytest.raises(ValueError):
            create_football_db_scraper.get_fantasy_df(2009, 2009)
