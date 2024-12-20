import copy
from dash import html, dcc, dash_table
import plotly.express as px


def create_conditional_style(df):
    """
    Necessary workaround for a Plotly Dash bug where table headers are cut off if row data is shorter than the header.
    """
    style = []
    for col in df.columns:
        name_length = len(col)
        pixel = 30 + round(name_length * 8)
        pixel = str(pixel) + "px"
        style.append({"if": {"column_id": col}, "minWidth": pixel})
    return style


def get_table_styles():
    styles = {
        "style_header": {
            "backgroundColor": "#fff",
            "text_align": "left",
            "font-family": "var(--global-font-family--sans--portal)",
            "font-size": "var(--global-font-size--small)",
            "border-bottom": "1px solid #222222",
            "border-top": "0px",
            "font-weight": "var(--bold)",
        },
        "style_cell": {
            "text_align": "left",
            "font-family": "var(--global-font-family--sans--portal)",
            "font-size": "var(--global-font-size--small)",
            "padding-right": "14px",
        },
        "style_data_conditional": [
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#f4f4f4",
            },
            {"if": {"column_id": "SU's Charged"}, "text-align": "right"},
            {"if": {"column_id": "Job Count"}, "text-align": "right"},
            {"if": {"column_id": "User Count"}, "text-align": "right"},
        ],
        "style_header_conditional": [
            {"if": {"column_id": "SU's Charged"}, "text-align": "right"},
            {"if": {"column_id": "Job Count"}, "text-align": "right"},
            {"if": {"column_id": "User Count"}, "text-align": "right"},
        ],
    }
    return styles


def make_color_map(months):
    m = copy.deepcopy(months)
    m.append("AVG")
    colors = ["#d5bfff", "#6039cc", "#281066"]
    color_map = {}
    for i in range(len(m)):
        color_map[m[i]] = colors[i % 3]
    return color_map


def make_df_download_button(page):
    return html.Div(
        children=[
            html.Button(
                "Download Data",
                id="btn-download",
                className="c-button c-button--primary btn-download",
            ),
            html.Hr(),
            dcc.Download(id=f"download-{page}-df"),
        ],
    )


def make_summary_panel(names, ids):
    if len(names) != len(ids):
        return "Name and ID lists must contain the same number of elements"
    else:
        stat_list = []
        for i in range(len(names)):
            stat_list.append(
                html.Div(
                    [
                        html.Div([names[i]], className="counter_title"),
                        html.Div([0], id=ids[i]),
                    ],
                    className="total_counters",
                )
            )
        return html.Div(stat_list, id="total_counters_wrapper")


def make_data_table(df, sort_by=None):
    styles = get_table_styles()

    if sort_by is None:
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
    else:
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
            sort_by=sort_by,
            filter_action="native",
            style_as_list_view=True,
        )
    return table


def make_bar_graph(df, title, dates, yaxis, ytitle=None, hover=None):
    colors = make_color_map(dates)
    if not yaxis:
        fig = px.histogram(
            data_frame=df,
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
        )
    else:
        fig = px.bar(
            data_frame=df,
            x="Institution",
            y=yaxis,
            color="Date",
            barmode="group",
            color_discrete_map=colors,
            text_auto=True,
            hover_data=[hover],
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
    if ytitle:
        fig.update_layout(yaxis_title=ytitle)
    return html.Div(
        [html.H2("Users per Institution"), dcc.Graph(figure=fig)],
        className="graph-card",
    )