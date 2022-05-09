from datetime import datetime, date, timedelta
import pandas as pd
import dash_daq as daq
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback_context
import plotly.graph_objects as go

from trading_tool.client import CLIENT
from trading_tool.db import get_db_klines_1d, CONN, get_coin_names_from_symbol, from_usdt
from trading_tool.binance import get_kline
from trading_tool.strategy import SimpleStrategy, DummyStrategy, Wallet
from trading_tool.constants import (
    MIN_DATE_ALLOWED,
    MAX_DATE_ALLOWED,
    INITIAL_VISIBLE_MONTH,
    PRECISION,
    INITIAL_AMOUNT_USDT,
)
from maindash import app
from views.components import (
    make_vertical_group,
    make_time_range,
    make_wallet,
    make_input_wallet,
    make_metric,
)
from views.plot import render_analytics_plot
from views.style import colors, LIGHT_GREEN, ORANGE, format_number


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

    analytics_options = html.Div(
        id="analytics-options",
        className="flex-container jc-sa ai-fs cool-container bg-color-1",
        children=[time_range, input_wallet],
    )

    start_wallet = make_wallet(
        wallet_title="💰 Start Wallet",
        id_suffix="-start",
        id_component="start-wallet",
        class_name="bg-color-1 cool-container small-padding",
    )
    end_wallet = make_wallet(
        wallet_title="💰 End Wallet",
        id_suffix="-end",
        id_component="end-wallet",
        class_name="bg-color-1 cool-container small-padding",
    )
    analytics_candle_plot = dcc.Graph(
        id="analytics-candle-plot", responsive=True, className="height-100 candle-plot"
    )

    # ---- Strategies ------

    # dummy

    dummy_strategy_label = html.Label(children="Dummy Strategy", className="big-font")

    dummy_strategy_activation = html.Button("Activate", id="dummy-strategy-btn")

    dummy_strategy_container = html.Div(
        id="dummy-strategy",
        className="flex-container-col strategy-container",
        children=[dummy_strategy_label, dummy_strategy_activation],
    )

    # simple

    simple_strategy_label = html.Label(children="Simple Strategy", className="big-font")

    delta_param = make_vertical_group(
        title_text="delta",
        element=dcc.Slider(0, 0.03, value=0.015, step=0.005, id="delta", className="slider"),
    )
    alpha_param = make_vertical_group(
        title_text="alpha",
        element=dcc.Slider(0, 0.03, value=0.015, step=0.005, id="alpha", className="slider"),
    )

    simple_strategy_activation = html.Button("Activate", id="simple-strategy-btn")

    simple_strategy_container = html.Div(
        id="simple-strategy",
        className="flex-container-col strategy-container",
        children=[simple_strategy_label, alpha_param, delta_param, simple_strategy_activation],
    )

    strategies = html.Div(
        id="strategies",
        className="flex-container jc-fs ai-stretch cool-container bg-color-1",
        children=[dummy_strategy_container, simple_strategy_container],
    )

    # ------ metrics ----------

    n_operations = make_metric(metric_name="# of operations", id_number="n-operations")
    n_good_operations = make_metric(
        metric_name="# of good operations ✅", id_number="n-good-operations"
    )
    n_bad_operations = make_metric(
        metric_name="# of bad operations ❌", id_number="n-bad-operations"
    )
    n_operations_by_hour = make_metric(
        metric_name="# of operations by hour 🕙", id_number="n-operations-by-hour"
    )
    mean_operation_time = make_metric(
        metric_name="Mean operation time ⏱", id_number="mean-operation-time"
    )

    metrics_1 = html.Div(
        id="metrics-1",
        className="bg-color-1 cool-container small-padding flex-container-col",
        children=[n_operations, n_good_operations, n_bad_operations],
    )

    metrics_2 = html.Div(
        id="metrics-2",
        className="bg-color-1 cool-container small-padding flex-container-col",
        children=[n_operations_by_hour, mean_operation_time],
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
            # metrics
            metrics_1,
            metrics_2,
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
    Output("a-coin-value-input", "value"),
    Output("b-coin-value-input", "value"),
    Output("a-coin-value-input", "step"),
    Output("b-coin-value-input", "step"),
    Input("symbols", "value"),
)
def get_coins(symbol):

    a_coin, b_coin = get_coin_names_from_symbol(symbol)

    # compute reasonable input values for a and b coins
    a = from_usdt(asset=a_coin, amount=INITIAL_AMOUNT_USDT)
    b = from_usdt(asset=b_coin, amount=INITIAL_AMOUNT_USDT)
    a_step = a / 20
    b_step = b / 20
    a = format_number(a, PRECISION)
    b = format_number(b, PRECISION)

    return a_coin, a_coin, a_coin, b_coin, b_coin, b_coin, a, b, a_step, b_step


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
    Output("dummy-strategy", "style"),
    Output("simple-strategy", "style"),
    Output("n-operations", "children"),
    Output("n-good-operations", "children"),
    Output("n-bad-operations", "children"),
    Output("n-operations-by-hour", "children"),
    Output("mean-operation-time", "children"),
    Output("strategies", "n_clicks"),
    Input("start-day", "date"),
    Input("end-day", "date"),
    Input("start-time", "value"),
    Input("end-time", "value"),
    Input("symbols", "value"),
    Input("delta", "value"),
    Input("alpha", "value"),
    Input("a-coin-value-input", "value"),
    Input("b-coin-value-input", "value"),
    Input("dummy-strategy-btn", "n_clicks_timestamp"),
    Input("simple-strategy-btn", "n_clicks_timestamp"),
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
    dummy_strategy_btn_timestamp,
    simple_strategy_btn_timestamp,
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
        interval=CLIENT.KLINE_INTERVAL_1MINUTE,
    )

    df["avg_10"] = df["close"].rolling(10).mean()
    df["avg_50"] = df["close"].rolling(50).mean()
    df.dropna(inplace=True)
    df["ds"] = df["dateTime"]
    df["y"] = df["close"]

    a_coin_input = float(a_coin_input)
    b_coin_input = float(b_coin_input)

    start_wallet = Wallet(
        symbol=symbol,
        a=a_coin_input,
        b=b_coin_input,
    )

    start_wallet_total = start_wallet.get_value_usdt()

    if dummy_strategy_btn_timestamp is None:
        dummy_strategy_btn_timestamp = 1
    if simple_strategy_btn_timestamp is None:
        simple_strategy_btn_timestamp = 0
    print("dummy_strategy_btn_timestamp", dummy_strategy_btn_timestamp)
    print("simple_strategy_btn_timestamp", simple_strategy_btn_timestamp)
    print("dummy_strategy_btn_timestamp type", type(dummy_strategy_btn_timestamp))
    print("simple_strategy_btn_timestamp type", type(simple_strategy_btn_timestamp))

    # by default, use dummy strategy
    strategies_btn_timestamps = {
        "dummy": dummy_strategy_btn_timestamp,
        "simple": simple_strategy_btn_timestamp,
    }

    strategies_btn_timestamps_sorted = {
        k: v for k, v in sorted(strategies_btn_timestamps.items(), key=lambda item: item[1])
    }

    print("strategies_btn_timestamps_sorted: ", strategies_btn_timestamps_sorted)

    selected_strategy = list(strategies_btn_timestamps_sorted.keys())[-1]

    print("selected_strategy: ", selected_strategy)

    dummy_strategy_style = {}
    simple_strategy_style = {}
    if "dummy" in selected_strategy:
        print("Dummy Strategy selected!")
        strategy = DummyStrategy(df=df, start_wallet=start_wallet)
        dummy_strategy_style = {"border-color": "red"}
    elif "simple" in selected_strategy:
        strategy = SimpleStrategy(df=df, start_wallet=start_wallet, alpha=alpha, delta=delta)
        simple_strategy_style = {"border-color": "red"}
        print("Simple Strategy selected!")
    else:
        print("Dummy Strategy selected!")
        strategy = DummyStrategy(df=df, start_wallet=start_wallet)
        dummy_strategy_style = {"border-color": "red"}

    end_wallet = strategy.end_wallet
    end_wallet_total = end_wallet.get_value_usdt()

    n_operations = strategy.get_n_operations()
    n_good_operations = strategy.get_n_good_operations()
    n_bad_operations = strategy.get_n_bad_operations()
    n_operations_by_hour = strategy.get_n_operations_by_hour()
    mean_operation_time = strategy.get_mean_operation_time()

    fig = render_analytics_plot(
        df=strategy.df,
        symbol=strategy.start_wallet.symbol,
        avgs={"avg_10": LIGHT_GREEN, "avg_50": ORANGE},
    )

    return (
        fig,
        format_number(end_wallet.a, PRECISION),
        format_number(end_wallet.b, PRECISION),
        format_number(a_coin_input, PRECISION),
        format_number(b_coin_input, PRECISION),
        format_number(start_wallet_total, PRECISION),
        format_number(start_wallet_total, PRECISION),
        format_number(end_wallet_total, PRECISION),
        dummy_strategy_style,
        simple_strategy_style,
        n_operations,
        n_good_operations,
        n_bad_operations,
        n_operations_by_hour,
        mean_operation_time,
        42,
    )
