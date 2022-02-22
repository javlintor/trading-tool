from misc import CRYPTOS
from binance.client import Client
import configparser
import time
from datetime import datetime
import pandas as pd

config = configparser.ConfigParser()
config.read_file(open("secret.cfg"))
actual_api_key = config.get("BINANCE", "ACTUAL_API-KEY")
actual_secret_key = config.get("BINANCE", "ACTUAL_SECRET_KEY")

client = Client(actual_api_key, actual_secret_key)

start_datetime = datetime(2018, 1, 1)
start_str = start_datetime.strftime("%c")

kline = client.get_historical_klines("ETHUSDT", "1d", start_str=start_str, limit=1000)




