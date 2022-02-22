from create import create_connection
from binance.client import Client
import configparser

def insert_symbol(conn, symbol):
    """
    Create a new task
    :param conn:
    :param symbol:
    :return:
    """

    sql = ''' INSERT INTO symbols(id, symbol)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, symbol)
    conn.commit()

    return cur.lastrowid

def get_symbols(client, limit=None):
    """
    Get all symbols from Binance API
    :param client
    :param limit
    """
    exchange_info = client.get_exchange_info()
    if limit:
        exchange_info = exchange_info[slice(limit)]
    symbols = []
    for s in exchange_info["symbols"]:
        symbols.append(s["symbol"])
    
    return symbols


def main():

    conn = create_connection("pythonsqlite.db")

    config = configparser.ConfigParser()
    config.read_file(open("secret.cfg"))
    actual_api_key = config.get("BINANCE", "ACTUAL_API_KEY")
    actual_secret_key = config.get("BINANCE", "ACTUAL_SECRET_KEY")

    client = Client(actual_api_key, actual_secret_key)

    symbols = get_symbols(client)

    for symbol in symbols:
        insert_symbol(conn, (None, symbol))

if __name__ == "__main__":
    main()

