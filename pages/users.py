import pandas as pd
import plotly.express as px

import dash
from dash import dcc, Output, Input, html, dash_table, State, ctx
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

download_button = html.Div(
    children=[
        html.Button(
            "Download Data",
            id="btn-download",
            className="c-button c-button--primary btn-download",
        ),
        html.Hr(),
        dcc.Download(id="download-users-df"),
    ],
)

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
                                    ["Average Total Users"], className="counter_title"
                                ),
                                html.Div([0], id="total_users"),
                            ],
                            className="total_counters",
                        ),
                        html.Div(
                            [
                                html.Div(["Average Active"], className="counter_title"),
                                html.Div([0], id="active_users"),
                            ],
                            className="total_counters",
                        ),
                        html.Div(
                            [
                                html.Div(["Average Idle"], className="counter_title"),
                                html.Div([0], id="idle_users"),
                            ],
                            className="total_counters",
                        ),
                    ],
                    id="total_counters_wrapper",
                ),
                html.Div(children=[], id="bargraph"),
                html.Div(children=[], id="table"),
                download_button,
            ],
        ),
        dcc.Location(id="url"),
    ]
)


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
    dates = get_date_list(start_date, end_date)
    df = select_df(
        DATAFRAMES,
        dropdown,
        checklist,
        dates,
        machines,
    )

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
        filter_action="native",
        style_as_list_view=True,
    )

    inst_grps = df.groupby(["Institution"])
    df_with_avgs = {"Institution": [], "Date": []}
    for group in checklist:
        try:
            monthly_avg = inst_grps.get_group((group,))["Date"].value_counts().mean()
            for i in range(int(monthly_avg)):
                df_with_avgs["Institution"].append(group)
                df_with_avgs["Date"].append("AVG")
        except:
            continue  # For some date ranges, even if an institution is checked, it doesn't appear in the data, throwing an error
    combined_df = pd.concat([df, pd.DataFrame(df_with_avgs)])

    colors = make_color_map(dates)
    print(colors)

    bargraph = html.Div(
        [
            html.H2("Users per Institution"),
            dcc.Graph(
                figure=px.histogram(
                    data_frame=combined_df,
                    x="Institution",
                    color="Date",
                    barmode="group",
                    color_discrete_map=colors,
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
            ),
        ],
        className="graph-card",
    )

    totals = get_totals(
        DATAFRAMES,
        checklist,
        dates,
        "22-23",
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
