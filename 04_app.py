"""
# ======================================================================
# Imports
# ======================================================================
"""
import os
import sys
import pandas               as pd
import numpy                as np

import dash_table
import dash
import dash_core_components as dcc
import dash_html_components as html
from   dash.dependencies    import Input, Output

"""
# ======================================================================
# Imports & Accelerators
# ======================================================================
"""
TOP = r"C:/Users/vishk/Desktop/WIP/2020/2020 Q1/07 - Self Learning"
sys.path.append(f"{TOP}/lib")
os.environ["TOP"] = TOP
from bootstrap import *

"""
# ======================================================================
# Get data
# ======================================================================
"""
min_date  = '2020-03-01'

mysql_con, sql_svr_con = get_con(cfg['mysql'], cfg['sql_svr'])

con        = sql_svr_con
sql        = f"select * from covid19_us_mds"
df         = get_df_from_sql(sql, con)
df['date'] = df['date'].astype('datetime64[ns]')
df         = df[df['date'] >= min_date]

rcnt_dt    = df['date'].max().date()
states     = df['state'].unique()
towns      = df['town'].unique()

df_rcnt    = df[df['date'] == rcnt_dt]

"""
# ======================================================================
# Definitions
# ======================================================================
"""
tab_dict = {
  'tab_smry': f"Summary",
  'tab_0':    f"US 'High Risk'",
  'tab_1':    f"State 'High Risk'",
  'tab_2':    f"Over time trends",
  'tab_3':    f"Data",
}

dim_desc = [
  'State ',
  'Town ',
  'Date '
]

dim_cols = [
  'state',
  'town',
  'date',
]

measure_cols = [
  'population',
  'incidence',
  'incidence_inc',
  'incidence_inc_pct',
  'incidence_rate_pct',
  'deaths',
  'death_rate_pct'
]

measure_desc = [
  'Population ',
  'Incidence (Counts) ',
  'Incidence increase over previous day ',
  'Pct. Incidence increase over previous day ',
  'Incidence rate pct (Incid/Pop) ',
  'Deaths (Counts) ',
  'Death Rate Pct (Deaths/Incid) '
]

us_measure_cols = [
  'population',
  'incidence',
  'incidence_inc',
  'deaths',
]

state_measure_cols = [
  'population',
  'incidence',
  'incidence_inc',
  'deaths',
]

dim_dict          = dict(zip(dim_cols, dim_desc))
measures_dict     = dict(zip(measure_cols, measure_desc))
town_measure_cols = measure_cols
cols              = dim_cols + measure_cols

"""
# ======================================================================
# Set defaults
# ======================================================================
"""
def_metric        = 'incidence'
def_ver           = 'state'
def_state         = 'Massachusetts'
def_town          = 'Middlesex, Massachusetts, US'

state             = def_state
town              = def_town
us_metric         = def_metric
us_metric_ver     = def_ver
state_metric      = def_metric
town_metric       = def_metric
town_metric_ver   = def_ver

"""
# ======================================================================
# Convert to css. Styling of html div sections
# ======================================================================
"""
sel_left = {
  'width':            '64%',
  'display':          'inline-block',
  'vertical-align':   'top',
  'padding':          '5px',
  'overflow-x':       'scroll',
  'overflow-y':       'scroll',
  'height':           '650px',
  'font':             'Century Gothic',
}

sel_right = {
  'width':            '34%',
  'display':          'inline-block',
  'vertical-align':   'top',
  'padding':          '5px',
  'background-color': 'rgba(234,234,234)',
  'overflow-x':       'scroll',
  'overflow-y':       'scroll',
  'height':           '650px',
  'font':             'Century Gothic',
}

"""
# ======================================================================
# Define tabs - summary
# ======================================================================
"""
def get_smry_tab():
  tab   = 'tab_smry'
  label = tab_dict[tab]
  tab_smry = dcc.Tab(
      label = label,
      value = tab,
      children = [
        dcc.Markdown(f"""
        # US COVID 19 Tracker (as of {rcnt_dt})
        ---
        >  | Metric | Value |
        >  | ------ | ------|
        >  | States analyzed: | **{len(states)}** |
        >  | Towns analyzed:  | **{len(towns):,.0f}**  |
        >  | Incidents:       | **{df_rcnt['incidence'].sum():,.0f}**  |
        >  | Incidents increase from prev day: | **{df_rcnt['incidence_inc'].sum():,.0f}**  |
        >  | Deaths:          | **{df_rcnt['deaths'].sum():,.0f}**  |
        ---
        """
        )
      ]
    )
  return tab_smry

"""
# ======================================================================
# Define tabs - US
# ======================================================================
"""
def get_us_tab():
  tab    = 'tab_0'
  label  = tab_dict[tab]
  rb_id  = 'us_metric_rb'
  rb2_id = 'us_metric_ver_rb'
  fig_id = f"{tab}_fig"
  
  tab_0 = dcc.Tab(
    label = label,
    value = tab,
    children = [
      html.Div([
        dcc.Graph(
          id     = fig_id,
          figure = upd_us_fig(us_metric, us_metric_ver)
        )
      ], style = sel_left,
      ),
      html.Div(
        children = [
          dcc.Markdown(f"""
          ---
          ####  Select Metric
          """),
          dcc.RadioItems(
            id      = rb_id,
            options = [{'label': measures_dict[i], 'value': i} for i in us_measure_cols],
            value   = us_measure_cols[0]
          ),
          dcc.Markdown(f"""
          ---
          ####  Select View
          """),
          dcc.RadioItems(
            id      = rb2_id,
            options = [{'label': dim_dict[i], 'value': i} for i in ['state','town']],
            value   = 'state'
          ),      
          dcc.Markdown(f"""
          ---
          """),
        ], style = sel_right,
      )
    ]
  )
  
  return tab_0

"""
# ======================================================================
# Define tabs - State
# ======================================================================
"""
def get_state_tab():
  tab    = 'tab_1'
  label  = tab_dict[tab]
  dd_id  = 'state_metric_dd'
  rb_id  = 'state_metric_rb'
  fig_id = f"{tab}_fig"

  tab_1 = dcc.Tab(
    label = label,
    value = tab,
    children = [
      html.Div(
        children = [
        dcc.Graph(
          id     = fig_id,
          figure = upd_state_fig(state, state_metric)
        )
        ], style = sel_left,
      ),
      html.Div(
        children = [
          dcc.Markdown(f"""
          ---
          ####  Select State
          """),
          dcc.Dropdown(
            id      = dd_id,
            options = [{'label': i, 'value': i} for i in states],
            value   = states[0]
          ),
          dcc.Markdown(f"""
          ---
          ####  Select Metric
          """),
          dcc.RadioItems(
            id      = rb_id,
            options = [{'label': measures_dict[i], 'value': i} for i in state_measure_cols],
            value   = state_measure_cols[0]
          ),
          dcc.Markdown(f"""
          ---
          """),
        ], style = sel_right,
        )
    ]
  )
      
  return tab_1

"""
# ======================================================================
# Define tabs - County
# ======================================================================
"""
def get_county_tab():
  tab    = 'tab_2'
  label  = tab_dict[tab]
  dd_id  = 'town_metric_dd'
  rb_id  = 'town_metric_rb'
  rb2_id = 'town_metric_ver_rb'
  fig_id = f"{tab}_fig"

  tab_2 = dcc.Tab(
    label = label,
    value = tab,
    children = [
      html.Div(
        children = [
          dcc.Graph(
            id     = fig_id,
            figure = upd_town_fig(state, town, town_metric, 'state')
          )
        ], style = sel_left,
      ),
      html.Div(
        children = [
          dcc.Markdown(f"""
          ---
          ####  Select County/Town
          """),
          dcc.Dropdown(
            id      = dd_id,
            options = [{'label': i, 'value': i} for i in towns],
            value   = towns[0]
          ),
          dcc.Markdown(f"""
          ---
          ####  Select Metric
          """),
          dcc.RadioItems(
            id      = rb_id,
            options = [{'label': measures_dict[i], 'value': i} for i in town_measure_cols],
            value   = town_measure_cols[0]
          ),
          dcc.Markdown(f"""
          ---
          ####  Select View
          """),
          dcc.RadioItems(
            id      = rb2_id,
            options = [{'label': dim_dict[i], 'value': i} for i in ['state','town']],
            value   = 'state'
          ),
          dcc.Markdown(f"""
          ---
          """),
        ], style = sel_right,
    )]
  )
  return tab_2  

"""
# ======================================================================
# Define tabs - Data tab
# ======================================================================
"""
def get_data_tab():
  tab        = 'tab_3'
  label      = tab_dict[tab]
  st_dd_id   = 'data_state_metric_dd'
  twn_dd_id  = 'data_town_metric_dd'
  tab_3 = dcc.Tab(
    label = label,
    value = tab,
    children = [
      html.Div(
        children = [
          dash_table.DataTable(
            id='dat_tab',
            columns = [
                {'name': i, "id": i} for i in (df_rcnt.columns)
            ],
            page_current      = 0,
            page_size         = 10,
            page_action       = 'custom',
            style_data_conditional=[{
                'if':{'row_index':'odd'},
                'backgroundColor': 'rgb(248,248,248)'
            }]
          )
        ], style = sel_left,
      ),
      html.Div(
        children = [
          dcc.Markdown(f"""
          ---
          ####  Select State
          """),
          dcc.Dropdown(
            id      = st_dd_id,
            options = [{'label': i, 'value': i} for i in states],
            value   = state[0]
          ),
          dcc.Markdown(f"""
          ---
          ####  Select Town
          """),
          dcc.Dropdown(
            id      = twn_dd_id,
            options = [{'label': i, 'value': i} for i in towns],
            value   = towns[0]
          ),
          dcc.Markdown(f"""
          ---
          """),
        ], style = sel_right,
      )        
    ]
  )
  return tab_3

"""
# ======================================================================
# Prep main layout
# ======================================================================
"""
def get_tabs():
  tabs = []

  tabs.append(get_smry_tab())
  tabs.append(get_us_tab())
  tabs.append(get_state_tab())
  tabs.append(get_county_tab())
  tabs.append(get_data_tab())

  return tabs

"""
# ======================================================================
# Component update functions - get top values
# ======================================================================
"""
def get_top_fig(x_top, y_top, x_title, y_title):
  """get_top_fig - Get a horizontal bar chart representing
     the top values by a given measure on a given date

  x_top:   x_axis values
  y_top:   y_axis values
  x_title: title of x_axis
  y_title: title of y_axis
  """
  
  # ====================================================================
  # Adjust anotations
  # Invest some more time in auto adjustment of formattt based on c
  # and based on data
  # ====================================================================
  annotations = []
  x_top = x_top.values
  y_top = y_top.values
  for x, y in zip(x_top, y_top):
    annotations.append(dict(
        x         = x,
        y         = y,
        text      = f"{x}",
        showarrow = False
    ))

  # ====================================================================
  # Boiler plate configuration for horizontal bar charts
  # ====================================================================
  fig = {
    'data': [
      {
        'x':           x_top,
        'y':           y_top,
        'type':        'bar',
        'orientation': 'h',
      },
    ],
    'layout': {
      'paper_bgcolor': "LightSteelBlue",
      'bgcolor':       'White',
      'height':        600,
      'margin':        {'l': 200, 'b': 70, 'r': 10, 't': 5},
      'xaxis':         {'title': f"{x_title}"},
      'yaxis':         {'tickformat':',.0f'},
      'font':          {'family':'Century Gothic', 'size':'14', 'color':'black'},
      'annotations':   annotations,
    }
  }
  return fig

"""
# ======================================================================
# Component update functions - get trend chart
# ======================================================================
"""
def get_trend(x, y, x_title, y_title):
  """get_trend - Get a line chart
  x:       x_axis values
  y:       y_axis values
  x_title: title of x_axis
  y_title: title of y_axis
  """
  # ====================================================================
  # Boiler plate configuration for line charts
  # ====================================================================
  fig = {
    'data': [ dict(
      x =    x,
      y =    y,
      mode = 'lines+markers',
      name = y_title,
    ) ],
    'layout': {
      'paper_bgcolor': "LightSteelBlue",
      'bgcolor':       'White',
      'height':        600,
      'margin':        {'l': 75, 'b': 70, 'r': 10, 't': 5},
      'xaxis':         {'title': f"{x_title}"},
      'yaxis':         {'tickformat':',.1f'},
      'font':          {'family':'Century Gothic', 'size':'14', 'color':'black'},
      'clickmode':     'event+select',
      'hovermode':     'x unified',
      'hoverlabel':    {'bgcolor':'lightgray', 'font_size':'14'},
      'showlegend':    True,
      'legend_orientation': 'h',
      'legend':        dict(x=0, y=1.1),
      'traceorder':    'normal',
    }
  }
  return fig

"""
# ======================================================================
# Helper function - get relevant data
# ======================================================================
"""
def get_rlvt_data(
  df,
  viz_type,
  metric,
  metric_ver = 'town',
  filter_val = 'none'
):
  """get_rlvt_data - get relevant data
  df:          input data frame
  metric_type: top (towns) or all towns or all data points
  metric:      the metric value
  filter_col:  the column to filter on
  filter_val:  the value to filter on
  """
  num_top_points = 20
  
  def summarize_df(df, metric, group_by):
    avg_metrics = [ 'incidence_inc_pct',  'incidence_rate_pct', 'death_rate_pct' ]
    sum_metrics = [ 'population', 'incidence', 'incidence_inc', 'deaths' ] 
    
    if (metric in avg_metrics):
      df_out = df.groupby(group_by)[metric].agg('mean')
    elif (metric in sum_metrics):
      df_out = df.groupby(group_by)[metric].sum()
      
    df_out = pd.DataFrame(df_out)
    df_out = df_out.reset_index()
    
    return df_out
  
  df_out    = df[dim_cols + [metric]]
  curr_date = df_out['date'].max()

  if (viz_type in [ 'us'] ):
    df_out    = df_out[df_out['date'] == curr_date]
    if (metric_ver == 'state'):
      df_out = summarize_df(df_out, metric, metric_ver)
  elif (viz_type == 'state'):
    df_out = df_out[df_out['date'] == curr_date]
    df_out = df_out[df_out['state'] == filter_val]
  elif (viz_type == 'town'):
    df_out = df_out[df_out['state'] == filter_val]
    if (metric_ver == 'state'):
      df_out = summarize_df(df_out, metric, ['date', metric_ver])

  if (viz_type in [ 'us', 'state' ]):
    # get top 20 by metric
    df_out.sort_values(by=[metric], inplace=True, ascending=False)
    df_out = df_out.head(num_top_points)
    
    # Re-sort for display
    df_out.sort_values(by=[metric], inplace=True)
  
  return df_out, curr_date.date()

"""
# ======================================================================
# Helper function - cap_it -> cap the value especially if it is a percentage
# Make this function more sophisticated
# ======================================================================
"""
def cap_it(y, cap_val):
  """cap_it - cap the value to something more meaningful - for analysis onnly
  for now, if the abs(y) is less than cap_val, then use y, else use capped
  value
  """
  if (y >= cap_val): return cap_val
  if (y <= -cap_val): return -cap_val
  else: return y

"""
# ======================================================================
# Helper function - upd_us_fig
# Make the title more contextual based on the metric
# ======================================================================
"""
def upd_us_fig(
  us_metric,
  us_metric_ver
):
  """upd_fig - Update a given chart
  metric: The metric to update
  """
  df_us, curr_date = get_rlvt_data(
      df, 'us', 
      us_metric, us_metric_ver)

  x_top   = df_us[us_metric]
  y_top   = df_us[us_metric_ver]
  x_title = f"Cumulative {us_metric.upper()} as of {curr_date}"
  y_title = f""
  fig = get_top_fig(x_top, y_top, x_title, y_title)

  return fig

"""
# ======================================================================
# Helper function - upd_state_fig
# Make the title more contextual based on the metric
# ======================================================================
"""
def upd_state_fig(
  state,
  state_metric
):
  """upd_fig - Update a given chart
  state:        The town to update
  state_metric: The metric to update
  """
  df_state, curr_date = get_rlvt_data(
      df, 'state', 
      state_metric, 'state', state)

  x_top   = df_state[state_metric]
  y_top   = df_state['town']
  x_title = f"Cumulative {state_metric.upper()} as of {curr_date}"
  y_title = f""
  fig = get_top_fig(x_top, y_top, x_title, y_title)

  return fig

"""
# ======================================================================
# Helper function - upd_town_fig
# Make the title more contextual based on the metric
# Do not filter on any dates - this is the most granular metric
# ======================================================================
"""
def upd_town_fig(
  state,
  town,
  town_metric,
  town_metric_ver
):
  """upd_town_fig - Update a given chart
  state:  The state to which the town belongs
  town:   The town to update
  metric: The metric to update
  """
  df_town, curr_date  = get_rlvt_data(
      df, 'town', town_metric, 
      town_metric_ver, state)

  if (town_metric_ver == 'town'):
    df_town = df_town[df_town['town'] == town]

  x       = df_town['date']
  y       = df_town[town_metric]
  x_title = f"Date"
  if (town_metric_ver == 'state'):
    y_title = f"{town_metric.upper()} in {state}"
  else:
    y_title = f"{town_metric.upper()} in {town}"
    
  fig     = get_trend(x, y, x_title, y_title)

  return fig

"""
# ======================================================================
# Define app
# ======================================================================
"""
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True
app.layout = html.Div([
    dcc.Tabs(id='tabs', value = 'tab_smry',
        children=get_tabs()
      )
  ], style={'width': '95%'}
)

"""
# ======================================================================
# US fig call back
# ======================================================================
"""
@app.callback(
  Output('tab_0_fig', 'figure'),
  [
    Input('us_metric_rb',     'value'),
    Input('us_metric_ver_rb', 'value'),
  ]
)
def upd_us_fig_cb(
  us_metric,
  us_metric_ver
):
  comp = upd_us_fig(us_metric, us_metric_ver)
  return comp

"""
# ======================================================================
# State fig call back
# ======================================================================
"""
@app.callback(
  Output('tab_1_fig', 'figure'),
  [
    Input('state_metric_dd', 'value'),
    Input('state_metric_rb', 'value'),
  ]
)
def upd_state_fig_cb(
  state,
  state_metric
):
  comp = upd_state_fig(state, state_metric)

  return comp

"""
# ======================================================================
# County fig call back
# ======================================================================
"""
@app.callback(
  [
     Output('tab_2_fig',      'figure'),
     Output('town_metric_dd', 'options'),
  ],
  [
    Input('state_metric_dd',    'value'),
    Input('town_metric_dd',     'value'),
    Input('town_metric_rb',     'value'),
    Input('town_metric_ver_rb', 'value')
  ]
)
def upd_town_fig_cb(
  state,
  town,
  town_metric,
  town_metric_ver,
):
  comp    =  upd_town_fig(state, town, town_metric, town_metric_ver)
  df_town = df[df['state'] == state]
  towns   = df_town['town'].unique()
  options = [{'label': i, 'value': i} for i in towns]
  
  return comp, options

"""
# ======================================================================
# Data table call back
# ======================================================================
"""
@app.callback(
    Output('dat_tab', 'data'),
    [
        Input('dat_tab', "page_current"),
        Input('dat_tab',  "page_size")
    ]
)
def update_table(page_current, page_size):
  return df_rcnt.iloc[
      page_current*page_size : (page_current+ 1)*page_size
  ].to_dict('records')

"""
# ======================================================================
# Need this to be able to run this from command line
# Use debug = True so the app can auto reload after
# every save - CPU intensive - so turn this off, when ready
# for promotion to production
# ======================================================================
"""
#debug_flag = False
debug_flag = True
if __name__ == '__main__':
  app.run_server(debug=debug_flag)