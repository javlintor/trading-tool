from trading_tool.db import create_connection, select_query, insert_asset
from trading_tool.load import get_assets
from trading_tool.client import CLIENT


def main():

    conn = create_connection("trading_tool.db")

    bi_assets = get_assets(CLIENT)
    db_assets = select_query(conn, table_name="assets")["asset"].values.tolist()

    assets_to_load = list(set(bi_assets) - set(db_assets))

    for asset in assets_to_load:
        insert_asset(conn, (None, asset))

    print("Assets loaded.")


if __name__ == "__main__":
    main()
