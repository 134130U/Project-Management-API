import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/teams')

layout = html.Div([
    html.H1("Teams Management"),
    html.P("This page will show all teams and their members.")
])
