import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import os 
import dash_bootstrap_components as dbc
import base64
import re

cleanData_path = 'data_clean/'
data_path = 'data'
picture_path = 'NBA_Picture.png'

## LOADING DATA ##
# Results data
combined_data = pd.read_csv(f'{cleanData_path}full.csv')
with open(f'{cleanData_path}dates_list.txt','r') as f: 
    dates_list = f.read() 
overtimeCount = pd.read_csv(f'{cleanData_path}overtime_table.csv')
results_dd_options = [
       {'label': 'Quarter 1', 'value': 'Q1'},
       {'label': 'Quarter 2', 'value': 'Q2'},
       {'label': 'Quarter 3', 'value': 'Q3'},
       {'label' : 'Quarter 4', 'value' : 'Q4'},
       {'label' : 'Overtime', 'value' : 'Overtime'}
   ]
OT = pd.read_csv(f'{cleanData_path}OT_count.csv')
OT2 = pd.read_csv(f'{cleanData_path}OT2_count.csv')
OT3 = pd.read_csv(f'{cleanData_path}OT3_count.csv')
OT4 = pd.read_csv(f'{cleanData_path}OT4_count.csv')
OT5 = pd.read_csv(f'{cleanData_path}OT5_count.csv')
full_results = pd.read_csv(f'{cleanData_path}total_score_count.csv')
# NBA table data
nba_table = pd.read_csv(f'{cleanData_path}NBA_table.csv') #reads data for All times NBA df
nba_table_copy = nba_table.copy(deep=True).drop(columns=['Draw']) #makes a copy and drops the Draw columns, because there are no values bigger than 0
nba_table_toDict = nba_table_copy.to_dict('records') #to pass into datatable
# Barchart data
year_id = [file.split('.')[0] for file in os.listdir(f'{data_path}')] #creates list of years (from filenames) to pass onto dropdown manu as in Most/Least NBA stats
# Style
style_table_OT = {'display': 'inline-block', 'text-align': 'center'}
style_cell_variable = {'text-align': 'center', 'backgroundColor': 'transparent', 'border': '1px solid #909090', }
style_header_variable = {'fontWeight': 'bold', 'border': '1px solid black'}

#____________________________________________________________________________________________________________________________________________-
## MODIFY DATA FOR MOST/LEAST TABLES ##

def make_fig(data_name, title, y_name):
    max_value = data_name['Count'].max()
    min_value = data_name['Count'].min()

    # These lines add a new column 'Day Distribution' to the DataFrame data_name. Initially, it is set to 'Remaining days' for all rows.
    # Loc method is a function in pandas (location), is used to access a group of rows and columns
    data_name['Day Distribution'] = 'Remaining days'
    # Rows where 'Count' is equal to max_value will have 'Day Distribution' set to 'Highest outcomes'.
    data_name.loc[data_name['Count'] == max_value, 'Day Distribution'] = 'Highest outcomes'
    # Rows where 'Count' is equal to min_value will have 'Day Distribution' set to 'Lowest outcomes'.
    data_name.loc[data_name['Count'] == min_value, 'Day Distribution'] = 'Lowest outcomes'
        
    fig = px.bar(data_name, x='date_game', y='Count',
            title=title, labels={"date_game": "Date", "Count": y_name},
            color='Day Distribution', color_discrete_map={'Highest outcomes': '#ff8c1a', 'Lowest outcomes': '#0000e6', 'Remaining days': '#9fbfdf'})
    
    fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    )

    return fig

# Convert "date_game" to datetime with correct format
combined_data['date_game'] = pd.to_datetime(combined_data['date_game'], format='%a %b %d %Y')

# Create a new column for the day and month
combined_data['day_month'] = combined_data['date_game'].dt.strftime('%B %d')

# Count the number of games for each day in all months
game_counts = combined_data['day_month'].value_counts().sort_index()

# Reorder the index for correct plotting
game_counts = game_counts.reindex(index=[re.sub(r"[\n\t]*", "", i).strip("' ") for i in dates_list.split(',')])
#____________________________________________________________________________________________________________________________________________-
## DASH APP ##

# Existing code for encoding the image
image_frontpage = picture_path
encoded_image = base64.b64encode(open(image_frontpage, 'rb').read()).decode()

app = dash.Dash(external_stylesheets=[dbc.themes.MORPH], suppress_callback_exceptions=True)

# Set initial background style for the main div
initial_style = {
    'background-image': f'url("data:image/png;base64,{encoded_image}")',
    'background-size': 'cover',
    'height': '100vh'
}

app.layout = html.Div([
    html.Div(children=[
        html.Br(),
        html.H1("Project 1: Basketball(NBA)", style={"background-color": "#d9e3f1",
                "opacity": 0.7} ),
        html.Div(children=[
            html.H2('Select a page from the dropdown menu',style={"background-color": "#d9e3f1",
                    "opacity": 0.7}),
            dcc.Dropdown(['Results stats', 'All times NBA table', 'Most/Least NBA stats'],  id='page_type', style={"background-color": "#d9e3f1"})
        ]), 
        html.Div(id='dd-output-container', children=[
            html.P('The page that is chosen from the dropdown menu will be displayed here')
        ])
    ], id='main-content', style=initial_style)
])

# Callback to change the background based on the dropdown selection
@app.callback(
    Output('main-content', 'style'),
    [Input('page_type', 'value')]
)
def update_background(value):
    if value:
        # Apply different style (remove background image) if any dropdown option is selected
        return {'height': '100vh'}
    else:
        # Show the background image if no option is selected
        return initial_style
    
#_____________________________________________________________________________________________________________________________________________
# Callback for dropdown menu with id page_type
@app.callback(
    Output('dd-output-container', 'children'),
    Input('page_type', 'value')
)
# Function for callback, to change layout based on dropdown option 
def update_page_output(value): 
    value_filter = '' 
    result = None #sets result to none to not raise an error when called later in the code

    if value: #if option in dropdown meny is chosen sets value_filter to option (in this case the page type)
        value_filter = value
    
    # Changes the layot depending on the condition
    if value_filter == 'Results stats':
        result = html.Div(
        children=[
            html.Br(),
            html.Plaintext('Choose playing period'),
            dcc.Dropdown(options=results_dd_options, #years list passed onto options variable
                    id='list_type'),
            html.Ul(id='my-list', children=[])
        ])

    elif value_filter == 'All times NBA table':
        result = html.Div(
            children=[
            html.Br(),
            html.H4('All times NBA table'),
            html.Br(),
            dash_table.DataTable(data = nba_table_toDict, #creates a datatable and passes df as data
                        id='datatable-interactivity',
                        columns=[
                            {"name": i, "id": i, "deletable": False, "selectable": False} for i in nba_table_copy.columns], #passes values
                        sort_action="native", #adds sort option to each column
                        page_size = 20,
                        virtualization=True,
                        page_action="none",
                        fixed_rows = {'headers':True},
                        style_cell={'maxWidth': 0, 'backgroundColor': 'transparent', 'border': '1px solid #909090'},
                        style_header=style_header_variable,
                        style_cell_conditional=[{'if': {'column_id': 'Team Name'}, 'width': '25%', 'border': '1px solid grey'},
                                                {'if': {'column_id': 'Rank'}, 'width': '5%', 'border': '1px solid grey'}]
                        )]
            )

    elif value_filter == 'Most/Least NBA stats':
        result = html.Div(
            children=[
                html.Br(),
                html.Plaintext('Choose year: '),
                dcc.Dropdown(options=year_id, id='barchart_year'),  # Dropdown for selecting the year
                html.Div(id='barplot_viz',  # This div will be updated based on the selected year
                )
            ]
        )
                
    return result

#_____________________________________________________________________________________________________________________________________________
# Callback for dropdown menu with most/least matches
@app.callback(
    Output('barplot_viz', 'children'),
    Input('barchart_year', 'value')
)

# Updates div with id barchart viz by year
def update_barByYear(value):
    # Check if the value is None (i.e., no year is selected yet)
    if value is None:
        # Return the default content (which is the initial bar chart)
        return [
            html.Plaintext(children='Number of NBA matches on each date of the year.'),
            dcc.Graph(
                id='nba-game-counts',
                figure={
                    'data': [
                        {'x': game_counts.index, 'y': game_counts.values, 'type': 'bar', 'name': 'NBA Game Counts'},
                    ],
                    'layout': {
                        'xaxis': {
                            'tickvals': [game_counts.index.get_loc(date) for date in game_counts.index if date.endswith('01')],
                            'ticktext': [date[:-2] for date in game_counts.index if date.endswith('01')],
                            'tickangle': 45, 'tickmode': 'array', 'title': 'Date'
                        },
                        'yaxis': {'title': 'Number of matches'},
                        'title': 'Number of NBA matches on each date of the year. Accumulated for all years 1970-2021.',
                        'paper_bgcolor':'rgba(0,0,0,0)', 'plot_bgcolor':'rgba(0,0,0,0)'
                    }
                },
                config={"displayModeBar": False},         # This line removes the modebar    
            )           
        ]
    else:
        year = value #saves value in variable year to create path for file 
        data = pd.read_csv(f'{data_path}/{year}.csv')
        data['date_game'] = pd.to_datetime(data['date_game'])
        df = data.copy(deep=True)
        
        #creates column Result where a value for each row will be stored depending on the condition 
        df.loc[df['visitor_pts'] > df['home_pts'], 'Result'] = 'Away Win'
        df.loc[df['visitor_pts'] < df['home_pts'], 'Result'] = 'Home Win'
        df.loc[df['visitor_pts'] == df['home_pts'], 'Result'] = 'Draw'
        
        result_games = df.groupby(['date_game']).size().reset_index(name='Count') #groups by date to find number of dates(games) and saves into Count column
        
        result = df.groupby(['date_game', 'Result']).size().reset_index(name='Count') #groups by date and counts the number of different outcomes in Result column
        outcome_home = result[result['Result'] == 'Home Win'] #creates df for putcome 'home wins'
        outcome_away = result[result['Result'] == 'Away Win'] #creates df for outcome 'away wins'

        result = html.Div(
                            children=[
                            html.Br(),
                            html.Plaintext(f'Barchart illustrating which days of the year have seen most and least NBA games, away wins and home wins for {year}.\nScroll down for away- and homewins.'),
                            #dcc.RadioItems(options=[{'label': 'outcome_home', 'value': 'outcome_home'}, {'label': 'outcome_away', 'value': 'outcome_away'}, {'label': 'outcome_draw', 'value': 'outcome_draw'}], value='outcome_home', inline=True, id = 'radio_barchart'),
                            dcc.Graph(figure=make_fig(result_games, 'Total games per day', 'Number of games'),config={"displayModeBar": False}), #calles function to create a fig, passed onto varibale figure to display 
                            html.Br(),
                            dcc.Graph(figure=make_fig(outcome_away, 'Total away wins per day','Number of away wins'),config={"displayModeBar": False}), 
                            html.Br(),
                            dcc.Graph(figure=make_fig(outcome_home, 'Total home wins per day', 'Number of home wins'),config={"displayModeBar": False}) 
                            ])
    return result
#_____________________________________________________________________________________________________________________________________________
# Callback for dropdown menu Ordered list
@app.callback(
    Output('my-list', 'children'), #changes output in id barplot_viz
    Input('list_type', 'value') #dropdown with id barchart_year
)

# Function for dropdown menu Ordered list
def update_OrderedList(value):
    if value is None:
        # Return the default content (which is the initial table)
        return [html.Div(children=[html.Br(),
                        html.Plaintext('Table of final score occurrences in games from 1970 to 2021, without distinguishing between home and visitor teams.'),
                        dbc.Row([dbc.Col(html.Div(
                            dash_table.DataTable(
                                id= 'full_results_table', 
                                columns=[{"name": i, "id": i} for i in full_results.columns],
                                data = full_results.to_dict('records'),
                                sort_action='native',
                                virtualization=True,
                                fixed_rows = {'headers':True},
                                page_action="none", style_table=style_table_OT, style_cell=style_cell_variable, style_cell_conditional=[{'if': {'column_id': 'Final Score Set'}, 'width': '20%', 'border': '1px solid grey'},
                                                                                                                                        {'if': {'column_id': 'Total Count'}, 'width': '20%', 'border': '1px solid grey'}],
                                style_header=style_header_variable)), width=8)])])
              ]  
    # Create output if dropdown option is clicked 
    if value:
        type = value #saves value in type (of result) variable
        # Checks if the chosen option is one of the following
        if type in 'Q1 Q2 Q3 Q4': 
            quarter_df = pd.read_csv(f'{cleanData_path}/{type}_table.csv')
            fig = px.scatter(quarter_df, x = 'Points', y='Count', labels={"Points": "Points", "Count": 'Count'}, title='Scatterplot of points distribution')
            fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            )
            # Plotting data into datatable
            result = html.Div(children=[html.Plaintext(f'List of score occurrences in {type} of each match'),
                    dbc.Row([dbc.Col(html.Div(
                            dash_table.DataTable(
                                data=quarter_df.to_dict('records'),  # creates a datatable and passes df as data
                                id='quarter_results',
                                sort_action='native',
                                columns=[{"name": i, "id": i, "deletable": False, "selectable": False} for i in quarter_df.columns], 
                                style_table=style_table_OT, 
                                style_cell={'text-align': 'center', 'backgroundColor': 'transparent', 'border': '1px solid #909090'}, style_header=style_header_variable)), width=4),  # Display quarter_results table in 2 columns
                            dbc.Col(
                                html.Div(
                                    dcc.Graph(figure=fig, config={'displayModeBar': False})), width=8),  # Display scatter plot in 10 columns
                        ]
                        ),
                ])
            
        elif type == 'Overtime':  # checks if the chosen option is overtime then creates a table with OT df
            result = html.Div(
                children=[
            html.Plaintext('List showing how many times each type of overtime has occured in 1970-2021.\nChoose overtime row to display list of score occurrences for each type of overtime.'),
            dbc.Row(
                [
                    dbc.Col(html.Div( children=[
                        dash_table.DataTable(
                            id='overtimeCount_table',
                            columns=[{"name": i, "id": i} for i in overtimeCount.columns],
                            data=overtimeCount.to_dict('records'),
                            sort_action='native', style_table={'display': 'inline-block', 'text-align': 'center'}, style_cell={'text-align': 'center', 'backgroundColor': 'transparent', 'border': '1px solid #909090',}, style_header=style_header_variable)]),width=4),  # Display overtimeCount table in 6 columns
                    dbc.Col(html.Div(id='overtime_results', children=[]), width=4)  # Display overtime_results table in 6 columns
                ]
                    ),
                        ]
                            )
                     
    return result

#_____________________________________________________________________________________________________________________________________________
# Callback for dropdown menu Ordered list
@app.callback(
    Output('overtime_results', 'children'),
    Input('overtimeCount_table', 'active_cell') #dropdown with id barchart_year
)

# Function for dropdown menu Ordered list
def active_cell_uptade(active_cell):
    result=None
    overtime_table=overtimeCount.to_dict('records')
    if active_cell:
        row_index = active_cell.get('row', active_cell.get('row_id', active_cell.get('index')))
        col_index = active_cell['column_id']
        # Access the value of the selected cell index
        cell_value = overtime_table[row_index][col_index]

        if cell_value == 'OT':
            result = dash_table.DataTable(
                            columns=[{"name": i, "id": i} for i in OT.columns],
                            data=OT.to_dict('records'),
                            sort_action='native', style_table={'width': '90%', 'display': 'inline-block', 'text-align': 'center'}, style_cell=style_cell_variable, style_header=style_header_variable)
        elif cell_value == '2OT':
            result = dash_table.DataTable(
                            columns=[{"name": i, "id": i} for i in OT2.columns],
                            data=OT2.to_dict('records'),
                            sort_action='native', style_table={'width': '90%', 'display': 'inline-block', 'text-align': 'center'}, style_cell=style_cell_variable, style_header=style_header_variable)
        elif cell_value == '3OT':
            result = dash_table.DataTable(
                            columns=[{"name": i, "id": i} for i in OT3.columns],
                            data=OT3.to_dict('records'),
                            sort_action='native', style_table={'width': '90%', 'display': 'inline-block', 'text-align': 'center'}, style_cell=style_cell_variable, style_header=style_header_variable), 
        elif cell_value == '4OT':
            result = dash_table.DataTable(
                            columns=[{"name": i, "id": i} for i in OT4.columns],
                            data=OT4.to_dict('records'),
                            sort_action='native', style_table={'width': '90%', 'display': 'inline-block', 'text-align': 'center'}, style_cell=style_cell_variable, style_header=style_header_variable)
        elif cell_value == '5OT':
            result = dash_table.DataTable(
                            columns=[{"name": i, "id": i} for i in OT5.columns],
                            data=OT5.to_dict('records'),
                            sort_action='native', style_table={'width': '90%', 'display': 'inline-block', 'text-align': 'center'}, style_cell=style_cell_variable, style_header=style_header_variable)
        
    return result
        
if __name__ == '__main__':
    app.run_server(debug=True, port=8080)

