import sqlite3
from sqlite3 import Error
import pandas as pd


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
