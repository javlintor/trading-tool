import pandas as pd

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
        symbols.append(s["symbol"])
    
    return symbols


def get_kline(client, start_datetime, symbol):
    """
    Get klines from Binance API
    :param client
    :param start_datetime
    :param symbol
    """

    start_str = start_datetime.strftime("%c")
    kline = client.get_historical_klines(
        symbol="ETHBTC",
        interval="1d", 
        start_str=start_str, 
        limit=1000
    )
    # warning: we are assuming col order by Binance API documentation
    columns = ['dateTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol', 'takerBuyQuoteVol', 'ignore']
    df = pd.DataFrame(kline, columns=columns)
    df.dateTime = pd.to_datetime(df.dateTime, unit="ms")
    df.closeTime = pd.to_datetime(df.closeTime, unit="ms")
    num_cols = ['open', 'high', 'low', 'close', 'volume', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol', 'takerBuyQuoteVol']
    df[num_cols] = df[num_cols].apply(pd.to_numeric)
    # delete 'ignore' column
    df.drop("ignore", axis=1, inplace=True)

    return df