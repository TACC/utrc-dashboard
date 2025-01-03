import dash

from dash import html, dcc, Input, Output, ctx, State, no_update
import logging
from src.data_functions import create_fy_options, get_marks
import json
import os
from dotenv import load_dotenv
from flask import Flask
from flask_login import login_user, LoginManager, UserMixin, current_user

from config import settings

load_dotenv()
LOGGING_LEVEL = settings["LOGGING_LEVEL"]
logging.basicConfig(level=LOGGING_LEVEL)

FY_OPTIONS = create_fy_options()

server = Flask(__name__)
app = dash.Dash(
    __name__,
    server=server,
    use_pages=True,
    prevent_initial_callbacks="initial_duplicate",
    suppress_callback_exceptions=True,
    title="UTRC Dashboard",
)


with open("./assets/data/accounts.txt") as f:
    data = f.read()
    ACCOUNTS = json.loads(data)

server.config.update(SECRET_KEY=os.getenv("SECRET_KEY"))
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/login"


class User(UserMixin):
    def __init__(self, username):
        self.id = username


@login_manager.user_loader
def load_user(username):
    return User(username)


app.layout = html.Div(
    [
        dcc.Location(id="url"),
        html.Header(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            [
                                html.A(
                                    html.Img(
                                        src="assets/images/utrc-horizontal-logo-white-simple.svg",
                                        className="portal-logo",
                                    ),
                                    href="https://utrc.tacc.utexas.edu/",
                                    className="navbar-brand",
                                ),
                                html.Div(
                                    [
                                        html.Button(
                                            [
                                                html.Span(
                                                    className="navbar-toggler-icon"
                                                )
                                            ],
                                            # className="navbar-toggler collapsed",
                                            className="hamburger-icon",
                                            id="hamburger-icon",
                                        ),
                                    ]
                                ),
                            ],
                            className="navbar-logo-section",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    html.Ul(
                                        children=[
                                            html.Li(
                                                html.A(
                                                    "Users",
                                                    href="/",
                                                    className="nav-link",
                                                ),
                                                className="nav-item",
                                            ),
                                            html.Li(
                                                html.A(
                                                    "Allocations",
                                                    href="/allocations",
                                                    className="nav-link",
                                                ),
                                                className="nav-item",
                                            ),
                                            html.Li(
                                                html.A(
                                                    "Usage",
                                                    href="/usage",
                                                    className="nav-link",
                                                ),
                                                className="nav-item",
                                            ),
                                        ],
                                        className="s-cms-nav navbar-nav mr-auto",
                                    ),
                                    # className="navbar-collapse collapse menu-links",
                                    className="menu-links",
                                    id="navbar-links",
                                ),
                                html.Div(
                                    [
                                        html.Div(id="auth-link"),
                                    ],
                                    className="auth-nav nav-item login-menu",
                                    id="auth-nav",
                                ),
                            ],
                            className="toggle-menu",
                        ),
                    ],
                    className="s-header navbar navbar-dark navbar-expand-md flex-nav",
                    id="navbar-content",
                ),
            ],
        ),
        html.Div(
            [
                dash.page_container,
            ],
            className="body",
        ),
    ]
)

for page in dash.page_registry.values():
    logging.debug((f"{page['name']} - {page['path']}"))


@app.callback(
    Output("navbar-content", "className"),
    Input("hamburger-icon", "n_clicks"),
)
def toggle_menu(n_clicks):
    if n_clicks % 2 == 0:
        # hide
        return "s-header navbar navbar-dark navbar-expand-md flex-nav"
    else:
        # show
        return "s-header navbar navbar-dark navbar-expand-md flex-nav show-nav"


@app.callback(
    Output("auth-link", "children"),
    Input("url", "pathname"),
)
def update_authentication_status(_):
    if current_user.is_authenticated:
        return html.A(
            [
                html.I(
                    id="auth-icon",
                    className="bi bi-person-circle",
                ),
                "Log out",
            ],
            href="/logout",
            className="nav-link",
        )
    return html.A(
        [
            html.I(
                id="auth-icon",
                className="bi bi-person-circle",
            ),
            "Log in",
        ],
        href="/login",
        className="nav-link",
    )


@app.callback(
    Output("filters", "style"),
    Output("chevron-icon", "className"),
    Input("toggle-filters", "n_clicks"),
    State("filters", "style"),
    prevent_initial_call=True,
)
def toggle_filters(click, state):
    if state == {"display": "none"}:
        return {
            "display": "",
        }, "bi bi-chevron-down chevron"
    else:
        return {"display": "none"}, "bi bi-chevron-up chevron"


@app.callback(
    Output("select_institutions_dd", "value"),
    Input("select_institutions_dd", "value"),
    [State("select_institutions_dd", "options")],
)
def select_all_none_inst(selected, possible):
    opts = []
    if "All" in selected:
        opts = possible
    else:
        opts = selected
    return opts


@app.callback(
    Output("select_machine_dd", "value"),
    Input("select_machine_dd", "value"),
    [State("select_machine_dd", "options")],
)
def select_all_none_machine(selected, possible):
    opts = []
    if "All" in selected:
        opts = possible
    else:
        opts = selected
    return opts


@app.callback(
    Output("start_date_dd", "value"),
    Output("end_date_dd", "value"),
    Input("fy_dd", "value"),
)
def update_dates(fy):
    if fy:
        marks = get_marks(fy)
        marks_list = [x for x in marks.values()]
        return marks_list[0], marks_list[-1]
    else:
        return no_update


@app.callback(
    Output("date_range_selector", "children"),
    Input("date_filter", "value"),
    Input("year_radio_dcc", "value"),
)
def update_date_range(date_range, fiscal_year):
    logging.debug(f"Callback trigger id: {ctx.triggered_id}")
    marks = get_marks(fiscal_year)
    if ctx.triggered_id == "year_radio_dcc":
        logging.debug(f"Marks = {marks}")
        slider_children = [
            "By month:",
            dcc.RangeSlider(
                id="date_filter",
                value=[0, len(marks)],
                step=None,
                marks=marks,
                min=0,
                max=len(marks) - 1,
            ),
        ]
    else:
        logging.debug(f"Marks = {marks}")
        logging.debug(f"date_range = {date_range}")
        slider_children = [
            "By month:",
            dcc.RangeSlider(
                id="date_filter",
                value=date_range,
                step=None,
                marks=marks,
                min=0,
                max=len(marks) - 1,
            ),
        ]
    return slider_children


@app.callback(
    Output("url", "href"),
    Output("output-state", "children"),
    Input("login-button", "n_clicks"),
    State("uname-box", "value"),
    State("pwd-box", "value"),
    prevent_initial_call=True,
)
def auth_button_click(n_clicks_login, username, password):
    if n_clicks_login > 0:
        if username not in ACCOUNTS:
            return no_update, html.P("Invalid username", className="login-error")
        if ACCOUNTS[username] == password:
            login_user(User(username))
            return "/", ""
        return no_update, html.P("Incorrect password", className="login-error")
    else:
        return no_update, no_update


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=settings["DEBUG_MODE"])
