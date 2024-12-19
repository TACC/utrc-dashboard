import dash
import dash_auth
from dash import html, dcc, Input, Output, ctx, State, no_update
import logging
from src.scripts import create_fy_options, get_marks, get_all_months
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


def make_date_dd(which):
    dates = get_all_months()
    if which == "start":
        dd = dcc.Dropdown(
            dates,
            dates[0],
            id="start_date_dd",
        )
    elif which == "end":
        dd = dcc.Dropdown(
            dates,
            dates[-1],
            id="end_date_dd",
        )
    return dd


users_filter = html.Div(
    [
        html.Label(
            "Users:",
            htmlFor="dropdown",
            className="filter-label",
        ),
        dcc.Dropdown(
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
        ),
    ],
)

usage_filter = html.Div(
    [
        html.Label(
            "Usage:",
            htmlFor="dropdown",
            className="filter-label",
        ),
        dcc.Dropdown(
            id="dropdown",
            options=[
                {"label": "Active Allocations", "value": "utrc_active_allocations"},
                {"label": "Corral Usage", "value": "utrc_corral_usage"},
            ],
            value="utrc_active_allocations",
            clearable=False,
        ),
    ]
)


allocations_filter = html.Div(
    [
        html.Label(
            "Allocations:",
            htmlFor="dropdown",
            className="filter-label",
        ),
        dcc.Dropdown(
            id="dropdown",
            options=[
                {"label": "Active Allocations", "value": "utrc_active_allocations"},
                {"label": "Current Allocations", "value": "utrc_current_allocations"},
                {"label": "New Allocations", "value": "utrc_new_allocation_requests"},
            ],
            value="utrc_active_allocations",
            clearable=False,
        ),
    ]
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
                html.Button(
                    [
                        html.H3(
                            "Filters",
                            className="toggle-title",
                        ),
                        html.I(
                            id="chevron-icon",
                            className="bi bi-chevron-down chevron",
                        ),
                    ],
                    id="toggle-filters",
                    n_clicks=0,
                    className="toggle-button",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label(
                                    "Institution:",
                                    htmlFor="select_institutions_dd",
                                    className="filter-label",
                                ),
                                html.Div(
                                    [
                                        dcc.Dropdown(
                                            [
                                                "All",
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
                                            ["All"],
                                            multi=True,
                                            id="select_institutions_dd",
                                        ),
                                    ],
                                ),
                            ],
                            id="select_institutions_div",
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.Label(
                                    "Machine:",
                                    htmlFor="select_machine_dd",
                                    className="filter-label",
                                ),
                                html.Div(
                                    dcc.Dropdown(
                                        [
                                            "All",
                                            "Lonestar6",
                                            "Frontera",
                                            "Longhorn3",
                                            "Stampede4",
                                            "Lonestar5",
                                            "Maverick3",
                                            "Jetstream",
                                            "Hikari",
                                        ],
                                        ["All"],
                                        multi=True,
                                        id="select_machine_dd",
                                    )
                                ),
                            ],
                            id="select_machine_div",
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label(
                                            "Start month:",
                                            htmlFor="start_date_dd",
                                            className="filter-label",
                                        ),
                                        make_date_dd("start"),
                                    ],
                                    className="date-dropdown horizontal-beginning",
                                ),
                                html.Div(
                                    [
                                        html.Label(
                                            "End month:",
                                            htmlFor="end_date_dd",
                                            className="filter-label",
                                        ),
                                        make_date_dd("end"),
                                    ],
                                    className="date-dropdown horizontal-beginning",
                                ),
                                html.Div(
                                    [
                                        html.Label(
                                            "Fiscal year:",
                                            htmlFor="fy_dd",
                                            className="filter-label",
                                        ),
                                        dcc.Dropdown(
                                            FY_OPTIONS,
                                            id="fy_dd",
                                        ),
                                    ],
                                    className="date-dropdown",
                                ),
                            ],
                            style={"display": "flex"},
                        ),
                        html.Hr(),
                        html.Div(id="page-filter"),
                    ],
                    id="filters",
                    style={
                        "display": "",
                        "border": "0px",
                        "margin-top": "0px",
                        "font-size": "1.2rem",
                    },
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
    Output("chevron-icon", "className"),
    Input("toggle-filters", "n_clicks"),
    State("filters", "style"),
    prevent_initial_call=True,
)
def toggle_filters(click, state):
    if state == {"display": "none"}:
        return {
            "display": "",
            "border": "0px",
            "margin-top": "0px",
            "font-size": "1.2rem",
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=settings["DEBUG_MODE"])
