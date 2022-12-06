# Import the `configparser` and `os` modules
import configparser
import os

# Import the `Client` class from the `binance` library
from binance.client import Client

# Attempt to read the API keys from the `secret.cfg` file
# If the file is not found, the API keys are read from environment variables
try: 
    with open("secret.cfg", encoding="UTF-8") as secret_file:
        
        # Create a `configparser` object and read the contents of the file
        config = configparser.ConfigParser()
        config.read_file(secret_file)
        
        # Read the actual and test API keys and secret keys from the file
        actual_api_key = config.get("BINANCE", "ACTUAL-API-KEY")
        actual_secret_key = config.get("BINANCE", "ACTUAL-SECRET-KEY")
        test_api_key = config.get("BINANCE", "TEST-API-KEY")
        test_secret_key = config.get("BINANCE", "TEST-SECRET-KEY")
        
# If the file is not found, read the API keys from environment variables
except FileNotFoundError:
    actual_api_key = os.environ.get('ACTUAL_API_KEY')
    actual_secret_key = os.environ.get('ACTUAL_SECRET_KEY')
    test_api_key = os.environ.get('TEST_API_KEY')
    test_secret_key = os.environ.get('TEST_SECRET_KEY')

# Create a `Client` object using the actual API keys
CLIENT = Client(actual_api_key, actual_secret_key)

# Create a `Client` object using the test API keys
TEST_CLIENT = Client(test_api_key, test_secret_key, testnet=True)
