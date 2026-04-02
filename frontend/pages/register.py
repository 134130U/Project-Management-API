import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from frontend.services.auth import AuthService

dash.register_page(__name__, path='/register')

layout = dbc.Row(
    dbc.Col([
        html.H2("Register", className="text-center mb-4"),
        dbc.Form([
            html.Div([
                dbc.Label("Email"),
                dbc.Input(type="email", id="register-email", placeholder="Enter email"),
            ], className="mb-3"),
            html.Div([
                dbc.Label("Password"),
                dbc.Input(type="password", id="register-password", placeholder="Enter password"),
            ], className="mb-3"),
            html.Div([
                dbc.Label("Confirm Password"),
                dbc.Input(type="password", id="register-confirm-password", placeholder="Confirm password"),
            ], className="mb-3"),
            dbc.Button("Register", id="register-button", color="success", className="w-100"),
        ]),
        html.Div(id="register-output", className="mt-3"),
        html.Div([
            "Already have an account? ",
            dcc.Link("Login here", href="/login")
        ], className="text-center mt-3")
    ], width={"size": 4, "offset": 4}),
    className="mt-5"
)

@callback(
    Output("register-output", "children"),
    Output("session-store", "data", allow_duplicate=True),
    Input("register-button", "n_clicks"),
    State("register-email", "value"),
    State("register-password", "value"),
    State("register-confirm-password", "value"),
    prevent_initial_call='initial_duplicate'
)
def register_user(n_clicks, email, password, confirm_password):
    if not email or not password or not confirm_password:
        return dbc.Alert("Please fill in all fields", color="danger"), dash.no_update
    
    email = email.strip().lower()
    if password != confirm_password:
        return dbc.Alert("Passwords do not match", color="danger"), dash.no_update
    
    response = AuthService.register(email, password)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        return dbc.Alert("Registration successful!", color="success"), {
            "access_token": token,
            "user_email": email
        }
    else:
        try:
            error_msg = response.json().get("detail", "Registration failed")
        except:
            error_msg = "Registration failed"
        return dbc.Alert(f"Error: {error_msg}", color="danger"), dash.no_update
