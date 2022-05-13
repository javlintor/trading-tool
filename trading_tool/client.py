import os
from binance.client import Client

with open("secret.cfg", encoding="UTF-8") as secret_file:
    config.read_file(secret_file)

actual_api_key = os.environ.get('ACTUAL-API-KEY')
actual_secret_key = os.environ.get('ACTUAL-SECRET-KEY')

CLIENT = Client(actual_api_key, actual_secret_key)

test_api_key = os.environ.get('TEST-API-KEY')
test_secret_key = os.environ.get('TEST-SECRET-KEY')

TEST_CLIENT = Client(test_api_key, test_secret_key, testnet=True)
