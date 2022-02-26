import sys
sys.path.append(".")
from trading_tool.db import create_connection, select_query, insert_symbol
from trading_tool.binance import get_symbols
from binance.client import Client
import configparser


def main():

    conn = create_connection("trading_tool.db")

    config = configparser.ConfigParser()
    config.read_file(open("secret.cfg"))
    actual_api_key = config.get("BINANCE", "ACTUAL_API_KEY")
    actual_secret_key = config.get("BINANCE", "ACTUAL_SECRET_KEY")

    client = Client(actual_api_key, actual_secret_key)

    bi_symbols = get_symbols(client)
    db_symbols = select_query(conn, table_name="symbols")["symbol"].values.tolist()

    symbols_to_load = list(
        set(bi_symbols) - set(db_symbols)
    )

    for symbol in symbols_to_load:
        insert_symbol(conn, (None, symbol))

    print("Symbols loaded.")

if __name__ == "__main__":
    main()

