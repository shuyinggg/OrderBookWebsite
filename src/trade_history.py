# I DO NOT own this code. Author: @marketstack
# See: https://steemit.com/python/@marketstack/how-to-download-historical-price-data-from-binance-with-python

import requests  # for making http requests to binance
import json  # for parsing what binance sends back to us
import pandas as pd  # for storing and manipulating the data we get back
import numpy as np  # numerical python, i usually need this somewhere
# and so i import by habit nowadays

import datetime as dt  # for dealing with times

root_url = 'https://api.binance.com/api/v1/klines'

symbol = 'STEEMETH'

interval = '1h'

url = root_url + '?symbol=' + symbol + '&interval=' + interval
#print(url)
data = json.loads(requests.get(url).text)
#print(len(data))
df = pd.DataFrame(data)
df.columns = ['open_time',
              'o', 'h', 'l', 'c', 'v',
              'close_time', 'qav', 'num_trades',
              'taker_base_vol', 'taker_quote_vol', 'ignore']

df.index = [dt.datetime.fromtimestamp(x/1000.0) for x in df.close_time]
df.open_time = df.index

with open("trade.json", "w") as f:
    f.write(df.to_json(orient='records'))