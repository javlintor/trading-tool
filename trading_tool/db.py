import sqlite3
import pandas as pd

from sqlite3 import Error



def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    
    return conn



def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def insert_symbol(conn, symbol):
    """
    Insert symbol to database
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

def select_query(conn, query=None, table_name=None, where=None):
    """
    Insert symbol to database
    :param conn:
    :param query:
    :return:
    """

    cur = conn.cursor()
    
    if query:

        if not (table_name or where):
            raise "If query is specified, other fileds must be left default"

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
