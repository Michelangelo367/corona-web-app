# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__) #external_stylesheets=external_stylesheets)

data_cases = pd.read_csv("https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
data_deaths = pd.read_csv("https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
data_recovered = pd.read_csv("https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")

country = "Germany"
germany_cases = data_cases.loc[data_cases["Country/Region"] == country]
germany_deaths = data_deaths.loc[data_deaths["Country/Region"] == country]
germany_recovered = data_recovered.loc[data_recovered["Country/Region"] == country]
cases = germany_cases.to_numpy()[0][4:]
deaths = germany_deaths.to_numpy()[0][4:]
recovered = germany_recovered.to_numpy()[0][4:]

# reformatting to daily data
daily_cases = [0]
daily_deaths = [0]
daily_recovered = [0]
for i in range(1,len(cases)):
	daily_cases.append(cases[i]-cases[i-1])
	daily_deaths.append(deaths[i]-deaths[i-1])
	daily_recovered.append(recovered[i]-recovered[i-1])
daily_deaths = [abs(num) for num in daily_deaths]


df = pd.DataFrame({"days": range(1, len(daily_cases)+1), "cases": daily_cases,
					"deaths": daily_deaths, "recovered": daily_recovered})

fig = go.Figure()
fig.add_trace(go.Bar(x=df["days"], y=df["cases"],name="Cases"))
fig.add_trace(go.Bar(x=df["days"], y=df["deaths"],name="Deaths"))
fig.add_trace(go.Bar(x=df["days"], y=df["recovered"],name="Recoveries"))

fig.update_layout(updatemenus=[dict(
			visible=True,
			active=0,
			buttons=list([
				dict(label="All",
					 method="update",
					 args=[{"visible": [True, True, True]}]),
				dict(label="Cases",
					 method="update",
					 args=[{"visible": [True, False, False]}]),
				dict(label="Deaths",
					 method="update",
					 args=[{"visible": [False, True, False]}]),
				dict(label="Recoveries",
					 method="update",
					 args=[{"visible": [False, False, True]}]),
			]),
		)
	])


app.layout = html.Div(
	children=[html.Div(className='row',
		children=[html.Div(className='four columns div-user-controls',
			children=[
				html.H1('COVID DATA GERMANY'),
				html.P('Data from JHU, presented by Jonas Dieker'),
				]
			),
		html.Div(className='eight columns div-for-charts bg-grey',
			children=[
			dcc.Graph(id='corona', figure=fig, config={'displayModeBar': False}, animate=True)
		])
	])
])

if __name__ == '__main__':
	app.run_server(debug=True)
