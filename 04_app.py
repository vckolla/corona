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
  'tab_top': f"Top",
  'tab_trends':  f"Trends",
  'tab_data':    f"Data",
}

dim_desc = [
  'States',
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
  'State',
  'County/Town'
]

views = [
  'us',
  'state',
  'town'
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

def get_yes_no(flag):
  disp_no  = {'display': 'none'}
  disp_yes = {'display': 'block'}
  
  if (flag == 1): ret_val =  disp_yes
  else: ret_val = disp_no

  return ret_val

def get_disp_cntrl(disp_vec):
    v               = disp_vec
    state_dd_style  = get_yes_no(v[0])
    cb_style        = get_yes_no(v[1])
    metric_style    = get_yes_no(v[2])
   
    vw_options = [ {'label': views_dict[i], 'value': i} for i in v[3] ]
    cb_options = [ {'label': i, 'value': i} for i in v[4]]

    return [
      state_dd_style,
      cb_style,
      metric_style,

      vw_options,
      cb_options,
    ]

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
trend_metric      = def_metric
trend_metric_ver  = def_ver

def upd_app(
  tab,
  view,
  state,
  cb_list,
  metric,
):
  vw_opt_val      = views.copy()
  md_txt          = ""
  fig_top         = None
  fig_trends      = None
  group_by_cols   = []
  rcnt_dt         = df['date'].max().date()

  if (cb_list == None):
    cb_list = ['None']

  p_str = f"""
  tab     = {tab}
  view    = {view}
  state   = {state}
  cb_list = {cb_list}
  metric  = {metric}
  """
  p_print(p_str)

  df_all   = df
  df_st    = df[df['state'] == state]
  df_sts   = df[(df['state']).isin(cb_list)]
  df_towns = df[
    (df['state'] == state) &
    (df['town']).isin(cb_list)
  ]

  disp_states = sorted(df_all['state'].unique())
  disp_towns  = sorted(df_st['town'].unique())
  
  df_all_curr   = df_all[df_all['date'] == rcnt_dt]
  df_st_curr    = df_st[df_st['date'] == rcnt_dt]
  df_sts_curr   = df_sts[df_sts['date'] == rcnt_dt]
  df_towns_curr = df_towns[df_towns['date'] == rcnt_dt]

  vw_opt_val = views.copy()
  trend_data = []
  disp_vec   = [0, 0, 0, vw_opt_val, disp_states]

  if (tab == 'tab_smry'):
    if (view == 'us'):
      disp_vec  = [0, 0, 0, vw_opt_val, disp_states]
      df_md, df_md_curr = df_all, df_all_curr

    elif (view == 'state'):
      disp_vec   = [0, 1, 0, vw_opt_val, disp_states]
      df_md, df_md_curr = df_sts, df_sts_curr

    elif (view == 'town'):
      disp_vec   = [1, 1, 0, vw_opt_val, disp_towns]
      df_md, df_md_curr = df_towns, df_towns_curr
    
    md_txt     = get_md(df_md, df_md_curr)
  elif (tab == 'tab_top'):
    vw_opt_val = ['us', 'state']
    viz_type   = 'top'
    df_rlvt    = df_all
    y_col      = 'state'
    
    if (view == 'us'):
      disp_vec  = [0, 0, 1, vw_opt_val, disp_states]
      df_rlvt   = df_all
      y_col     = 'state'

    elif (view == 'state'):
      disp_vec  = [1, 0, 1, vw_opt_val, disp_states]
      df_rlvt   = df_st_curr
      y_col     = 'town'

    df_top      = get_rlvt_data(df_rlvt, viz_type, view, metric, cb_list)
    x_top       = df_top[metric]
    y_top       = df_top[y_col]
    x_title     = f"Cumulative {metric.upper()} as of {rcnt_dt}"
    y_title     = f""
    fig_top    = get_top_fig(x_top, y_top, x_title, y_title)

  elif (tab == 'tab_trends'):
    x_title     = f"Date"
    y_title     = f"{metric.upper()}"
    viz_type    = 'trend'
    mode        = 'lines+markers'
    df_rlvt     = df_all

    if (view == 'us'):
      disp_vec  = [0, 0, 1, vw_opt_val, disp_states]
      df_rlvt   = df_all
      df_trend  = get_rlvt_data(df_rlvt, viz_type, view, metric, cb_list)

      y_title     += ' for US'
      x           = df_trend['date']
      y           = df_trend[metric]
      trend_data.append({'x': x, 'y': y, 'mode': mode, 'name': 'US'})

    elif (view == 'state'):
      disp_vec  = [0, 1, 1, vw_opt_val, disp_states]
      df_rlvt   = df_sts

      y_title += ' for States'
      for s in (cb_list):
        df_trend    = get_rlvt_data(df_rlvt, viz_type, view, metric, cb_list)
        x           = df_trend['date']
        y           = df_trend[df_trend['state'] == s][metric]
        trend_data.append({'x': x, 'y': y, 'mode': mode, 'name': s})

    elif (view == 'town'):
      disp_vec  = [1, 1, 1, vw_opt_val, disp_towns]
      df_rlvt   = df_towns

      y_title += ' for Counties'
      for t in (cb_list):
        df_trend    = get_rlvt_data(df_rlvt, viz_type, view, metric, cb_list)
        print(df_trend)
        x           = df_trend['date']
        y           = df_trend[df_trend['town'] == t][metric]
        trend_data.append({'x': x, 'y': y, 'mode': mode, 'name': t})
    
    fig_trends = get_trend_fig(trend_data, x_title, y_title)

  disp_rslt  = get_disp_cntrl(disp_vec)
  #print(fig_top)
  print(fig_trends)

  return (
    disp_rslt[0],
    disp_rslt[1],
    disp_rslt[2],
    disp_rslt[3],
    disp_rslt[4],  

    md_txt,
    #f"{fig_top}",
    fig_trends,
    #f"{fig_trends}",
  )

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
      'height':        575,
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
def get_trend_fig(
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
# Update summary tab
# ======================================================================
"""
def get_md(df, df_rcnt):
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
        children = get_md(df, df_rcnt)          
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
  tab_name = 'tab_top'
  tab_label = tab_dict[tab_name]
  fig_id = f"{tab_name}_fig"

  (_, _, _, _, _, _, fig_top, _) = \
    upd_app('tab_top','state', def_state, [states[0]], 'population')

  tab = dcc.Tab(
    value = tab_name,
    label = tab_label,
    className="custom-tab",
    selected_className="custom-tab--selected",
    children = [
      #dcc.Graph(
      #  id     = fig_id,
      #  figure = fig_top,
      #)
      dcc.Markdown(
        id = fig_id,
        children = 
          f"""
      {fig_top}
      """)
      
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

  ( _, _, _, _, _, _, fig_trends) = \
    upd_app('tab_trend','state', def_state, [states[0]], 'population')

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
            figure = fig_trends,
          ),
          #dcc.Markdown(
          #  id = fig_id,
          #  children = f"""
          #{fig_trends}
          #""")
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
# summarize_df - summarize data
# ======================================================================
"""
def summarize_df(df, metric, group_by_cols):
  avg_metrics = [ 'incidence_inc_pct',  'incidence_rate_pct', 'death_rate_pct' ]
  sum_metrics = [ 'population', 'incidence', 'incidence_inc', 'deaths' ] 
  
  if (metric in avg_metrics):
    df_out = round(df.groupby(group_by_cols)[metric].agg('mean'),2)
  elif (metric in sum_metrics):
    df_out = round(df.groupby(group_by_cols)[metric].sum(),0)
    
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

  if (viz_type == 'top' ):
    group_by = 'date'
    if (view == 'us'):  group_by = 'state'
    elif (view == 'state'): group_by = 'town'
    df_out = summarize_df(df_out, metric, group_by)
    # get top 20 by metric
    df_out.sort_values(by=[metric], inplace=True, ascending=False)
    df_out = df_out.head(num_top_points)
    
    # Re-sort for display
    df_out.sort_values(by=[metric], inplace=True)

  elif (viz_type == 'trend'):
    group_by = ['date']
  
    if (view == 'state'):
      df_out = df_out[(df_out['state']).isin(cb_list)]
      group_by += ['state']

    elif (view == 'town'):
      df_out = df_out[(df_out['town']).isin(cb_list)]

    df_out = summarize_df(df_out, metric, group_by)
  
  return df_out

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
  #tabs.append(get_distrib_tab())
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
    html.Div(
      id = 'view_comp',
      style = {'display': 'block'},
      children = [
      dcc.Markdown(f"""
      ---
      ####  Select View
      """),
      dcc.RadioItems(
        id         = view_rb_id,
        options    = [{'label': views_dict[i], 'value': i} for i in views],
        value      = view,
        labelStyle = {'display':'in-line block'}
      )]
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

    html.Div(
      id = 'chk_bx_comp',
      style = {'display': 'block'},
      children = [
        dcc.Markdown(f"""
        ---
        ####  Select State / Town
        """),
        dcc.Checklist(
          className   = "chk_bx_style",
          id          = chk_bx_id,
          options     = [{'label': i, 'value': i} for i in display],
          labelStyle  = {'display':'block'},
        )
      ]
    ),

    html.Div(
      id = 'metric_comp',
      style = {'display': 'block'},
      children = [
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
        """)
      ],  
    ), 
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
    Output('chk_bx_comp',     'style'),
    Output('metric_comp',     'style'),

    Output('view_rb_cntrl',   'options'),
    Output('chk_bx_cntrl',    'options'),

    Output('tab_smry_md',     'children'),
    #Output('tab_top_fig',     'figure'),
    #Output('tab_top_fig',     'children'),
    Output('tab_trends_fig',  'figure'),
    #Output('tab_trends_fig',  'children'),
  ],
  [
    Input('tabs',          'value'),
    Input('view_rb_cntrl', 'value'),
    Input('state_cntrl',   'value'),
    Input('chk_bx_cntrl',  'value'),
    Input('metric_cntrl',  'value'),
  ]
)
def upd_app_cb(
  tab,
  view,
  state,
  cb_list,
  metric,
):
  return upd_app(tab, view, state, cb_list, metric)

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
