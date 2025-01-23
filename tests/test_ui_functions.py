import json

import pandas as pd
import plotly
import plotly.express as px
import pytest
from dash import dash_table, dcc, html

from src.data_functions import create_fy_options, get_all_months
from src.ui_functions import (
    create_conditional_style,
    get_table_styles,
    make_bar_graph,
    make_color_map,
    make_data_table,
    make_date_dd,
    make_df_download_button,
    make_filters,
    make_summary_panel,
)
from src.constants import MACHINES_MENU, INSTITUTIONS_MENU


def test_make_df_download_button():
    b1 = html.Div(
        children=[
            html.Button(
                "Download Data",
                id="btn-download",
                className="c-button c-button--primary button--medium",
            ),
            dcc.Download(id="download-allocations-df"),
        ],
    )
    b1obj = json.loads(json.dumps(b1, cls=plotly.utils.PlotlyJSONEncoder))
    t1 = make_df_download_button("allocations")
    t1obj = json.loads(json.dumps(t1, cls=plotly.utils.PlotlyJSONEncoder))
    assert t1obj == b1obj

    b1 = html.Div(
        children=[
            html.Button(
                "Download Data",
                id="btn-download",
                className="c-button c-button--primary button--medium",
            ),
            dcc.Download(id="download--df"),
        ],
    )
    b1obj = json.loads(json.dumps(b1, cls=plotly.utils.PlotlyJSONEncoder))
    t1 = make_df_download_button("")
    t1obj = json.loads(json.dumps(t1, cls=plotly.utils.PlotlyJSONEncoder))
    assert t1obj == b1obj


def test_make_summary_panel():
    r1 = "Name and ID lists must contain the same number of elements"
    t1 = make_summary_panel(["test1", "test2"], [0])
    assert t1 == r1

    with pytest.raises(TypeError):
        make_summary_panel(["test1", "test2"], [0, 1])

    r2 = html.Div(
        [
            html.Div(
                [
                    html.Div(["test1"], className="summary-panel__metric__title"),
                    html.Div([0], id="0"),
                ],
                className="summary-panel__metric",
            ),
            html.Div(
                [
                    html.Div(["test2"], className="summary-panel__metric__title"),
                    html.Div([0], id="1"),
                ],
                className="summary-panel__metric",
            ),
        ],
        id="total_counters_wrapper",
        className="summary-panel__wrapper",
    )
    t2 = make_summary_panel(["test1", "test2"], ["0", "1"])
    r2obj = json.loads(json.dumps(r2, cls=plotly.utils.PlotlyJSONEncoder))
    t2obj = json.loads(json.dumps(t2, cls=plotly.utils.PlotlyJSONEncoder))
    assert r2obj == t2obj


def test_make_data_table():
    styles = get_table_styles()

    d = {
        "col1": [x for x in range(7)],
        "col2": [x for x in range(6, -1, -1)],
        "col3": [0 for x in range(7)],
    }
    df = pd.DataFrame(data=d)

    r1 = dash_table.DataTable(
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
    t1 = make_data_table(df)
    r1obj = json.loads(json.dumps(r1, cls=plotly.utils.PlotlyJSONEncoder))
    t1obj = json.loads(json.dumps(t1, cls=plotly.utils.PlotlyJSONEncoder))
    assert r1obj == t1obj

    r2 = dash_table.DataTable(
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
        sort_by="col2",
        filter_action="native",
        style_as_list_view=True,
    )
    t2 = make_data_table(df, "col2")
    r2obj = json.loads(json.dumps(r2, cls=plotly.utils.PlotlyJSONEncoder))
    t2obj = json.loads(json.dumps(t2, cls=plotly.utils.PlotlyJSONEncoder))
    assert r2obj == t2obj


def test_make_color_map():
    months = ["23-01", "23-02", "23-03"]
    # colors repeat in this order: ["#d5bfff", "#6039cc", "#281066"]
    r1 = {"23-01": "#d5bfff", "23-02": "#6039cc", "23-03": "#281066", "AVG": "#d5bfff"}
    t1 = make_color_map(months)
    assert t1 == r1


def test_make_bar_graph():
    # make_bar_graph(df, title, dates, yaxis, ytitle=None, hover=None)
    category_orders = {
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
    }
    months1 = ["23-01", "23-02", "23-03"]
    colors1 = make_color_map(months1)

    # Allocations Page
    d1 = {
        "Institution": [x for x in range(7)],
        "Date": [x for x in range(6, -1, -1)],
        "Resource": [0 for x in range(7)],
        "Count": [0 for x in range(7)],
    }
    df = pd.DataFrame(data=d1)
    fig1 = px.bar(
        data_frame=df,
        x="Institution",
        y="Count",
        color="Date",
        barmode="group",
        color_discrete_map=colors1,
        text_auto=True,
        hover_data=["Resource"],
        category_orders=category_orders,
    )
    fig1.update_layout(yaxis_title="Number of Allocations")
    r1 = html.Div(
        [html.H2("Allocations per Institution"), dcc.Graph(figure=fig1)],
        className="graph-card",
    )
    t1 = make_bar_graph(
        df,
        "Allocations per Institution",
        months1,
        "Count",
        "Number of Allocations",
        "Resource",
    )
    r1obj = json.loads(json.dumps(r1, cls=plotly.utils.PlotlyJSONEncoder))
    t1obj = json.loads(json.dumps(t1, cls=plotly.utils.PlotlyJSONEncoder))
    assert r1obj == t1obj

    # Usage page
    d2 = {
        "Institution": [x for x in range(7)],
        "Resource": [0 for x in range(7)],
        "Date": [x for x in range(6, -1, -1)],
        "SU's Charged": [0 for x in range(7)],
    }
    df2 = pd.DataFrame(data=d2)
    fig2 = px.bar(
        data_frame=df2,
        x="Institution",
        y="SU's Charged",
        color="Date",
        barmode="group",
        color_discrete_map=colors1,
        text_auto=True,
        hover_data=["Resource"],
        category_orders=category_orders,
    )
    r2 = html.Div(
        [html.H2("SU's Charged for Active Allocations"), dcc.Graph(figure=fig2)],
        className="graph-card",
    )
    t2 = make_bar_graph(
        df2,
        "SU's Charged for Active Allocations",
        months1,
        "SU's Charged",
        hover="Resource",
    )
    r2obj = json.loads(json.dumps(r2, cls=plotly.utils.PlotlyJSONEncoder))
    t2obj = json.loads(json.dumps(t2, cls=plotly.utils.PlotlyJSONEncoder))
    assert r2obj == t2obj

    d3 = {
        "Institution": [x for x in range(7)],
        "Date": [x for x in range(6, -1, -1)],
        "Storage Granted (TB)": [0 for x in range(7)],
    }
    df3 = pd.DataFrame(data=d3)

    fig3 = px.bar(
        data_frame=df3,
        x="Institution",
        y="Storage Granted (TB)",
        color="Date",
        barmode="group",
        color_discrete_map=colors1,
        text_auto=True,
        hover_data=[None],
        category_orders=category_orders,
    )
    r3 = html.Div(
        [html.H2("Corral Usage"), dcc.Graph(figure=fig3)],
        className="graph-card",
    )
    t3 = make_bar_graph(df3, "Corral Usage", months1, "Storage Granted (TB)")
    r3obj = json.loads(json.dumps(r3, cls=plotly.utils.PlotlyJSONEncoder))
    t3obj = json.loads(json.dumps(t3, cls=plotly.utils.PlotlyJSONEncoder))
    assert r3obj == t3obj

    # Users page
    d4 = {
        "Institution": [x for x in range(7)],
        "Resource": [0 for x in range(7)],
        "Type": [0 for x in range(7)],
        "SU's Charged": [0 for x in range(7)],
        "Last Name": [x for x in range(6, -1, -1)],
        "First Name": [x for x in range(6, -1, -1)],
        "Email": [x for x in range(6, -1, -1)],
        "Project Name": [x for x in range(6, -1, -1)],
        "Title": [x for x in range(6, -1, -1)],
        "Project Type": [x for x in range(6, -1, -1)],
        "Job Count": [x for x in range(6, -1, -1)],
        "Login": [x for x in range(6, -1, -1)],
        "New User?": [x for x in range(6, -1, -1)],
        "Suspended?": [x for x in range(6, -1, -1)],
        "Date": [0 for x in range(7)],
    }
    df4 = pd.DataFrame(data=d4)
    fig4 = px.histogram(
        data_frame=df4,
        x="Institution",
        color="Date",
        barmode="group",
        color_discrete_map=colors1,
        text_auto=True,
        category_orders=category_orders,
    )
    fig4.update_layout(yaxis_title="Number of Users")
    r4 = html.Div(
        [html.H2("Users per Institution"), dcc.Graph(figure=fig4)],
        className="graph-card",
    )
    t4 = make_bar_graph(df4, "Users per Institution", months1, None, "Number of Users")
    r4obj = json.loads(json.dumps(r4, cls=plotly.utils.PlotlyJSONEncoder))
    t4obj = json.loads(json.dumps(t4, cls=plotly.utils.PlotlyJSONEncoder))
    assert r4obj == t4obj


def test_make_date_dd():
    dates = get_all_months()
    r1 = dcc.Dropdown(
        dates,
        dates[0],
        id="start_date_dd",
    )
    t1 = make_date_dd("start")
    r1obj = json.loads(json.dumps(r1, cls=plotly.utils.PlotlyJSONEncoder))
    t1obj = json.loads(json.dumps(t1, cls=plotly.utils.PlotlyJSONEncoder))
    assert r1obj == t1obj

    r2 = dcc.Dropdown(
        dates,
        dates[-1],
        id="end_date_dd",
    )
    t2 = make_date_dd("end")
    r2obj = json.loads(json.dumps(r2, cls=plotly.utils.PlotlyJSONEncoder))
    t2obj = json.loads(json.dumps(t2, cls=plotly.utils.PlotlyJSONEncoder))
    assert r2obj == t2obj


def test_make_filters():
    FY_OPTIONS = create_fy_options()
    dd_options = [
        {"label": "Active Allocations", "value": "utrc_active_allocations"},
        {"label": "Current Allocations", "value": "utrc_current_allocations"},
        {"label": "New Allocations", "value": "utrc_new_allocation_requests"},
    ]

    r1 = html.Div(
        [
            html.Button(
                [
                    html.H3(
                        "Filters",
                        className="filter-toggle__title",
                    ),
                    html.I(
                        id="chevron-icon",
                        className="bi bi-chevron-down filter-toggle__chevron",
                    ),
                ],
                id="toggle-filters",
                n_clicks=0,
                className="filter-toggle__button",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label(
                                "Institution:",
                                htmlFor="select_institutions_dd",
                                className="filter-box__label",
                            ),
                            html.Div(
                                [
                                    dcc.Dropdown(
                                        INSTITUTIONS_MENU,
                                        ["All"],
                                        multi=True,
                                        id="select_institutions_dd",
                                    ),
                                ],
                            ),
                        ],
                        id="select_institutions_div",
                    ),
                    html.Hr(),
                    html.Div(
                        [
                            html.Label(
                                "Machine:",
                                htmlFor="select_machine_dd",
                                className="filter-box__label",
                            ),
                            html.Div(
                                dcc.Dropdown(
                                    MACHINES_MENU,
                                    ["All"],
                                    multi=True,
                                    id="select_machine_dd",
                                )
                            ),
                        ],
                        id="select_machine_div",
                    ),
                    html.Hr(),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label(
                                        "Start month:",
                                        htmlFor="start_date_dd",
                                        className="filter-box__label",
                                    ),
                                    make_date_dd("start"),
                                ],
                                className="date-dropdown date-dropdown--not-last",
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "End month:",
                                        htmlFor="end_date_dd",
                                        className="filter-box__label",
                                    ),
                                    make_date_dd("end"),
                                ],
                                className="date-dropdown date-dropdown--not-last",
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "Fiscal year:",
                                        htmlFor="fy_dd",
                                        className="filter-box__label",
                                    ),
                                    dcc.Dropdown(
                                        FY_OPTIONS,
                                        id="fy_dd",
                                    ),
                                ],
                                className="date-dropdown",
                            ),
                        ],
                        style={"display": "flex"},
                    ),
                    html.Hr(),
                    html.Div(
                        [
                            html.Label(
                                "Allocations:",
                                htmlFor="dropdown",
                                className="filter-box__label",
                            ),
                            dcc.Dropdown(
                                id="dropdown",
                                options=dd_options,
                                value="utrc_active_allocations",
                                clearable=False,
                            ),
                        ]
                    ),
                ],
                id="filters",
                style={
                    "display": "",
                },
                className="c-island filter-box",
            ),
        ]
    )

    t1 = make_filters("Allocations:", dd_options, "utrc_active_allocations")
    r1obj = json.loads(json.dumps(r1, cls=plotly.utils.PlotlyJSONEncoder))
    t1obj = json.loads(json.dumps(t1, cls=plotly.utils.PlotlyJSONEncoder))
    assert r1obj == t1obj
