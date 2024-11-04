#pip install pandas beautifulsoup4 lxml requests
import time
import pandas as pd
from bs4 import BeautifulSoup, Comment
from urllib.request import urlopen
import requests

last_request_time = time.time()
# Function for optimizing speed performance 
def dynamic_sleep():
    # Calculate the time elapsed since the last request
    elapsed_time = time.time() - last_request_time
    
    # If less than 3 seconds have passed, sleep for the remaining time
    if elapsed_time < 3:
        time.sleep(3 - elapsed_time)

# Function that appends to dictionary (to avoid repeating lines of code)
def app_dictionary(id, list):
    if id not in dictionary: #checks if column with key already exists 
        dictionary[id] = []
        dictionary[id].append(list)
    else:
        dictionary[id].append(list) #if yes, it appends to key value

for y in range(2020,2022): #loops over schedual and results for years in range
    # Try except added for handling errors when loading url
    try:
        url = f"https://www.basketball-reference.com/leagues/NBA_{y}_games.html"
        html = urlopen(url)
    except:
        print(f'Error accured when loading url for year {y} - {url}')
    else:
        soup = BeautifulSoup(html, 'lxml')

    links = soup.findAll('div', {'class', 'filter'}, 'a')
    #we scraped the text in
    months = [a.getText() for a in soup.find('div', {'class', 'filter'}).findAll('a')]

    # Creating a dictionary with the data we want to scrape
    dictionary = {'date_game':[],
                'visitor_team_name':[],
                'visitor_pts':[],
                'home_team_name':[],
                'home_pts':[],
                'box_score_text': [],
                'arena_name':[]}

    dynamic_sleep()
    last_request_time = time.time() 

    # Loops over months for the year y
    for month in months:
        month = month.lower() #makes month lower case
        # Try except added for handling errors when month names include the year e.g. month 'october 2019' and 'october 2020'. this happens when we loop over season 2020 -> https://www.basketball-reference.com/leagues/NBA_2020_games.html)
        #This catches an error when the url is not found. When exception accures it replaces the ' ' with '-' e.g. 'october 2019' to 'october-2019'
        #Then it creates a url and a soup oject with the new month variable 'error_month' and is then able to execute the rest of for loop
        #The month is written in the "error month" text file, to keep track of the pages that raised an error 
        #If error is not raised it continues to else statement and executes the rest of the for loop 
        try: 
            url_month = f"https://www.basketball-reference.com/leagues/NBA_{y}_games-{month}.html" #putting the right year and month into link
            html_month = urlopen(url_month)
        except:
            print(f'Error when scraping month {month}')
            with open('/home/ucloud/NBAproject/final/error months.txt', 'a') as f:
                f.write(f'\n {month}')
            error_month = month.replace(' ', '-')
            url_error_month = f"https://www.basketball-reference.com/leagues/NBA_{y}_games-{error_month}.html"
            html_month = urlopen(url_error_month)
            soup = BeautifulSoup(html_month, 'lxml')
        else:
            soup = BeautifulSoup(html_month, 'lxml') #creating soup object
        
        # Looping over dictionary keys and appending scraped data into values
        for attr, value in dictionary.items():
            if attr == 'date_game':
                rows = soup.findAll('th',attrs={'data-stat':f'{attr}'}) #scraping date 
                for row in rows: #looping over each row to get the 
                    data_text = row.text
                    dictionary[f'{attr}'].append(data_text.replace(',', ''))
            elif attr == 'box_score_text': 
                rows = soup.findAll('td',attrs={'data-stat':f'{attr}'}) #scraping links for box score to loop over later
                for row in rows:
                    data = row.a.get('href') 
                    dictionary[f'{attr}'].append(data)
            else:
                rows = soup.findAll('td',attrs={'data-stat':f'{attr}'}) #scraping the rest of the data
                for row in rows: 
                    data = row.text
                    dictionary[f'{attr}'].append(data)
        print(dictionary)
        dynamic_sleep()
        last_request_time = time.time() 
    
    # Deleting date strings from date dict 
    for value in dictionary['date_game']: 
        if value == 'Date': 
            dictionary['date_game'].remove(value)
    
    for link in dictionary['box_score_text']:
        try:
            url_month_box = f"https://www.basketball-reference.com{link}" #putting the right year and month into link
            response = requests.get(url_month_box)
        except:
            print(f"Error accured when scraping box score link {link}")
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
        #https://stackoverflow.com/questions/33138937/how-to-find-all-comments-with-beautiful-soup
        comment_sections = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment_section in comment_sections:
            # Parse the content of the comment as HTML
            comment_soup = BeautifulSoup(comment_section, 'html.parser')

            # Finds the HTML elements containing comments within the comment section
            table_elements = comment_soup.find('table', id='line_score') 

            # Extracts table content using list comprehensions
            if table_elements:
                headers = [th.get_text() for th in table_elements.find_all('th', scope = 'col')[1:]]
                pts = [td.get_text() for td in table_elements.find_all('td')]
                
        middle_index = int(len(pts)/2) #finds middle index to use for slicing
        # Split the points list into visitor (first half) and home (second half)
        pts_visitor = pts[:middle_index] #first half
        pts_home = pts[middle_index:] #second half

        # Calling function for appending to dictionary
        app_dictionary('box_id', headers)
        app_dictionary('visitor_boxscore', pts_visitor)
        app_dictionary('home_boxscore', pts_home)

        dynamic_sleep()
        last_request_time = time.time() 

    # Try except added to catch erros when transforming dict to pandas dataframe, e.g. when columns are not the same lenght
    try:
        df = pd.DataFrame.from_dict(dictionary)
    except:
        print(f'Couldnt save pd for year {y}')
    else:
        df.to_csv(f'/home/ucloud/NBAproject/final/data/{y}.csv', index=False)
    finally:
        print(f'Year {y} completed')
