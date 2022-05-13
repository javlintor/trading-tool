import dash
import dash_auth

from trading_tool.auth import VALID_USERNAME_PASSWORD_PAIRS

app = dash.Dash(__name__)
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)