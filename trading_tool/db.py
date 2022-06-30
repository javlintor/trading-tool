from datetime import timedelta

import sqlite3
from sqlite3 import Error
import pandas as pd

from trading_tool.load import get_prices, get_kline
from trading_tool.client import CLIENT


def create_connection(db_file):
    """create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        return conn
    except Error as e:
        print(e)

    return conn


CONN = create_connection("trading_tool.db")


def create_table(conn, create_table_sql):
    """create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def insert_asset(conn, row):
    """
    Insert asset to database
    :param conn:
    :param row:
    :return:
    """

    sql = """ INSERT INTO assets(id, asset)
              VALUES(?,?) """
    cur = conn.cursor()
    cur.execute(sql, row)
    conn.commit()

    return cur.lastrowid


def insert_symbol(conn, row):
    """
    Insert symbol to database
    :param conn:
    :param row:
    :return:
    """

    sql = """ INSERT INTO symbols(id, symbol, id_baseAsset, id_quoteAsset)
              VALUES(?,?,?,?) """
    cur = conn.cursor()
    cur.execute(sql, row)
    conn.commit()

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

    query = """
    SELECT DISTINCT symbol FROM symbols
    INNER JOIN klines_1d 
        ON symbols.id = klines_1d.id_symbol
    """

    return pd.read_sql(query, conn)["symbol"].tolist()


def get_db_klines_1d(conn, symbol=None, start_date="2022-01-01", end_date="2022-03-01"):

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

    df = pd.read_sql(query, conn)

    return df


def get_coin_names_from_symbol(symbol):

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

    if df_coins.shape[0] == 0:
        print("symbol is not in ddbb")
        return None, None

    a_coin = df_coins["a_coin"].iloc[0]
    b_coin = df_coins["b_coin"].iloc[0]

    return a_coin, b_coin


def get_usdt_conversion_rate(asset, time=None):

    if asset == "USDT":
        return 1

    # If time is None (default), get prices using get_all_ticker
    # to get the most recent exchange
    if time is None:
        df_prices = get_prices(CLIENT)
        conversion_rate = df_prices.loc[df_prices["asset"] == asset]["price"][0]
        return conversion_rate

    # If time is passed, then use klines to calculate conversion
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

    conversion_rate = get_usdt_conversion_rate(asset, time)
    value_usdt = amount * conversion_rate
    return value_usdt


def from_usdt(asset, amount, time=None):

    conversion_rate = get_usdt_conversion_rate(asset, time)
    value_coin = amount / conversion_rate
    return value_coin
