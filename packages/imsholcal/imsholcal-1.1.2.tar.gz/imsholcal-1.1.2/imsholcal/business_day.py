# -*- coding: utf-8 -*-
"""
Created on Fri May 12 18:55:08 2023

@author: Matthew.Cunnington
"""

import os
from pandas.tseries.offsets import CustomBusinessDay
import pandas as pd
import requests
import io


def exch_hols(n, country):
    # Clear cache
    requests_cache.clear()
    url = 'https://raw.githubusercontent.com/mcunningto/imsholcal/main/exchange_holidays.csv'
    response = requests.get(url)
    holidays_df = pd.read_csv(io.StringIO(response.text))
	
    # Filter the DataFrame to include only holidays for the specified country
    filtered_df = holidays_df[holidays_df['country'] == country]
    # Convert the date column to datetime format with specified date format
    filtered_df['date'] = pd.to_datetime(filtered_df['date'], format='%d/%m/%Y')
    # Create a list of dates from the filtered DataFrame
    dates = filtered_df['date'].tolist()
    # Create a CustomBusinessDay object that uses the list of dates as holidays
    bday = CustomBusinessDay(holidays=dates) * n
    return bday
