import sys

sys.path.append(".")
from trading_tool.db import create_connection, select_query

from trading_tool.binance import get_kline
from datetime import datetime, date
from trading_tool.client import CLIENT
import configparser

import pandas as pd


def main():

    conn = create_connection("trading_tool.db")
    symbols = pd.read_sql(f"SELECT * FROM symbols", conn)

    symbols = symbols[symbols.symbol.str.contains("USD")]

    # loop over symbols and call get_kline

    start_datetime = datetime(2018, 1, 1)
    end_datetime = date.today()

    df_klines = []
    n_klines = symbols.shape[0]
    for i in range(n_klines):
        print("--- Progress %04.2f ----" % (100 * i / n_klines))
        row = symbols.iloc[i]
        symbol = row[1]
        df = get_kline(
            client=CLIENT,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            symbol=symbol,
            interval="1d",
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
