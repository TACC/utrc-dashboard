import dash
from dash import html, dcc, Input, Output, ctx, State
import logging
from src.scripts import create_fy_options, get_marks

from config import settings
LOGGING_LEVEL = settings['LOGGING_LEVEL']
logging.basicConfig(level=LOGGING_LEVEL)

FY_OPTIONS = create_fy_options()

app = dash.Dash(__name__, use_pages=True, prevent_initial_callbacks='initial_duplicate',
		suppress_callback_exceptions=True, title='UTRC Dashboard')

app.layout = html.Div([
    html.Div(
        [
	     html.A(html.Img(src='assets/images/utrc-horizontal-logo-white-simple.svg', className='utrc-logo'), href='https://utrc.tacc.utexas.edu/'),
         html.A("Users", href='/'),
		 html.A("Allocations", href='/allocations'),
		 html.A("Usage", href='/usage'),
	    ],
        id='header2'
	),
	html.Div([
	html.Button('Toggle Filters', id='toggle-filters', n_clicks=0),
	html.Div([
            html.Div([
                "By institution:",
                html.Div([
                html.Div(["?", html.Span(html.P(children=["UTAus: The University of Texas at Austin", html.Br(), 
                                                "UTA: The University of Texas at Arlington", html.Br(), 
                                                "UTD: The University of Texas at Dallas", html.Br(), 
                                                "UTEP: The University of Texas at El Paso", html.Br(), 
                                                "UTPB: The University of Texas Permian Basin", html.Br(), 
                                                "UTRGV: The University of Texas Rio Grande Valley", html.Br(), 
                                                "UTSA: The University of Texas at San Antonio", html.Br(), 
                                                "UTT: The University of Texas at Tyler", html.Br(), 
                                                "UTHSC-H: The University of Texas Health Science Center-Houston", html.Br(),
                                                "UTHSC-SA: The University of Texas Health Science Center-San Antonio", html.Br(), 
                                                "UTMB: The University of Texas Medical Branch", html.Br(), 
                                                "UTMDA: The University of Texas MD Anderson Cancer Center", html.Br(), 
                                                "UTSW: The University of Texas Southwestern Medical Center", html.Br(), 
                                                "UTSYS: The University of Texas Systems"]),
						                 className='tooltiptext')
					    ], className='tooltip'),
			    dcc.Checklist(
                        id="all-or-none-inst",
                        options=[{"label": "Select All", "value": "All"}],
                        value=[],
                        className='select-all'
                    ),
	            dcc.Checklist(
                    id='select_institutions_checklist',
                    options=[
                        {'label': 'UTAus', 'value': 'UTAus'},
                        {'label': 'UTA', 'value': 'UTA'},
                        {'label': 'UTD', 'value': 'UTD'},
                        {'label': 'UTEP', 'value': 'UTEP'},
			            {'label': 'UTPB', 'value': 'UTPB'},
				        {'label': 'UTRGV', 'value': 'UTRGV'},
                        {'label': 'UTSA', 'value': 'UTSA'},
			            {'label': 'UTT', 'value': 'UTT'},
                        {'label': 'UTHSC-H', 'value': 'UTHSC-H'},
                        {'label': 'UTHSC-SA', 'value': 'UTHSC-SA'},
                        {'label': 'UTMB', 'value': 'UTMB'},
                        {'label': 'UTMDA', 'value': 'UTMDA'},
                        {'label': 'UTSW', 'value': 'UTSW'}, 
                        {'label': 'UTSYS', 'value': 'UTSYS'}
                    ],
                    value=['UTA', 'UTHSC-SA', 'UTSW', 'UTHSC-H', 'UTMDA', 'UTRGV', 'UTMB', 'UTD', 'UTSA', 'UTEP', 'UTT', 'UTSYS', 'UTPB'],
                    persistence=True,
                    persistence_type='session'
                ),], className='single_line_checklist'),
            ], id='select_institutions_div', className='filter_div'),

            html.Div([
                "By machine:",
                html.Div([
                dcc.Checklist(
                        id="all-or-none-machine",
                        options=[{"label": "Select All", "value": "All"}],
                        value=["All"],
                        className='select-all'
                    ),
                dcc.Checklist(
                    id='select_machine_checklist',
                    options=[
                        {'label': 'Lonestar6', 'value': 'Lonestar6'},
                        {'label': 'Frontera', 'value': 'Frontera'},
                        {'label': 'Longhorn3', 'value': 'Longhorn3'},
                        {'label': 'Stampede4', 'value': 'Stampede4'},
			            {'label': 'Lonestar5', 'value': 'Lonestar5'},
				        {'label': 'Maverick3', 'value': 'Maverick3'},
                        {'label': 'Jetstream', 'value': 'Jetstream'},
			            {'label': 'Hikari', 'value': 'Hikari'}
                    ],
                    value=['Lonestar6', 'Frontera', 'Longhorn3', 'Stampede4', 'Lonestar5', 'Maverick3', 'Jetstream', 'Hikari'],
                    persistence=True,
                    persistence_type='session'
                ),], className='single_line_checklist'),
            ], id='select_machine_div', className='filter_div'),
	    
            html.Div([
                "By fiscal year:",
                dcc.RadioItems(id='year_radio_dcc',
			       			   options=FY_OPTIONS,
							   value='21-22',
							   inline=True,
							   persistence=True,
                    		   persistence_type='session')], id='year_radio_box', className='filter_div'),

            html.Div([
                "By month:",
                dcc.RangeSlider(id='date_filter', 
                                value=[0, 12],
                                step=None, 
                                marks={0: '21-09',
                                       1: '21-10',
                                       2: '21-11',
                                       3: '21-12',
                                       4: '22-01',
                                       5: '22-02',
                                       6: '22-03',
                                       7: '22-04',
                                       8: '22-05',
                                       9: '22-06',
                                       10: '22-07',
                                       11: '22-08'}, 
                                min=0, 
                                max=11,
								persistence=True,
                    			persistence_type='session')
            ], id='date_range_selector', className='filter_div'),], id='filters', style={'display':''}),
	dash.page_container], className='body')
])

for page in dash.page_registry.values():
	logging.debug((f"{page['name']} - {page['path']}"))

@app.callback(
    Output('filters', 'style'),
    Input('toggle-filters', 'n_clicks'),
    State('filters', 'style'), prevent_initial_call=True
)
def toggle_filters(click, state):
    if state == {'display':'none'}:
        return {'display':''}
    else:
        return {'display':'none'}

@app.callback(
    Output("select_institutions_checklist", "value"),
    [Input("all-or-none-inst", "value")],
    [State("select_institutions_checklist", "options")], prevent_initial_call=True,
)
def select_all_none(all_selected, options):
    all_or_none = []
    all_or_none = [option["value"] for option in options if all_selected]
    return all_or_none

@app.callback(
    Output("select_machine_checklist", "value"),
    [Input("all-or-none-machine", "value")],
    [State("select_machine_checklist", "options")], prevent_initial_call=True,
)
def select_all_none(all_selected, options):
    all_or_none = []
    all_or_none = [option["value"] for option in options if all_selected]
    return all_or_none


@app.callback(
	Output('date_range_selector', 'children'),
	Input('date_filter', 'value'),
	Input('year_radio_dcc', 'value')
)
def update_date_range(date_range, fiscal_year):
	logging.debug(f'Callback trigger id: {ctx.triggered_id}')
	marks = get_marks(fiscal_year)
	if ctx.triggered_id == 'year_radio_dcc':
		logging.debug(f'Marks = {marks}')
		slider_children = ["By month:",
                       dcc.RangeSlider(id='date_filter', value=[0, len(marks)],
                                       step=None, marks=marks, min=0, max=len(marks)-1)]
	else:
		logging.debug(f'Marks = {marks}')
		logging.debug(f'date_range = {date_range}')
		slider_children = ["By month:",
                       dcc.RangeSlider(id='date_filter', value=date_range,
                                       step=None, marks=marks, min=0, max=len(marks)-1)]
	return slider_children

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8051, debug=settings['DEBUG_MODE'])