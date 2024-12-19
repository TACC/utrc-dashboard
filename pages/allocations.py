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
WORKSHEETS = [
    "utrc_active_allocations",
    "utrc_current_allocations",
    "utrc_new_allocation_requests",
]
FY_OPTIONS = create_fy_options()
logging.debug(f"FY Options: {FY_OPTIONS}")

DATAFRAMES = merge_workbooks(WORKSHEETS)

download_button = html.Div(
    children=[
        html.Button(
            "Download Data",
            id="btn-download",
            className="c-button c-button--primary btn-download",
        ),
        html.Hr(),
        dcc.Download(id="download-allocations-df"),
    ],
)

layout = html.Div(
    [
        # TOTALS
        html.Div(
            [
                html.Div(
                    [
                        html.Div(["Avg Total Allocations"], className="counter_title"),
                        html.Div([0], id="total_allocations"),
                    ],
                    className="total_counters",
                ),
                html.Div(
                    [
                        html.Div(["Avg Active"], className="counter_title"),
                        html.Div([0], id="active_allocations"),
                    ],
                    className="total_counters",
                ),
                html.Div(
                    [
                        html.Div(["Avg Idle"], className="counter_title"),
                        html.Div([0], id="idle_allocations"),
                    ],
                    className="total_counters",
                ),
            ],
            id="total_counters_wrapper",
        ),
        # END TOTALS
        html.Div(children=[], id="allocations_bargraph", className="my_graphs"),
        html.Div(children=[], id="allocations_table", className="my_tables"),
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
        sort_by=[{"column_id": "SU's Charged", "direction": "desc"}],
        filter_action="native",
        export_format="xlsx",
        style_as_list_view=True,
    )

    df_with_avgs = calc_monthly_avgs(df, institutions)

    bargraph = html.Div(
        [
            html.H2("Allocations per Institution"),
            dcc.Graph(
                figure=px.bar(
                    data_frame=df_with_avgs,
                    x="Institution",
                    y="Count",
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
                ).update_layout(yaxis_title="Number of Allocations")
            ),
        ],
        className="graph-card",
    )

    totals = get_allocation_totals(
        DATAFRAMES,
        institutions,
        dates,
        "22-23",
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
