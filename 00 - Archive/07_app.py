import  dash_table.FormatTemplate    as dft
import  dash_core_components         as dcc
import  dash_bootstrap_components    as dbc
import  dash_html_components         as html
import  plotly.express               as px
import  pandas                       as pd
import  dash
import  dash_table

import  os
import  sys
import  traceback

from    dash.dependencies           import Input, Output
from    dash_table.Format           import Format, Scheme, Sign, Symbol
from    lstm                        import *
TOP = r"C:/Users/vishk/Desktop/WIP/2020/2020 Q1/07 - Self Learning"
sys.path.append(f"{TOP}/lib")
os.environ["TOP"] = TOP

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
from bootstrap import *

app.layout = desktop_layout

if __name__ == '__main__':
    app.run_server(debug=True)



