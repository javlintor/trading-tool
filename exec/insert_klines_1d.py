from datetime import datetime, date, timedelta

import pandas as pd

from trading_tool.db import create_connection
from trading_tool.load import get_kline
from trading_tool.client import CLIENT

# Import the necessary modules

def main():
    # Create a database connection
    conn = create_connection("trading_tool.db")

    # Read the symbols table from the database
    symbols = pd.read_sql("SELECT * FROM symbols", conn)

    # Filter the symbols to only include those with USD in their name
    symbols = symbols[symbols.symbol.str.contains("USD")]

    # Set the start and end dates for the kline data
    start_datetime = date.today() - timedelta(days=15)
    end_datetime = date.today()

    # Initialize an empty list for storing the kline dataframes
    df_klines = []

    # Get the number of symbols for tracking progress
    n_klines = symbols.shape[0]

    # Iterate over the symbols
    for i in range(n_klines):
        # Calculate the percentage of symbols processed
        prct = 100 * i / n_klines
        print(f"--- Progress {prct:.2f} ----")
        row = symbols.iloc[i]
        symbol = row[1]  # Get the symbol name
        # Retrieve the kline data for the current symbol
        df = get_kline(
            client=CLIENT,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            symbol=symbol,
            interval=CLIENT.KLINE_INTERVAL_1DAY,
        )
        # Print the symbol name and the first few rows of the dataframe
        print(symbol)
        print(df.head())
        # Add the symbol's id to the dataframe
        df["id_symbol"] = row[0]
        # Append the dataframe to the list of dataframes
        df_klines.append(df)
        print(f"Loaded kline_1d for {symbol}")

    # Concatenate the dataframes into a single dataframe
    df = pd.concat(df_klines)

    # Save the DataFrame to the database
    ok = df.to_sql(name="klines_1d", con=conn, if_exists="append", index=False)
    # Check if the save was successful
    if not ok:
        print("Some problem with database injection")
    else:
        print("Updated database.")


if __name__ == "__main__":
    main()
