from dash import html, dcc, dash_table
import plotly.express as px
from trading_tool.binance import initialize_token_usdt, get_current_porfolio_usdt
from trading_tool.client import TWM, TEST_CLIENT, token_usdt
from views.style import colors, gray5

def make_profile_description():

    # get current portfolio in usdt
    initialize_token_usdt(TWM, TEST_CLIENT)
    df = get_current_porfolio_usdt(TEST_CLIENT)

    # create pie chart with plotly
    fig = px.pie(df, values='value_usdt', names='asset', hole=0.3, color_discrete_sequence=px.colors.sequential.RdBu)
    fig.update_traces(textposition='inside', textinfo='value+label')
    fig.update_layout(showlegend=False)
    fig.update_layout(
        {
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': gray5,
            'font': {
                'color': colors['text']
            }
        }
    )

    profile_container = html.Div([

        html.Div([
            # bar chart
            dcc.Graph(
                id='pie-chart',
                responsive=True, 
                className="pie-chart", 
                figure=fig
            )
        ], 
        className = "pie-chart-container"), 

        html.Div([
            dash_table.DataTable(
                df.to_dict('records'), 
                [{"name": i, "id": i} for i in df.columns], 
                style_cell=dict(textAlign='left'),
                style_header=dict(backgroundColor="#12181b"),
                style_data=dict(backgroundColor="#2a2e35")
            )
        ], 
        className = "table-info-container"
        )
    ],
    className = "profile-container"
    )

    return profile_container
