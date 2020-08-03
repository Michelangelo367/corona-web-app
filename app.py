import dash
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# getting csv data
data_cases = pd.read_csv("https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
data_deaths = pd.read_csv("https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
data_recovered = pd.read_csv("https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")

# graph styling
layout = go.Layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=30))

# html of dashboard
app.layout = html.Div(
	children=[
			html.H1(children='COVID DATA BY COUNTRY'),
			html.P(children='Data from JHU, presented by Jonas Dieker'),
			dcc.Dropdown(className='selectDrop', id='dropdown',
						options=[{'label': 'Germany', 'value': 'Germany'},
								{'label': 'Austria', 'value': 'Austria'},
								{'label': 'USA', 'value': 'US'}],
								value='Germany'),
			#dcc.Slider(className='selectSlider', min=0, max=len(daily_cases), marks={i: 'Days {}'.format(i) for i in range(0, len(daily_cases), 10)}, value=len(daily_cases)),
			dcc.Graph(id='corona', config={'displayModeBar': False}, animate=True, style={}),
			dcc.Graph(id='active_cases', config={'displayModeBar': False}),
			html.Div(id='intermediate-value', style={'display': 'none'}),
])



@app.callback(Output('intermediate-value', 'children'), [Input('dropdown', 'value')])
def clean_data(dropdown_value):

	country = str(dropdown_value)
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

	active_cases = cases - deaths - recovered

	df = pd.DataFrame({"days": range(1, len(daily_cases)+1), "cases": daily_cases,
						"deaths": daily_deaths, "recovered": daily_recovered, "active": active_cases})

	return df.to_json()


@app.callback(Output('corona', 'figure'), [Input('intermediate-value', 'children')])
def update_figure1(jsonified_df):

	df = pd.read_json(jsonified_df)
	fig = go.Figure(layout=layout)
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
	return fig


@app.callback(Output('active_cases', 'figure'), [Input('intermediate-value', 'children')])
def update_figure2(jsonified_df):

	df = pd.read_json(jsonified_df)
	fig2 = go.Figure(layout=layout)
	fig2.add_trace(go.Bar(x=df["days"], y=df["active"], name="Active Cases"))
	fig2.update_layout(xaxis_title="Days from Start of Pandemic", yaxis_title="Active Case Numbers")

	return fig2



if __name__ == '__main__':
	app.run_server(debug=True)
