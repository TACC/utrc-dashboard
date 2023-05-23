import pandas as pd
import plotly.express as px

import dash
from dash import dcc, Output, Input, html, ctx
import logging

from src.scripts import *

from config import settings
LOGGING_LEVEL = settings['LOGGING_LEVEL']
logging.basicConfig(level=LOGGING_LEVEL)

dash.register_page(__name__)
app = dash.get_app()

# INCORPORATE DATA
WORKSHEETS = ['utrc_current_allocations', 'utrc_new_allocation_requests']
FY_OPTIONS = create_fy_options()
logging.debug(f'FY Options: {FY_OPTIONS}')

DATAFRAMES = merge_workbooks(WORKSHEETS)

layout=html.Div([
    # DROPDOWN
    html.Div([
        dcc.Dropdown(id='dropdown',
                        options=[
                        {'label': 'Current Allocations', 'value': 'utrc_current_allocations'},
                        {'label': 'New Allocations', 'value': 'utrc_new_allocation_requests'}
                    ],
                        value='utrc_current_allocations',
                        clearable=False
                ),
        ],),
    # END DROPDOWN

    html.Div(children=[], id='allocations_bargraph', className='my_graphs'),

    dcc.Location(id='url'),

], className='body')


# ADD INTERACTIVITY THROUGH CALLBACKS
@app.callback(
    Output('allocations_bargraph', 'children'),
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

    return bargraph