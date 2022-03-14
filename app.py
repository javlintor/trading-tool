from dash import Dash, html, dcc, Input, Output
import dash_mantine_components as dmc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, date, timedelta, time
from trading_tool.db import create_connection, get_symbols, get_klines_1d
from trading_tool.binance import get_kline, get_last_price
from trading_tool.strategy import simple_strategy
import json
from binance.client import Client
import configparser

app = Dash(__name__)

colors = {
    "background": "#12181b",
    "text": "white"
}

conn = create_connection("trading_tool.db")

config = configparser.ConfigParser()
config.read_file(open('secret.cfg'))
actual_api_key = config.get('BINANCE', 'ACTUAL_API_KEY')
actual_secret_key = config.get('BINANCE', 'ACTUAL_SECRET_KEY')

client = Client(actual_api_key, actual_secret_key)

min_date_allowed = date(2015, 1, 1)
max_date_allowed = date(2025, 1, 1)
initial_visible_month=date(2022, 2, 1)

app.layout = html.Div([

    html.Div(
        [
            html.H1('Trading-tool', className="title"),
            html.Div([
                html.P(
                    'Lucas de Lecea', className="description-name"
                ),
                html.P(
                    'Boosting group', className="description"
                )
            ])
        ], 
        className="header"
    ),

    html.Hr(),

    html.Div(
        [
            html.Div(
                [
                    dcc.Graph(
                        id='candle_1d',
                        responsive=True, 
                        className="candle_plot"
                    ),
                ], 
                className="candle_plot-container"
            ), 

            html.Div(
                [
                    html.Div([
                        html.Label(
                            "Select a symbol:", 
                            form="symbols"
                        ),
                        dcc.Dropdown(
                            options=get_symbols(conn), 
                            value="BTCUSDT",
                            id='symbols'
                        ), 
                    ], 
                    className="symbols-container"),

                    html.Div([
                        html.Label(
                            "Select a date range:", 
                            form="date_range"
                        ),
                        dcc.DatePickerRange(
                            id='date_range',
                            min_date_allowed=min_date_allowed,
                            max_date_allowed=max_date_allowed,
                            initial_visible_month=initial_visible_month,
                            start_date=date.today() - timedelta(365),
                            end_date=date.today()
                        ),
                    ],
                    className="flex-container"), 

                    html.Div([
                        html.P(
                            "Choose time interval for analysis:", 
                            id="time_range-label"
                        ),
                        dcc.DatePickerSingle(
                            id='start_day',
                            min_date_allowed=min_date_allowed,
                            max_date_allowed=max_date_allowed,
                            initial_visible_month=initial_visible_month,
                            date=date.today()
                        ), 
                        dmc.TimeInput(
                            label="Start time:",
                            id="start_time",
                            value=datetime.combine(date.today(), datetime.min.time()),
                            class_name="Timeinput"
                        ),   
                        dcc.DatePickerSingle(
                            id='end_day',
                            min_date_allowed=min_date_allowed,
                            max_date_allowed=max_date_allowed,
                            initial_visible_month=initial_visible_month,
                            date=date.today()
                        ), 
                        dmc.TimeInput(
                            label="End time:",
                            id="end_time",
                            value=datetime.now().replace(microsecond=0), 
                            class_name="Timeinput"
                        ),   
                    ],
                    className="time_range-container"),
                ],
                className="options1-container"
            ), 

        ], 
        className="main-container"
    ),

    html.Div(
        [

            html.Div(
                [

                    html.Div([
                        html.Label(
                            "Choose delta parameter:", 
                            form="delta"
                        ),
                        dcc.Slider(0, 0.03, value=0.01, step=0.002, id="delta") 
                    ]),

                    html.Div([
                        html.Label(
                            "Choose alpha parameter:", 
                            form="day_picked"
                        ),
                        dcc.Slider(0, 0.2, value=0.08, step=0.01, id="alpha")    
                    ]),

                    html.Div([
                        html.Label(
                            "Start wallet:", 
                        ),
                        html.Div(
                            [
                                dcc.Input(
                                    id="start-wallet-ratio-1",
                                    type="number",
                                    placeholder=None,
                                    value=0.3, 
                                    step=0.01
                                ),
                                dcc.Input(
                                    id="start-wallet-ratio-2",
                                    type="number",
                                    placeholder=None,
                                    value=0.3, 
                                    step=0.01
                                ) 
                            ], 
                            className="num-input-container"
                        )   
                    ],
                    className="flex-container"),
                ],
                className="options2-container"
            ), 

            html.Div(
                [
                    dcc.Graph(
                        id='candle_1m',
                        responsive=True, 
                        className="candle_1m"
                    ),
                ], 
                className="candle_1m-container"
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.P("Start Wallet", className="title-wallet"), 
                            html.P("A Coin", id="start-wallet-1-title"), 
                            html.P("B Coin", id="start-wallet-2-title"),
                            html.P(id="start-wallet-1", className="big-numbers"), 
                            html.P(id="start-wallet-2", className="big-numbers"),
                            html.P("Total (USD); ", className="total-text"),
                            html.P(id="start-wallet-total", className="big-numbers")
                        ], 
                        className="wallet")
                ], 
                className="result1-container"
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.P("End Wallet", className="title-wallet"), 
                            html.P("A Coin", id="end-wallet-1-title"), 
                            html.P("B Coin", id="end-wallet-2-title"),
                            html.P(id="end-wallet-1", className="big-numbers"), 
                            html.P(id="end-wallet-2", className="big-numbers"), 
                            html.P("Total (USD); ", className="total-text"),
                            html.P(id="end-wallet-total", className="big-numbers")
                        ], className="wallet")
                ], 
                className="result2-container"
            )
        ], 
        className="main-container-2"
    ), 

    html.Div(
        [
            html.P("Copyright © 2022"), 
            html.A("javlintor", href="https://github.com/javlintor", target="_blank")
        ], 
        className="footer"
    )


], className="body")

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
)
def get_candle_1m_plot(start_day, end_day, start_time, end_time, symbol, delta, alpha, start_wallet_ratio_1, start_wallet_ratio_2):

    print(start_day)
    print(end_day)
    print(start_time)
    print(end_time)

    start_day = datetime.strptime(start_day, "%Y-%m-%d")
    end_day = datetime.strptime(end_day, "%Y-%m-%d")
    start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S").time()
    end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S").time()

    start_datetime = datetime.combine(start_day, start_time)
    end_datetime = datetime.combine(end_day, end_time)

    time_diff =  end_datetime - start_datetime

    if time_diff.seconds // 60 < 60:
        start_datetime = start_datetime - timedelta(minutes=180)

    print(start_datetime)
    print(end_datetime)    

    df = get_kline(
        client=client, 
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        symbol=symbol, 
        interval="1m"
    )

    first = df.iloc[0]["close"]
    last = df.iloc[-1]["close"]
    start_wallet_1 = start_wallet_ratio_1
    start_wallet_2 = first*start_wallet_ratio_2

    # df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].apply(
    #     lambda row: row / actual
    # )

    wallet = (start_wallet_1, start_wallet_2)
    buy, sell, end_wallet = simple_strategy(df=df, alpha=alpha, delta=delta, wallet=wallet)

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



if __name__ == '__main__':
    app.run_server(debug=True)