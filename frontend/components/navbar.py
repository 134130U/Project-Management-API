import dash_bootstrap_components as dbc
from dash import html

def create_navbar(user_email=None):
    is_authenticated = user_email is not None
    nav_links = [
        dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard")),
        dbc.NavItem(dbc.NavLink("Projects", href="/projects")),
        dbc.NavItem(dbc.NavLink("Teams", href="/teams")),
        dbc.NavItem(dbc.NavLink("Budgets", href="/budgets")),
    ]
    
    if is_authenticated:
        nav_links.append(dbc.NavItem(dbc.NavLink(f"Logout ({user_email})", id="logout-link", href="/logout")))
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
