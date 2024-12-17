import pandas as pd
import plotly.express as px

import dash
from dash import dcc, Output, Input, html, dash_table, ctx
from src.scripts import *
import logging

from config import settings

LOGGING_LEVEL = settings["LOGGING_LEVEL"]
logging.basicConfig(level=LOGGING_LEVEL)

dash.register_page(__name__, path="/")
app = dash.get_app()

# INCORPORATE DATA
FY_OPTIONS = create_fy_options()
WORKSHEETS = [
    "utrc_individual_user_hpc_usage",
    "utrc_new_users",
    "utrc_idle_users",
    "utrc_suspended_users",
]

DATAFRAMES = merge_workbooks(WORKSHEETS)


# CUSTOMIZE LAYOUT
layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    ["Avg Total Users"], className="counter_title"
                                ),
                                html.Div([0], id="total_users"),
                            ],
                            className="total_counters",
                        ),
                        html.Div(
                            [
                                html.Div(["Avg Active"], className="counter_title"),
                                html.Div([0], id="active_users"),
                            ],
                            className="total_counters",
                        ),
                        html.Div(
                            [
                                html.Div(["Avg Idle"], className="counter_title"),
                                html.Div([0], id="idle_users"),
                            ],
                            className="total_counters",
                        ),
                    ],
                    id="total_counters_wrapper",
                ),
                html.Div(children=[], id="bargraph"),
                html.Div(children=[], id="table"),
            ],
            className="body",
        ),
        # dcc.Location(id="url"),
    ]
)


# ADD INTERACTIVITY THROUGH CALLBACKS
@app.callback(
    Output("table", "children"),
    Output("bargraph", "children"),
    Output("active_users", "children"),
    Output("idle_users", "children"),
    Output("total_users", "children"),
    Input("dropdown", "value"),
    Input("select_institutions_dd", "value"),
    Input("date_filter", "value"),
    Input("year_radio_dcc", "value"),
    Input("select_machine_checklist", "value"),
)
def update_figs(dropdown, checklist, date_range, fiscal_year, machines):
    marks = get_marks(fiscal_year)
    if ctx.triggered_id == "year_radio_dcc":
        df = select_df(
            DATAFRAMES, dropdown, checklist, [0, len(marks)], fiscal_year, machines
        )
    else:
        df = select_df(
            DATAFRAMES, dropdown, checklist, date_range, fiscal_year, machines
        )

    table = dash_table.DataTable(
        id="datatable_id",
        data=df.to_dict("records"),
        columns=[{"name": i, "id": i} for i in df.columns],
        fixed_rows={"headers": True},
        page_size=200,
        style_header={"backgroundColor": "#222222", "text_align": "center"},
        style_cell={"text_align": "left"},
        style_data_conditional=[
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#f4f4f4",
            }
        ],
        style_cell_conditional=create_conditional_style(df),
        sort_action="native",
        filter_action="native",
        export_format="xlsx",
    )

    inst_grps = df.groupby(["Institution"])
    df_with_avgs = {"Institution": [], "Date": []}
    for group in checklist:
        try:
            monthly_avg = inst_grps.get_group(group)["Date"].value_counts().mean()
            for i in range(int(monthly_avg)):
                df_with_avgs["Institution"].append(group)
                df_with_avgs["Date"].append("AVG")
        except:
            continue  # For some date ranges, even if an institution is checked, it doesn't appear in the data, throwing an error
    combined_df = pd.concat([df, pd.DataFrame(df_with_avgs)])

    bargraph = dcc.Graph(
        figure=px.histogram(
            data_frame=combined_df,
            x="Institution",
            color="Date",
            barmode="group",
            text_auto=True,
            category_orders={
                "Institution": [
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
                ]
            },
        ).update_layout(yaxis_title="Number of Users")
    )

    totals = get_totals(
        DATAFRAMES,
        checklist,
        date_range,
        fiscal_year,
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
