# Import the Dash and Dash Auth libraries
import dash
import dash_auth

# Import the valid username and password pairs from the `auth` module
from trading_tool.auth import VALID_USERNAME_PASSWORD_PAIRS

# Initialize the Dash app and set the app's title
app = dash.Dash(__name__)
app.title = "Trading tool"

# Use the BasicAuth class from the Dash Auth library to set up authentication for the app
# The `VALID_USERNAME_PASSWORD_PAIRS` variable will be used to check user credentials
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)
