import dash
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# getting csv data
data_cases = pd.read_csv("https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
data_deaths = pd.read_csv("https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
data_recovered = pd.read_csv("https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")

# graph styling
layout = go.Layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=30, b=70, l=50, r=50))

# test pie chart (static)
pie_chart = go.Figure(layout=layout)
labels = ['Germany', 'US', 'United Kingdom', 'France', 'Spain']
population = [83.0, 328.2, 66.7, 67.0, 46.9]
values = []
for i, country in enumerate(labels):
	cum_cases = data_cases.loc[data_cases["Country/Region"] == country].to_numpy()
	value = 0
	if len(cum_cases) > 1:
		for j in range(len(cum_cases)):
				value += cum_cases[j][-1]
		values.append(round(value/population[i]))
	else:
		values.append(round(cum_cases[0][-1]/population[i]))
pie_chart.add_trace(go.Pie(labels=labels, values=values, hole=0.3))
pie_chart.update_layout(title='Cases per million', uniformtext_minsize=10, uniformtext_mode='hide')
pie_chart.update_traces(textposition='inside', textinfo='percent+label')

# html of dashboard
app.layout = html.Div(
	children=[
			html.H1(children='COVID DATA BY COUNTRY'),
			html.P(children='Data from JHU, presented by Jonas Dieker'),
			html.Div(className='selectDrop row', children=
				[dcc.Dropdown(className='six columns', id='dropdown',
							options=[{'label': 'Germany', 'value': 'Germany'},
							{'label': 'USA', 'value': 'US'},
							{'label': 'United Kingdom', 'value': 'United Kingdom'},
							{'label': 'France', 'value': 'France'},
							{'label': 'Spain', 'value': 'Spain'},],
							value='Germany'),
				dcc.Dropdown(className='six columns', id='dropdown2',
							options=[{'label': 'Cases', 'value': 'cases'},
							{'label': 'Deaths', 'value': 'deaths'},
							{'label': 'Recoveries', 'value': 'recovered'},
							{'label': 'Active Cases', 'value': 'active'}],
							value='cases')
				]),
			#dcc.Slider(className='selectSlider', min=0, max=len(daily_cases), marks={i: 'Days {}'.format(i) for i in range(0, len(daily_cases), 10)}, value=len(daily_cases)),
			dcc.Graph(id='first_fig', config={'displayModeBar': False}),
			html.Div(className='row', children=
				[dcc.Graph(className='four columns', id='third_fig', figure=pie_chart, config={'displayModeBar': False}),
				dcc.Graph(className='eight columns', id='second_fig', config={'displayModeBar': False})
				]),
			html.Div(id='intermediate-value', style={'display': 'none'}),
])



@app.callback(Output('intermediate-value', 'children'), [Input('dropdown', 'value')])
def clean_data(dropdown_value):

	country = str(dropdown_value)
	country_cases = data_cases.loc[data_cases["Country/Region"] == country].to_numpy()
	country_deaths = data_deaths.loc[data_deaths["Country/Region"] == country].to_numpy()
	country_recovered = data_recovered.loc[data_recovered["Country/Region"] == country].to_numpy()

	data_items = len(country_cases[0][4:])
	cases = np.zeros(data_items)
	deaths = np.zeros(data_items)
	recovered = np.zeros(data_items)

	for i in range(0, len(country_cases)):
		for j in range(4, len(country_cases[0])):
			cases[j-4] += abs(country_cases[i][j])
			deaths[j-4] += abs(country_deaths[i][j])
			recovered[j-4] += abs(country_recovered[i][j])

	# reformatting to daily data
	daily_cases = [0]
	daily_deaths = [0]
	daily_recovered = [0]
	for i in range(1,len(cases)):
		daily_cases.append(abs(cases[i]-cases[i-1]))
		daily_deaths.append(abs(deaths[i]-deaths[i-1]))
		daily_recovered.append(abs(recovered[i]-recovered[i-1]))

	active_cases = cases - deaths - recovered

	df = pd.DataFrame({"days": range(1, len(daily_cases)+1), "cases": daily_cases,
						"deaths": daily_deaths, "recovered": daily_recovered, "active": active_cases})

	return df.to_json()


@app.callback(Output('first_fig', 'figure'), [Input('intermediate-value', 'children')])
def update_figure1(jsonified_df):

	df = pd.read_json(jsonified_df)
	fig = go.Figure(layout=layout)
	fig.add_trace(go.Bar(x=df["days"], y=df["cases"],name="Cases"))
	fig.add_trace(go.Bar(x=df["days"], y=df["deaths"],name="Deaths"))
	fig.add_trace(go.Bar(x=df["days"], y=df["recovered"],name="Recoveries"))
	fig.update_layout(xaxis_title="Days from Start of Pandemic")

	return fig


@app.callback(Output('second_fig', 'figure'), [Input('intermediate-value', 'children'), Input('dropdown2', 'value')])
def update_figure2(jsonified_df, type_data):

	df = pd.read_json(jsonified_df)
	fig = go.Figure(layout=layout)
	fig.add_trace(go.Bar(x=df["days"], y=df[type_data], name="Active Cases"))
	fig.update_layout(xaxis_title="Days from Start of Pandemic")

	return fig



if __name__ == '__main__':
	app.run_server(debug=True)