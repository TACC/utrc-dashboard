import pandas as pd
import plotly.express as px

import dash
from dash import dcc, Output, Input, html, dash_table, State, ctx
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

download_button = html.Div(
    children=[
        html.Button(
            "Download Data",
            id="btn-download",
            className="c-button c-button--primary btn-download",
        ),
        html.Hr(),
        dcc.Download(id="download-usage-df"),
    ],
)

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
        download_button,
        dcc.Location(id="url"),
    ],
)


@app.callback(
    Output("download-usage-df", "data"),
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
    # prepare df
    dates = get_date_list(start_date, end_date)
    df = select_df(
        DATAFRAMES,
        dropdown,
        checklist,
        dates,
        machines,
    )
    return dcc.send_data_frame(df.to_csv, "utrc_data.csv")


# ADD INTERACTIVITY THROUGH CALLBACKS
@app.callback(
    Output("usage_table", "children"),
    Output("node_graph", "children"),
    Output("corral_graph", "children"),
    Output("total_sus", "children"),
    Output("total_storage", "children"),
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
    df = select_df(DATAFRAMES, dropdown, institutions, dates, machines)

    styles = get_table_styles()

    table = dash_table.DataTable(
        id="datatable_id",
        data=df.to_dict("records"),
        columns=[{"name": i, "id": i} for i in df.columns],
        fixed_rows={"headers": True},
        page_size=200,
        style_header=styles["style_header"],
        style_cell=styles["style_cell"],
        style_data_conditional=styles["style_data_conditional"],
        style_cell_conditional=create_conditional_style(df),
        style_header_conditional=styles["style_header_conditional"],
        sort_action="native",
        sort_by=[
            {"column_id": "SU's Charged", "direction": "desc"},
            {"column_id": "Storage Granted (Gb)", "direction": "desc"},
            {"column_id": "Institution", "direction": "asc"},
        ],
        filter_action="native",
        export_format="xlsx",
        style_as_list_view=True,
    )

    sus_df = select_df(
        DATAFRAMES,
        "utrc_active_allocations",
        institutions,
        dates,
        machines,
    )
    sus_df_calculated = calc_node_monthly_sums(sus_df, institutions)
    total_sus = int(sus_df["SU's Charged"].sum())
    node_graph = html.Div(
        [
            html.H2("SU's Charged for Active Allocations"),
            dcc.Graph(
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
            ),
        ],
        className="graph-card",
    )

    corral_df = select_df(
        DATAFRAMES, "utrc_corral_usage", institutions, dates, machines
    )
    corral_df_calculated = calc_corral_monthly_sums(corral_df, institutions)
    total_storage = calc_corral_total(corral_df, institutions)
    corral_graph = html.Div(
        [
            html.H2("Corral Usage"),
            dcc.Graph(
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
            ),
        ],
        className="graph-card",
    )

    return (
        table,
        node_graph,
        corral_graph,
        "{:,}".format(total_sus),
        "{:,}".format(total_storage),
    )
