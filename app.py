import dash
import dash_auth
from dash import html, dcc, Input, Output, ctx, State
import logging
from src.scripts import create_fy_options, get_marks
import json

from config import settings

LOGGING_LEVEL = settings["LOGGING_LEVEL"]
logging.basicConfig(level=LOGGING_LEVEL)

FY_OPTIONS = create_fy_options()

app = dash.Dash(
    __name__,
    use_pages=True,
    prevent_initial_callbacks="initial_duplicate",
    suppress_callback_exceptions=True,
    title="UTRC Dashboard",
)

with open("./assets/data/accounts.txt") as f:
    data = f.read()
    ACCOUNTS = json.loads(data)
dash_auth.BasicAuth(app, ACCOUNTS)

users_filter = dcc.Dropdown(
    id="dropdown",
    options=[
        {
            "label": "Active Users",
            "value": "utrc_individual_user_hpc_usage",
        },
        {"label": "New Users", "value": "utrc_new_users"},
        {"label": "Idle Users", "value": "utrc_idle_users"},
        {
            "label": "Suspended Users",
            "value": "utrc_suspended_users",
        },
    ],
    value="utrc_individual_user_hpc_usage",
    clearable=False,
)

usage_filter = dcc.Dropdown(
    id="dropdown",
    options=[
        {"label": "Active Allocations", "value": "utrc_active_allocations"},
        {"label": "Corral Usage", "value": "utrc_corral_usage"},
    ],
    value="utrc_active_allocations",
    clearable=False,
)

allocations_filter = dcc.Dropdown(
    id="dropdown",
    options=[
        {"label": "Active Allocations", "value": "utrc_active_allocations"},
        {"label": "Current Allocations", "value": "utrc_current_allocations"},
        {"label": "New Allocations", "value": "utrc_new_allocation_requests"},
    ],
    value="utrc_active_allocations",
    clearable=False,
)

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        html.Header(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            html.A(
                                html.Img(
                                    src="assets/images/utrc-horizontal-logo-white-simple.svg",
                                    className="portal-logo",
                                ),
                                href="https://utrc.tacc.utexas.edu/",
                                className="navbar-brand",
                            ),
                        ),
                        html.Div(
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
                                className="collapse navbar-collapse",
                            ),
                        ),
                    ],
                    className="s-header navbar navbar-dark navbar-expand-md",
                ),
            ],
        ),
        html.Div(
            [
                html.Div(id="main-title"),
                # html.Hr(),
                html.Button(
                    html.H3(
                        "Filters",
                        style={
                            "font-size": "18px",
                            "margin-top": "10px",
                            "margin-bottom": "10px",
                            "font-family": "inherit",
                            "font-weight": "500",
                            "line-height": "1.1",
                            "color": "inherit",
                        },
                    ),
                    id="toggle-filters",
                    n_clicks=0,
                    style={
                        "margin-bottom": "-10px",
                        "background-color": "#ffffff",
                        "color": "black",
                        "box-shadow": "0px",
                        "text-align": "left",
                        "border-top": "0px",
                        "border-left": "0px",
                        "border-right": "0px",
                        "border-bottom": "var(--global-border-width--thick) solid var(--global-color-tertiary--normal)",
                    },
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                "By institution:",
                                html.Div(
                                    [
                                        dcc.Dropdown(
                                            [
                                                # "All",
                                                "UTAus",
                                                "UTA",
                                                "UTD",
                                                "UTEP",
                                                "UTPB",
                                                "UTRGV",
                                                "UTSA",
                                                "UTT",
                                                "UTHSC-H",
                                                "UTHSC-SA",
                                                "UTMB",
                                                "UTMDA",
                                                "UTSW",
                                                "UTSYS",
                                            ],
                                            ["UTAus"],
                                            multi=True,
                                            id="select_institutions_dd",
                                        ),
                                    ],
                                    # className="single_line_checklist",
                                ),
                            ],
                            id="select_institutions_div",
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                "By machine:",
                                html.Div(
                                    [
                                        dcc.Checklist(
                                            id="all-or-none-machine",
                                            options=[
                                                {"label": "Select All", "value": "All"}
                                            ],
                                            value=["All"],
                                            className="select-all",
                                        ),
                                        dcc.Checklist(
                                            id="select_machine_checklist",
                                            options=[
                                                {
                                                    "label": "Lonestar6",
                                                    "value": "Lonestar6",
                                                },
                                                {
                                                    "label": "Frontera",
                                                    "value": "Frontera",
                                                },
                                                {
                                                    "label": "Longhorn3",
                                                    "value": "Longhorn3",
                                                },
                                                {
                                                    "label": "Stampede4",
                                                    "value": "Stampede4",
                                                },
                                                {
                                                    "label": "Lonestar5",
                                                    "value": "Lonestar5",
                                                },
                                                {
                                                    "label": "Maverick3",
                                                    "value": "Maverick3",
                                                },
                                                {
                                                    "label": "Jetstream",
                                                    "value": "Jetstream",
                                                },
                                                {"label": "Hikari", "value": "Hikari"},
                                            ],
                                            value=[
                                                "Lonestar6",
                                                "Frontera",
                                                "Longhorn3",
                                                "Stampede4",
                                                "Lonestar5",
                                                "Maverick3",
                                                "Jetstream",
                                                "Hikari",
                                            ],
                                            persistence=True,
                                            persistence_type="session",
                                        ),
                                    ],
                                    className="single_line_checklist",
                                ),
                            ],
                            id="select_machine_div",
                            className="filter_div",
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                "By fiscal year:",
                                dcc.RadioItems(
                                    id="year_radio_dcc",
                                    options=FY_OPTIONS,
                                    value="21-22",
                                    inline=True,
                                    persistence=True,
                                    persistence_type="session",
                                ),
                            ],
                            id="year_radio_box",
                            className="filter_div",
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                "By month:",
                                dcc.RangeSlider(
                                    id="date_filter",
                                    value=[0, 12],
                                    step=None,
                                    marks={
                                        0: "21-09",
                                        1: "21-10",
                                        2: "21-11",
                                        3: "21-12",
                                        4: "22-01",
                                        5: "22-02",
                                        6: "22-03",
                                        7: "22-04",
                                        8: "22-05",
                                        9: "22-06",
                                        10: "22-07",
                                        11: "22-08",
                                    },
                                    min=0,
                                    max=11,
                                    persistence=True,
                                    persistence_type="session",
                                ),
                            ],
                            id="date_range_selector",
                            className="filter_div",
                        ),
                        html.Hr(),
                        html.Div(id="page-filter"),
                    ],
                    id="filters",
                    style={"display": "", "border": "0px", "margin-top": "0px"},
                    className="c-island",
                ),
                dash.page_container,
            ],
            className="body",
        ),
    ]
)

for page in dash.page_registry.values():
    logging.debug((f"{page['name']} - {page['path']}"))


@app.callback(
    Output("main-title", "children"),
    Output("page-filter", "children"),
    [Input("url", "pathname")],
)
def render_page_specific(pathname):
    if pathname == "/":
        return html.H1("Users", className="page-title"), users_filter
    elif pathname == "/usage":
        return html.H1("Usage", className="page-title"), usage_filter
    elif pathname == "/allocations":
        return html.H1("Allocations", className="page-title"), allocations_filter


@app.callback(
    Output("filters", "style"),
    Input("toggle-filters", "n_clicks"),
    State("filters", "style"),
    prevent_initial_call=True,
)
def toggle_filters(click, state):
    if state == {"display": "none"}:
        return {"display": "", "border": "0px", "margin-top": "0px"}
    else:
        return {"display": "none"}


# @app.callback(
#     Output("select_institutions_dd", "value"),
#     [State("select_institutions_dd", "options")],
#     prevent_initial_call=True,
# )
# def select_all_none(all_selected, options):
#     all_or_none = []
#     all_or_none = [option["value"] for option in options if all_selected == "All"]
#     return all_or_none


@app.callback(
    Output("select_machine_checklist", "value"),
    [Input("all-or-none-machine", "value")],
    [State("select_machine_checklist", "options")],
    prevent_initial_call=True,
)
def select_all_none(all_selected, options):
    all_or_none = []
    all_or_none = [option["value"] for option in options if all_selected]
    return all_or_none


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=settings["DEBUG_MODE"])
