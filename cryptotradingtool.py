# Import the `make_layout` function from the `layout` module
from views.layout import make_layout

# Import the Dash app instance
from maindash import app

# Set the layout of the Dash app to the output of the `make_layout` function
app.layout = make_layout()

# Assign the server object to the `server` variable
server = app.server
