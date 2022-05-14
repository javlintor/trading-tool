from views.layout import make_layout
from maindash import app


app.layout = make_layout()
app.run_server(debug=True)
server = app.server
