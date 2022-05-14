from views.layout import make_layout
from maindash import app

app.layout = make_layout()
app.run_server(debug=True, port=8050)
server = app.server
