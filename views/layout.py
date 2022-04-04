from dash import html, dcc
from trading_tool.db import create_connection
from views.header import make_header
from views.main_container import make_main_container, make_main_container2
from views.profile import make_profile_description
from views.footer import make_footer


conn = create_connection("trading_tool.db")


def make_layout():

    overview_tab = dcc.Tab(
        label="Overview",
        value="overview-tab",
        className="my-tab",
        selected_className="my-tab-selected",
        children=[make_profile_description()],
    )

    backtesting_tab = dcc.Tab(
        label="Backtesting",
        value="backtesting-tab",
        className="my-tab",
        selected_className="my-tab-selected",
        children=[make_main_container(), make_main_container2()],
    )

    # body
    layout = html.Div(
        [
            # header
            make_header(),
            # horizontal line
            html.Hr(),
            # tabs
            dcc.Tabs(
                value="overview-tab",
                className="my-tab-container",
                children=[overview_tab, backtesting_tab],
            ),
            # footer
            make_footer(),
        ],
        id="layout",
    )

    return layout
