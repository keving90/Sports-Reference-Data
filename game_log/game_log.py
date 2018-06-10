#!/usr/bin/env python3

"""
This module scrapes an individual player's game log for an NFL season.
"""

from nfl_scraper import scrape_game_log


if __name__ == '__main__':
    input_url = '/players/B/BellLe00.htm'
    input_year = 2016
    output_df = scrape_game_log(input_url, input_year)
    print(output_df)


"""
Sample output:

          date  game_number     age team location opponent   result  \
0   2016-10-02            4  24.227  PIT     home      KAN  W 43-14   
1   2016-10-09            5  24.234  PIT     home      NYJ  W 31-13   
2   2016-10-16            6  24.241  PIT     away      MIA  L 15-30   
3   2016-10-23            7  24.248  PIT     home      NWE  L 16-27   
4   2016-11-06            8  24.262  PIT     away      BAL  L 14-21   
5   2016-11-13            9  24.269  PIT     home      DAL  L 30-35   
6   2016-11-20           10  24.276  PIT     away      CLE   W 24-9   
7   2016-11-24           11  24.280  PIT     away      IND   W 28-7   
8   2016-12-04           12  24.290  PIT     home      NYG  W 24-14   
9   2016-12-11           13  24.297  PIT     away      BUF  W 27-20   
10  2016-12-18           14  24.304  PIT     away      CIN  W 24-20   
11  2016-12-25           15  24.311  PIT     home      BAL  W 31-27   

    rush_attempts  rush_yards  yards_per_rush       ...        qb_rating  \
0              18         144            8.00       ...              NaN   
1              20          66            3.30       ...              NaN   
2              10          53            5.30       ...              NaN   
3              21          81            3.86       ...              NaN   
4              14          32            2.29       ...              NaN   
5              17          57            3.35       ...              NaN   
6              28         146            5.21       ...              NaN   
7              23         120            5.22       ...              NaN   
8              29         118            4.07       ...             39.6   
9              38         236            6.21       ...              NaN   
10             23          93            4.04       ...              NaN   
11             20         122            6.10       ...              NaN   

    times_sacked  yards_lost_to_sacks  yards_per_pass_attempt  \
0              0                    0                     NaN   
1              0                    0                     NaN   
2              0                    0                     NaN   
3              0                    0                     NaN   
4              0                    0                     NaN   
5              0                    0                     NaN   
6              0                    0                     NaN   
7              0                    0                     NaN   
8              0                    0                     0.0   
9              0                    0                     NaN   
10             0                    0                     NaN   
11             0                    0                     NaN   

    adjusted_yards_per_pass_attempt  pass_2_point_conversions  total_td  \
0                               NaN                       NaN         0   
1                               NaN                       NaN         0   
2                               NaN                       1.0         0   
3                               NaN                       NaN         0   
4                               NaN                       NaN         0   
5                               NaN                       NaN         2   
6                               NaN                       NaN         1   
7                               NaN                       NaN         1   
8                               0.0                       NaN         0   
9                               NaN                       NaN         3   
10                              NaN                       NaN         0   
11                              NaN                       NaN         2   

    total_points  year  fantasy_points  
0              0  2016            17.8  
1              0  2016            15.4  
2              2  2016            10.8  
3              0  2016            14.9  
4              0  2016             7.0  
5             12  2016            25.4  
6              6  2016            26.1  
7              6  2016            20.2  
8              0  2016            18.2  
9             18  2016            47.8  
10             0  2016            13.1  
11            12  2016            25.7  

[12 rows x 34 columns]
"""