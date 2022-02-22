import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from binance.client import Client
import configparser
from binance import ThreadedWebsocketManager
import time

SYMBOLS = [
    "BTC", 
    "ETH", 
    "BNB", 
    "XRP", 
    "ADA", 
    "SOL", 
    "LUNA", 
    "AVAX", 
    "DOGE",
    "DOT", 
    "SHIB", 
    "MATIC", 
    "WBTC", 
    "LTC"
]

def streaming_data_process(msg):
    """
    Function to process the received messages and add latest token pair price
    into the token_usdt dictionary
    :param msg: input message
    """
    global token_usdt
    token_usdt[msg['s']] = msg['c']


def total_amount_usdt(assets, values, token_usdt):
    """
    Function to calculate total portfolio value in USDT
    :param assets: Assets list
    :param values: Assets quantity
    :param token_usdt: Token pair price dict
    :return: total value in USDT
    """
    total_amount = 0
    for i, token in enumerate(assets):
        if token != 'USDT':
            total_amount += float(values[i]) * float(
                token_usdt[token + 'USDT'])
        else:
            total_amount += float(values[i]) * 1
    return total_amount


def total_amount_btc(assets, values, token_usdt):
    """
    Function to calculate total portfolio value in BTC
    :param assets: Assets list
    :param values: Assets quantity
    :param token_usdt: Token pair price dict
    :return: total value in BTC
    """
    total_amount = 0
    for i, token in enumerate(assets):
        if token != 'BTC' and token != 'USDT':
            total_amount += float(values[i]) \
                            * float(token_usdt[token + 'USDT']) \
                            / float(token_usdt['BTCUSDT'])
        if token == 'BTC':
            total_amount += float(values[i]) * 1
        else:
            total_amount += float(values[i]) \
                            / float(token_usdt['BTCUSDT'])
    return total_amount


def assets_usdt(assets, values, token_usdt):
    """
    Function to convert all assets into equivalent USDT value
    :param assets: Assets list
    :param values: Assets quantity
    :param token_usdt: Token pair price dict
    :return: list of asset values in USDT
    """
    assets_in_usdt = []
    for i, token in enumerate(assets):
        if token != 'USDT':
            assets_in_usdt.append(
                float(values[i]) * float(token_usdt[token + 'USDT'])
            )
        else:
            assets_in_usdt.append(float(values[i]) * 1)
    return assets_in_usdt
