import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from sports_reference.pro_football_reference import ProFootballReference


class TestProReferenceScraper(object):

    @pytest.fixture
    def create_pro_ref_scraper(self):
        #stat_types = ['passing', 'receiving', 'rushing', 'kicking', 'returns', 'scoring', 'fantasy', 'defense']
        return ProFootballReference()

    # Oldest year: 1932
    def test_pro_football_ref_scraper_rushing(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_season_player_stats(years=range(1935, 1931, -1), stat_type='rushing')  # Passed on previous run

    # Oldest year: 1932
    def test_pro_football_ref_scraper_passing(self, create_pro_ref_scraper):
        # 2006 has QBR, 2005 does not
        create_pro_ref_scraper.get_season_player_stats(years=range(1935, 1931, -1), stat_type='passing')

    # Catch % stat not available before 1992
    # Oldest year: 1932
    def test_pro_football_ref_scraper_receiving(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_season_player_stats(years=range(1935, 1931, -1), stat_type='receiving')

    # Oldest year: 1938
    def test_pro_football_ref_scraper_kicking(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_season_player_stats(years=range(1941, 1937, -1), stat_type='kicking')

    # Oldest year: 1941
    def test_pro_football_ref_scraper_returns(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_season_player_stats(years=range(1943, 1940, -1), stat_type='returns')

    # Oldest year: 1922
    def test_pro_football_ref_scraper_scoring(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_season_player_stats(years=range(1926, 1921, -1), stat_type='scoring')

    # Oldest year: 1970
    def test_pro_football_ref_scraper_fantasy(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_season_player_stats(years=range(1972, 1969, -1), stat_type='fantasy')

    # Oldest year: 1932
    def test_pro_football_ref_scraper_defense(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_season_player_stats(years=range(1943, 1939, -1), stat_type='defense')

    def test_single_years_list_with_single_stat_type(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_season_player_stats(years=[2020], stat_type='passing')

    def test_single_year_with_single_stat_types_list(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_season_player_stats(year=2019, stat_types=['receiving'])

    def test_single_year_two_length_stat_types(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_season_player_stats(year=2019, stat_types=['passing', 'receiving'])

    def test_single_year_three_length_stat_types(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_season_player_stats(year=2019, stat_types=['passing', 'receiving', 'rushing'])

    def test_two_years_two_length_stat_types(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_season_player_stats(years=[2000, 2001], stat_types=['passing', 'receiving'])

    def test_three_years_three_length_stat_types(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_season_player_stats(years=[2010, 2011, 2012],
                                                       stat_types=['passing', 'receiving', 'rushing'])

    def test_all_stat_types(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_season_player_stats(years=[2020, 2019, 2018],
                                                       stat_types=['passing', 'receiving', 'rushing', 'kicking',
                                                                   'returns', 'scoring', 'fantasy', 'defense'])

    def test_single_year_passing(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_passing_stats(year=2020)
        create_pro_ref_scraper.get_season_player_stats(year=1999, stat_type='passing')
        create_pro_ref_scraper.get_season_player_stats(years=[2000], stat_types=['passing'])

    def test_single_year_receiving(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_receiving_stats(year=2020)
        create_pro_ref_scraper.get_season_player_stats(year=1999, stat_type='receiving')
        create_pro_ref_scraper.get_season_player_stats(years=[2000], stat_types=['receiving'])

    def test_single_year_rushing(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_rushing_stats(year=2020)
        create_pro_ref_scraper.get_season_player_stats(year=1999, stat_type='rushing')
        create_pro_ref_scraper.get_season_player_stats(years=[2000], stat_types=['rushing'])

    def test_single_year_kicking(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_kicking_stats(year=2020)
        create_pro_ref_scraper.get_season_player_stats(year=1999, stat_type='kicking')
        create_pro_ref_scraper.get_season_player_stats(years=[2000], stat_types=['kicking'])

    def test_single_year_returns(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_return_stats(year=2020)
        create_pro_ref_scraper.get_season_player_stats(year=1999, stat_type='returns')
        create_pro_ref_scraper.get_season_player_stats(years=[2000], stat_types=['returns'])

    def test_single_year_scoring(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_scoring_stats(year=2020)
        create_pro_ref_scraper.get_season_player_stats(year=1999, stat_type='scoring')
        create_pro_ref_scraper.get_season_player_stats(years=[2000], stat_types=['scoring'])

    def test_single_year_fantasy(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_fantasy_stats(year=2020)
        create_pro_ref_scraper.get_season_player_stats(year=1999, stat_type='fantasy')
        create_pro_ref_scraper.get_season_player_stats(years=[2000], stat_types=['fantasy'])

    def test_single_year_defense(self, create_pro_ref_scraper):
        create_pro_ref_scraper.get_defensive_player_stats(year=2020)
        create_pro_ref_scraper.get_season_player_stats(year=1999, stat_type='defense')
        create_pro_ref_scraper.get_season_player_stats(years=[2000], stat_types=['defense'])

    def test_stat_types_property(self, create_pro_ref_scraper):
        assert create_pro_ref_scraper.stat_types == ['rushing', 'passing', 'receiving', 'kicking', 'returns',
                                                     'scoring', 'fantasy', 'defense']
