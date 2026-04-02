import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import dash
from dash import Dash, html, dcc, Output, Input
import dash_bootstrap_components as dbc
from flask import Flask

from frontend.components.navbar import create_navbar

# Create the server for deployment
server = Flask(__name__)

# Initialize the Dash app
app = Dash(
    __name__,
    server=server,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    prevent_initial_callbacks='initial_duplicate',
)

# Main layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='session-store', storage_type='session'),
    html.Div(id='navbar-container'),
    dbc.Container(
        dash.page_container,
        className="mt-4",
        fluid=True
    )
])

# Callback to manage the navbar and redirection
@app.callback(
    Output('navbar-container', 'children'),
    Output('url', 'pathname'),
    Input('url', 'pathname'),
    Input('session-store', 'data')
)
def manage_auth_and_navbar(pathname, session_data):
    # Check if the user is authenticated (token exists in session storage)
    is_authenticated = session_data and 'token' in session_data
    
    # Define public pages that don't require authentication
    public_pages = ['/login', '/register']
    
    # Redirect logic: if not authenticated and not on a public page, go to login
    if not is_authenticated and pathname not in public_pages:
        return create_navbar(is_authenticated), '/login'
    
    # If authenticated and trying to go to login/register, go to dashboard
    if is_authenticated and pathname in public_pages:
        return create_navbar(is_authenticated), '/'
    
    # Otherwise, return the navbar and the current pathname
    return create_navbar(is_authenticated), dash.no_update

# Callback to handle logout
@app.callback(
    Output('session-store', 'data'),
    Input('logout-link', 'n_clicks'),
    prevent_initial_call=True
)
def logout(n_clicks):
    if n_clicks:
        return {}
    return dash.no_update

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8050)
