from datetime import datetime, date, timedelta

import pandas as pd

from trading_tool.db import create_connection
from trading_tool.load import get_kline
from trading_tool.client import CLIENT


def main():

    conn = create_connection("trading_tool.db")
    symbols = pd.read_sql("SELECT * FROM symbols", conn)

    symbols = symbols[symbols.symbol.str.contains("USD")]

    # loop over symbols and call get_kline

    start_datetime = date.today() - timedelta(days=15)
    end_datetime = date.today()

    df_klines = []
    n_klines = symbols.shape[0]
    for i in range(n_klines):

        prct = 100 * i / n_klines
        print(f"--- Progress {prct:.2f} ----")
        row = symbols.iloc[i]
        symbol = row[1]
        df = get_kline(
            client=CLIENT,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            symbol=symbol,
            interval=CLIENT.KLINE_INTERVAL_1DAY,
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
