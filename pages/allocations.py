import pandas as pd
import plotly.express as px

import dash
from dash import dcc, Output, Input, html, dash_table, ctx
from src.scripts import *
import logging

from config import settings
LOGGING_LEVEL = settings['LOGGING_LEVEL']
logging.basicConfig(level=LOGGING_LEVEL)

dash.register_page(__name__)
app = dash.get_app()

# INCORPORATE DATA
WORKSHEETS = ['utrc_active_allocations', 'utrc_current_allocations', 'utrc_new_allocation_requests']
FY_OPTIONS = create_fy_options()
logging.debug(f'FY Options: {FY_OPTIONS}')

DATAFRAMES = merge_workbooks(WORKSHEETS)

layout=html.Div([
    # TOTALS
    html.Div([
            html.Div([html.Div(["Avg Total Allocations"], className='counter_title'), html.Div([0], id='total_allocations')], className="total_counters"),
            html.Div([html.Div(["Avg Active"], className='counter_title'), html.Div([0], id='active_allocations')], className="total_counters"),
            html.Div([html.Div(["Avg Idle"], className='counter_title'), html.Div([0], id="idle_allocations")], className="total_counters"),
        ], id='total_counters_wrapper'),
    # END TOTALS

    # DROPDOWN
    html.Div([
        dcc.Dropdown(id='dropdown',
                        options=[
                        {'label': 'Active Allocations', 'value': 'utrc_active_allocations'},
                        {'label': 'Current Allocations', 'value': 'utrc_current_allocations'},
                        {'label': 'New Allocations', 'value': 'utrc_new_allocation_requests'}
                    ],
                        value='utrc_active_allocations',
                        clearable=False
                ),
        ],),
    # END DROPDOWN

    html.Div(children=[], id='allocations_bargraph', className='my_graphs'),

    html.Div(children=[], id='allocations_table', className='my_tables'),

    dcc.Location(id='url'),

], className='body')


# ADD INTERACTIVITY THROUGH CALLBACKS
@app.callback(
    Output('allocations_table', 'children'),
    Output('allocations_bargraph', 'children'),
    Output('total_allocations', 'children'),
    Output('active_allocations', 'children'),
    Output('idle_allocations', 'children'),
    Input('dropdown', 'value'),
    Input('select_institutions_checklist', 'value'),
    Input('date_filter', 'value'),
    Input('year_radio_dcc', 'value'),
    Input('select_machine_checklist', 'value')
)
def update_figs(dropdown, institutions, date_range, fiscal_year, machines):
    logging.debug(f'Callback trigger id: {ctx.triggered_id}')
    marks = get_marks(fiscal_year)
    if ctx.triggered_id == 'year_radio_dcc':
        df = select_df(DATAFRAMES, dropdown, institutions, [0, len(marks)], fiscal_year, machines)
    else:
        df = select_df(DATAFRAMES, dropdown, institutions, date_range, fiscal_year, machines)

    table = dash_table.DataTable(id='datatable_id',
                                 data=df.to_dict('records'),
                                 columns=[{"name": i, "id": i} for i in df.columns],
                                 fixed_rows={'headers': True},
                                 page_size=200,
                                 style_header={'backgroundColor': '#222222', 'text_align': 'center'},
                                 style_cell={'text_align': 'left'},
                                 style_data_conditional=[{
                                                    'if': {'row_index': 'odd'},
                                                    'backgroundColor': '#f4f4f4',
                                                }],
                                 style_cell_conditional=create_conditional_style(df),
                                 sort_action='native',
                                 sort_by=[{'column_id': 'SU\'s Charged', 'direction': 'desc'}],
                                 filter_action='native',
                                 export_format='xlsx'
                            )

    df_with_avgs = calc_monthly_avgs(df, institutions)
    bargraph = dcc.Graph(figure=px.bar(
                         data_frame=df_with_avgs,
                         x="Institution",
                         y='Count',
                         color='Date',
                         barmode='group',
                         text_auto=True,
                         hover_data=['Resource'],
                         category_orders={'Institution': ['UTAus', 'UTA', 'UTD', 'UTEP', 'UTPB', 'UTRGV', 'UTSA', 'UTT', 'UTHSC-H', 'UTHSC-SA', 'UTMB', 'UTMDA', 'UTSW', 'UTSYS']}
                    ).update_layout(yaxis_title="Number of Allocations"))

    
    totals = get_allocation_totals(DATAFRAMES, institutions, date_range, fiscal_year, ['utrc_active_allocations', 'utrc_current_allocations'], machines)
    totals['total_allocations'] = totals['idle_allocations'] + totals['active_allocations']

    return table, bargraph, totals['total_allocations'], totals['active_allocations'], totals['idle_allocations']