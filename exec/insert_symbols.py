import sys

sys.path.append(".")
from trading_tool.db import create_connection, select_query, insert_symbol
from trading_tool.binance import get_symbols
from trading_tool.client import CLIENT
import pandas as pd


def main():

    conn = create_connection("trading_tool.db")

    bi_symbols = get_symbols(CLIENT)
    db_symbols = select_query(conn, table_name="symbols")["symbol"].values.tolist()

    symbols_to_load = list(set([s["symbol"] for s in bi_symbols]) - set(db_symbols))

    df_assets = select_query(conn, table_name="assets")
    df_symbols = pd.DataFrame(bi_symbols)
    df_symbols = df_symbols[df_symbols["symbol"].isin(symbols_to_load)]
    df_symbols = df_symbols.merge(df_assets, left_on="baseAsset", right_on="asset")
    df_symbols["id_baseAsset"] = df_symbols["id"]
    df_symbols.drop(["id", "asset"], inplace=True, axis=1)
    df_symbols = df_symbols.merge(df_assets, left_on="quoteAsset", right_on="asset")
    df_symbols["id_quoteAsset"] = df_symbols["id"]
    df_symbols.drop(["id", "asset"], inplace=True, axis=1)
    df_symbols = df_symbols[["symbol", "id_baseAsset", "id_quoteAsset"]]

    print(df_symbols.head())

    # save dataframe to db
    ok = df_symbols.to_sql(name="symbols", con=conn, if_exists="append", index=False)
    if not ok:
        print("Some problem with database injection")
    else:
        print("Updated database.")

    print("Symbols loaded.")


if __name__ == "__main__":
    main()
