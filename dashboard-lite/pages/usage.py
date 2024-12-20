import pandas as pd
import plotly.express as px

import dash
from dash import dcc, Output, Input, html, ctx
import logging

from src.data_functions import *

from config import settings

LOGGING_LEVEL = settings["LOGGING_LEVEL"]
logging.basicConfig(level=LOGGING_LEVEL)

dash.register_page(__name__)
app = dash.get_app()

# INCORPORATE DATA
WORKSHEETS = ["utrc_active_allocations", "utrc_corral_usage"]

DATAFRAMES = merge_workbooks(WORKSHEETS)

layout = html.Div(
    [
        # TOTALS
        html.Div(
            [
                html.Div(
                    [
                        html.Div(["Sum SUs Used"], className="counter_title"),
                        html.Div([0], id="total_sus"),
                    ],
                    className="total_counters",
                ),
                html.Div(
                    [
                        html.Div(
                            ["Peak Storage Allocated (TB)"], className="counter_title"
                        ),
                        html.Div([0], id="total_storage"),
                    ],
                    className="total_counters",
                ),
            ],
            id="total_counters_wrapper",
        ),
        # END TOTALS
        html.Div(children=[], id="node_graph"),
        html.Div(children=[], id="corral_graph"),
        # DROPDOWN
        html.Div(
            [
                dcc.Dropdown(
                    id="dropdown",
                    options=[
                        {
                            "label": "Active Allocations",
                            "value": "utrc_active_allocations",
                        },
                        {"label": "Corral Usage", "value": "utrc_corral_usage"},
                    ],
                    value="utrc_active_allocations",
                    clearable=False,
                ),
            ],
            hidden=True,
        ),
        # END DROPDOWN
        dcc.Location(id="url"),
    ],
    className="body",
)


# ADD INTERACTIVITY THROUGH CALLBACKS
@app.callback(
    Output("node_graph", "children"),
    Output("corral_graph", "children"),
    Output("total_sus", "children"),
    Output("total_storage", "children"),
    Input("dropdown", "value"),
    Input("select_institutions_checklist", "value"),
    Input("date_filter", "value"),
    Input("year_radio_dcc", "value"),
    Input("select_machine_checklist", "value"),
)
def update_figs(dropdown, institutions, date_range, fiscal_year, machines):
    logging.debug(f"Callback trigger id: {ctx.triggered_id}")
    marks = get_marks(fiscal_year)
    if ctx.triggered_id == "year_radio_dcc":
        df = select_df(
            DATAFRAMES, dropdown, institutions, [0, len(marks)], fiscal_year, machines
        )
    else:
        df = select_df(
            DATAFRAMES, dropdown, institutions, date_range, fiscal_year, machines
        )

    sus_df = select_df(
        DATAFRAMES,
        "utrc_active_allocations",
        institutions,
        date_range,
        fiscal_year,
        machines,
    )
    sus_df_calculated = calc_node_monthly_sums(sus_df, institutions)
    total_sus = int(sus_df["SU's Charged"].sum())
    node_graph = dcc.Graph(
        figure=px.bar(
            data_frame=sus_df_calculated,
            title="SU Usage",
            x="Institution",
            y="SU's Charged",
            color="Date",
            barmode="group",
            text_auto=True,
            hover_data=["Resource"],
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
        )
    )

    corral_df = select_df(
        DATAFRAMES, "utrc_corral_usage", institutions, date_range, fiscal_year, machines
    )
    corral_df_calculated = calc_corral_monthly_sums(corral_df, institutions)
    total_storage = calc_corral_total(corral_df, institutions)
    corral_graph = dcc.Graph(
        figure=px.bar(
            data_frame=corral_df_calculated,
            title="Corral Storage Allocation",
            x="Institution",
            y="Storage Granted (TB)",
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
        )
    )

    return (
        node_graph,
        corral_graph,
        "{:,}".format(total_sus),
        "{:,}".format(total_storage),
    )
