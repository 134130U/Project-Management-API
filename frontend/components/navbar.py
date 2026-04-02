import dash_bootstrap_components as dbc
from dash import html

def create_navbar(is_authenticated=False):
    nav_links = [
        dbc.NavItem(dbc.NavLink("Dashboard", href="/")),
        dbc.NavItem(dbc.NavLink("Projects", href="/projects")),
        dbc.NavItem(dbc.NavLink("Teams", href="/teams")),
        dbc.NavItem(dbc.NavLink("Budgets", href="/budgets")),
    ]
    
    if is_authenticated:
        nav_links.append(dbc.NavItem(dbc.NavLink("Logout", id="logout-link", href="/login")))
    else:
        nav_links.extend([
            dbc.NavItem(dbc.NavLink("Login", href="/login")),
            dbc.NavItem(dbc.NavLink("Register", href="/register")),
        ])

    return dbc.NavbarSimple(
        brand="Project Management System",
        brand_href="/",
        color="primary",
        dark=True,
        children=nav_links
    )
