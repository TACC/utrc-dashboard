import pandas as pd
import plotly.express as px

import dash
from dash import dcc, Output, Input, html, ctx
import logging
from src.scripts import *

from config import settings
LOGGING_LEVEL = settings['LOGGING_LEVEL']
logging.basicConfig(level=LOGGING_LEVEL)

dash.register_page(__name__, path="/")
app = dash.get_app()

# INCORPORATE DATA
FY_OPTIONS = create_fy_options()
WORKSHEETS = ['utrc_individual_user_hpc_usage', 'utrc_new_users']

DATAFRAMES = merge_workbooks(WORKSHEETS)


# CUSTOMIZE LAYOUT
layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(id='dropdown',
                         options=[
                            {'label': 'Active Users', 'value': 'utrc_individual_user_hpc_usage'},
                            {'label': 'New Users', 'value': 'utrc_new_users'}
                        ],
                         value='utrc_individual_user_hpc_usage',
                         clearable=False
                    ),
            ],),
        
        html.Div(children=[], id='bargraph'),

    ], className='body'),

    dcc.Location(id='url')
])

# ADD INTERACTIVITY THROUGH CALLBACKS
@app.callback(
    Output('bargraph', 'children'),
    Input('dropdown', 'value'),
    Input('select_institutions_checklist', 'value'),
    Input('date_filter', 'value'),
    Input('year_radio_dcc', 'value'),
    Input('select_machine_checklist', 'value')
)
def update_figs(dropdown, checklist, date_range, fiscal_year, machines):
    marks = get_marks(fiscal_year)
    if ctx.triggered_id == 'year_radio_dcc':
        df = select_df(DATAFRAMES, dropdown, checklist, [0, len(marks)], fiscal_year, machines)
    else:
        df = select_df(DATAFRAMES, dropdown, checklist, date_range, fiscal_year, machines)
    
    inst_grps = df.groupby(['Institution'])
    df_with_avgs = {'Institution': [], 'Date': []}
    for group in checklist:
        try:
            monthly_avg = inst_grps.get_group(group)['Date'].value_counts().mean()
            for i in range(int(monthly_avg)):
                df_with_avgs['Institution'].append(group)
                df_with_avgs['Date'].append('AVG')
        except:
            continue # For some date ranges, even if an institution is checked, it doesn't appear in the data, throwing an error
    combined_df = pd.concat([df, pd.DataFrame(df_with_avgs)])


    bargraph = dcc.Graph(figure=px.histogram(
                         data_frame=combined_df,
                         x="Institution",
                         color='Date',
                         barmode='group',
                         text_auto=True,
                         category_orders={'Institution': ['UTAus', 'UTA', 'UTD', 'UTEP', 'UTPB', 'UTRGV', 'UTSA', 'UTT', 'UTHSC-H', 'UTHSC-SA', 'UTMB', 'UTMDA', 'UTSW', 'UTSYS']}
                    ).update_layout(yaxis_title="Number of Users"))
    
    return bargraph