import sys
sys.path.append(".")
from trading_tool.db import create_connection, create_table

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
    CREATE TABLE IF NOT EXISTS klines_1d (
        id integer PRIMARY KEY AUTOINCREMENT, 
        id_symbol integer NOT NULL, 
        dateTime integer NOT NULL, 
        open real NOT NULL, 
        high real NOT NULL, 
        low real NOT NULL, 
        close real NOT NULL, 
        volume real NOT NULL,
        closeTime integer NOT NULL,
        quoteAssetVolume real NOT NULL,
        numberOfTrades real NOT NULL,
        takerBuyBaseVol real NOT NULL,
        takerBuyQuoteVol real NOT NULL, 
        FOREIGN KEY (id_symbol) REFERENCES symbols (id)
    )
    """

    # create a database connection
    conn = create_connection("trading_tool.db")

    # # create tables
    if conn is not None:
        # create symbols table
        create_table(conn, create_symbols_query)

        # create klines table
        create_table(conn, create_klines_1d_query)
    else:
        print("Error! cannot create the database connection.")

    print("Tables created.")

if __name__ == '__main__':
    main()