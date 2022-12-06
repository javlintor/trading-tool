# Import the `timedelta` class and `Error` exception from the `datetime` module
# and the `sqlite3` module
from datetime import timedelta
import sqlite3
from sqlite3 import Error

# Import the `pandas` module
import pandas as pd

# Import the `get_prices` and `get_kline` functions and the `CLIENT` object
# from the `load` and `client` modules
from trading_tool.load import get_prices, get_kline
from trading_tool.client import CLIENT

# Function to create a connection to a SQLite database
def create_connection(db_file):
    """create a database connection to a SQLite database"""
    conn = None
    try:
        # Create a connection to the SQLite database file
        conn = sqlite3.connect(db_file, check_same_thread=False)
        return conn
    except Error as e:
        # Print any error messages
        print(e)

    return conn

# Create a connection to the SQLite database file
CONN = create_connection("trading_tool.db")


def create_table(conn, create_table_sql):
    """create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        # create a cursor
        c = conn.cursor()
        # execute the CREATE TABLE statement
        c.execute(create_table_sql)
    except Error as e:
        # print the error if there is any
        print(e)


def insert_asset(conn, row):
    """
    Insert asset to database
    :param conn: Connection object
    :param row:
    :return: ID of the last inserted row
    """

    # create an INSERT INTO statement
    sql = """ INSERT INTO assets(id, asset)
              VALUES(?,?) """
    # create a cursor
    cur = conn.cursor()
    # execute the INSERT statement
    cur.execute(sql, row)
    # commit the changes to the database
    conn.commit()

    # return the ID of the last inserted row
    return cur.lastrowid



def insert_symbol(conn, row):
    """
    Insert symbol to database
    :param conn: Connection object
    :param row:
    :return: ID of the last inserted row
    """

    # create an INSERT INTO statement
    sql = """ INSERT INTO symbols(id, symbol, id_baseAsset, id_quoteAsset)
              VALUES(?,?,?,?) """
    # create a cursor
    cur = conn.cursor()
    # execute the INSERT statement
    cur.execute(sql, row)
    # commit the changes to the database
    conn.commit()

    # return the ID of the last inserted row
    return cur.lastrowid



# DEPRECATED: instead use pd.read_sql
def select_query(conn, query=None, table_name=None, where=None):
    """
    Insert symbol to database
    :param conn:
    :param query:
    :return:
    """

    cur = conn.cursor()

    if query:

        if table_name or where:
            print("If query is specified, other fileds must be left default")
            return None

        cur.execute(query)
        rows = cur.fetchall()

    if table_name:
        query = f"SELECT * FROM {table_name}"
        if where:
            query += f" WHERE {where}"
        cur.execute(query)
        rows = cur.fetchall()
        cur.execute(f"PRAGMA table_info({table_name});")
        cols = cur.fetchall()
        col_names = list(map(lambda col: col[1], cols))
        df = pd.DataFrame(rows, columns=col_names)
        return df

    df = pd.DataFrame(rows)

    return df


def get_db_symbols(conn):
    """
    Get a list of symbols in the database
    :param conn: Connection object
    :return: list of symbols
    """

    # create a query to get a list of distinct symbols from the `symbols` and `klines_1d` tables
    query = """
    SELECT DISTINCT symbol FROM symbols
    INNER JOIN klines_1d 
        ON symbols.id = klines_1d.id_symbol
    """

    # return the list of symbols
    return pd.read_sql(query, conn)["symbol"].tolist()


def get_db_klines_1d(conn, symbol=None, start_date="2022-01-01", end_date="2022-03-01"):
    """
    Get 1D kline data for a symbol in the database
    :param conn: Connection object
    :param symbol: symbol to get data for (default: None)
    :param start_date: start date in the format 'YYYY-MM-DD' (default: '2022-01-01')
    :param end_date: end date in the format 'YYYY-MM-DD' (default: '2022-03-01')
    :return: DataFrame containing 1D kline data
    """

    # create a query to get 1D kline data for the specified symbol and date range
    query = f"""
    SELECT
    dateTime, 
    open, 
    high, 
    low, 
    close
    FROM symbols
    INNER JOIN klines_1d 
        ON symbols.id = klines_1d.id_symbol
    WHERE symbol = '{symbol}' AND 
        dateTime BETWEEN '{start_date}' AND '{end_date}'
    """

    # get the data as a DataFrame
    df = pd.read_sql(query, conn)

    # return the DataFrame
    return df


def get_coin_names_from_symbol(symbol):
    """
    Get the names of the base and quote assets for a given symbol
    :param symbol: symbol to get names for
    :return: names of the base and quote assets as a tuple
    """

    # get the names of the base and quote assets from the database
    df_coins = pd.read_sql(
        con=CONN,
        sql=f"""
        SELECT
            a_coin.asset AS a_coin,
            b_coin.asset AS b_coin
        FROM symbols AS symbols
        INNER JOIN assets AS a_coin
            ON symbols.id_baseAsset = a_coin.id
        INNER JOIN assets AS b_coin 
            ON symbols.id_quoteAsset = b_coin.id
        WHERE symbols.symbol = '{symbol}'
        """,
    )

    # if the symbol is not in the database, return None for both names
    if df_coins.shape[0] == 0:
        print("symbol is not in ddbb")
        return None, None

    # get the names of the base and quote assets
    a_coin = df_coins["a_coin"].iloc[0]
    b_coin = df_coins["b_coin"].iloc[0]

    # return the names as a tuple
    return a_coin, b_coin


def get_usdt_conversion_rate(asset, time=None):
    """
    Get the USDT conversion rate for a given asset
    :param asset: asset to get the conversion rate for
    :param time: time to get the conversion rate for (default: None)
    :return: USDT conversion rate
    """

    # if the asset is USDT, the conversion rate is 1
    if asset == "USDT":
        return 1

    # if no time is specified, get the most recent price using get_all_ticker
    if time is None:
        df_prices = get_prices(CLIENT)
        conversion_rate = df_prices.loc[df_prices["asset"] == asset]["price"][0]
        return conversion_rate

    # if a time is specified, use klines to calculate the conversion rate
    symbol = asset + "USDT"
    df_trade = get_kline(
        CLIENT,
        start_datetime=time,
        end_datetime=time + timedelta(minutes=1),
        symbol=symbol,
        interval=CLIENT.KLINE_INTERVAL_1MINUTE,
    )
    conversion_rate = df_trade["close"].iloc[0]
    return conversion_rate



def to_usdt(asset, amount, time=None):
    """
    Convert a given amount of an asset to USDT
    :param asset: asset to convert
    :param amount: amount of the asset to convert
    :param time: time to use for conversion rate (default: None)
    :return: equivalent amount in USDT
    """

    # get the conversion rate for the asset
    conversion_rate = get_usdt_conversion_rate(asset, time)
    # convert the amount to USDT
    value_usdt = amount * conversion_rate
    # return the equivalent amount in USDT
    return value_usdt


def from_usdt(asset, amount, time=None):
    """
    Convert a given amount of USDT to an asset
    :param asset: asset to convert to
    :param amount: amount of USDT to convert
    :param time: time to use for conversion rate (default: None)
    :return: equivalent amount in the asset
    """

    # get the conversion rate for the asset
    conversion_rate = get_usdt_conversion_rate(asset, time)
    # convert the amount from USDT to the asset
    value_coin = amount / conversion_rate
    # return the equivalent amount in the asset
    return value_coin
