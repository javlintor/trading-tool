from dash import html, dcc, dash_table
import plotly.express as px
from trading_tool.binance import get_portfolio
from trading_tool.client import TEST_CLIENT
from views.style import colors, table_colors, GRAY5


def make_profile_description(client):

    # get current portfolio in usdt
    df = get_portfolio(client)

    # create pie chart with plotly
    fig = px.pie(
        df,
        values="price_usdt",
        names="asset",
        hole=0.3,
        color_discrete_sequence=px.colors.sequential.RdBu,
    )
    fig.update_traces(textinfo="value+label")
    fig.update_layout(showlegend=False)
    fig.update_layout(
        {
            "plot_bgcolor": colors["background"],
            "paper_bgcolor": GRAY5,
            "font": {"color": colors["text"]},
        }
    )

    # this should be done inside dash_table.DataTable
    df["price_usdt"] = df["price_usdt"].apply(lambda x: "$ " + str(x))

    pie_chart = dcc.Graph(
        id="portfolio-pie-chart",
        responsive=True,
        figure=fig,
    )

    portfolio_table = dash_table.DataTable(
        id="portfolio-table",
        data=df.to_dict("records"),
        columns=[{"name": i.upper(), "id": i} for i in df.columns],
        style_cell=dict(textAlign="left", width="70px"),
        style_header=dict(
            backgroundColor=table_colors["header"],
            fontWeight="bold",
            fontSize=20,
            border="1px solid white",
        ),
        style_data=dict(backgroundColor=table_colors["background"]),
        style_as_list_view=True,
    )

    profile = html.Div(
        className="flex-container cool-container margins",
        children=[pie_chart, portfolio_table],
    )

    return profile
