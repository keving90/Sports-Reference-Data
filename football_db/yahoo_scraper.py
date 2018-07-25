#!/usr/bin/env python3

"""
This module uses selenium and a Firefox browser to log into Yahoo, go to a fantasy league player stats page, and scrape
player name and fantasy points data for 2017. The players stats page and fantasy point totals are based on my personal
league settings.

Built with Python 3.6.1.
"""

import pandas as pd
from selenium import webdriver

if __name__ == '__main__':
    login_url = 'https://login.yahoo.com/'
    user = 'not_my_actual_username'
    password = 'not_my_actual_password'
    fantasy_url = 'https://football.fantasysports.yahoo.com/f1/61123/players?status=A&pos=O&cut_type=9&stat1=S_S_2017' \
                  + '&myteam=0&sort=PR&sdir=1&count='

    # Open the browser to the 'url' page
    browser = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver')
    browser.implicitly_wait(30)
    browser.get(login_url)

    # Type the user name in text box and click "next".
    user_elem = browser.find_element_by_xpath("""//*[@id="login-username"]""")
    user_elem.send_keys(user)
    next_button = browser.find_element_by_xpath("""//*[@id="login-signin"]""")
    next_button.click()

    # Type the password into the text box and log in.
    pw_elem = browser.find_element_by_xpath("""//*[@id="login-passwd"]""")
    pw_elem.send_keys(password)
    sign_in_button = browser.find_element_by_xpath("""//*[@id="login-signin"]""")
    sign_in_button.click()

    # This will be a list of lists, where each nested list has a player's name and their fantasy point total.
    data = []

    # Iterate through Yahoo fantasy football's player list, scraping 25 players' name and fantasy points data on each
    # page. The fantasy point values are based on my personal league's settings.
    for num in range(0, 1050, 25):
        # Build the URL. The num variable is used to load a page containing payers num to num + 24.
        url = fantasy_url + str(num)

        # Go to the player data containing players num to num + 24
        browser.get(url)

        # Get the table element.
        table = browser.find_element_by_xpath("""//*[@class="Table Ta-start Fz-xs """
                                              + """Table-mid Table-px-sm Table-interactive"]""")

        # Get the element containing each row of data.
        rows = table.find_element_by_xpath("""//*[starts-with(@id, 'yui_3_18_1_2_')]""")

        # Get the elements containing player names, and add their text representation to a list.
        names_elems = rows.find_elements_by_xpath("""//*[@class="Nowrap name F-link"]""")
        names_list = [name.text for name in names_elems]

        # Get the elements containing player fantasy points, and add their text representation to a list.
        points_elems = rows.find_elements_by_xpath("""//*[@class="Fw-b"]""")
        points_list = [points.text for points in points_elems]

        # Append a list of each player's name and their respective fantasy point total to a main list.
        [data.append([name, point_value]) for name, point_value in zip(names_list, points_list)]

    # Create a data frame from the scraped data.
    df = pd.DataFrame(data=data, columns=['name', 'fantasy_points'])

    # Save the data frame to a csv file.
    df.to_csv('yahoo_data.csv')
