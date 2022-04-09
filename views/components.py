from datetime import datetime, date, timedelta

from dash import html, dcc
import dash_mantine_components as dmc


def make_vertical_group(element, title_text="", tiny_gap=False, id_title=None, class_title=""):

    class_name = "flex-container-col"

    if tiny_gap:
        class_name = class_name + " tiny-gap"

    title = html.P(className=class_title, children=[title_text])

    if id_title:
        title.id = id_title

    vertical_group = html.Div(className=class_name, children=[title, element])

    return vertical_group


def make_time_range(max_date_allowed, min_date_allowed, initial_visible_month, id_suffix=""):

    start_day = dcc.DatePickerSingle(
        id="start_day" + id_suffix,
        min_date_allowed=min_date_allowed,
        max_date_allowed=max_date_allowed,
        initial_visible_month=initial_visible_month,
        date=date.today(),
    )

    end_day = dcc.DatePickerSingle(
        id="end_day" + id_suffix,
        min_date_allowed=min_date_allowed,
        max_date_allowed=max_date_allowed,
        initial_visible_month=initial_visible_month,
        date=date.today(),
    )

    start_time = dmc.TimeInput(
        # label="Start time:",
        id="start_time" + id_suffix,
        value=datetime.combine(date.today(), datetime.min.time()),
        class_name="Timeinput",
    )

    end_time = dmc.TimeInput(
        # label="End time:",
        id="end_time" + id_suffix,
        value=datetime.now().replace(microsecond=0),
        class_name="Timeinput",
    )

    time_grid = html.Div(
        className="time-range-grid",
        children=[
            make_vertical_group("Start day", start_day, tiny_gap=True),
            make_vertical_group("End day", end_day, tiny_gap=True),
            make_vertical_group("Start time", start_time, tiny_gap=True),
            make_vertical_group("End time", end_time, tiny_gap=True),
        ],
    )

    time_range = make_vertical_group("Select time interval", time_grid)

    return time_range

def make_wallet(wallet_title, id_suffix="", id=None, class_name=None):

    a_coin = make_vertical_group(
        id_title="a-coin-name" + id_suffix,
        element=html.P(id="a-coin-value" + id_suffix, className="big-numbers")
    )
    a_coin.className = "a-coin"
    
    b_coin = make_vertical_group(
        id_title="b-coin-name" + id_suffix,
        element=html.P(id="b-coin-value" + id_suffix, className="big-numbers")
    )
    b_coin.className = "b-coin"
    
    total = make_vertical_group(
        title_text="Total (USDT)", 
        element=html.P(id="total-value" + id_suffix, className="big-numbers")
    )
    total.className = "total"
    
    wallet_grid = html.Div(
        className="wallet-grid", 
        children=[
            a_coin, 
            b_coin, 
            total
        ]
    )

    wallet = make_vertical_group(title_text=wallet_title, element=wallet_grid)

    if id:
        wallet.id = id

    if class_name:
        wallet.className = class_name


    return wallet
