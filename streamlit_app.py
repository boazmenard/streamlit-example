from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import time
import requests
from datetime import date
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

"""
# Welcome to the NCC Parcel Search!

Welcome Forward Real Estate Team! 👋 
 This is the automation tool for parcel search of New Castle County ***ONLY***. 
Right now you can only search one parcel at at time 😭. 
But I'm working on getting you able to search multiple at a time. 
So far I focused on getting you this tool available so that you can start using it right away from your own computers. 
I'll communicate updates to this tool as they come. **Let's work!** 🚀

In the meantime, below is an example of what you can do with just a few lines of code:
"""
import os, sys

@st.experimental_singleton
def installff():
  os.system('sbase install geckodriver')
  os.system('ln -sf /home/appuser/venv/bin/geckodriver /home/appuser/venv/lib/python3.7/site-packages/seleniumbase/drivers/geckodriver')

@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

_ = installff()
opts = Options()
opts.add_argument("--headless")
service = Service(GeckoDriverManager().install())
browser = webdriver.Firefox(options=opts)
parcel_number = st.text_input('Input Parcel Number', '')

if st.button("RUN AUTOMATION"):
    st.write("RUNNING WITH THIS NUMBER: " + parcel_number)
    try:
        website_search_url = 'http://www3.nccde.org/parcel/search/'
        browser.implicitly_wait(3)
        browser.get(website_search_url)
        todays_date = date.today()
        parcel_search_box = browser.find_element('xpath' ,'//*[@id="ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1__TextBoxParcelNumber"]')
        parcel_search_box.send_keys(parcel_number)
        search_button = browser.find_element('xpath' ,'//*[@id="ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1__ButtonSearch"]')
        search_button.click()
        details = browser.find_element('xpath' ,'//*[@id="ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1__GridViewResults_ctl02__LinkButtonDetails"]')
        details.click()
        time.sleep(5)
        detail_url = browser.current_url

        browser.quit()

        #parsing HTML
        page = requests.get(detail_url)
        page_html = BeautifulSoup(page.text, 'html.parser')
        residence_characteristics = page_html.find("div", class_="residence level4")
        table = residence_characteristics.find("table", class_="form")
        all_rows = table.find_all('tr')

        ## Creating the df
        parcel_dictionary = {'Parcel #': parcel_number}
        house_data = []
        for row in all_rows:
            columns = row.find_all('td')
            columns = [elem.text.strip() for elem in columns]
            house_data.append([elem for elem in columns])

        features = []
        data = []
        for sublist in house_data:
            for i in range(len(sublist)):
                if i % 2 == 0:
                    elem = sublist[i].replace(':', '')
                    features.append(elem)
                else:
                    data.append(sublist[i])

        for i in range(len(features)):
            parcel_dictionary[features[i]] = data[i]

        del parcel_dictionary['']
        parcel_data_df = pd.DataFrame([parcel_dictionary])

        # export to excel
        csv = convert_df(parcel_data_df)
        st.write('Your excel sheet is done! Thanks! Please download below.')
        fileName = f'{todays_date}-parcel_sheet_export.csv'
        st.download_button(
        label="Download Here (CSV, resave as .xlsx if needed)",
        data=csv,
        file_name=fileName,
        mime='text/csv'
        )
        job_finished = True
    except Exception as e:
        st.write("The automation couldn't find the information. Please DOUBLE CHECK the parcel number and try again.")
        st.write("If you've already double checked and can find information for the property manually, my apologies! Please note the number down and get back to me.")

