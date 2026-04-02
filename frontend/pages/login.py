import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from frontend.services.auth import AuthService

dash.register_page(__name__, path='/login')

layout = dbc.Row(
    dbc.Col([
        html.H2("Login", className="text-center mb-4"),
        dbc.Form([
            html.Div([
                dbc.Label("Email"),
                dbc.Input(type="email", id="login-email", placeholder="Enter email"),
            ], className="mb-3"),
            html.Div([
                dbc.Label("Password"),
                dbc.Input(type="password", id="login-password", placeholder="Enter password"),
            ], className="mb-3"),
            dbc.Button("Login", id="login-button", color="primary", className="w-100"),
        ]),
        html.Div(id="login-output", className="mt-3"),
        html.Div([
            "Don't have an account? ",
            dcc.Link("Register here", href="/register")
        ], className="text-center mt-3")
    ], width={"size": 4, "offset": 4}),
    className="mt-5"
)

@callback(
    Output("login-output", "children"),
    Output("session-store", "data", allow_duplicate=True),
    Input("login-button", "n_clicks"),
    State("login-email", "value"),
    State("login-password", "value"),
    prevent_initial_call='initial_duplicate'
)
def login_user(n_clicks, email, password):
    if not email or not password:
        return dbc.Alert("Please fill in all fields", color="danger"), dash.no_update
    
    email = email.strip().lower()
    response = AuthService.login(email, password)
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        return dbc.Alert("Login successful!", color="success"), {"token": token}
    else:
        try:
            error_msg = response.json().get("detail", "Login failed")
        except:
            error_msg = "Login failed"
        return dbc.Alert(f"Error: {error_msg}", color="danger"), dash.no_update
