from dash import html, dcc
import plotly.express as px
from trading_tool.binance import get_balances
from trading_tool.client import CLIENT

def make_profile_description():

    balances = get_balances(CLIENT)
