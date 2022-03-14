import pandas as pd
from datetime import datetime

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


def get_kline(
    client, 
    start_datetime=datetime(2022, 1, 1), 
    end_datetime=datetime(2022, 1, 1),
    symbol="BTCUSDT",
    interval="1d"
):
    """
    Get klines from Binance API
    :param client
    :param start_datetime
    :param symbol
    :param interval
    """

    start_str = start_datetime.strftime("%c")
    end_str = end_datetime.strftime("%c")
    kline = client.get_historical_klines(
        symbol=symbol,
        interval=interval, 
        start_str=start_str, 
        end_str=end_str, 
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

def get_last_price(client, symbol):

    ret = client.get_recent_trades(symbol=symbol)
    last_price = float(ret[-1]["price"])

    return last_price 