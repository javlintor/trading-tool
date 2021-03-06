import re

from datetime import datetime
import pandas as pd


def get_assets(client, limit=None):
    """
    Get all symbols from Binance API
    :param client
    :param limit
    """
    exchange_info = client.get_exchange_info()
    if limit:
        exchange_info = exchange_info[slice(limit)]

    base_asset = []
    quote_asset = []

    for s in exchange_info["symbols"]:
        base_asset.append(s["baseAsset"])
        quote_asset.append(s["quoteAsset"])

    assets = list(set(base_asset).union(set(quote_asset)))

    return assets


def get_symbols(client, limit=None):
    """
    Get all symbols from Binance API
    :param client
    :param limit
    """
    exchange_info = client.get_exchange_info()
    if limit:
        exchange_info = exchange_info[slice(limit)]
    symbols = []
    for s in exchange_info["symbols"]:
        symbols.append(
            {
                "symbol": s["symbol"],
                "baseAsset": s["baseAsset"],
                "quoteAsset": s["quoteAsset"],
            }
        )

    return symbols


def get_kline(
    client,
    start_datetime=datetime(2022, 1, 1),
    end_datetime=datetime(2022, 1, 1),
    symbol="BTCUSDT",
    interval=None,
):
    """
    Get klines from Binance API
    :param client
    :param start_datetime
    :param symbol
    :param interval
    """

    if interval is None:
        interval = client.KLINE_INTERVAL_1MINUTE

    start_str = start_datetime.strftime("%c")
    end_str = end_datetime.strftime("%c")
    kline = client.get_historical_klines(
        symbol=symbol,
        interval=interval,
        start_str=start_str,
        end_str=end_str,
        limit=1000,
    )
    # warning: we are assuming col order by Binance API documentation
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
    df = pd.DataFrame(kline, columns=columns)
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

    ret = client.get_recent_trades(symbol=symbol)
    last_price = float(ret[-1]["price"])

    return last_price


def get_balances(client):

    account = client.get_account()
    balances = account["balances"]
    df = pd.DataFrame(balances)[["asset", "free"]]
    df["free"] = pd.to_numeric(df["free"])
    df = df.loc[df["free"] > 0]

    return df


def get_prices(client):

    all_tickers = client.get_all_tickers()
    symbol_price_pairs = [
        symbol_price for symbol_price in all_tickers if "USDT" in symbol_price["symbol"]
    ]
    df = pd.DataFrame(symbol_price_pairs)
    df["price"] = pd.to_numeric(df["price"])
    df["asset"] = df["symbol"].map(lambda x: re.sub("USDT", "", x))

    return df


def get_portfolio(client):

    df_balances = get_balances(client)
    df_prices = get_prices(client)

    df = df_balances.merge(df_prices, on="asset")
    df["price_usdt"] = df["free"] * df["price"]
    df["price_usdt"] = df["price_usdt"].round(1)

    df = df[["asset", "free", "price_usdt"]]

    df.sort_values(by=["price_usdt"], inplace=True)

    return df
