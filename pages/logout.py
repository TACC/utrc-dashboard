"""
Code from this example: https://github.com/AnnMarieW/dash-flask-login
TODO: replace/modify
"""

import dash
from dash import html, dcc
from flask_login import logout_user, current_user

dash.register_page(__name__)


def layout():
    if current_user.is_authenticated:
        logout_user()
    return html.Div(
        [
            html.Div(
                html.H2(
                    "You have been logged out - Please login", className="auth-title"
                )
            ),
            html.Br(),
            dcc.Link("Home", href="/"),
        ]
    )
