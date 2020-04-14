import plotly.express as px
#fig = go.Figure() # or any Plotly Express function e.g. px.bar(...)
# fig.add_trace( ... )
# fig.update_layout( ... )

import sys
import os
import dash
import dash_core_components as dcc
import dash_html_components as html


TOP = "C:/Users/vishk/Desktop/WIP/2020/2020 Q1/07 - Self Learning"
sys.path.append(f"{TOP}/lib")
os.environ["TOP"] = TOP
from bootstrap import *

mysql_con, sql_svr_con = get_con(cfg['mysql'], cfg['sql_svr'])
con = sql_svr_con
sql = "select * from covid19_us_mds"
df  = get_df_from_sql(sql, con)

df2 = pd.DataFrame(df.groupby('date')['incidence'].sum())
print(df2)

df2['date'] = df2.index
#df2 = df2.reset_index()
#print(df2)

fig = px.line(df2, x = "date", y = "incidence")

app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure=fig)
])

app.run_server(debug=True)
