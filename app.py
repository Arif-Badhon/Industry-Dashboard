import dash
import dash_core_components as dcc
import dash_html_components as html
# from dash import dcc, html
import pymongo
import pandas as pd
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import dash_auth

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
#external_stylesheets = ["https://github.com/plotly/dash-app-stylesheets/blob/master/dash-technical-charting.css"]

# VALID_USERNAME_PASSWORD_PAIRS = {
#     'arif': '@arf121!'
# }
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, title='Industry Dashboard')

server = app.server

# auth = dash_auth.BasicAuth(
#     app,
#     VALID_USERNAME_PASSWORD_PAIRS
# )

client = pymongo.MongoClient("mongodb+srv://Badhon:arf123bdh@dataterminal1.gc4xk.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client["DATATERMINAL"]
collection = db["Industry Dashboard"]
collection = collection.find()
collection = pd.DataFrame(collection)
collection.drop('_id', inplace=True, axis=1)


industry_name = collection['Sector'].unique()

markdown_text = '''
#### **Welcome to Industry Dashboard!**


*150+ Indicators* &nbsp; &nbsp; *More than 50 thousands Data points*



###### INSTRUCTIONS

###### Select Sector/Industry --> Select Indicator --> Select Relevant Timeline (Monthly, Yearly or Budget Yearly)
'''

app.layout = html.Div([ 
    html.Div([
    #html.Img(src="/assests/1.png"),
    html.H2("BIZDATA INSIGHTS - INDUSTRY DASHBOARD", style={'textAlign':'center'}, className="app-header--title"),
    html.H6("Welcome To INDUSTRY DASHBOARD", style={'textAlign':'center'}, className="app-header--title"),
    html.Br(),
    html.H5("Select a Sector/Industry"),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id="Sector",
                options=[{'label':i, 'value': i} for i in industry_name],
                value='Select'
            ),
            html.Br(),
            html.H6("Select Indicator"),
            dcc.Dropdown(id='indicator'),
            html.Br(),
            html.H6("Choose best visualization type"),
            dcc.Dropdown(id='type'),
            html.Br(),
            dcc.Graph(id='graph')
        ])
    ])
])
])

@app.callback(
    Output('indicator', 'options'),
    Input('Sector', 'value'))
def select_indicator(industry_name):
    data = collection[collection['Sector'] == industry_name]
    indicator = data['Indicator']
    return [{'label': i, 'value': i} for i in np.unique(indicator)]



@app.callback(
    Output('type', 'options'),
    Input('indicator', 'value'),
    Input('Sector', 'value'))
def select_indicator(indicator, industry_name):
    data = collection[collection['Sector'] == industry_name]
    data = data[data['Indicator'] == indicator]
    
    CalenderYearData = data[~data['Calendar Value'].isnull()]
    BudgetYearData = data[~data['Budget Value'].isnull()]
    MonthlyData = data[~data['Calendar Year'].isnull() & data['Calendar Value'].isnull()]
    Type =[]
    if not CalenderYearData.empty:
        Type.append("Yearly")
    if not BudgetYearData.empty:
        Type.append("Budget Yearly")
    if not MonthlyData.empty:
        Type.append("Monthly")
    return [{'label': i, 'value': i} for i in Type]


@app.callback(
    Output('graph', 'figure'),
    Input('type', 'value'),
    Input('indicator', 'value'),
    Input('Sector', 'value'))
def graph_build(type, indicator, Sector):
    data = collection[collection['Sector'] == Sector]
    data = data[data['Indicator'] == indicator]
    
    CalenderYearData = data[~data['Calendar Value'].isnull()]
    BudgetYearData = data[~data['Budget Value'].isnull()]
    MonthlyData = data[~data['Calendar Year'].isnull() & data['Calendar Value'].isnull()]

    figure = {}

    if type == 'Yearly':
        cdata = CalenderYearData[['Calendar Year', 'Calendar Value']]
        cdata = cdata.sort_values('Calendar Year')
        figure = px.bar(cdata, x='Calendar Year', y='Calendar Value', text='Calendar Value')
        figure.update_layout(title={'text':"Yearly data plot of "+ indicator,  'y':0.9,
            'x':0.5,'xanchor':'center', 'yanchor':'top'}, xaxis_title="Source: " + str(np.unique(CalenderYearData['Source'])[0]), yaxis_title=str(np.unique(CalenderYearData['Unit'])[0]))
        #figure.show()
        #figure.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        #figure.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        return figure
    elif type == 'Budget Yearly':
        cdata = BudgetYearData[['Budget Year', 'Budget Value']]
        cdata = cdata.sort_values('Budget Year')
        figure = px.bar(cdata, x='Budget Year', y='Budget Value', text='Budget Value')
        figure.update_layout(title={'text':"Budget Yearly data plot of "+ indicator,  'y':0.9,
            'x':0.5,'xanchor':'center', 'yanchor':'top'}, xaxis_title="Source: " + str(np.unique(BudgetYearData['Source'])[0]), yaxis_title=str(np.unique(BudgetYearData['Unit'])[0]))
        return figure
    else:
        cdata = MonthlyData[["Calendar Year", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]]
        Year = cdata["Calendar Year"]
        January = cdata["Jan"]
        February = cdata["Feb"]
        March = cdata["Mar"]
        April = cdata["Apr"]
        May = cdata["May"]
        June = cdata["Jun"]
        July = cdata["Jul"]
        August = cdata["Aug"]
        September = cdata["Sep"]
        October = cdata["Oct"]
        November = cdata["Nov"]
        December = cdata["Dec"]

        figure = go.Figure(data=[
            go.Bar(name='January', x=Year, y=January),
            go.Bar(name='February', x=Year, y=February),
            go.Bar(name='March', x=Year, y=March),
            go.Bar(name='April', x=Year, y=April),
            go.Bar(name='May', x=Year, y=May),
            go.Bar(name='June', x=Year, y=June),
            go.Bar(name='July', x=Year, y=July),
            go.Bar(name='August', x=Year, y=August),
            go.Bar(name='September', x=Year, y=September),
            go.Bar(name='October', x=Year, y=October),
            go.Bar(name='November', x=Year, y=November),
            go.Bar(name='December', x=Year, y=December)
        ])
        figure.update_layout(barmode='group')
        figure.update_layout(title={'text':"Monthly data plot of "+ indicator,  'y':0.9,
            'x':0.5,'xanchor':'center', 'yanchor':'top'}, xaxis_title="Source: " + str(np.unique(MonthlyData['Source'])), yaxis_title=str(np.unique(MonthlyData['Unit'])))
        return figure





if __name__ == '__main__':
    app.run_server(debug=True)
