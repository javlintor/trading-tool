import configparser
from binance.client import Client
from binance import ThreadedWebsocketManager

config = configparser.ConfigParser()
config.read_file(open('secret.cfg'))
actual_api_key = config.get('BINANCE', 'ACTUAL_API_KEY')
actual_secret_key = config.get('BINANCE', 'ACTUAL_SECRET_KEY')

CLIENT = Client(actual_api_key, actual_secret_key)

test_api_key = config.get('BINANCE', 'TEST_API_KEY')
test_secret_key = config.get('BINANCE', 'TEST_SECRET_KEY')

TEST_CLIENT = Client(test_api_key, test_secret_key, testnet=True)


# Streaming data for tokens in the portfolio
TWM = ThreadedWebsocketManager(actual_api_key, actual_secret_key)

token_usdt = {}
