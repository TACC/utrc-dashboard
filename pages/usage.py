import logging
import dash
from dash import Input, Output, State, ctx, dcc, html
from flask_login import current_user

from config import settings
from src.data_functions import (
    calc_corral_monthly_sums_with_peaks,
    calc_corral_total,
    calc_node_monthly_sums,
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

USAGE_DATAFRAMES = {
    "utrc_active_allocations": DATAFRAMES["utrc_active_allocations"],
    "utrc_corral_usage": DATAFRAMES["utrc_corral_usage"],
}

dd_options = [
    {"label": "Active Allocations", "value": "utrc_active_allocations"},
    {"label": "Corral Usage", "value": "utrc_corral_usage"},
]

layout = html.Div(
    [
        html.H1("Usage", className="page-title"),
        make_filters("Usage:", dd_options, "utrc_active_allocations"),
        # TOTALS
        make_summary_panel(
            ["Sum SUs Used", "Peak Storage Allocated (TB)"],
            ["total_sus", "total_storage"],
        ),
        # END TOTALS
        html.Div(children=[], id="node_graph"),
        html.Div(children=[], id="corral_graph"),
        html.Div(children=[], id="usage_table", className="my_tables"),
        html.Hr(),
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
    if not current_user.is_authenticated:
        return ""
    else:
        # prepare df
        dates = get_date_list(start_date, end_date)
        df = select_df(
            USAGE_DATAFRAMES,
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
    df = select_df(USAGE_DATAFRAMES, dropdown, institutions, dates, machines)

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
            make_data_table(
                df,
                [
                    {"column_id": "SU's Charged", "direction": "desc"},
                    {"column_id": "Storage Granted (Gb)", "direction": "desc"},
                    {"column_id": "Institution", "direction": "asc"},
                ],
            ),
            make_df_download_button("usage"),
        ]

    sus_df = select_df(
        USAGE_DATAFRAMES,
        "utrc_active_allocations",
        institutions,
        dates,
        machines,
    )
    sus_df_calculated = calc_node_monthly_sums(sus_df, institutions)
    total_sus = int(sus_df["SU's Charged"].sum())

    node_graph = make_bar_graph(
        sus_df_calculated,
        "SU's Charged for Active Allocations",
        dates,
        "SU's Charged",
        hover="Resource",
    )

    corral_df = select_df(
        USAGE_DATAFRAMES, "utrc_corral_usage", institutions, dates, machines
    )
    corral_df_calculated = calc_corral_monthly_sums_with_peaks(corral_df, institutions)
    total_storage = calc_corral_total(corral_df_calculated)

    corral_graph = make_bar_graph(
        corral_df_calculated, "Corral Usage", dates, "Storage Granted (TB)"
    )

    return (
        table,
        node_graph,
        corral_graph,
        "{:,}".format(total_sus),
        "{:,}".format(total_storage),
    )
