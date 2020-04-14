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
import plotly.express       as px

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
  'tab_top':     f"Top",
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

view_cuts = [
  'state',
  'town',
  ''
]

view_color_col = [
  '',
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
views_color       = dict(zip(views, view_color_col))
view_cuts         = dict(zip(views, view_cuts))
states_dict       = dict(zip(states, states))

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
trend_metric      = def_metric
trend_metric_ver  = def_ver

"""
# ======================================================================
# Get content for summary tab
# ======================================================================
"""
def get_md(df, df_rcnt):
  #print(len(df), len(df_rcnt))
  if (len(df) == 0 or len(df_rcnt) == 0):
    min_date   = 'NA'
    max_date   = 'NA'
    days       = 0
    num_states = 0
    states     = 0
    towns      = 0
    num_towns  = 0
    population = 0
    cum_incids = 0
    incid_rate = 0
    incid_inc  = 0
    cum_deaths = 0
    death_rate = 0
  else:    
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
  |---:  | :-: | :-: |
  |      |     |     |
  | *From Date:*              || **{min_date}**         |
  | *To Date:*                || **{max_date}**         |
  | *Days:*                   || **{days}**             |
  | *# States (1):*           || **{num_states}**       |
  | *# Counties (2):*         || **{num_towns:,.0f}**   |
  | *Population:*             || **{population:,.0f}**  |
  | *Cumulative Incidents:*   || **{cum_incids:,.0f}**  |
  | *Incidents rate (pct):*   || **{incid_rate:,.2f}**  |
  | *Incidents increase (from prior day):* || **{incid_inc:,.0f}**  |
  | *Cumulative Deaths:*      || **{cum_deaths:,.0f}**  |
  | *Death rate (pct):*       || **{death_rate:,.2f}**  |

  ---
  
  Source: ***[Corona John Hopkins University Git Repo] (https://github.com/CSSEGISandData/COVID-19) ***
  
  ---
  
  Built on: ***[Python Dash framework] (https://plotly.com/dash/)***

  ***(c) 2020 me:dha:.ai***

  ---
  """
  #print(md_txt)  
  return md_txt

"""
# ======================================================================
# Get tab contents
# ======================================================================
"""
def get_tab_contents(
  tab,
  view,
  state,
  cb_list,
  metric,
):
  # =======================================================================
  # Defaults
  # =======================================================================
  if (cb_list == None): cb_list = ['None']
  if (metric == None):  metric = 'incidence'
  
  p_str = f"""
  get_tab_contents
  ---------------
  tab     = {tab}
  view    = {view}
  state   = {state}
  cb_list = {cb_list}
  metric  = {metric}
  """
  p_print(p_str)
  
  # =======================================================================
  # Data
  # =======================================================================
  df_all   = df
  df_st    = df[df['state'] == state]
  df_sts   = df[(df['state']).isin(cb_list)]
  df_towns = df[
    (df['state'] == state) &
    (df['town']).isin(cb_list)
  ]

  # =======================================================================
  # Initializations
  # =======================================================================
  md_txt, top_fig, trend_fig = "", None, None

  if (view == 'us'):      df_rlvt   = df_all
  elif (view == 'state'): df_rlvt   = df_sts
  elif (view == 'town'):  df_rlvt   = df_towns

  df_rlvt_curr = df_rlvt[df_rlvt['date'] == rcnt_dt]

  # =======================================================================
  # Summary tab
  # =======================================================================
  if (tab == 'tab_smry'):
    md_txt = get_md(df_rlvt, df_rlvt_curr)

  # =======================================================================
  # Top values
  # =======================================================================
  elif (tab == 'tab_top'):
    #print("get_tab_contents - tab_top")
    viz_type = 'top'
    df_plt = get_rlvt_data(df_rlvt_curr, viz_type, view, metric, cb_list)
    top_fig = px.bar(df_plt, orientation = 'h', x= metric, y = view_cuts[view])

  # =======================================================================
  # Over-time values
  # =======================================================================
  elif (tab == 'tab_trends'):
    #print("get_tab_contents - tab_trends")
    viz_type = 'trend'
    df_plt = get_rlvt_data(df_rlvt, viz_type, view, metric, cb_list)
    if (view == 'us'): trend_fig = px.line(df_plt, x = 'date', y = metric)
    else:              trend_fig = px.line(df_plt, x = 'date', y = metric, color = views_color[view])
  
  return (
    md_txt, top_fig, trend_fig
  )
  
"""
# ======================================================================
# Boiler plate for a generic tab
# ======================================================================
"""
def get_tab(tab_type, name, init_val, controls = None):
  
  p_str = f"""
  tab_type    = {tab_type}
  name        = {name}
  md_name     = {name}_md
  graph_name  = {name}_fig
  data_name   = {name}_dat_tbl
  init_val    = {init_val}
  """
  p_print(p_str)
  
  # Define child component
  if (tab_type == 'md'):
    child_comp = [
      dcc.Markdown(
        id = f"{name}_md",
        children = init_val
      )
    ]
  elif (tab_type == 'graph'):
    child_comp = [
      dcc.Graph(
        id     = f"{name}_fig",
        figure = init_val,
      )
    ]
  elif (tab_type == 'data'):
    child_comp = [
      dash_table.DataTable(
        id            = '{name}_dat_tbl',
        columns       = [ {'name': i, "id": i} for i in (init_val) ],
        page_current  = 0,
        page_size     = 15,
        page_action   = 'custom',
        style_data_conditional  =[{
            'if':{'row_index':'odd'},
            'backgroundColor': 'rgb(248,248,248)'
        }],
        style_cell    = {'fontSize':14, 'font-family':'Century Gothic'},
        style_header  = {
          'backgroundColor': 'rgb(0, 102, 255)',
          'fontWeight':      'bold',
          'color':       'white',
        },
      )
    ]

  # Define tab
  tab = dcc.Tab(
    value               = name,
    label               = tab_dict[name],
    className           = "custom-tab",
    selected_className  = "custom-tab--selected",
    children            = child_comp
  )
  
  return tab

"""
# ======================================================================
# summarize_df - summarize data
# ======================================================================
"""
def summarize_df(df, metric, group_by_cols):
  avg_metrics = [ 'incidence_inc_pct', 'incidence_rate_pct', 'death_rate_pct' ]
  sum_metrics = [ 'population', 'incidence', 'incidence_inc', 'deaths' ] 
  
  if (metric in avg_metrics):
    df_out = round(df.groupby(group_by_cols)[metric].agg('mean'), 2)
  elif (metric in sum_metrics):
    df_out = round(df.groupby(group_by_cols)[metric].sum(), 0)
    
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
  cb_list,
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
      group_by += ['town']

    df_out = summarize_df(df_out, metric, group_by)
  
  return df_out

"""
# ======================================================================
# Prep main layout - tabs
# ======================================================================
"""
def get_tabs():
  smry_txt, top_fig, trend_fig = get_tab_contents(
      'tab_trends',
      'us',
      f'{def_state}',
      ['None'],
      'population',
  )
  
  #print(smry_txt)
  #print(trend_fig)
  
  tabs = []

  tabs.append(get_tab('md',    'tab_smry',    smry_txt))
  #tabs.append(get_tab('graph', 'tab_top',     top_fig))
  tabs.append(get_tab('graph', 'tab_trends',  trend_fig))
  #tabs.append(get_tab('data',  'tab_data',   df_rcnt.columns))

  #cntrl_smry = get_controls('smry')
  #tab_smry = get_tab('md', 'tab_smry', smry_txt, cntrl_smry)
  
  
  tabs_content = [
    dcc.Tabs(
      id                = 'tabs',
      value             = 'tab_smry',
      parent_className  = 'custom-tabs',
      children          = tabs,
    )
  ]
  
  return tabs_content

"""
# ======================================================================
# get_cntrl_comp():
# ======================================================================
"""
def get_cntrl_comp(
    cntrl,
    name,
    val_list,
    disp_dict,
    style = 'in-line block'
):
  comp_id       = f"{name}_comp"
  cntrl_id      = f"{name}_cntrl"
  if (val_list != ''):
    cntrl_options = [{'label': disp_dict[i], 'value': i} for i in val_list]
    init_val      = val_list[0]
  else:
    cntrl_options = None
    init_val      = None    
  
  comp = None
  
  if (cntrl == dcc.RadioItems):
    #print(111)
    comp = html.Div(
      id        = comp_id,
      style     = {'display': 'block'},
      children  = [
        dcc.Markdown(f"""
        ---
        ####  Select {name}
        """),
        dcc.RadioItems(
          id         = cntrl_id,
          options    = cntrl_options,
          value      = init_val,
          labelStyle = {'display': style}
        )
      ]
    )
  elif (cntrl == dcc.Checklist):
    #print(111)
    comp = html.Div(
      id        = comp_id,
      className = "chk_bx_style",
      style     = {'display': 'block'},
      children  = [
        dcc.Markdown(f"""
        ---
        ####  Select {name}
        """),
        dcc.Checklist(
          id         = cntrl_id,
          options    = cntrl_options,
          labelStyle = {'display': style}
        )
      ]
    )  
  elif (cntrl == dcc.Dropdown):
    #print(222)
    comp = html.Div(
      id        = comp_id,
      style     = {'display': 'block'},
      children  = [
        dcc.Markdown(f"""
        ---
        ####  Select {name}
        """),
        dcc.Dropdown(
          id         = cntrl_id,
          options    = cntrl_options,
          value      = init_val,
        )
      ]
    )    
  elif (cntrl == dcc.Markdown):    
    #print(333)
    comp = html.Div(
      style     = {'display': 'block'},
      children  = [
        dcc.Markdown(f"""
        ---
        """)
        ]
    )

  return comp

"""
# ======================================================================
# get_controls
# ======================================================================
"""
def get_controls(tab_name = ""):
  # Define styles  
  in_line = 'in-line block'
  block   = 'block'
  blank   = ''

  comps = []

  comps.append(get_cntrl_comp(dcc.RadioItems,  f'{tab_name}_view',     views,         views_dict,    in_line))
  comps.append(get_cntrl_comp(dcc.Dropdown,    f'{tab_name}_st_dd',    states,        states_dict,   in_line))
  comps.append(get_cntrl_comp(dcc.Checklist,   f'{tab_name}_chk_bx',   states,        states_dict,   block))
  comps.append(get_cntrl_comp(dcc.RadioItems,  f'{tab_name}_metric',   measure_cols,  measures_dict, block))
  comps.append(get_cntrl_comp(dcc.Markdown,    blank,      blank,      blank,         block))
  
  return comps

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
# get_disp_cntrl(disp_vec):
# ======================================================================
"""
def get_disp_cntrl(disp_vec):
  """
  # ======================================================================
  # get_yes_no(flag)
  # ======================================================================
  """
  def get_yes_no(flag):
    disp_no  = {'display': 'none'}
    disp_yes = {'display': 'block'}
    
    if (flag == 1): ret_val =  disp_yes
    else: ret_val = disp_no
  
    return ret_val  
  
  return [
    get_yes_no(disp_vec[0]),
    get_yes_no(disp_vec[1]),
    get_yes_no(disp_vec[2]),
  ]
  
"""
# ======================================================================
# Component control (based on tab)
# ======================================================================
"""
@app.callback(
  [
    Output('st_dd_comp',      'style'),
    Output('chk_bx_comp',     'style'),
    Output('metric_comp',     'style'),
    
    Output('chk_bx_cntrl',    'options'),
    Output('view_cntrl',      'options')
  ],
  [
    Input('tabs',             'value'),
    Input('view_cntrl',       'value'),
    Input('st_dd_cntrl',         'value'),
    Input('chk_bx_cntrl',     'value'),
  ]
)
def comp_cntrl_cb(
  tab,
  view,
  state,
  cb_list
):
  if (cb_list == None): cb_list = ['None']
    
  p_str = f"""
  comp_cntrl
  ----------
  tab     = {tab}
  view    = {view}
  state   = {state}
  cb_list = {cb_list}
  """
  #p_print(p_str)

  # =======================================================================
  # View Control
  # =======================================================================
  disp_views = ['us','state', 'town']
  if (tab == 'tab_top'): disp_views = ['us','state']
  vw_options = [ {'label': views_dict[i], 'value': i} for i in disp_views ]
  
  # =======================================================================
  # Check-box Control
  # =======================================================================
  disp_states = states
  disp_towns  = sorted(df[df['state'] == state]['town'].unique())
  cb_val = disp_states

  if (view == 'state'):  cb_val = disp_states
  elif (view == 'town'): cb_val = disp_towns
  
  cb_options = [ {'label': i, 'value': i} for i in cb_val ]

  # =======================================================================
  # Display Control
  # =======================================================================
  disp_vec = [0, 0, 0]
  if (tab == 'tab_smry'):
    if   (view == 'us'):      disp_vec  = [0, 0, 0]
    elif (view == 'state'):   disp_vec  = [0, 1, 0]
    elif (view == 'town'):    disp_vec  = [1, 1, 0]
  
  elif (tab == 'tab_top'):
    if   (view == 'us'):      disp_vec  = [0, 0, 1]
    elif (view == 'state'):   disp_vec  = [1, 0, 1]
  
  elif (tab == 'tab_trends'):
    if   (view == 'us'):      disp_vec  = [0, 0, 1]
    elif (view == 'state'):   disp_vec  = [0, 1, 1]
    elif (view == 'town'):    disp_vec  = [1, 1, 1]
  
  disp_cntrl = get_disp_cntrl(disp_vec)
  
  # =======================================================================
  # Return values
  # =======================================================================
  return (
    disp_cntrl[0], 
    disp_cntrl[1], 
    disp_cntrl[2],
    
    cb_options,
    vw_options
  )

"""
# ======================================================================
# Tab Contents call back
# ======================================================================
"""
@app.callback(
  [
   Output('tab_smry_md',     'children'),
   #Output('tab_top_fig',     'figure'),
   Output('tab_trends_fig',  'figure'),
  ],
  [
    Input('tabs',             'value'),
    Input('view_cntrl',       'value'),
    Input('st_dd_cntrl',      'value'),

    Input('chk_bx_cntrl',     'value'),
    Input('metric_cntrl',     'value'),
  ]
)
def md_contents_cb(
  tab,
  view,
  state,
  cb_list,
  metric,
):
  md_txt, top_fig, trend_fig = get_tab_contents(tab, view, state, cb_list, metric)
  
  print(md_txt)
  print(trend_fig)
  return (
    md_txt,
    #top_fig,
    trend_fig
  )

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
