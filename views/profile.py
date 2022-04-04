from dash import html, dcc, dash_table
import plotly.express as px
from trading_tool.binance import get_portfolio
from trading_tool.client import TEST_CLIENT
from views.style import colors, GRAY5


def make_profile_description():

    # get current portfolio in usdt
    df = get_portfolio(TEST_CLIENT)

    # create pie chart with plotly
    fig = px.pie(
        df,
        values="price_usdt",
        names="asset",
        hole=0.3,
        color_discrete_sequence=px.colors.sequential.RdBu,
    )
    fig.update_traces(textposition="inside", textinfo="value+label")
    fig.update_layout(showlegend=False)
    fig.update_layout(
        {
            "plot_bgcolor": colors["background"],
            "paper_bgcolor": GRAY5,
            "font": {"color": colors["text"]},
        }
    )

    profile_container = html.Div(
        [
            html.Div(
                [
                    # bar chart
                    dcc.Graph(
                        id="pie-chart",
                        responsive=True,
                        className="pie-chart",
                        figure=fig,
                    )
                ],
                className="pie-chart-container",
            ),
            html.Div(
                [
                    dash_table.DataTable(
                        df.to_dict("records"),
                        [{"name": i, "id": i} for i in df.columns],
                        style_cell=dict(textAlign="left"),
                        style_header=dict(backgroundColor="#12181b"),
                        style_data=dict(backgroundColor="#2a2e35"),
                    )
                ],
                className="table-info-container",
            ),
        ],
        className="profile-container",
    )

    return profile_container
