import dash
from dash import dcc, Output, Input, html, State, ctx
from src.data_functions import (
    create_fy_options,
    merge_workbooks,
    get_date_list,
    select_df,
    calc_monthly_avgs,
    get_allocation_totals,
)
from src.ui_functions import (
    make_df_download_button,
    make_summary_panel,
    make_data_table,
    make_bar_graph,
)
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

layout = html.Div(
    [
        # TOTALS
        make_summary_panel(
            ["Average Total Allocations", "Average Active", "Average Idle"],
            ["total_allocations", "active_allocations", "idle_allocations"],
        ),
        # END TOTALS
        html.Div(children=[], id="allocations_bargraph", className="my_graphs"),
        html.Div(children=[], id="allocations_table", className="my_tables"),
        make_df_download_button("allocations"),
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

    table = make_data_table(df, [{"column_id": "SU's Charged", "direction": "desc"}])

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
