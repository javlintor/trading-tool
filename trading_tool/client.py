import configparser
import os

from binance.client import Client

try: 
    with open("secret.cfg", encoding="UTF-8") as secret_file:
        
        config = configparser.ConfigParser()
        
        config.read_file(secret_file)
        
        actual_api_key = config.get("BINANCE", "ACTUAL-API-KEY")
        actual_secret_key = config.get("BINANCE", "ACTUAL-SECRET-KEY")
        test_api_key = config.get("BINANCE", "TEST-API-KEY")
        test_secret_key = config.get("BINANCE", "TEST-SECRET-KEY")
        
except FileNotFoundError:
    actual_api_key = os.environ.get('ACTUAL_API_KEY')
    actual_secret_key = os.environ.get('ACTUAL_SECRET_KEY')
    test_api_key = os.environ.get('TEST_API_KEY')
    test_secret_key = os.environ.get('TEST_SECRET_KEY')


CLIENT = Client(actual_api_key, actual_secret_key)
TEST_CLIENT = Client(test_api_key, test_secret_key, testnet=True)