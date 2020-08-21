# corona-dash-a8fe8

import dash
import dash_table
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
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


#-static-stuff-just-as-a-test--------------------------------------------------------------------------------------------------------------
# test pie chart (static)
pie_chart = go.Figure(layout=layout)
labels = ['Germany', 'US', 'United Kingdom', 'France', 'Spain', 'Belgium', 'Argentina', 'Brazil', 'Russia', 'India', 'Mexico', 'Italy', 'Netherlands']
population = [83.0, 328.2, 66.7, 67.0, 46.9, 11.5, 44.5, 209.5, 144.5, 1353.0, 126.2, 60.4, 17.3]
values = []
for i, country in enumerate(labels):
	cum_cases = data_cases.loc[data_cases["Country/Region"] == country].to_numpy()
	value = 0
	if len(cum_cases) > 1:
		for j in range(len(cum_cases)):
				value += cum_cases[j][-1]
		values.append(round(value))    # /population[i]))
	else:
		values.append(round(cum_cases[0][-1])) #/population[i]))
pie_chart.add_trace(go.Pie(labels=labels, values=values, hole=0.3))
pie_chart.update_layout(title='Cases', uniformtext_minsize=10, uniformtext_mode='hide')
pie_chart.update_traces(textposition='inside', textinfo='percent+label')

# test DataTable
# creating data for table
data_frames = [data_cases, data_deaths, data_recovered]
data = [labels,[],[],[], []]

for i, country in enumerate(labels):
	for column in range(len(data_frames)):
		cum_cases = data_frames[column].loc[data_frames[column]["Country/Region"] == country].to_numpy()
		value = 0
		if len(cum_cases) > 1:
			for j in range(len(cum_cases)):
					value += cum_cases[j][-1]
			data[column+1].append(round(value))
		else:
			data[column+1].append(round(cum_cases[0][-1]))

data[-1] = np.array(data[1]) - np.array(data[2]) - np.array(data[3])
df_table = pd.DataFrame({'Country': data[0], 'Total Cases': data[1], 'Total Deaths': data[2], 'Total Recovered': data[3], 'Total Active': data[4]})
df_table = df_table.sort_values(by=["Total Cases"], ascending=False)
#------------------------------------------------------------------------------------------------------------------------------------------


#-html-of-dashboard------------------------------------------------------------------------------------------------------------------------
app.layout = html.Div(className='grey',
	children=[
			html.H1(children='COVID DATA BY COUNTRY'),
			html.P(children='Data from JHU, presented by Jonas Dieker'),
						html.Div(className='grey selectDrop row', children=
				[dcc.Dropdown(className='six columns', id='dropdown',
							options=[{'label': 'Germany', 'value': 'Germany'},
							{'label': 'USA', 'value': 'US'},
							{'label': 'United Kingdom', 'value': 'United Kingdom'},
							{'label': 'France', 'value': 'France'},
							{'label': 'Spain', 'value': 'Spain'},
							{'label': 'Belgium', 'value': 'Belgium'},
							{'label': 'Argentina', 'value': 'Argentina'},
							{'label': 'Brazil', 'value': 'Brazil'},
							{'label': 'Russia', 'value': 'Russia'},
							{'label': 'India', 'value': 'India'},
							{'label': 'Mexico', 'value': 'Mexico'},
							{'label': 'Italy', 'value': 'Italy'},
							{'label': 'Netherlands', 'value': 'Netherlands'},],
							value='Germany',
							clearable=False,
							style={'backgroundColor': '#797979'}),
				dcc.Dropdown(className='six columns', id='dropdown2',
							options=[{'label': 'Cases', 'value': 'cases'},
							{'label': 'Deaths', 'value': 'deaths'},
							{'label': 'Recoveries', 'value': 'recovered'},
							{'label': 'Active Cases', 'value': 'active'}],
							value='cases',
							clearable=False,
							style={'backgroundColor': '#797979'})
				],),
			#dcc.Slider(className='selectSlider', min=0, max=len(daily_cases), marks={i: 'Days {}'.format(i) for i in range(0, len(daily_cases), 10)}, value=len(daily_cases)),
			html.Div(className='row', children=
				[html.Div(className='four columns', children=
					[dash_table.DataTable(id='table', data=df_table.to_dict('records'), columns=[{'id': c, 'name':c} for c in df_table.columns], fixed_rows={'headers':True}, 
					style_table={
					'maxHeight': '50ex',
					'overflowY': 'auto',
					'overflowX': 'auto',
					'width': '100%',
					'minWidth': '100%',
					},
					style_data={
					'whiteSpace': 'normal',
					'height': 'auto',},
					style_header={
					'textAlign': 'left',
					'backgroundColor': '#676767',
					'fontWeight': 'bold',
					'fontSize': 13},
					style_cell={
					'textAlign': 'left',
					'backgroundColor': '#676767',
					'color': '#B7B7B7'},
					style_cell_conditional=[
        			{'if': {'column_id': 'Country'},
        			'width': '20%'},
        			{'if': {'column_id': 'Total Recovered'},
        			'width': '22%'},
        			{'if': {'column_id': 'Total Active'},
        			'width': '18%'},]
					)]),
				dcc.Graph(className='eight columns', id='first_fig', config={'displayModeBar': False})
				]),
			html.Div(className='row', children=
				[dcc.Graph(className='four columns', id='third_fig', figure=pie_chart, config={'displayModeBar': False}),
				dcc.Graph(className='eight columns', id='second_fig', config={'displayModeBar': False})
				]),
			html.Div(id='intermediate-value', style={'display': 'none'}),
])
#------------------------------------------------------------------------------------------------------------------------------------------


#-helper-functions-------------------------------------------------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------------------------------------------------------------------



if __name__ == '__main__':
	app.run_server(debug=True)