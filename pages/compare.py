from dash import (
    dcc,
    html,
    register_page,
    callback,
    Output,
    Input,
    State,
    MATCH,
    ALL,
    no_update,
    Patch,
)
import pandas as pd
from src.ui_functions import (
    make_bar_graph_comparison,
    make_other_filters,
    make_date_filters,
    make_date_range,
)
from src.data_functions import (
    get_marks,
    get_date_list,
    select_df,
    split_month,
    check_date_order,
    calc_node_monthly_sums_no_machine,
    calc_corral_monthly_sums,
)
from src.constants import MONTH_NAMES, DD_OPTIONS, REPORT_INFO
from pages.users import DATAFRAMES


register_page(__name__)

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

bg1 = html.Div(
    [
        html.H2("", id="comparison-title"),
        dcc.Graph(
            figure={},
            id="bar-graph-comparison",
        ),
    ],
    className="graph-card",
)


def check_valid_date_ranges(start, end):
    # trigger a warning if start/ end months don't match across date ranges
    start_months = []
    end_months = []
    for idx, (start_date, end_date) in enumerate(zip(start, end)):
        if not start_date or not end_date:
            return html.P(
                "Please choose start and end dates for all of the date ranges.",
                className="filter-error",
            )
        range_validity = check_date_order(start_date, end_date)
        if range_validity is False:
            return html.P(
                "For each range, the start date must be earlier than the end date.",
                className="filter-error",
            )
        start_month = split_month(start_date)
        end_month = split_month(end_date)
        if idx != 0 and (
            start_month != start_months[idx - 1] or end_month != end_months[idx - 1]
        ):
            return html.P(
                "Please align all of the date ranges to use the same start and end month so that the date ranges are the same length. Date ranges can cover different years.",
                className="filter-error",
            )
        start_months.append(start_month)
        end_months.append(end_month)
    return ""


layout = html.Div(
    [
        html.H1("Compare Date Ranges", className="page-title"),
        make_other_filters(
            DD_OPTIONS["Users"], "utrc_individual_user_hpc_usage", "Users"
        ),
        make_date_filters(),
        bg1,
        html.Div(id="test-div"),
    ]
)


# Callbacks
@callback(
    Output({"type": "start-date-dd", "index": MATCH}, "value"),
    Output({"type": "end-date-dd", "index": MATCH}, "value"),
    Input({"type": "fy-dd", "index": MATCH}, "value"),
)
def update_dates(fy):
    if fy:
        marks = get_marks(fy)
        marks_list = [x for x in marks.values()]
        return marks_list[0], marks_list[-1]
    else:
        return no_update


@callback(
    Output({"type": "date-range", "index": MATCH}, "children"),
    Input({"type": "remove-date-range", "index": MATCH}, "n_clicks"),
    prevent_initial_call=True,
)
def remove_date_range(n_clicks):
    if n_clicks == 0:
        return no_update
    return []


@callback(
    Output("other-filters", "children"),
    Input("report-picker-dd", "value"),
)
def update_report_metrics(which_report):
    if which_report == "Users":
        dd_options = DD_OPTIONS["Users"]
        dd_default = "utrc_individual_user_hpc_usage"
    elif which_report == "Allocations":
        dd_options = DD_OPTIONS["Allocations"]
        dd_default = "utrc_active_allocations"
    elif which_report == "Usage":
        dd_options = DD_OPTIONS["Usage"]
        dd_default = "utrc_sus_charged"
    return make_other_filters(dd_options, dd_default, which_report)


@callback(
    Output("date-ranges-div", "children"),
    Input("add-date-range", "n_clicks"),
    State({"type": "start-date-dd", "index": ALL}, "value"),
    State({"type": "end-date-dd", "index": ALL}, "value"),
)
def add_date_range(n_clicks, start, end):
    if n_clicks == 0:
        return no_update
    else:
        patched_range_list = Patch()
        if len(start) == 0:
            new_pos = 0
            new_elem = make_date_range()
        else:
            new_pos = len(start) + 1
            new_elem = make_date_range(start[-1], end[-1], pos=new_pos)
        patched_range_list.append(new_elem)
        return patched_range_list


@callback(
    Output("bar-graph-comparison", "figure"),
    Output("comparison-title", "children"),
    Output("error-div", "children"),
    Input("report-specific-dd", "value"),
    Input("select-institution-dd", "value"),
    Input("select-machine-dd", "value"),
    Input({"type": "start-date-dd", "index": ALL}, "value"),
    Input({"type": "end-date-dd", "index": ALL}, "value"),
)
def update_figs(
    report_dd,
    institution,
    machines,
    start_dates,
    end_dates,
):
    err = check_valid_date_ranges(start_dates, end_dates)
    if err:
        return no_update, no_update, err
    dfs = []
    names = []

    # zip through the start/end date pairs and use get_date_list to get the dates in each range
    for idx, (start, end) in enumerate(zip(start_dates, end_dates)):
        date_range = get_date_list(start, end)
        name = f"{date_range[0]} to {date_range[-1]}"
        names.append(name)

        df = select_df(
            DATAFRAMES,
            REPORT_INFO[report_dd][2],
            [institution],
            date_range,
            machines,
        )

        # do additional aggregation for usage charts
        if report_dd == "utrc_sus_charged":
            df = calc_node_monthly_sums_no_machine(df, [institution])
        elif report_dd == "utrc_corral_usage":
            df = calc_corral_monthly_sums(df, [institution])

        # assign each unique date a bin number
        unique_bins = df["Date"].unique()
        num_bins = unique_bins.size
        bins_list = unique_bins.tolist()

        map_df = pd.DataFrame(
            {"dates": bins_list, "bins": [x for x in range(num_bins)]}
        )
        df["Bin"] = df["Date"].map(map_df.set_index("dates").squeeze())

        def get_month_name(date, bin):
            month_num = split_month(date)
            which_year = bin // 12
            # when a month appears again in a date range > 1 year, append a space to the end so that it will be a new bin
            month_name = MONTH_NAMES[month_num] + (which_year * " ")
            return month_name

        df["Month Name"] = df.apply(lambda x: get_month_name(x.Date, x.Bin), axis=1)
        dfs.append(df)

    if report_dd == "utrc_sus_charged" or report_dd == "utrc_corral_usage":
        fig = make_bar_graph_comparison(
            dfs,
            names=names,
            xaxis="Month",
            yaxis=REPORT_INFO[report_dd][1],
            chart_type="Bar",
        )
    else:
        fig = make_bar_graph_comparison(
            dfs, names=names, xaxis="Month", yaxis=REPORT_INFO[report_dd][1]
        )
    title = REPORT_INFO[report_dd][0]
    return fig, title, err
