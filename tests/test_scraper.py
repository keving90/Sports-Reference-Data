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
