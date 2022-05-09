from dash import Dash, html, Input, Output, callback_context

app = Dash(__name__)

app.layout = html.Div([
    html.Button('Button 1', id='btn-nclicks-1', n_clicks=0),
    html.Button('Button 2', id='btn-nclicks-2', n_clicks=0),
    html.Button('Button 3', id='btn-nclicks-3', n_clicks=0),
    html.Div(id='container-button-timestamp')
])

@app.callback(
    Output('container-button-timestamp', 'children'),
    Input('btn-nclicks-1', 'n_clicks'),
    Input('btn-nclicks-2', 'n_clicks'),
    Input('btn-nclicks-3', 'n_clicks')
)
def displayClick(btn1, btn2, btn3):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'btn-nclicks-1' in changed_id:
        msg = 'Button 1 was most recently clicked'
    elif 'btn-nclicks-2' in changed_id:
        msg = 'Button 2 was most recently clicked'
    elif 'btn-nclicks-3' in changed_id:
        msg = 'Button 3 was most recently clicked'
    else:
        msg = 'None of the buttons have been clicked yet'
    return html.Div(msg)

if __name__ == '__main__':
    app.run_server(debug=True)