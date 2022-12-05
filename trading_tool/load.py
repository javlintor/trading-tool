import re

from datetime import datetime
import pandas as pd


def get_assets(client, limit=None):
    """
    Get a list of assets from the Binance API
    :param client: Binance API client
    :param limit: maximum number of assets to return (default: None)
    :return: list of assets
    """

    # get exchange info from the API
    exchange_info = client.get_exchange_info()
    # if a limit is specified, slice the exchange info to the specified limit
    if limit:
        exchange_info = exchange_info[slice(limit)]

    # create lists to store the base and quote assets
    base_asset = []
    quote_asset = []

    # loop through the symbols in the exchange info
    for s in exchange_info["symbols"]:
        # add the base and quote assets to the corresponding lists
        base_asset.append(s["baseAsset"])
        quote_asset.append(s["quoteAsset"])

    # combine the lists of base and quote assets and remove duplicates
    assets = list(set(base_asset).union(set(quote_asset)))

    # return the list of assets
    return assets


def get_symbols(client, limit=None):
    """
    Get a list of symbols from the Binance API
    :param client: Binance API client
    :param limit: maximum number of symbols to return (default: None)
    :return: list of symbols
    """

    # get exchange info from the API
    exchange_info = client.get_exchange_info()
    # if a limit is specified, slice the exchange info to the specified limit
    if limit:
        exchange_info = exchange_info[slice(limit)]

    # create a list to store the symbols
    symbols = []
    # loop through the symbols in the exchange info
    for s in exchange_info["symbols"]:
        # add the symbol, base asset, and quote asset to the list
        symbols.append(
            {
                "symbol": s["symbol"],
                "baseAsset": s["baseAsset"],
                "quoteAsset": s["quoteAsset"],
            }
        )

    # return the list of symbols
    return symbols


def get_kline(
    client,
    start_datetime=datetime(2022, 1, 1),
    end_datetime=datetime(2022, 1, 1),
    symbol="BTCUSDT",
    interval=None,
):
    """
    Get klines (candlestick data) from the Binance API
    :param client: Binance API client
    :param start_datetime: start date and time for the klines (default: 2022-01-01)
    :param end_datetime: end date and time for the klines (default: 2022-01-01)
    :param symbol: symbol for the klines (default: BTCUSDT)
    :param interval: time interval for the klines (default: None)
    :return: DataFrame of klines
    """

    # if no interval is specified, use the default interval of 1 minute
    if interval is None:
        interval = client.KLINE_INTERVAL_1MINUTE

    # convert the start and end datetimes to strings
    start_str = start_datetime.strftime("%c")
    end_str = end_datetime.strftime("%c")

    # get the klines from the API
    kline = client.get_historical_klines(
        symbol=symbol,
        interval=interval,
        start_str=start_str,
        end_str=end_str,
        limit=1000,
    )

    # create a list of column names
    columns = [
        "dateTime",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "closeTime",
        "quoteAssetVolume",
        "numberOfTrades",
        "takerBuyBaseVol",
        "takerBuyQuoteVol",
        "ignore",
    ]

    # create a DataFrame from the klines
    df = pd.DataFrame(kline, columns=columns)

    # convert the dateTime and closeTime columns to datetime objects
    df.dateTime = pd.to_datetime(df.dateTime, unit="ms")
    df.closeTime = pd.to_datetime(df.closeTime, unit="ms")
    num_cols = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quoteAssetVolume",
        "numberOfTrades",
        "takerBuyBaseVol",
        "takerBuyQuoteVol",
    ]
    df[num_cols] = df[num_cols].apply(pd.to_numeric)
    # delete 'ignore' column
    df.drop("ignore", axis=1, inplace=True)

    return df


def get_last_price(client, symbol):
    # Get the recent trades for the given symbol
    ret = client.get_recent_trades(symbol=symbol)
    # Get the last trade price
    last_price = float(ret[-1]["price"])

    return last_price


def get_balances(client):
    # Get the account balances
    account = client.get_account()
    balances = account["balances"]
    # Create a DataFrame from the balances
    df = pd.DataFrame(balances)[["asset", "free"]]
    # Convert the "free" column to numeric
    df["free"] = pd.to_numeric(df["free"])
    # Filter out rows where the balance is 0
    df = df.loc[df["free"] > 0]

    return df


def get_prices(client):
    # Get all tickers
    all_tickers = client.get_all_tickers()
    # Filter out tickers that don't have "USDT" in the symbol
    symbol_price_pairs = [
        symbol_price for symbol_price in all_tickers if "USDT" in symbol_price["symbol"]
    ]
    # Create a DataFrame from the symbol-price pairs
    df = pd.DataFrame(symbol_price_pairs)
    # Convert the "price" column to numeric
    df["price"] = pd.to_numeric(df["price"])
    # Extract the asset name from the symbol and add it as a new column
    df["asset"] = df["symbol"].map(lambda x: re.sub("USDT", "", x))

    return df


def get_portfolio(client):
    # Get the balances DataFrame
    df_balances = get_balances(client)
    # Get the prices DataFrame
    df_prices = get_prices(client)

    # Merge the two DataFrames
    df = df_balances.merge(df_prices, on="asset")
    # Calculate the price of each asset in USDT
    df["price_usdt"] = df["free"] * df["price"]
    # Round the price_usdt to 1 decimal place
    df["price_usdt"] = df["price_usdt"].round(1)

    # Select only the columns we need
    df = df[["asset", "free", "price_usdt"]]

    # Sort the DataFrame by the price_usdt column
    df.sort_values(by=["price_usdt"], inplace=True)

    return df

