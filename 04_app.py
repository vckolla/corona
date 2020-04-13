"""
Copyright 2020 me:dha:.ai.

Permission is hereby granted, free of charge, to any person obtaining a 
copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation 
the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the 
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included 
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 

IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY 
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

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
from IPython.core.display import display

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
#df         = pd.read_csv("covid19_us_2020_04_07.csv")
df['date'] = df['date'].astype('datetime64[ns]')
df         = df[df['date'] >= min_date]

rcnt_dt    = df['date'].max().date()
states     = sorted(df['state'].unique())
towns      = sorted(df['town'].unique())

df_rcnt    = df[df['date'] == rcnt_dt]

"""
# ======================================================================
# Definitions
# ======================================================================
"""
tab_dict = {
  'tab_smry':    f"Summary",
  'tab_distrib': f"Top",
  'tab_trends':  f"Trends",
  'tab_data':    f"Data",
}

dim_desc = [
  'State',
  'County/Town',
  'Date'
]

dim_cols = [
  'state',
  'town',
  'date',
]

view_desc = [
  'US',
  'State'
]

views = [
  'us',
  'state'
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
views_dict        = dict(zip(views, view_desc))

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
trend_metric       = def_metric
trend_metric_ver   = def_ver

"""
# ======================================================================
# Update summary tab
# ======================================================================
"""
def upd_md(df, df_rcnt):
  min_date   = df['date'].min().date()
  max_date   = df['date'].max().date()
  days       = len(df['date'].unique())
  num_states = len(df['state'].unique())
  states     = sorted(df['state'].unique())
  towns      = sorted(df['town'].unique())
  num_towns  = len(df['town'].unique())
  population = df_rcnt['population'].sum()
  cum_incids = df_rcnt['incidence'].sum()
  incid_rate = (cum_incids * 100) / population
  incid_inc  = df_rcnt['incidence_inc'].sum()
  cum_deaths = df_rcnt['deaths'].sum()
  death_rate = (cum_deaths * 100) / cum_incids

  md_txt = f"""
  ---

  # US COVID 19 Tracker (as of {rcnt_dt})

  ---

  ## Data Summary


  |Metric|     |Value|
  |---:| :-: | :-: |
  | | | |
  | *From Date:*          || **{min_date}** |
  | *To Date:*            || **{max_date}** |
  | *Days:*                             || **{days}** |
  | *# States (1):*    || **{num_states}** |
  | *# Counties (2):*  || **{num_towns:,.0f}**  |
  | *Population:*  || **{population:,.0f}**  |
  | *Cumulative Incidents:*          || **{cum_incids:,.0f}**  |
  | *Incidents rate (pct):*          || **{incid_rate:,.2f}**  |
  | *Incidents increase (from prior day):* || **{incid_inc:,.0f}**  |
  | *Cumulative Deaths:*             || **{cum_deaths:,.0f}**  |
  | *Death rate (pct):*          || **{death_rate:,.2f}**  |

  ---
  
  Source: ***[Corona John Hopkins University Git Repo] (https://github.com/CSSEGISandData/COVID-19) ***
  
  ---
  
  Built on: ***[Python Dash framework] (https://plotly.com/dash/)***

  ***(c) 2020 me:dha:.ai***

  ---
  """  
  return md_txt

"""
# ======================================================================
# Define tabs - summary
# ======================================================================
"""
def get_smry_tab():
  tab_name = 'tab_smry'
  tab_label = tab_dict[tab_name]
  md_id = f"{tab_name}_md"
  tab = dcc.Tab(
    value = tab_name,
    label = tab_label,
    className = "custom-tab",
    selected_className = "custom-tab--selected",
    children = [
      dcc.Markdown(
        id = f"{md_id}",
        children = upd_md(df, df_rcnt)          
      )
    ]
  )
  return tab

"""
# ======================================================================
# Define tabs - Distributions
# ======================================================================
"""
def get_distrib_tab():
  tab_name = 'tab_distrib'
  tab_label = tab_dict[tab_name]
  fig_id = f"{tab_name}_fig"
  
  tab = dcc.Tab(
    value = tab_name,
    label = tab_label,
    className="custom-tab",
    selected_className="custom-tab--selected",
    children = [
      dcc.Graph(
        id     = fig_id,
        #figure = upd_top_fig(us_metric, us_metric_ver)
      )
    ]
  )
  
  return tab

"""
# ======================================================================
# Define tabs - Trends
# ======================================================================
"""
def get_trends_tab():
  tab_name = 'tab_trends'
  tab_label = tab_dict[tab_name]
  fig_id = f"{tab_name}_fig"

  tab = dcc.Tab (
    value = tab_name,
    label = tab_label,
    className="custom-tab",
    selected_className="custom-tab--selected",
    children = [
      html.Div(
        children = [
          dcc.Graph(
            id     = fig_id,
            #figure = upd_trend_fig('us', state, town, trend_metric)
          )
        ],
      ),
    ]
  )
  return tab

"""
# ======================================================================
# Define tabs - Data tab
# ======================================================================
"""
def get_data_tab():
  tab_name = 'tab_data'
  tab_label = tab_dict[tab_name]
  tab = dcc.Tab(
    value = tab_name,
    label = tab_label,
    className = "custom-tab",
    selected_className = "custom-tab--selected",
    children = [
      dash_table.DataTable(
        id      = 'dat_tab',
        columns = [
            {'name': i, "id": i} for i in (df_rcnt.columns)
        ],
        page_current      = 0,
        page_size         = 15,
        page_action       = 'custom',
        style_data_conditional=[{
            'if':{'row_index':'odd'},
            'backgroundColor': 'rgb(248,248,248)'
        }],
        style_cell = {'fontSize':14, 'font-family':'Century Gothic'},
        style_header={
          'backgroundColor': 'rgb(0, 102, 255)',
          'fontWeight':      'bold',
          'color':       'white',
        },
      )
    ],
  )
  return tab

"""
# ======================================================================
# Component update functions - get top values
# ======================================================================
"""
def get_top_fig(
  x_top, 
  y_top, 
  x_title, 
  y_title
):
  """get_top_fig - Get a horizontal bar chart representing
     the top values by a given measure on a given date

  x_top:   x_axis values
  y_top:   y_axis values
  x_title: title of x_axis
  y_title: title of y_axis
  """
  
  # ====================================================================
  # Adjust anotations
  # Invest some more time in auto adjustment of format based on 
  # metric type and and based on data
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
def get_trend(
  data, 
  x_title, 
  y_title
):
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
    'data': data,
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
      'connectgaps':    False,
    }
  }
  return fig

"""
# ======================================================================
# summarize_df - summarize data
# ======================================================================
"""
def summarize_df(df, metric, group_by_cols):
  avg_metrics = [ 'incidence_inc_pct',  'incidence_rate_pct', 'death_rate_pct' ]
  sum_metrics = [ 'population', 'incidence', 'incidence_inc', 'deaths' ] 
  
  if (metric in avg_metrics):
    df_out = df.groupby(group_by_cols)[metric].agg('mean')
  elif (metric in sum_metrics):
    df_out = df.groupby(group_by_cols)[metric].sum()
    
  df_out = pd.DataFrame(df_out)
  df_out = df_out.reset_index()
  
  return df_out

"""
# ======================================================================
# Helper function - get relevant data
# ======================================================================
"""
def get_rlvt_data(
  df,
  viz_type,
  view,
  metric,
  cb_list = None,
):
  """get_rlvt_data - get relevant data
  df:          input data frame
  metric_type: top (towns) or all towns or all data points
  metric:      the metric value
  filter_val:  the value to filter on
  """
  num_top_points = 20
  
  df_out    = df[ dim_cols + [metric] ]
  curr_date = df_out['date'].max()

  if (viz_type == 'us' ):
    df_out = df_out[df_out['date'] == curr_date]
    
    if (view == 'state'):  group_by = 'state'
    elif (view == 'town'): group_by = 'town'
    df_out = summarize_df(df_out, metric, group_by)
      
  elif (viz_type == 'state'):
    df_out = df_out[df_out['date'] == curr_date]
    df_out = df_out[df_out['state'] == cb_list]
    
  elif (viz_type == 'trend'):
    group_by = ['date']
  
    if (view == 'us'):
      df_out = df_out[(df_out['state']).isin(cb_list)]
      group_by += ['state']

    elif (view == 'state'):
      df_out = df_out[(df_out['town']).isin(cb_list)]

    df_out = summarize_df(df_out, metric, group_by)

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
  return None

"""
# ======================================================================
# Prep main layout
# ======================================================================
"""
def get_tabs():
  tabs = []

  tabs.append(get_smry_tab())
  tabs.append(get_distrib_tab())
  tabs.append(get_trends_tab())
  #tabs.append(get_data_tab())

  tabs_content = [
    dcc.Tabs(
      id    = 'tabs',
      value = 'tab_smry',
      parent_className='custom-tabs',
        children=tabs
    )
  ]      

  return tabs_content

def get_controls():
  view        = 'us'
  display     = states
  view_rb_id  = 'view_rb_cntrl'
  state_dd_id = 'state_cntrl'
  chk_bx_id   = 'chk_bx_cntrl'
  metric_id   = 'metric_cntrl'

  controls = [
    dcc.Markdown(f"""
    ---
    ####  Select View
    """),
    dcc.RadioItems(
      id         = view_rb_id,
      options    = [{'label': views_dict[i], 'value': i} for i in views],
      value      = view,
      labelStyle = {'display':'in-line block'}
    ),
    
    html.Div(
      id = 'state_dd_comp',
      style = {'display': 'block'},
      children = [
        dcc.Markdown(f"""
        ---
        ####  Select State
        """),
        dcc.Dropdown(
          id      = state_dd_id,
          options = [{'label': i, 'value': i} for i in states],
          value   = states[0]
        ),
      ], 
    ),

    dcc.Markdown(f"""
    ---
    ####  Select State / Town
    """),
    dcc.Checklist(
      className   = "chk_bx_style",
      id          = chk_bx_id,
      options     = [{'label': i, 'value': i} for i in display],
      labelStyle  = {'display':'block'},
    ),

    dcc.Markdown(f"""
    ---
    ####  Select Metric
    """),
    dcc.RadioItems(
      id          = metric_id,
      options     = [{'label': measures_dict[i], 'value': i} for i in town_measure_cols],
      value       = town_measure_cols[0],
      labelStyle  = {'display':'block'}
    ),
    dcc.Markdown(f"""
    ---
    """),  
  ]
  return controls

"""
# ======================================================================
# Define app
# ======================================================================
"""
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True
app.layout = html.Div(
  children = [
    html.Div(
      className = "app_left",
      children  = get_tabs()
    ),

    html.Div(
      className = "app_right",
      children  = get_controls()
    )
  ]
)

"""
# ======================================================================
# View
# ======================================================================
"""
@app.callback(
  [
    Output('state_dd_comp',   'style'),
    Output('chk_bx_cntrl',    'options'),
    Output('tab_smry_md',     'children'),
    Output('tab_distrib_fig', 'figure'),
    Output('tab_trends_fig',  'figure'),
  ],
  [
    Input('view_rb_cntrl', 'value'),
    Input('state_cntrl',   'value'),
    Input('chk_bx_cntrl',  'value'),
    Input('metric_cntrl',  'value'),
  ]
)
def upd_app_cb(
  view,
  state,
  cb_list,
  metric,
):
  if (cb_list == None):
    cb_list = ['None']

  p_str = f"""
  view    = {view}
  state   = {state}
  cb_list = {cb_list}
  metric  = {metric}
  """
  #p_print(p_str)

  display       = states
  style         = {'display': 'none'}
  group_by_cols = []

  if (view == 'us'):
    pass
  elif (view == 'state'):
    display = sorted(df[df['state'] == state]['town'].unique())
    style = {'display': 'block'}

  #display = ['All', 'None'] + display
  options = [ {'label': i, 'value': i} for i in display ]

  df_st   = df[(df['state']).isin(cb_list)]
  df_cnty = df[
    (df['town']).isin(cb_list) & 
    (df['state'] == state)
    ]
  df_st_curr   = df_st[df_st['date'] == rcnt_dt]
  df_cnty_curr = df_cnty[df_cnty['date'] == rcnt_dt]
  
  if (view == 'us'): md_txt = upd_md(df_st, df_st_curr)
  elif (view == 'state'): md_txt = upd_md(df_cnty, df_cnty_curr)

  return style, options, md_txt, None, None

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
