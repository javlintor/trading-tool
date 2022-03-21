from dash import html, dcc
import dash_daq as daq
import dash_mantine_components as dmc
from trading_tool.binance import get_symbols
from datetime import datetime, date, timedelta
from trading_tool.client import CLIENT

def make_main_container():

    min_date_allowed = date(2015, 1, 1)
    max_date_allowed = date(2025, 1, 1)
    initial_visible_month = date(2022, 2, 1)
    symbols = get_symbols(CLIENT)

    main_container = html.Div([
        # candle_plot-container
        html.Div([
            dcc.Graph(
                id='candle_1d',
                responsive=True, 
                className="candle_plot"
            ),
        ], 
        className="candle_plot-container"
        ), 

        # options1-container
        html.Div([
            # symbols container
            html.Div([
                html.Label(
                    "Select a symbol:", 
                    form="symbols"
                ),
                dcc.Dropdown(
                    value="BTCUSDT",
                    options=symbols,
                    id='symbols'
                ), 
            ], 
            className="symbols-container"
            ),

            # date_range
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
            className="flex-container-col"
            ), 

            # time range
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
    )

    return main_container


def make_main_container2():

    main_container2 = html.Div([
        # options2-container
        html.Div([

            # delta 
            html.Div([
                html.Label(
                    "Choose delta parameter:", 
                    form="delta"
                ),
                dcc.Slider(0, 0.03, value=0.01, step=0.002, id="delta") 
            ]),

            # alpha
            html.Div([
                html.Label(
                    "Choose alpha parameter:", 
                    form="day_picked"
                ),
                dcc.Slider(0, 0.2, value=0.08, step=0.01, id="alpha")    
            ]),

            # wallet + switch
            html.Div([
                # wallet
                html.Div([
                    html.Label(
                        "Start wallet:", 
                    ),
                    html.Div([
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
                className="flex-container-col"
                ), 

                # switch 
                html.Div([
                    html.P("Switch trader"),
                    daq.ToggleSwitch(
                        id='reverse',
                        value=False
                    ),
                ], 
                className="flex-container-col"
                )   
            ],
            className="flex-container"
            )
        ],
        className="options2-container"
        ), 

        # candle_1m
        html.Div([
            dcc.Graph(
                id='candle_1m',
                responsive=True, 
                className="candle_1m"
            ),
        ], 
        className="candle_1m-container"
        ),

        # result1-container
        html.Div([
            html.Div(
                [
                    html.P("Start Wallet", className="title-wallet"), 
                    html.P("A Coin", id="start-wallet-1-title"), 
                    html.P("B Coin", id="start-wallet-2-title"),
                    html.P(id="start-wallet-1", className="big-numbers"), 
                    html.P(id="start-wallet-2", className="big-numbers"),
                    html.P("Total (USD) ", className="total-text"),
                    html.P(id="start-wallet-total", className="big-numbers")
                ], 
                className="wallet")
        ], 
        className="result1-container"
        ),

        # result2-container
        html.Div([
            html.Div([
                    html.P("End Wallet", className="title-wallet"), 
                    html.P("A Coin", id="end-wallet-1-title"), 
                    html.P("B Coin", id="end-wallet-2-title"),
                    html.P(id="end-wallet-1", className="big-numbers"), 
                    html.P(id="end-wallet-2", className="big-numbers"), 
                    html.P("Total (USD) ", className="total-text"),
                    html.P(id="end-wallet-total", className="big-numbers")
                ], 
                className="wallet"
                )
        ], 
        className="result2-container"
        )
    ], 
    className="main-container-2"
    ), 

    return main_container2