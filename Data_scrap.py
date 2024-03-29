# Scrap data from wikipedia web page using Buitifulsoup and pandas
import os
from bs4 import BeautifulSoup
import requests
import pandas as pd

def SP500_scrap(file_path=os.path.join(os.getcwd(), "Finance_data", "SP500_list.csv")):
    print("Scrap SP500 Constituents list data from wikipedia....")
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, features="html.parser")

    #table = soup.find_all('table')[1] # Find the first table 
    #print(str(table)[:200]) # display and find the tabel class
    # First table's id="constituents", 2nd table id="changes"
    table = soup.find('table', class_='wikitable sortable', id="constituents")

    # Get the table head
    heads = table.find_all('th') # In html, "th" tab for table heading 
    words_heads = [head.text.strip().lower() for head in heads]
    df = pd.DataFrame(columns=words_heads)
    df.columns.values[2] = 'sector' 
    df.columns.values[3] = 'subSector' 
    
    # Get the table content
    row_data = table.find_all('tr') # "tr" tab for table row
    for row in row_data[1:]: # the first row is empty
        column_data = row.find_all('td') # "td" for table column element
        element_col_data = [data.text.strip() for data in column_data]

        length = len(df) # get the next row index
        df.loc[length] = element_col_data
    #print(df)

    # Save to CSV file
    df.to_csv(file_path)
    print("SP500 Constituents list is saved to"+file_path)

if __name__ == "__main__":
    SP500_scrap()