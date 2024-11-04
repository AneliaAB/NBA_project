import pandas as pd
import os
import re
import numpy as np

## FULL DF ##
print('Full table in progress..')
# Creating df from all files in data folder
files_list = [] 
team_file_count = {}  # Dictionary to count in how many CSV files each team appears

for file in os.listdir('data'):
    file_df = pd.read_csv(f'data/{file}')
    files_list.append(file_df)
    
    teams_in_file = set(file_df['visitor_team_name'].unique()).union(set(file_df['home_team_name'].unique()))
    for team in teams_in_file:
        if team not in team_file_count:
            team_file_count[team] = 1
        else:
            team_file_count[team] += 1

# Concatenates all files in list to make a df with all files data
full_df = pd.concat(files_list, ignore_index=True)
full_df.to_csv('data_clean/full.csv', index=False)  #saves the data to a csv file
df = full_df.copy(deep=True) #makes copy to save as csv
print('Full table done!')

## HELPER FUNCTIONS FOR NBA TABLE ##
# Helper function to append items to dictionary
def app_dictionary(id, list):
    if id not in dictionary: #checks if column with key already exists 
        dictionary[id] = list
    else:
        dictionary[id].append(list) #if yes, it appends to key value

# Helper function to calculate the wins, losses and draws
def cal_stats(team_name):
    win = 0
    loss = 0
    draw = 0

    for i in home_tuple:
        index = home_tuple.index(i)
        if team_name in i:
            if home_tuple[index][1] > visitor_tuple[index][1]:
                win += 1
            elif home_tuple[index][1] < visitor_tuple[index][1]:
                loss += 1
            else:
                draw += 1

    for i in visitor_tuple:
        index = visitor_tuple.index(i)
        if team_name in i:
            if visitor_tuple[index][1] > home_tuple[index][1]:
                win += 1
            elif visitor_tuple[index][1] < home_tuple[index][1]:
                loss += 1
            else:
                draw += 1

    return win, loss, draw

## CREATING FULL NBA TABLE ##
print('NBA table in progress..')
dictionary ={}
team_names = [i for i in df['visitor_team_name'].unique()] #creates list from all team names

# Make tuples with team name and points 
visitor_tuple = list(zip(df.visitor_team_name, df.visitor_pts))
home_tuple = list(zip(df.home_team_name, df.home_pts))
# Two tuple list combined (to shorten the cal_stats function)
combined_list = visitor_tuple + home_tuple

# Makes dictionary with all team names and sets the value to 0
pts_dictionary = {}
for name in team_names:
        pts_dictionary[name] = 0

# Loops over tuples and adds pts (in order to find full pts for each team)
for i in combined_list: 
    if i[0] in pts_dictionary: #checks for team_name in keys
        pts_dictionary[i[0]] += i[1] #adds points to key value
        
wins = [] 
loss = []
draw = []

for name in team_names:
    win_nr, loss_nr, draw_nr = cal_stats(name)
    wins.append(win_nr)
    loss.append(loss_nr)
    draw.append(draw_nr)

# Appends data to dictionary (using def app_dictionary)
app_dictionary('Team Name', team_names)
app_dictionary('Win', wins)
app_dictionary('Loss', loss)
app_dictionary('Pts', [v for k,v in pts_dictionary.items()])
file_counts = [team_file_count.get(team, 0) for team in team_names]
app_dictionary('Years in NBA', file_counts)
app_dictionary('Draw', draw)

# Makes df from dict
df_full = pd.DataFrame.from_dict(dictionary)

# Prepares data by sorting and adding rank in order of 'wins' descending and adding win rate
df_full['Win Rate(%)'] = df_full.apply(lambda row: round((row.Win / (row.Win + row.Loss + row.Draw)) * 100, 2), axis=1)
#sort df by win
df_full = df_full.sort_values(by='Win', ascending=False) 
#create rank 
df_len = len(df_full['Team Name']) + 1
rank = [i for i in range(1, df_len)]
df_full.insert (0, "Rank", rank)

# Saves df to csv file
df_full.to_csv('data_clean/NBA_table.csv', index=False)
print('NBA table done!')

## FINDS OVERTIME OCCURRANCES ##
print('Overtime frequency table in progress..')
df = full_df.copy(deep=True) #makes new copy of full_df to work with
# Creates dict with all the overtimes and sets all values to zero
dict_OT = {'OT' : 0,
        '2OT' : 0,
        '3OT' : 0,
        '4OT' : 0,
        '5OT' : 0}
# Adds 1 each time a key (overtime) is found in the row 
for row in df['box_id']:
    for key in dict_OT:
        if key in row:
            dict_OT[key] += 1
# Creates dataframe with keys as column 1 and number of OT as column 2
overtime_df = pd.DataFrame()
overtime_df['Overtime'] = [k for k,v in dict_OT.items()] #list comprehension from all keys in dict
overtime_df['Count'] = [v for k,v in dict_OT.items()] #list comprehension from all values in dict

overtime_df.to_csv('data_clean/overtime_table.csv', index=False) #saves df to csv
print('Overtime frequency table done!')

## CREATES DATAFRAME FOR 'RESULTS - FULL RESULTS' MENU ##
print('Full result table in progress..')
df = pd.read_csv('data_clean/full.csv', usecols=['visitor_pts','home_pts'])

df.columns = ['score_1', 'score_2']

combination_counts = df.groupby(['score_1', 'score_2']).size().reset_index(name='Total Count')

combination_counts['Final Score Set'] = list(zip(combination_counts['score_1'], combination_counts['score_2']))

# Create a new DataFrame with 'scores_tuple' and 'count' columns
new_df = combination_counts[['Final Score Set', 'Total Count']]

new_df = new_df.sort_values(by='Total Count', ascending=False)

# Checking if it fits with the original amount of entries
total_count = new_df['Total Count'].sum()

new_df.to_csv('data_clean/total_score_count.csv', index=False)
print('Full result table done!')

## CREATING QUARTER TABLES ##
print('Quarter tables in progress..')
dict_overtime = {'overtime' : []} #creates overtime dict for later

def overtime_append(path, column_names):
    df = pd.read_csv(path)
    Q1 = []
    Q2 = []
    Q3 = []
    Q4 = []

    for column in column_names:
        for row in df[column]:
            # Clean row data
            row_values = row.split(',') #splits numbers in each row by the comma
            row_clean = [int(re.sub('[^\d\w]', '', i)) for i in row_values] 
            # Appends values at indexes 0:3 to list
            Q1.append(row_clean[0])
            Q2.append(row_clean[1])
            Q3.append(row_clean[2])
            Q4.append(row_clean[3])
            # Appends overtime scores to dict_overtime
            if len(row_clean) > 5:
                dict_overtime['overtime'].append(row_clean[4:-1])
    # Returns quarters lists 
    return Q1, Q2, Q3, Q4 

Q1, Q2, Q3, Q4 = overtime_append('data_clean/full.csv', ['visitor_boxscore', 'home_boxscore'])

# Helper function for creating csv file for each quarter
def quarter_table(quarter_number, name):
    quarter_df = pd.DataFrame() 
    unique, counts = np.unique(quarter_number, return_counts=True)
    quarter_df['Points'] = unique
    quarter_df['Count'] = counts
    quarter_df = quarter_df.sort_values(by='Count', ascending=False)
    quarter_df.to_csv(f'data_clean/{name}_table.csv', index=False)

quarter_table(Q1, 'Q1')
quarter_table(Q2, 'Q2')
quarter_table(Q3, 'Q3')
quarter_table(Q4, 'Q4')

print('Quarter tables done!')

## OVERTIME ##
print('Overtime tables in progress..')

OT = []
OT2 = []
OT3 = []
OT4 = []
OT5 = []
# OT6 = []

for value in dict_overtime['overtime']:
    if len(value) == 1:
        OT.append(value[0])
    if len(value) == 2:
        OT2.append(value[1])
    if len(value) == 3:
        OT3.append(value[2])
    if len(value) == 4:
        OT4.append(value[3])
    if len(value) == 5:
        OT5.append(value[4])
    #check for a sixth overtime
    # if len(value) == 6:
    #     OT6.append(value[5])

#checking length (number of overtimes)
#print(len(OT), len(OT2), len(OT3), len(OT4), len(OT5))

# Saves overtime counts as csv file
def OT_df(list, name):
    OT_dictionary = pd.Series(list).value_counts().to_dict() #finds unique values in series and its frequency as a dict
    OT_dictionary = dict(sorted(OT_dictionary.items(), key=lambda x:x[1], reverse=True)) #sorts dict items by value (decreasing)
    OT_df = pd.DataFrame.from_dict({'Points': [k for k,v in OT_dictionary.items()], 'Count': [v for k,v in OT_dictionary.items()]}) #creates dataframe where keys are col 1 and values are col2
    OT_df.to_csv(f'data_clean/{name}_count.csv', index=False) #saves to csv file

OT_df(OT, 'OT')
OT_df(OT2, 'OT2')
OT_df(OT3, 'OT3')
OT_df(OT4, 'OT4')
OT_df(OT5, 'OT5')

print('Overtime tables done!')