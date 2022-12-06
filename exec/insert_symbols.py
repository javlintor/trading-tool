import pandas as pd

from trading_tool.db import create_connection, select_query
from trading_tool.load import get_symbols
import trading_tool.configloader as cfg
from trading_tool.client import CLIENT

# Import the necessary modules

def main():
    # Establish a database connection
    conn = create_connection(cfg.DB_FILENAME)

    # Retrieve the list of symbols from the client
    bi_symbols = get_symbols(CLIENT)
    # Retrieve the list of symbols already in the database
    db_symbols = select_query(conn, table_name="symbols")["symbol"].values.tolist()

    # Create a list of symbols that need to be loaded
    symbols_to_load = list(set(s["symbol"] for s in bi_symbols) - set(db_symbols))

    # Retrieve the list of assets from the database
    df_assets = select_query(conn, table_name="assets")

    # Create a DataFrame from the symbols that need to be loaded
    df_symbols = pd.DataFrame(bi_symbols)
    df_symbols = df_symbols[df_symbols["symbol"].isin(symbols_to_load)]
    # Merge the symbols DataFrame with the assets DataFrame to add the ids of the base and quote assets
    df_symbols = df_symbols.merge(df_assets, left_on="baseAsset", right_on="asset")
    df_symbols["id_baseAsset"] = df_symbols["id"]
    # Drop unnecessary columns
    df_symbols.drop(["id", "asset"], inplace=True, axis=1)
    # Merge the symbols DataFrame with the assets DataFrame again to add the id of the quote asset
    df_symbols = df_symbols.merge(df_assets, left_on="quoteAsset", right_on="asset")
    df_symbols["id_quoteAsset"] = df_symbols["id"]
    # Drop unnecessary columns
    df_symbols.drop(["id", "asset"], inplace=True, axis=1)
    # Select only the columns we need
    df_symbols = df_symbols[["symbol", "id_baseAsset", "id_quoteAsset"]]

    # Save the DataFrame to the database
    ok = df_symbols.to_sql(name="symbols", con=conn, if_exists="append", index=False)
    # Check if the save was successful
    if not ok:
        print("Some problem with database injection")
    else:
        print("Updated database.")

    print("Symbols loaded.")


if __name__ == "__main__":
    main()

