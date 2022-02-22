import sqlite3
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

def main():

    # create master_data.symbols table
    create_symbols_query = f"""
    CREATE TABLE IF NOT EXISTS symbols (
        id integer PRIMARY KEY AUTOINCREMENT, 
        symbol text NOT NULL, 
        UNIQUE (symbol)
    )
    """

    # create series.klines_1d table
    create_klines_1d_query = f"""
    CREATE TABLE IF NOT EXISTS klines (
        id integer PRIMARY KEY AUTOINCREMENT, 
        id_symbol integer NOT NULL, 
        timestamp integer NOT NULL, 
        open real NOT NULL, 
        high real NOT NULL, 
        low real NOT NULL, 
        clse real NOT NULL, 
        FOREIGN KEY (id_symbol) REFERENCES symbols (id)
    )
    """

    # create a database connection
    conn = create_connection("pythonsqlite.db")

    # # create tables
    if conn is not None:
        # create symbols table
        create_table(conn, create_symbols_query)

        # create klines table
        create_table(conn, create_klines_1d_query)
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()