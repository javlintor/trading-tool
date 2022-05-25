from views.layout import make_layout
from maindash import app

app.layout = make_layout()
server = app.server
