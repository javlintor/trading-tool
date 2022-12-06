# Import the `make_layout` function from the `layout` module
from views.layout import make_layout
import trading_tool.configloader as cfg

# Import the Dash app instance
from maindash import app

# Set the layout of the Dash app to the output of the `make_layout` function
app.layout = make_layout()

# Assign the server object to the `server` variable
server = app.server

# Check if the environment is set to local
if cfg.ENV_LOCAL:
    # Start the server on local environment
    server.run()
