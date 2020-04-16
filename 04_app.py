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
from   lstm                 import *
import traceback

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

os.environ['TF_CPP_MIN_LOG_LEVEL']='3'
with warnings.catch_warnings():
	warnings.filterwarnings("ignore", category=DeprecationWarning)

"""
# ======================================================================
# Get data
# ======================================================================
"""
min_date  = '2020-03-01'

#mysql_con, sql_svr_con = get_con(cfg['mysql'], cfg['sql_svr'])

#con        = sql_svr_con
sql        = f"select * from covid19_us_mds"
#df         = get_df_from_sql(sql, con)
df         = pd.read_csv('covid19_us_2020-04-16.csv')
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
  'tab_top':     f"High Risk on {rcnt_dt}",
  'tab_trends':  f"Trends",
  'tab_data':    f"Data",
}

dim_desc        = [ 'States', 'County/Town', 'Date' ]
dim_cols        = [ 'state',  'town',        'date']
view_desc       = [ 'US', 'State', 'County' ]
views           = [ 'us', 'state', 'town' ]
view_cuts       = [ 'state', 'town', '' ]
view_color_col  = [ '', 'state', 'town' ]

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
def_state         = 'Massachusetts'
def_town          = 'Middlesex, Massachusetts, US'

"""
# ======================================================================
# Get content for summary tab
# ======================================================================
"""
def get_md(df, df_rcnt):
  if (len(df) == 0 or len(df_rcnt) == 0):
    ( min_date, max_date ) = ('NA', 'NA')
    (
    days, num_states, states, towns, 
    num_towns, population, cum_incids, incid_rate, 
    incid_inc, cum_deaths, death_rate
    ) = \
    (
      0, 0, 0, 0,
      0, 0, 0, 0,
      0, 0, 0
    )      
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
  return md_txt

"""
# ======================================================================
# Get tab contents
# ======================================================================
"""
def get_tab_contents(
  view,
  state,
  cb_list,
  metric,
  
  predict_btn_clcks   = 0,
  #clear_btn_clcks     = 0,
  modal_cls_btn_clcks = 0,
):
  # =======================================================================
  # Defaults
  # =======================================================================
  if (cb_list == None): cb_list = ['None']
  if (metric == None):  metric = 'incidence'
  
  try:
    # =======================================================================
    # Initializations
    # =======================================================================
    md_txt, top_fig, trend_fig, modal_txt = "Empty", None, None, ""

    # =======================================================================
    # Gather data
    # =======================================================================
    df_all   = df
    df_st    = df[df['state'] == state]
    df_sts   = df[(df['state']).isin(cb_list)]
    df_towns = df[
      (df['state'] == state) &
      (df['town']).isin(cb_list)
    ]

    if (view == 'us'):
      df_md, df_top, df_trend  = df_all, df_all, df_all
    elif (view == 'state'):
      df_md, df_top, df_trend  = df_sts, df_st, df_sts
    elif (view == 'town'):
      df_md, df_top, df_trend  = df_towns, df_towns, df_towns

    df_md_curr  = df_md[df_md['date'] == rcnt_dt]
    df_top_curr = df_top[df_top['date'] == rcnt_dt]

    # =======================================================================
    # Refresh data for summary tab
    # =======================================================================
    md_txt = get_md(df_md, df_md_curr)

    # =======================================================================
    # Refresh plot for high risk tab
    # =======================================================================
    if (view != 'town'):
      viz_type = 'top'
      top_attribs = dict(
      )
      df_plt_top = get_rlvt_data(df_top_curr, viz_type, view, metric, cb_list)
      top_fig = px.bar(df_plt_top, orientation = 'h', x = metric, y = view_cuts[view], height = 650)
    else:
      top_fig = None

    # =======================================================================
    # Refresh data for over-time trends tab
    # =======================================================================
    viz_type = 'trend'
    df_plt_trend = get_rlvt_data(df_trend, viz_type, view, metric, cb_list)

    if (predict_btn_clcks > 0):
      df_pred = get_lstm_rslts(df_plt_trend, metric)
      df_pred['type']       = 'predicted'
      df_plt_trend['type']  = 'actual'
      df_plt_trend  = df_plt_trend.append(df_pred)
      trend_fig     = px.line(df_plt_trend, x = 'date', y = metric, height = 600, color = 'type')
    else:
      if (view == 'us'): trend_fig = px.line(df_plt_trend, x = 'date', y = metric, height = 600)
      else:              trend_fig = px.line(df_plt_trend, x = 'date', y = metric, height = 600, color = views_color[view])

    if (modal_cls_btn_clcks > 0): modal_txt = ""
  except Exception as err:
    print(f"Exception:\n{traceback.format_exc()}")
  finally:
    return ( md_txt, top_fig, trend_fig, modal_txt )
  
"""
# ======================================================================
# Boiler plate for a generic tab
# ======================================================================
"""
def get_tab(tab_type, name, init_val):
  
  p_str = f"""
  tab_type    = {tab_type}
  name        = {name}
  md_name     = {name}_md
  graph_name  = {name}_fig
  data_name   = {name}_dat_tbl
  init_val    = {init_val}
  """
  #p_print(p_str)
  
  # Define child component
  if (tab_type == 'md'):
    child_comp = [
      dcc.Markdown(
        id        = f"{name}_md",
        children  = init_val
      )
    ]
  elif (tab_type == 'graph'):
    child_comp = [
      dcc.Graph(
        id     = f"{name}_fig",
        figure = init_val,
      ),
      dcc.Store(
        id     = f"{name}_fig_store",
        data   = init_val,
      ),
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
          'if': {'row_index':'odd'},
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
    children            = child_comp,
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
  
  if (metric in avg_metrics):   df_out = round(df.groupby(group_by_cols)[metric].agg('mean'), 2)
  elif (metric in sum_metrics): df_out = round(df.groupby(group_by_cols)[metric].sum(), 0)
    
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
    if (view == 'us'):      group_by = 'state'
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
  def_smry_txt, def_top_fig, def_trend_fig, \
  modal_txt = get_tab_contents(
    'us', f'{def_state}', ['None'], f'{def_metric}'
  )
  
  tabs = []

  tabs.append(get_tab('md',    'tab_smry',    def_smry_txt))
  tabs.append(get_tab('graph', 'tab_top',     def_top_fig))
  tabs.append(get_tab('graph', 'tab_trends',  def_trend_fig))
  #tabs.append(get_tab('data',  'tab_data',   df_rcnt.columns))

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
  comp_id  = f"{name}_comp"
  cntrl_id = f"{name}_cntrl"
  if (val_list != ''):
    cntrl_options = [{'label': disp_dict[i], 'value': i} for i in val_list]
    init_val      = val_list[0]
  else:
    cntrl_options = None
    init_val      = None
  
  comp = None
  
  if (cntrl == dcc.RadioItems):
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
    comp = html.Div(
      style     = {'display': 'block'},
      children  = [
        dcc.Markdown(f"""
        ---
        """)
        ]
    )
  elif (cntrl == html.Button):
    comp = html.Div(
      className = "button_layout",
      id        = comp_id,
      style     = {'display': 'block'},
      children  = [
        dcc.Markdown(f"""
        ---
        """),
        html.Button(
          'Get Trend (Algo = LSTM)',
          id        = cntrl_id,
          className = "button_style submit",
          n_clicks  = 0,
        ),
        #html.Button(
        #  'Clear', 
        #  id        = f'clr_{cntrl_id}',
        #  className = "button_style clear",
        #  n_clicks  = 0,
        #)
      ]
    )

  return comp

"""
# ======================================================================
# get_controls
# ======================================================================
"""
def get_controls():
  # Define styles  
  in_line = 'in-line block'
  block   = 'block'
  blank   = ''

  comps = []

  comps.append(get_cntrl_comp(dcc.RadioItems,  'view',     views,          views_dict,    in_line))
  comps.append(get_cntrl_comp(dcc.Dropdown,    'st_dd',    states,         states_dict,   in_line))
  comps.append(get_cntrl_comp(dcc.Checklist,   'chk_bx',   states,         states_dict,   block))
  comps.append(get_cntrl_comp(dcc.RadioItems,  'metric',   measure_cols,   measures_dict, block))
  comps.append(get_cntrl_comp(html.Button,     'predict',  blank,          blank,         in_line))
  comps.append(get_cntrl_comp(dcc.Markdown,    blank,      blank,          blank,         block))
  
  return comps

"""
# ======================================================================
# Define app
# ======================================================================
"""
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True
app.title = "US COVID19 Tracker"
app.layout = html.Div(
  children = [
    html.Div(
      className = "app_left",
      children  = get_tabs()
    ),

    html.Div(
      className = "app_right",
      children  = get_controls()
    ),

    html.Div(
      id        = 'modal_comp',
      className = 'modal',
      style     = {'display': 'none'},
      children  = [
        html.Div(
          style      = {'textAlign': 'center',},
          className  = 'modal-content',
          children = [
            html.Div(id = 'modal_cntrl', children = ['Model content']),
            html.Hr(),
            html.Button('Close', id='modal_close_button',)
          ]
        ),
      ]
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
    get_yes_no(disp_vec[3])
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
    Output('predict_comp',    'style'),
    
    Output('chk_bx_cntrl',    'options'),
    Output('view_cntrl',      'options')
  ],
  [
    Input('tabs',             'value'),
    Input('view_cntrl',       'value'),
    Input('st_dd_cntrl',      'value'),
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
    if   (view == 'us'):      disp_vec  = [0, 0, 0, 0]
    elif (view == 'state'):   disp_vec  = [0, 1, 0, 0]
    elif (view == 'town'):    disp_vec  = [1, 1, 0, 0]
  
  elif (tab == 'tab_top'):
    if   (view == 'us'):      disp_vec  = [0, 0, 1, 0]
    elif (view == 'state'):   disp_vec  = [1, 0, 1, 0]
    elif (view == 'town'):    disp_vec  = [1, 0, 1, 0]
  
  elif (tab == 'tab_trends'):
    if   (view == 'us'):      disp_vec  = [0, 0, 1, 1]
    elif (view == 'state'):   disp_vec  = [0, 1, 1, 1]
    elif (view == 'town'):    disp_vec  = [1, 1, 1, 1]
  
  disp_cntrl = get_disp_cntrl(disp_vec)
  
  # =======================================================================
  # Return values
  # =======================================================================
  return (
    disp_cntrl[0], 
    disp_cntrl[1], 
    disp_cntrl[2],
    disp_cntrl[3],
    
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
    Output('tab_smry_md',         'children'),
    Output('tab_top_fig',         'figure'),
    Output('tab_trends_fig',      'figure'),

    Output('modal_comp',          'style'),
    Output('modal_cntrl',         'children'),
  ],
  [
    Input('view_cntrl',           'value'),
    Input('st_dd_cntrl',          'value'),

    Input('chk_bx_cntrl',         'value'),
    Input('metric_cntrl',         'value'),

    Input('tab_top_fig_store',    'data'),
    Input('tab_trends_fig_store', 'data'),

    Input('predict_cntrl',        'n_clicks'),
    #Input('clr_predict_cntrl',    'n_clicks'),
    Input('modal_close_button',   'n_clicks'),
  ]
)
def md_contents_cb(
  view,
  state,
  cb_list,
  metric,

  def_top_fig,
  def_trend_fig,

  predict_btn_clcks,
  #clear_btn_clcks,
  modal_cls_btn_clcks,
):
  modal_style = {'display': 'none'}
  #predict_btn_clcks, clear_btn_clcks, modal_cls_btn_clcks = 0, 0, 0
  predict_btn_clcks, modal_cls_btn_clcks = 0, 0
  changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
  if ('predict_cntrl'       in changed_id): predict_btn_clcks   = 1
  #if ('clr_predict_cntrl'   in changed_id): clear_btn_clcks     = 1
  if ('modal_close_button'  in changed_id): modal_cls_btn_clcks = 1

  p_str = f"""
  get_tab_contents
  ---------------
  view                = {view}
  state               = {state}
  cb_list             = {cb_list}
  metric              = {metric}
  predict_btn_clcks   = {predict_btn_clcks}
  modal_cls_btn_clcks = {modal_cls_btn_clcks}
  """
  print(p_str)

  md_txt, top_fig, \
  trend_fig, modal_txt = get_tab_contents(
    view, state, cb_list, metric,
    #predict_btn_clcks, clear_btn_clcks, modal_cls_btn_clcks,
    predict_btn_clcks, modal_cls_btn_clcks,
  )
  
  if (top_fig == None):   top_fig = def_top_fig
  if (trend_fig == None): trend_fig = def_trend_fig
  if (modal_txt != ""):   modal_style = {'display': 'block'}

  return (
    md_txt, top_fig, trend_fig,
    modal_style, modal_txt,
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
  app.run_server(debug=debug_flag, threaded=False)
