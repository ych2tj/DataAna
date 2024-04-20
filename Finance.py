# Get finace data from API of https://financialmodelingprep.com 
import os
import numpy as np
import pandas as pd
import requests
from datetime import datetime
import json

class finance_data:
    customer_url = "http://127.0.0.1:8000/api/shareprices/"
    finance_url = "https://financialmodelingprep.com/api/"
    apikey = "your api key"
    # finance data links
    Symbol_List = "v3/stock/list"
    Historical_Price = "v3/historical-price-full/"
    SP500 = "v3/sp500_constituent"
    NASDAQ = "v3/nasdaq_constituent"
    DowJones = "v3/dowjones_constituent"
    
    def __init__(self):
        #self.daily_chart_eod = "v3/historical-price-full/SPARC.NS" # for debug
        # get my finace API key
        key_path = os.path.join(os.getcwd(), "key.json")
        with open(key_path, 'r') as json_file:
            data = json.load(json_file)
            self.apikey = data['apikey']
            print("Token retrieved from json file: ", self.apikey)
 

    def get_data(self, file_path, data_section, data_info=[]):
        '''
        This program checks if the CSV file's creation date is today. If it is, it opens the CSV file. If not, it fetches 
        data from an API and saves it to a CSV file.
        '''
        if os.path.exists(file_path): # check the CSV file is exist
            if  self._is_created_today(file_path): # Check if CSV file was created today
                print("CSV file was created today.")
                print("Opening CSV file...")
                df = pd.read_csv(file_path)
                print("CSV file is read.")
            else:
                print("CSV file was not created today.")
                df = self._fetch_data(data_section, data_info)
                if df.empty: # if no data found, return empty
                    return df
                else:
                    self.save_to_CSV(df, file_path)
        else:
            print("CSV file was not exist.")
            df = self._fetch_data(data_section, data_info)
            if df.empty: # if no data found, return empty
                    return df
            else:
                self.save_to_CSV(df, file_path)
        return df


    # Function to check if the file was created today
    def _is_created_today(self, file_path):
        creation_time = os.path.getmtime(file_path)
        creation_date = datetime.fromtimestamp(creation_time).date()
        current_date = datetime.now().date()
        return creation_date == current_date


    def _fetch_data(self, data_section, data_info=[]):
        print("Downloading data...")
        api_url = self.finance_url+data_section+self.apikey
        response = requests.get(api_url) # Make a GET request to the API
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
             # Parse the response JSON
            data = response.json()
            # print(data)
        else:
            print(f"Error: Unable to fetch data. Status code: {response.status_code}")
            return pd.DataFrame()
        # Convert json to data frame
        if not data_info:       
            df = pd.json_normalize(data)
        else:
            #df = pd.json_normalize(data, 'historical', ['symbol'])
            df = pd.json_normalize(data, data_info[0])
        df.tail()
        return df


    def save_to_CSV(self, df, file_path):
        print("Save the data...")
        df.to_csv(file_path, index=False)
        print("Data fetched from API and saved to", file_path)


    def fetch_custom_data(self):
        response = requests.get(self.customer_url)
        data = response.json()
        return data


    def send_custom_data(self, date, open, high, low, close, volumn, symbol):
        '''
        Create the customer data
        '''
        # date serialized to json
        date_str = date.strftime('%Y-%m-%d')
        change = round(close-open, 3) # Calculate the change
        changePercent = round(change/open*100, 5) # Calculate the change percentage
        data = {
            "date": date_str,
            "open": open,
            "high": high,
            "low": low,
            "close": close,
            "volumn": volumn,
            "change": change,
            "changePercent": changePercent,
            "symbol": symbol
        }
        response = requests.post(self.customer_url, json=data)
        return response


    def delete_custom_data(self, id):
        '''
        Delete one row data
        '''
        delete_url = self.customer_url+str(id)+'/'
        print(delete_url)
        response = requests.delete(delete_url)
        return response


if __name__ == "__main__":
    # Get current folder path
    current_folder = os.getcwd()
    data_folder = os.path.join(current_folder, "Finance_data")
    csv_file_path = os.path.join(data_folder, 'dayend_price_AAPL.csv') # SPARC_NS
    data_collect = finance_data()
    data_section = data_collect.Historical_Price+'AAPL'#'SPARC.NS'
    df = data_collect.get_data(csv_file_path, data_section, ['historical'])
    print(df)
    # save the data to CSV file
    #data_collect.save_to_CSV(df, csv_file_path)





