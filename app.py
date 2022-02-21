from misc import *


# Loading keys from config file
config = configparser.ConfigParser()
config.read_file(open('secret.cfg'))
test_api_key = config.get('BINANCE', 'TEST_API_KEY')
test_secret_key = config.get('BINANCE', 'TEST_SECRET_KEY')

# Setting up connection
client = Client(test_api_key, test_secret_key)
client.API_URL = 'https://testnet.binance.vision/api'  # To change endpoint URL for test account

# Getting account info to check balance
info = client.get_account()  # Getting account info

# Saving different tokens and respective quantities into lists
assets = []
values = []
for index in range(len(info['balances'])):
    for key in info['balances'][index]:
        if key == 'asset':
            assets.append(info['balances'][index][key])
        if key == 'free':
            values.append(info['balances'][index][key])


token_usdt = {}  # Dict to hold pair price in USDT
token_pairs = []  # List to hold different token pairs


# Creating token pairs and saving into a list
for token in assets:
    if token != 'USDT':
        token_pairs.append(token + 'USDT')

# Streaming data for tokens in the portfolio
twm = ThreadedWebsocketManager(api_key=test_api_key, api_secret=test_secret_key)
twm.start()
for tokenpair in token_pairs:
    twm.start_symbol_ticker_socket(symbol=tokenpair, callback=streaming_data_process)
time.sleep(5)  # To give sufficient time for all tokenpairs to establish connection


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Graph(
                id='figure-1',
                figure={
                    'data': [
                        go.Indicator(
                            mode="number",
                            value=total_amount_usdt(assets, values, token_usdt),
                        )
                    ],
                    'layout':
                        go.Layout(
                            title="Portfolio Value (USDT)"
                        )
                }
            )], style={'width': '30%', 'height': '300px',
                       'display': 'inline-block'}),
        html.Div([
            dcc.Graph(
                id='figure-2',
                figure={
                    'data': [
                        go.Indicator(
                            mode="number",
                            value=total_amount_btc(assets, values, token_usdt),
                            number={'valueformat': 'g'}
                        )
                    ],
                    'layout':
                        go.Layout(
                            title="Portfolio Value (BTC)"
                        )
                }
            )], style={'width': '30%', 'height': '300px',
                       'display': 'inline-block'}),
        html.Div([
            dcc.Graph(
                id='figure-3',
                figure={
                    'data': [
                        go.Indicator(
                            mode="number",
                            value=float(token_usdt['BNBUSDT']),
                            number={'valueformat': 'g'}
                        )
                    ],
                    'layout':
                        go.Layout(
                            title="BNB/USDT"
                        )
                }
            )],
            style={'width': '30%', 'height': '300px', 'display': 'inline-block'})
    ]),
    html.Div([
        html.Div([
            dcc.Graph(
                id='figure-4',
                figure={
                    'data': [
                        go.Pie(
                            labels=assets,
                            values=assets_usdt(assets, values, token_usdt),
                            hoverinfo="label+percent"
                        )
                    ],
                    'layout':
                        go.Layout(
                            title="Portfolio Distribution (in USDT)"
                        )
                }
            )], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(
                id='figure-5',
                figure={
                    'data': [
                        go.Bar(
                            x=assets,
                            y=values,
                            name="Token Quantities For Different Assets",
                        )
                    ],
                    'layout':
                        go.Layout(
                            showlegend=False,
                            title="Tokens distribution"
                        )
                }
            )], style={'width': '50%', 'display': 'inline-block'}),
        dcc.Interval(
            id='1-second-interval',
            interval=1000,  # 1000 milliseconds
            n_intervals=0
        )
    ]),
])


@app.callback(Output('figure-1', 'figure'),
              Output('figure-2', 'figure'),
              Output('figure-3', 'figure'),
              Output('figure-4', 'figure'),
              Output('figure-5', 'figure'),
              Input('1-second-interval', 'n_intervals'))
def update_layout(n):
    figure1 = {
        'data': [
            go.Indicator(
                mode="number",
                value=total_amount_usdt(assets, values, token_usdt),
            )
        ],
        'layout':
            go.Layout(
                title="Portfolio Value (USDT)"
            )
    }
    figure2 = {
        'data': [
            go.Indicator(
                mode="number",
                value=total_amount_btc(assets, values, token_usdt),
                number={'valueformat': 'g'}
            )
        ],
        'layout':
            go.Layout(
                title="Portfolio Value (BTC)"
            )
    }
    figure3 = {
        'data': [
            go.Indicator(
                mode="number",
                value=float(token_usdt['BNBUSDT']),
                number={'valueformat': 'g'}
            )
        ],
        'layout':
            go.Layout(
                title="BNB/USDT"
            )
    }
    figure4 = {
        'data': [
            go.Pie(
                labels=assets,
                values=assets_usdt(assets, values, token_usdt),
                hoverinfo="label+percent"
            )
        ],
        'layout':
            go.Layout(
                title="Portfolio Distribution (in USDT)"
            )
    }
    figure5 = {
        'data': [
            go.Bar(
                x=assets,
                y=values,
                name="Token Quantities For Different Assets",
            )
        ],
        'layout':
            go.Layout(
                showlegend=False,
                title="Tokens distribution"
            )
    }

    return figure1, figure2, figure3, figure4, figure5


if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port='8050', debug=True)