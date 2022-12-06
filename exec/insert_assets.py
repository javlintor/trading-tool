from trading_tool.db import create_connection, select_query, insert_asset
from trading_tool.load import get_assets
import trading_tool.configloader as cfg
from trading_tool.client import CLIENT


def main():
    # Create a database connection
    conn = create_connection(cfg.DB_FILENAME)

    # Get the assets available in the Binance API
    bi_assets = get_assets(CLIENT)

    # Get the assets already stored in the database
    db_assets = select_query(conn, table_name="assets")["asset"].values.tolist()

    # Get the assets that are not yet in the database
    assets_to_load = list(set(bi_assets) - set(db_assets))

    # Insert the missing assets into the database
    for asset in assets_to_load:
        insert_asset(conn, (None, asset))

    print("Assets loaded.")


if __name__ == "__main__":
    main()
