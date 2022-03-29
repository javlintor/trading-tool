from dash import html, dcc, Input, Output
import dash_daq as daq
import dash_mantine_components as dmc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, date, timedelta, time
from trading_tool.db import create_connection, get_symbols, get_klines_1d
from trading_tool.binance import get_kline, get_last_price
from trading_tool.strategy import simple_strategy
from trading_tool.client import CLIENT
import json
from maindash import app
from views.header import make_header
from views.main_container import make_main_container, make_main_container2

colors = {
    "background": "#12181b",
    "text": "white"
}

conn = create_connection("trading_tool.db")


def make_layout():

    # body
    layout = html.Div([

        # header
        make_header(),

        # horizontal line
        html.Hr(),

        dcc.Tabs(value='overview-tab', className="my-tab-container", parent_className="custom-tabs", children=[
            dcc.Tab(label='Overview', value='overview-tab', className="my-tab", selected_className="my-tab-selected", children=[

            ]),
            dcc.Tab(label='Analytics', value='analytics-tab', className="my-tab", selected_className="my-tab-selected", children=[
                make_main_container(),
                make_main_container2()
            ]),
        ]),

        # footer
        html.Div([
            html.P("Copyright © 2022"), 
            html.A("javlintor", href="https://github.com/javlintor", target="_blank")
        ], 
        className="footer"
        )


    ], className="body")

    return layout


# app callbacks

@app.callback(
    Output('candle_1d', 'figure'),
    Input('symbols', 'value'),
    Input('date_range', 'start_date'),
    Input('date_range', 'end_date')
)
def get_candle_1d_plot(symbol, start_date, end_date):

    df = get_klines_1d(conn, symbol, start_date, end_date)

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df['dateTime'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close']
            )
        ]
    )

    fig.update_layout(
        {
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                'color': colors['text']
            }
        }
    )

    fig.update_layout(
        title={
            'text': symbol,
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

    fig.update_layout(xaxis_rangeslider_visible=False)

    return fig


@app.callback(
    Output('start_day', 'date'),
    Output('end_day', 'date'),
    Input('candle_1d', 'clickData'), 
)
def get_clicked_day(clickData):

    if clickData:
        day = clickData["points"][0]["x"]

    else: 
        day =  date.today().strftime("%Y-%m-%d")

    return day, day


@app.callback(
    Output("candle_1m", "figure"), 
    Output("end-wallet-1", "children"), 
    Output("end-wallet-2", "children"), 
    Output("start-wallet-1", "children"), 
    Output("start-wallet-2", "children"), 
    Output("start-wallet-total", "children"),
    Output("end-wallet-total", "children"),
    Input("start_day", "date"), 
    Input("end_day", "date"), 
    Input("start_time", "value"), 
    Input("end_time", "value"), 
    Input('symbols', 'value'),
    Input('delta', 'value'),
    Input('alpha', 'value'),
    Input('start-wallet-ratio-1', 'value'),
    Input('start-wallet-ratio-2', 'value'),
    Input('reverse', 'value')
)
def get_candle_1m_plot(start_day, end_day, start_time, end_time, symbol, delta, alpha, start_wallet_ratio_1, start_wallet_ratio_2, reverse):

    start_day = datetime.strptime(start_day, "%Y-%m-%d")
    end_day = datetime.strptime(end_day, "%Y-%m-%d")
    start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S").time()
    end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S").time()

    start_datetime = datetime.combine(start_day, start_time)
    end_datetime = datetime.combine(end_day, end_time)

    time_diff =  end_datetime - start_datetime

    if time_diff.seconds // 60 < 60:
        start_datetime = start_datetime - timedelta(minutes=180)


    df = get_kline(
        client=CLIENT, 
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        symbol=symbol, 
        interval="1m"
    )

    first = df.iloc[0]["close"]
    last = df.iloc[-1]["close"]
    start_wallet_1 = start_wallet_ratio_1
    start_wallet_2 = first*start_wallet_ratio_2

    wallet = (start_wallet_1, start_wallet_2)
    buy, sell, end_wallet = simple_strategy(df=df, alpha=alpha, delta=delta, wallet=wallet, reverse=reverse)

    start_wallet_total = wallet[0]*first + wallet[1]
    end_wallet_total = end_wallet[0]*last + end_wallet[1]

    break_points = buy + sell + [df['dateTime'].iloc[-1]]
    break_points.sort()

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df['dateTime'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'], 
                increasing_line_color='cyan',
                decreasing_line_color='yellow', 
                name="candle"
            )
        ]
    )

    time_aux = df['dateTime'].iloc[0]
    for break_point in break_points:

        y = df.loc[df["dateTime"] == time_aux]["close"].iloc[0]

        fig.add_trace(
            go.Scatter(
                x=[time_aux, break_point], 
                y=[y*(1 - delta)]*2, 
                mode='lines', 
                line = dict(width=2, dash='dash', color="red")
            )
        )

        fig.add_trace(
            go.Scatter(
                x=[time_aux, break_point], 
                y=[y*(1 + delta)]*2, 
                mode='lines', 
                line = dict(width=2, dash='dash', color="green")
            )
        )
        time_aux = break_point


    fig.update_layout(
        {
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                'color': colors['text']
            }
        }
    )

    fig.update_layout(
        title={
            'text': symbol,
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.update_layout(showlegend=False)

    return fig, round(end_wallet[0], 2), round(end_wallet[1], 2), round(start_wallet_1, 2), round(start_wallet_2, 2), round(start_wallet_total, 2), round(end_wallet_total, 2)