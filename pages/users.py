import logging

import dash
import pandas as pd
from dash import Input, Output, State, ctx, dcc, html
from flask_login import current_user

from config import settings
from src.data_functions import (
    create_fy_options,
    get_date_list,
    get_totals,
    select_df,
)
from src.ui_functions import (
    make_bar_graph,
    make_data_table,
    make_df_download_button,
    make_filters,
    make_summary_panel,
)
from src.startup import DATAFRAMES

LOGGING_LEVEL = settings["LOGGING_LEVEL"]
logging.basicConfig(level=LOGGING_LEVEL)

dash.register_page(__name__, path="/")
app = dash.get_app()

FY_OPTIONS = create_fy_options()

USER_DATAFRAMES = {
    "utrc_individual_user_hpc_usage": DATAFRAMES["utrc_individual_user_hpc_usage"],
    "utrc_new_users": DATAFRAMES["utrc_new_users"],
    "utrc_idle_users": DATAFRAMES["utrc_idle_users"],
    "utrc_suspended_users": DATAFRAMES["utrc_suspended_users"],
}


dd_options = [
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
]

# CUSTOMIZE LAYOUT
layout = html.Div(
    [
        html.Div(
            [
                html.H1("Users", className="page-title"),
                make_filters("Users:", dd_options, "utrc_individual_user_hpc_usage"),
                make_summary_panel(
                    ["Average Total Users", "Average Active", "Average Idle"],
                    ["total_users", "active_users", "idle_users"],
                ),
                html.Div(children=[], id="bargraph"),
                html.Div(children=[], id="table"),
                html.Hr(),
            ],
        ),
        dcc.Location(id="url"),
    ]
)


# ADD INTERACTIVITY THROUGH CALLBACKS
@app.callback(
    Output("download-users-df", "data"),
    Input("btn-download", "n_clicks"),
    State("dropdown", "value"),
    State("select_institutions_dd", "value"),
    State("select_machine_dd", "value"),
    State("start_date_dd", "value"),
    State("end_date_dd", "value"),
    prevent_initial_call=True,
)
def func(
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
            USER_DATAFRAMES,
            dropdown,
            checklist,
            dates,
            machines,
        )
        return dcc.send_data_frame(df.to_csv, "utrc_data.csv")


@app.callback(
    Output("table", "children"),
    Output("bargraph", "children"),
    Output("active_users", "children"),
    Output("idle_users", "children"),
    Output("total_users", "children"),
    Input("dropdown", "value"),
    Input("select_institutions_dd", "value"),
    Input("select_machine_dd", "value"),
    Input("start_date_dd", "value"),
    Input("end_date_dd", "value"),
)
def update_figs(
    dropdown,
    checklist,
    machines,
    start_date,
    end_date,
):
    logging.debug(f"Callback trigger id: {ctx.triggered_id}")
    dates = get_date_list(start_date, end_date)
    df = select_df(
        USER_DATAFRAMES,
        dropdown,
        checklist,
        dates,
        machines,
    )

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
            make_data_table(df),
            make_df_download_button("users"),
        ]

    inst_grps = df.groupby(["Institution"])
    df_with_avgs = {"Institution": [], "Date": []}
    for group in checklist:
        try:
            monthly_avg = inst_grps.get_group((group,))["Date"].value_counts().mean()
            for i in range(int(monthly_avg)):
                df_with_avgs["Institution"].append(group)
                df_with_avgs["Date"].append("AVG")
        except KeyError:
            continue  # For some date ranges, even if an institution is checked, it doesn't appear in the data, throwing an error
    combined_df = pd.concat([df, pd.DataFrame(df_with_avgs)])

    bargraph = make_bar_graph(
        combined_df, "Users per Institution", dates, None, "Number of Users"
    )
    totals = get_totals(
        USER_DATAFRAMES,
        checklist,
        dates,
        ["utrc_individual_user_hpc_usage", "utrc_idle_users"],
        machines,
    )
    totals["total_users"] = totals["active_users"] + totals["idle_users"]

    return (
        table,
        bargraph,
        totals["active_users"],
        totals["idle_users"],
        totals["total_users"],
    )
