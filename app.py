from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, date, timedelta
from trading_tool.db import create_connection, get_symbols, get_klines_1d
from trading_tool.binance import get_kline
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
                    ]),

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
                    className="date_range-container"), 

                    html.Div([
                        html.Label(
                            "Choose a day in graph:", 
                            form="day_picked"
                        ),
                        dcc.DatePickerSingle(
                            id='day_picked',
                            min_date_allowed=min_date_allowed,
                            max_date_allowed=max_date_allowed,
                            initial_visible_month=initial_visible_month,
                            date=date.today()
                        )    
                    ],
                    className="date_range-container"),
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
                    ],
                    className="date_range-container"),

                    html.Div([
                        html.Label(
                            "Choose alpha parameter:", 
                            form="day_picked"
                        ),
                        dcc.Slider(0, 0.2, value=0.08, step=0.01, id="alpha")    
                    ],
                    className="date_range-container"),
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
                    html.P("Start Wallet:"), 
                    html.Div(
                        [
                            html.P("1", id="start-wallet-1", className="big-numbers"), 
                            html.P("/", className="space"), 
                            html.P("1", id="start-wallet-2", className="big-numbers")
                        ], 
                        className="wallet")
                ], 
                className="result1-container"
            ),
            html.Div(
                [
                    html.P("End Wallet:"), 
                    html.Div(
                        [
                            html.P(id="end-wallet-1", className="big-numbers"), 
                            html.P("/", className="space"), 
                            html.P(id="end-wallet-2", className="big-numbers")
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
    Output('day_picked', 'date'),
    Input('candle_1d', 'clickData'), 
    
)
def get_clicked_day(clickData):

    if clickData:
        day = clickData["points"][0]["x"]
        return day
    else: 
        return date.today().strftime("%Y-%m-%d")
        # return '2022-02-28'


@app.callback(
    Output("candle_1m", "figure"), 
    Output("end-wallet-1", "children"), 
    Output("end-wallet-2", "children"), 
    Input("day_picked", "date"), 
    Input('symbols', 'value'),
    Input('delta', 'value'),
    Input('alpha', 'value'),
)
def get_candle_1m_plot(day, symbol, delta, alpha):

    day_datetime = datetime.strptime(day, "%Y-%m-%d")
    tomorrow_datetime = day_datetime + timedelta(1)

    df = get_kline(
        client=client, 
        start_datetime=day_datetime,
        end_datetime=tomorrow_datetime,
        symbol=symbol, 
        interval="1m"
    )

    actual = df.loc[0, "open"]

    df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].apply(
        lambda row: row / actual
    )

    buy, sell, end_wallet = simple_strategy(df=df, alpha=alpha, delta=delta)
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
                increasing_line_color= 'cyan',
                decreasing_line_color= 'yellow', 
                name="candle"
            )
        ]
    )

    time_aux = df['dateTime'].iloc[0]
    for break_point in break_points:

        y = df.loc[df["dateTime"] == time_aux]["open"].iloc[0]

        fig.add_trace(
            go.Scatter(
                x=[time_aux, break_point], 
                y=[y - delta]*2, 
                mode='lines', 
                line = dict(width=2, dash='dash', color="red")
            )
        )

        fig.add_trace(
            go.Scatter(
                x=[time_aux, break_point], 
                y=[y + delta]*2, 
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
            'text': symbol + " " + day + " NORMALIZED",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.update_layout(showlegend=False)

    return fig, round(end_wallet[0], 3), round(end_wallet[1], 3)



if __name__ == '__main__':
    app.run_server(debug=True)