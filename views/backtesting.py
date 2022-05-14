from datetime import datetime, date, timedelta
import pandas as pd
from dash import html, dcc, Input, Output
import plotly.graph_objects as go

from trading_tool.client import CLIENT
from trading_tool.db import get_db_klines_1d, CONN, get_coin_names_from_symbol, from_usdt
from trading_tool.binance import get_kline
from trading_tool.strategy import SimpleStrategy, DummyStrategy, Wallet, MovingAverageStrategy
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
from views.style import colors, LIGHT_GREEN, ORANGE, format_number, format_percentage


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

    big_ma_selector = make_vertical_group(
        title_text="Big Moving Average",
        class_title="medium-font",
        element=dcc.Slider(
            50,
            500,
            value=100,
            step=10,
            id="big-ma-selector",
            className="slider",
            marks=None,
            tooltip={"placement": "bottom"},
        ),
    )

    small_ma_selector = make_vertical_group(
        title_text="Small Moving Average",
        class_title="medium-font",
        element=dcc.Slider(
            0,
            50,
            value=20,
            step=1,
            id="small-ma-selector",
            className="slider",
            marks=None,
            tooltip={"placement": "bottom"},
        ),
    )

    ma_selectors = html.Div(
        className="flex-container-col", children=[big_ma_selector, small_ma_selector]
    )

    analytics_options = html.Div(
        id="analytics-options",
        className="flex-container jc-sa ai-fs cool-container bg-color-1",
        children=[time_range, input_wallet, ma_selectors],
    )

    start_wallet = make_wallet(
        wallet_title="💰 Start Wallet",
        id_suffix="-start",
        id_component="start-wallet",
        class_name="bg-color-1 cool-container",
    )
    end_wallet = make_wallet(
        wallet_title="💰 End Wallet",
        id_suffix="-end",
        id_component="end-wallet",
        class_name="bg-color-1 cool-container",
    )
    analytics_candle_plot = dcc.Graph(
        id="analytics-candle-plot", responsive=True, className="candle-plot"
    )

    # ---- Strategies ------

    # dummy

    dummy_strategy_label = html.Label(children="Dummy Strategy", className="big-font")

    dummy_strategy_activation = html.Button("Activate", id="dummy-strategy-btn", className="hor-auto-margin")

    dummy_strategy_container = html.Div(
        id="dummy-strategy",
        className="flex-container-col strategy-container",
        children=[dummy_strategy_label, dummy_strategy_activation],
    )

    # simple

    simple_strategy_label = html.Label(children="Simple Strategy", className="big-font")

    delta_param = make_vertical_group(
        title_text="delta",
        element=dcc.Slider(
            0,
            0.02,
            value=0.008,
            step=0.0005,
            id="ss_delta",
            className="slider",
            marks=None,
            tooltip={"placement": "bottom"},
        ),
    )
    alpha_param = make_vertical_group(
        title_text="alpha",
        element=dcc.Slider(
            0,
            0.3,
            value=0.15,
            step=0.005,
            id="ss_alpha",
            className="slider",
            marks=None,
            tooltip={"placement": "bottom"},
        ),
    )

    simple_strategy_activation = html.Button("Activate", id="simple-strategy-btn", className="hor-auto-margin")

    simple_strategy_container = html.Div(
        id="simple-strategy",
        className="flex-container-col strategy-container",
        children=[simple_strategy_label, alpha_param, delta_param, simple_strategy_activation],
    )

    # moving average
    ma_strategy_label = html.Label(children="Moving Average Strategy", className="big-font")
    big_ma_param = make_vertical_group(
        title_text="Big Moving Average", element=html.P(id="big-ma"), tiny_gap=True
    )
    small_ma_param = make_vertical_group(
        title_text="Small Moving Average", element=html.P(id="small-ma"), tiny_gap=True
    )
    ma_alpha_param = make_vertical_group(
        title_text="alpha",
        element=dcc.Slider(
            0,
            0.3,
            value=0.15,
            step=0.005,
            id="ma_alpha",
            className="slider",
            marks=None,
            tooltip={"placement": "bottom"},
        ),
    )
    ma_activation = html.Button("Activate", id="ma-strategy-btn", className="hor-auto-margin")

    ma_strategy_container = html.Div(
        id="ma-strategy",
        className="flex-container-col strategy-container",
        children=[ma_strategy_label, big_ma_param, small_ma_param, ma_alpha_param, ma_activation],
    )

    strategies = html.Div(
        id="strategies",
        className="flex-container jc-fs ai-stretch cool-container bg-color-1",
        children=[dummy_strategy_container, simple_strategy_container, ma_strategy_container],
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
    interval_profitability = make_metric(
        metric_name="Profitability in selected interval", id_number="interval-profitability"
    )
    market_profitability = make_metric(
        metric_name="Market profitability", id_number="market-profitability"
    )
    mean_profitability = make_metric(
        metric_name="Mean profitability", id_number="mean-profitability"
    )
    daily_profitabiliy = make_metric(
        metric_name="Daily profitability", id_number="daily-profitability"
    )
    weekly_profitabiliy = make_metric(
        metric_name="Weekly profitability", id_number="weekly-profitability"
    )
    yearly_profitabiliy = make_metric(
        metric_name="Yearly profitability", id_number="yearly-profitability"
    )

    metrics_1 = html.Div(
        id="metrics-1",
        className="bg-color-1 cool-container flex-container-col",
        children=[n_operations, n_good_operations, n_bad_operations],
    )

    metrics_2 = html.Div(
        id="metrics-2",
        className="bg-color-1 cool-container flex-container-col",
        children=[n_operations_by_hour, mean_operation_time],
    )

    metrics_3 = html.Div(
        id="metrics-3",
        className="bg-color-1 cool-container flex-container-col",
        children=[interval_profitability, market_profitability, mean_profitability],
    )

    metrics_4 = html.Div(
        id="metrics-4",
        className="bg-color-1 cool-container flex-container-col",
        children=[daily_profitabiliy, weekly_profitabiliy, yearly_profitabiliy],
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
            metrics_3,
            metrics_4,
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
    Output("ma-strategy", "style"),
    Output("n-operations", "children"),
    Output("n-good-operations", "children"),
    Output("n-bad-operations", "children"),
    Output("n-operations-by-hour", "children"),
    Output("mean-operation-time", "children"),
    Output("interval-profitability", "children"),
    Output("interval-profitability", "style"),
    Output("market-profitability", "children"),
    Output("mean-profitability", "children"),
    Output("daily-profitability", "children"),
    Output("weekly-profitability", "children"),
    Output("yearly-profitability", "children"),
    Output("strategies", "n_clicks"),
    Input("start-day", "date"),
    Input("end-day", "date"),
    Input("start-time", "value"),
    Input("end-time", "value"),
    Input("symbols", "value"),
    Input("ss_delta", "value"),
    Input("ss_alpha", "value"),
    Input("ma_alpha", "value"),
    Input("a-coin-value-input", "value"),
    Input("b-coin-value-input", "value"),
    Input("dummy-strategy-btn", "n_clicks_timestamp"),
    Input("simple-strategy-btn", "n_clicks_timestamp"),
    Input("ma-strategy-btn", "n_clicks_timestamp"),
    Input("big-ma-selector", "value"),
    Input("small-ma-selector", "value"),
)
def get_analytics_candle_plot(
    start_day,
    end_day,
    start_time,
    end_time,
    symbol,
    ss_delta,
    ss_alpha,
    ma_alpha,
    a_coin_input,
    b_coin_input,
    dummy_strategy_btn_timestamp,
    simple_strategy_btn_timestamp,
    ma_strategy_btn_timestamp,
    big_ma_selector,
    small_ma_selector,
):

    start_day = datetime.strptime(start_day, "%Y-%m-%d")
    end_day = datetime.strptime(end_day, "%Y-%m-%d")
    start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S").time()
    end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S").time()

    start_datetime = datetime.combine(start_day, start_time)
    # TODO: compute pre_start_datetime properly
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

    big_ma_name = "avg_" + str(big_ma_selector)
    small_ma_name = "avg_" + str(small_ma_selector)

    df[big_ma_name] = df["close"].rolling(big_ma_selector).mean()
    df[small_ma_name] = df["close"].rolling(small_ma_selector).mean()
    df["big_ma"] = df[big_ma_name]
    df["small_ma"] = df[small_ma_name]
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

    start_wallet_total = start_wallet.get_value_usdt(time=df["ds"].iloc[0])

    if dummy_strategy_btn_timestamp is None:
        dummy_strategy_btn_timestamp = 1
    if simple_strategy_btn_timestamp is None:
        simple_strategy_btn_timestamp = 0
    if ma_strategy_btn_timestamp is None:
        ma_strategy_btn_timestamp = 0

    # by default, use dummy strategy
    strategies_btn_ts = {
        "dummy": dummy_strategy_btn_timestamp,
        "simple": simple_strategy_btn_timestamp,
        "ma": ma_strategy_btn_timestamp,
    }

    strategies_btn_ts_sorted = {
        k: v for k, v in sorted(strategies_btn_ts.items(), key=lambda item: item[1])
    }

    selected_strategy = list(strategies_btn_ts_sorted.keys())[-1]

    dummy_strategy_style = {}
    simple_strategy_style = {}
    ma_strategy_style = {}
    if "dummy" in selected_strategy:
        strategy = DummyStrategy(df=df, start_wallet=start_wallet)
        dummy_strategy_style = {"border-color": "red"}
    elif "simple" in selected_strategy:
        strategy = SimpleStrategy(df=df, start_wallet=start_wallet, alpha=ss_alpha, delta=ss_delta)
        simple_strategy_style = {"border-color": "red"}
    elif "ma" in selected_strategy:
        strategy = MovingAverageStrategy(
            df=df,
            start_wallet=start_wallet,
            alpha=ma_alpha,
            big_ma_window=big_ma_selector,
            small_ma_window=small_ma_selector,
            compute_ma=False,
        )
        ma_strategy_style = {"border-color": "red"}
    else:
        strategy = DummyStrategy(df=df, start_wallet=start_wallet)
        dummy_strategy_style = {"border-color": "red"}

    dummy_strategy = DummyStrategy(df=df, start_wallet=start_wallet)
    end_wallet = strategy.end_wallet
    end_wallet_total = end_wallet.get_value_usdt(time=df["ds"].iloc[-1])

    n_operations = strategy.get_n_operations()
    n_good_operations = strategy.get_n_good_operations()
    n_bad_operations = strategy.get_n_bad_operations()
    n_operations_by_hour = strategy.get_n_operations_by_hour()
    mean_operation_time = strategy.get_mean_operation_time()
    profitabilities = strategy.get_profitabilities()
    interval_profitability = profitabilities["interval"]
    if interval_profitability > 0:
        interval_profitability_style = {"color": "green"}
    else:
        interval_profitability_style = {"color": "red"}
    market_profitability = dummy_strategy.get_profitabilities()["interval"]
    mean_profitability = profitabilities["mean"]
    daily_profitability = profitabilities["day"]
    weekly_profitability = profitabilities["week"]
    yearly_profitability = profitabilities["year"]

    fig = render_analytics_plot(
        df=strategy.df,
        symbol=strategy.start_wallet.symbol,
        avgs={big_ma_name: LIGHT_GREEN, small_ma_name: ORANGE},
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
        ma_strategy_style,
        n_operations,
        n_good_operations,
        n_bad_operations,
        n_operations_by_hour,
        mean_operation_time,
        format_percentage(interval_profitability),
        interval_profitability_style,
        format_percentage(market_profitability),
        format_percentage(mean_profitability),
        format_percentage(daily_profitability),
        format_percentage(weekly_profitability),
        format_percentage(yearly_profitability),
        42,
    )


@app.callback(
    Output("big-ma", "children"),
    Output("small-ma", "children"),
    Input("big-ma-selector", "value"),
    Input("small-ma-selector", "value"),
)
def get_ma_params(big_ma_value, small_ma_value):
    return big_ma_value, small_ma_value
