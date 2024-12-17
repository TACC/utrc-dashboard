import pandas as pd
import plotly.express as px

import dash
from dash import dcc, Output, Input, html, dash_table, ctx
from src.scripts import *
import logging

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
        html.Div(children=[], id="usage_table", className="my_tables"),
        dcc.Location(id="url"),
    ],
    className="body",
)


# ADD INTERACTIVITY THROUGH CALLBACKS
@app.callback(
    Output("usage_table", "children"),
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
        sort_by=[
            {"column_id": "SU's Charged", "direction": "desc"},
            {"column_id": "Storage Granted (Gb)", "direction": "desc"},
            {"column_id": "Institution", "direction": "asc"},
        ],
        filter_action="native",
        export_format="xlsx",
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
        table,
        node_graph,
        corral_graph,
        "{:,}".format(total_sus),
        "{:,}".format(total_storage),
    )
