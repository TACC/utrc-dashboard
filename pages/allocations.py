import logging

import dash
from dash import Input, Output, State, ctx, dcc, html
from flask_login import current_user

from config import settings
from src.data_functions import (
    calc_monthly_avgs,
    create_fy_options,
    get_allocation_totals,
    get_date_list,
    select_df,
)
from src.ui_functions import (
    make_bar_graph,
    make_data_table,
    make_df_download_button,
    make_filters,
    make_summary_panel,
)

from pages.users import DATAFRAMES

LOGGING_LEVEL = settings["LOGGING_LEVEL"]
logging.basicConfig(level=LOGGING_LEVEL)

dash.register_page(__name__)
app = dash.get_app()

FY_OPTIONS = create_fy_options()
logging.debug(f"FY Options: {FY_OPTIONS}")

ALLOC_DATAFRAMES = {
    "utrc_active_allocations": DATAFRAMES["utrc_active_allocations"],
    "utrc_current_allocations": DATAFRAMES["utrc_current_allocations"],
    "utrc_new_allocation_requests": DATAFRAMES["utrc_new_allocation_requests"],
}

dd_options = [
    {"label": "Active Allocations", "value": "utrc_active_allocations"},
    {"label": "Current Allocations", "value": "utrc_current_allocations"},
    {"label": "New Allocations", "value": "utrc_new_allocation_requests"},
]


layout = html.Div(
    [
        html.H1("Allocations", className="page-title"),
        make_filters("Allocations:", dd_options, "utrc_active_allocations"),
        # TOTALS
        make_summary_panel(
            ["Average Total Allocations", "Average Active", "Average Idle"],
            ["total_allocations", "active_allocations", "idle_allocations"],
        ),
        # END TOTALS
        html.Div(children=[], id="allocations_bargraph", className="my_graphs"),
        html.Div(children=[], id="allocations_table", className="my_tables"),
        html.Hr(),
        dcc.Location(id="url"),
    ],
)


@app.callback(
    Output("download-allocations-df", "data"),
    Input("btn-download", "n_clicks"),
    State("dropdown", "value"),
    State("select_institutions_dd", "value"),
    State("select_machine_dd", "value"),
    State("start_date_dd", "value"),
    State("end_date_dd", "value"),
    prevent_initial_call=True,
)
def deliver_download(
    n_clicks,
    dropdown,
    checklist,
    machines,
    start_date,
    end_date,
):
    if not current_user.is_authenticated:
        return ""
    else:
        # prepare df
        dates = get_date_list(start_date, end_date)
        df = select_df(
            ALLOC_DATAFRAMES,
            dropdown,
            checklist,
            dates,
            machines,
        )
        return dcc.send_data_frame(df.to_csv, "utrc_data.csv")


# ADD INTERACTIVITY THROUGH CALLBACKS
@app.callback(
    Output("allocations_table", "children"),
    Output("allocations_bargraph", "children"),
    Output("total_allocations", "children"),
    Output("active_allocations", "children"),
    Output("idle_allocations", "children"),
    Input("dropdown", "value"),
    Input("select_institutions_dd", "value"),
    Input("select_machine_dd", "value"),
    Input("start_date_dd", "value"),
    Input("end_date_dd", "value"),
)
def update_figs(
    dropdown,
    institutions,
    machines,
    start_date,
    end_date,
):
    logging.debug(f"Callback trigger id: {ctx.triggered_id}")
    dates = get_date_list(start_date, end_date)
    df = select_df(ALLOC_DATAFRAMES, dropdown, institutions, dates, machines)
    if not current_user.is_authenticated:
        table = html.Div(
            [
                "Please ",
                dcc.Link("login", href="/login"),
                " to view and download more data",
            ],
            className="login-note",
        )
    else:
        table = [
            make_data_table(df, [{"column_id": "SU's Charged", "direction": "desc"}]),
            make_df_download_button("allocations"),
        ]

    df_with_avgs = calc_monthly_avgs(df, institutions)

    bargraph = make_bar_graph(
        df_with_avgs,
        "Allocations per Institution",
        dates,
        "Count",
        "Number of Allocations",
        "Resource",
    )

    totals = get_allocation_totals(
        ALLOC_DATAFRAMES,
        institutions,
        dates,
        ["utrc_active_allocations", "utrc_current_allocations"],
        machines,
    )

    totals["total_allocations"] = (
        totals["idle_allocations"] + totals["active_allocations"]
    )

    return (
        table,
        bargraph,
        totals["total_allocations"],
        totals["active_allocations"],
        totals["idle_allocations"],
    )
