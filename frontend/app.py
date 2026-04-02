import dash
from dash import Dash, html, dcc, Output, Input
import dash_bootstrap_components as dbc
from flask import Flask, redirect, url_for
import os

from frontend.components.navbar import create_navbar

# Create the server for deployment
server = Flask(__name__)

# Initialize the Dash app
app = Dash(
    "project_management_frontend",
    server=server,
    use_pages=True,
    pages_folder=os.path.join(os.path.dirname(__file__), "pages"),
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    prevent_initial_callbacks='initial_duplicate',
)

import logging
import sys
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"DEBUG: sys.path: {sys.path}")
logger.info(f"DEBUG: __name__: {__name__}")

@server.route('/')
def index():
    return redirect('/dashboard')

# Fix duplicate paths error by removing entries without layouts or duplicates
import dash
logger.info("--- Dash Page Registry Before Cleanup ---")
for key, val in dash.page_registry.items():
    logger.info(f"Key: {key}, Path: {val['relative_path']}, Has Layout: {'layout' in val or 'layout_builder' in val}")

# If we have duplicates for the same path, keep the one with a layout
# If we have entries from different module paths for the same logical page, keep the one that works
path_to_keys = {}
for key, val in dash.page_registry.items():
    path = val['relative_path']
    if path not in path_to_keys:
        path_to_keys[path] = []
    path_to_keys[path].append(key)

for path, keys in path_to_keys.items():
    if len(keys) > 1:
        # Multiple keys for same path. Find one with layout.
        with_layout = [k for k in keys if 'layout' in dash.page_registry[k] or 'layout_builder' in dash.page_registry[k]]
        if with_layout:
            to_keep = with_layout[0]
            for k in keys:
                if k != to_keep:
                    logger.info(f"Removing duplicate for {path}: {k} (kept {to_keep})")
                    dash.page_registry.pop(k)
        else:
            # None have layout? Keep the first one and hope for the best, or keep all to see error
            logger.warning(f"Multiple entries for {path} but NONE have layout: {keys}")

logger.info("--- Dash Page Registry After Cleanup ---")
for key, val in dash.page_registry.items():
    logger.info(f"Key: {key}, Path: {val['relative_path']}, Has Layout: {'layout' in val or 'layout_builder' in val}")

# Main layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=True), # Changed refresh to True to help with clear state
    dcc.Store(id='session-store', storage_type='session'),
    html.Div(id='navbar-container'),
    dbc.Container(
        dash.page_container,
        className="mt-4",
        fluid=True
    )
])

# Logout callback
@app.callback(
    Output('session-store', 'data', allow_duplicate=True),
    Output('url', 'pathname', allow_duplicate=True),
    Input('url', 'pathname'),
    prevent_initial_call=True
)
def logout(pathname):
    if pathname == '/logout':
        logger.info("Logging out user")
        return {}, '/login'
    return dash.no_update, dash.no_update

# Callback to manage the navbar and redirection
@app.callback(
    Output('navbar-container', 'children'),
    Output('url', 'pathname'),
    Input('url', 'pathname'),
    Input('session-store', 'data')
)
def manage_auth_and_navbar(pathname, session_data):
    # Determine user email if authenticated
    user_email = session_data.get('user_email') if session_data and 'access_token' in session_data else None

    # Handle unauthenticated users
    if not user_email:
        if pathname not in ['/login', '/register']:
            return None, '/login'
        return create_navbar(None), pathname

    # Handle authenticated users redirecting from login/register or root
    if pathname in ['/login', '/register', '/']:
        return create_navbar(user_email), '/dashboard'

    # Return navbar for all other pages
    return create_navbar(user_email), pathname

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
