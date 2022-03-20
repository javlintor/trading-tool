import sys
sys.path.append(".")
from trading_tool.db import create_connection, select_query, SAMPLE_SYMBOLS

from trading_tool.binance import get_kline
from datetime import datetime, date
from binance.client import Client
import configparser

import pandas as pd


def main():
    config = configparser.ConfigParser()
    config.read_file(open("secret.cfg"))
    actual_api_key = config.get("BINANCE", "ACTUAL_API_KEY")
    actual_secret_key = config.get("BINANCE", "ACTUAL_SECRET_KEY")

    client = Client(actual_api_key, actual_secret_key)

    conn = create_connection("trading_tool.db")
    sampel_symbols = list(map(lambda symbol: "'" + symbol + "'", SAMPLE_SYMBOLS))
    sample_symbols = ",".join(sampel_symbols)
    symbols = pd.read_sql(
        f"SELECT * FROM symbols WHERE symbol IN ({sample_symbols})", 
        conn
    )

    # loop over symbols and call get_kline

    start_datetime = datetime(2018, 1, 1)
    end_datetime = date.today()

    df_klines = []
    n_klines = symbols.shape[0]
    for i in range(n_klines):
        print("--- Progress %04.2f ----"%(100 * i / n_klines))
        row = symbols.iloc[i]
        symbol = row[1]
        df = get_kline(
            client=client, 
            start_datetime=start_datetime, 
            end_datetime=end_datetime,
            symbol=symbol, 
            interval="1d"
        )
        print(symbol)
        print(df.head())
        df["id_symbol"] = row[0]
        df_klines.append(df)
        print(f"Loaded kline_1d for {symbol}")

    df = pd.concat(df_klines)


    # save dataframe to db
    ok = df.to_sql(name="klines_1d", con=conn, if_exists="append", index=False)
    if not ok:
        print("Some problem with database injection")
    else:
        print("Updated database.")
    

if __name__ == "__main__":
    main()