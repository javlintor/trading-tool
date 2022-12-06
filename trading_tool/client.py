# Import the `Client` class from the `binance` library
from binance.client import Client
import trading_tool.configloader as cfg

# Create a `Client` object using the actual API keys
CLIENT = Client(cfg.ACTUAL_API_KEY, cfg.ACTUAL_SECRET_KEY)

# Create a `Client` object using the test API keys
TEST_CLIENT = Client(cfg.TEST_API_KEY, cfg.TEST_SECRET_KEY, testnet=True)
