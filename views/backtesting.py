from datetime import datetime, date, timedelta
import pandas as pd
import dash_daq as daq
from dash import html, dcc, Input, Output
import plotly.graph_objects as go

from trading_tool.client import CLIENT
from trading_tool.db import get_db_klines_1d, CONN, get_coin_names_from_symbol
from trading_tool.binance import get_kline
from trading_tool.strategy import SimpleTrader, Wallet
from trading_tool.constants import (
    MIN_DATE_ALLOWED,
    MAX_DATE_ALLOWED,
    INITIAL_VISIBLE_MONTH,
)
from maindash import app
from views.components import make_vertical_group, make_time_range, make_wallet, make_input_wallet
from views.plot import render_analytics_plot
from views.style import colors, LIGHT_GREEN, ORANGE


def make_backtesting_container_1():

    df_symbols = pd.read_sql(
        con=CONN,
        sql="""
        SELECT DISTINCT symbol AS symbol FROM symbols
        INNER JOIN klines_1d 
            ON klines_1d.id_symbol = symbols.id
        """,
    )

    symbols = df_symbols["symbol"].to_list()

    symbols_dropdown = dcc.Dropdown(value="BTCUSDT", options=symbols, id="symbols")
    date_picker_range = dcc.DatePickerRange(
        id="date-range",
        min_date_allowed=MIN_DATE_ALLOWED,
        max_date_allowed=MAX_DATE_ALLOWED,
        initial_visible_month=INITIAL_VISIBLE_MONTH,
        start_date=date.today() - timedelta(365),
        end_date=date.today(),
    )

    summary_candle_plot = dcc.Graph(
        id="summary-candle-plot",
        responsive=True,
        className="height-100 candle-plot",
    )

    symbols = make_vertical_group(
        title_text="Select a symbol",
        element=symbols_dropdown,
        class_title="medium-font",
    )

    date_range = make_vertical_group(
        title_text="Select a date range",
        element=date_picker_range,
        class_title="medium-font",
    )

    backtesting_container_1 = html.Div(
        id="backtesting-container-1",
        className="grid-container cool-container margins",
        children=[
            # global-options-container
            html.Div(
                id="global-options-container",
                className="flex-container",
                children=[
                    # symbols
                    symbols,
                    # date_range
                    date_range,
                ],
            ),
            # summary-candle-plot
            summary_candle_plot,
        ],
    )

    return backtesting_container_1


def make_backtesting_container_2():

    time_range = make_time_range(
        max_date_allowed=MAX_DATE_ALLOWED,
        min_date_allowed=MIN_DATE_ALLOWED,
        initial_visible_month=INITIAL_VISIBLE_MONTH,
    )

    input_wallet = make_input_wallet(
        wallet_title="Input Wallet",
        id_suffix="-input",
        id_component="input-wallet",
        class_name="",
    )

    switch = make_vertical_group(
        title_text="Switch trader",
        element=daq.ToggleSwitch(id="reverse", value=False),
    )

    analytics_options = html.Div(
        id="analytics-options",
        className="flex-container jc-sa ai-fs cool-container bg-color-1",
        children=[time_range, input_wallet, switch],
    )

    start_wallet = make_wallet(
        wallet_title="Start Wallet",
        id_suffix="-start",
        id_component="start-wallet",
        class_name="bg-color-1 cool-container small-padding",
    )
    end_wallet = make_wallet(
        wallet_title="End Wallet",
        id_suffix="-end",
        id_component="end-wallet",
        class_name="bg-color-1 cool-container small-padding",
    )
    analytics_candle_plot = dcc.Graph(
        id="analytics-candle-plot", responsive=True, className="height-100 candle-plot"
    )

    delta_param = make_vertical_group(
        title_text="delta",
        element=dcc.Slider(0, 0.03, value=0.015, step=0.005, id="delta", className="slider"),
    )
    alpha_param = make_vertical_group(
        title_text="alpha",
        element=dcc.Slider(0, 0.03, value=0.015, step=0.005, id="alpha", className="slider"),
    )

    simple_strategy_activation = html.Button(
        "Activate", id="simply-strategy-activation", n_clicks=0
    )

    simple_strategy_container = html.Div(
        id="simple-strategy",
        className="flex-container-col strategy-container",
        n_clicks=0,
        children=[alpha_param, delta_param, simple_strategy_activation],
    )

    # buttons = html.Div(
    #     [
    #         html.Button("Button 1", id="btn-nclicks-1", n_clicks=0),
    #         html.Button("Button 2", id="btn-nclicks-2", n_clicks=0),
    #         html.Button("Button 3", id="btn-nclicks-3", n_clicks=0),
    #         html.Div(id="container-button-timestamp"),
    #     ]
    # )

    strategies = html.Div(
        id="strategies",
        className="flex-container jc-fs ai-fs cool-container bg-color-1",
        children=[simple_strategy_container],
    )

    backtesting_container_2 = html.Div(
        id="backtesting-container-2",
        className="grid-container cool-container",
        children=[
            # analytics_options
            analytics_options,
            # strategies
            strategies,
            # analytics_candle_plot
            analytics_candle_plot,
            # Start Wallet
            start_wallet,
            # End Wallet
            end_wallet,
        ],
    )

    return backtesting_container_2


@app.callback(
    Output("summary-candle-plot", "figure"),
    Input("symbols", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def get_summary_candle_plot(symbol, start_date, end_date):

    df = get_db_klines_1d(CONN, symbol, start_date, end_date)

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df["dateTime"],
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
            )
        ]
    )

    fig.update_layout(
        {
            "plot_bgcolor": colors["background"],
            "paper_bgcolor": colors["background"],
            "font": {"color": colors["text"]},
        }
    )

    fig.update_layout(
        title={
            "text": symbol,
            "y": 0.9,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        }
    )

    fig.update_layout(xaxis_rangeslider_visible=False)

    return fig


@app.callback(
    Output("a-coin-name-start", "children"),
    Output("a-coin-name-end", "children"),
    Output("a-coin-name-input", "children"),
    Output("b-coin-name-start", "children"),
    Output("b-coin-name-end", "children"),
    Output("b-coin-name-input", "children"),
    Input("symbols", "value"),
)
def get_coins(symbol):

    a_coin, b_coin = get_coin_names_from_symbol(symbol)

    return a_coin, a_coin, a_coin, b_coin, b_coin, b_coin


@app.callback(
    Output("start-day", "date"),
    Output("end-day", "date"),
    Input("summary-candle-plot", "clickData"),
)
def get_clicked_day(click_data):

    if click_data:
        day = click_data["points"][0]["x"]

    else:
        day = date.today().strftime("%Y-%m-%d")

    return day, day


@app.callback(
    Output("analytics-candle-plot", "figure"),
    Output("a-coin-value-end", "children"),
    Output("b-coin-value-end", "children"),
    Output("a-coin-value-start", "children"),
    Output("b-coin-value-start", "children"),
    Output("total-value-start", "children"),
    Output("total-value-input", "children"),
    Output("total-value-end", "children"),
    Input("start-day", "date"),
    Input("end-day", "date"),
    Input("start-time", "value"),
    Input("end-time", "value"),
    Input("symbols", "value"),
    Input("delta", "value"),
    Input("alpha", "value"),
    Input("a-coin-value-input", "value"),
    Input("b-coin-value-input", "value"),
)
def get_analytics_candle_plot(
    start_day,
    end_day,
    start_time,
    end_time,
    symbol,
    delta,
    alpha,
    a_coin_input,
    b_coin_input,
):

    start_day = datetime.strptime(start_day, "%Y-%m-%d")
    end_day = datetime.strptime(end_day, "%Y-%m-%d")
    start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S").time()
    end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S").time()

    start_datetime = datetime.combine(start_day, start_time)
    pre_start_datetime = start_datetime - timedelta(minutes=50)
    end_datetime = datetime.combine(end_day, end_time)

    time_diff = end_datetime - start_datetime

    if time_diff.seconds // 60 < 60:
        start_datetime = start_datetime - timedelta(minutes=180)

    df = get_kline(
        client=CLIENT,
        start_datetime=pre_start_datetime,
        end_datetime=end_datetime,
        symbol=symbol,
        interval="1m",
    )

    df["avg_10"] = df["close"].rolling(10).mean()
    df["avg_50"] = df["close"].rolling(50).mean()
    df.dropna(inplace=True)
    df["ds"] = df["dateTime"]
    df["y"] = df["close"]

    start_wallet = Wallet(
        symbol=symbol,
        a=a_coin_input,
        b=b_coin_input,
    )

    start_wallet_total = start_wallet.get_value_usdt()

    simple_trader = SimpleTrader(df=df, start_wallet=start_wallet, alpha=alpha, delta=delta)

    end_wallet = simple_trader.end_wallet
    end_wallet_total = end_wallet.get_value_usdt()

    fig = render_analytics_plot(
        df=simple_trader.df,
        symbol=simple_trader.start_wallet.symbol,
        avgs={"avg_10": LIGHT_GREEN, "avg_50": ORANGE},
    )

    return (
        fig,
        round(end_wallet.a, 2),
        round(end_wallet.b, 2),
        round(a_coin_input, 2),
        round(b_coin_input, 2),
        round(start_wallet_total, 2),
        round(start_wallet_total, 2),
        round(end_wallet_total, 2),
    )


# @app.callback(
#     Output("container-button-timestamp", "children"),
#     Input("btn-nclicks-1", "n_clicks"),
#     Input("btn-nclicks-2", "n_clicks"),
#     Input("btn-nclicks-3", "n_clicks"),
# )
# def display_click(btn1, btn2, btn3):
#     changed_id = [p["prop_id"] for p in callback_context.triggered][0]
#     if "btn-nclicks-1" in changed_id:
#         msg = "Button 1 was most recently clicked"
#     elif "btn-nclicks-2" in changed_id:
#         msg = "Button 2 was most recently clicked"
#     elif "btn-nclicks-3" in changed_id:
#         msg = "Button 3 was most recently clicked"
#     else:
#         msg = "None of the buttons have been clicked yet"
#     return html.Div(msg)
