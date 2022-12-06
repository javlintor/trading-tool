# Import the `configparser` and `os` modules
import configparser
import os

# Define environment constants values
_ENV_LOCAL = 'LOCAL'
_ENV_DEV = 'DEV'
_ENV_PROD = 'PROD'

# DB - SQLite
DB_FILENAME = 'trading_tool.db'
DB_FILE_EXISTS = os.path.exists(DB_FILENAME)

# Try to read the "secret.cfg" file
try: 
    # Open the file in read-only mode
    with open("secret.cfg", encoding="UTF-8") as secret_file:

        # Create a `configparser` object and read the contents of the file
        config = configparser.ConfigParser()
        config.read_file(secret_file)

        # Read the environment settings from the file
        ENV = config.get("ENVIRONMENT", "ENV", fallback=_ENV_LOCAL)
        ACTUAL_API_KEY = config.get("BINANCE", "ACTUAL-API-KEY")
        ACTUAL_SECRET_KEY = config.get("BINANCE", "ACTUAL-SECRET-KEY")
        TEST_API_KEY = config.get("BINANCE", "TEST-API-KEY")
        TEST_SECRET_KEY = config.get("BINANCE", "TEST-SECRET-KEY")

# If the file is not found, read the environment settings from the environment variables
except FileNotFoundError:
    ENV = os.environ.get('ENV')
    ACTUAL_API_KEY = os.environ.get('ACTUAL_API_KEY')
    ACTUAL_SECRET_KEY = os.environ.get('ACTUAL_SECRET_KEY')
    TEST_API_KEY = os.environ.get('TEST_API_KEY')
    TEST_SECRET_KEY = os.environ.get('TEST_SECRET_KEY')

# Define environment constants
ENV_LOCAL = ENV == _ENV_LOCAL 
ENV_DEV = ENV == _ENV_DEV
ENV_PROD = ENV == _ENV_PROD
