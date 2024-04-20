# Data dashboard from the finance API datasets
import os
import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import warnings

from Finance import finance_data
from Data_scrap import SP500_scrap
warnings.filterwarnings('ignore')

fnc_data = finance_data() # Build finance data object

st.set_page_config(page_title="Finance Data Dash Board", page_icon=":sparkles:", layout="wide")
st.title(" :bar_chart: Finance Data Dash Board")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# Get symbol list data
data_path = os.path.join(os.getcwd(), "Finance_data", "SymbolList.csv")
syn_list = fnc_data.get_data(data_path, fnc_data.Symbol_List)

# Create a side bar for filter
st.sidebar.header(" :receipt: Choose your filter from symbol list: ")
# Filter for exchange
exchange = st.sidebar.multiselect(":golf: Pick your Exchange", syn_list["exchange"].unique())
if not exchange:
    syn_list2 = syn_list.copy()
else:
    syn_list2 = syn_list[syn_list["exchange"].isin(exchange)]
# Filter for symbol name (.unique() is for removing the duplicate info.)
syn_name1 = st.sidebar.multiselect(" :rainbow-flag: Pick the Symbol (Only choose one)", syn_list2["symbol"].unique())

st.sidebar.header(" :receipt: Choose your filter from American Constituents: ")
index_list = ["NASDAQ", "Dow Jones", "S&P500 (no update)"]
cnt_index = st.sidebar.multiselect(":golf: Pick your Index ", index_list)
cnt_list = pd.DataFrame()
if cnt_index == ['NASDAQ']:
    data_path = os.path.join(os.getcwd(), "Finance_data", "NasdaqList.csv")
    cnt_list = fnc_data.get_data(data_path, fnc_data.NASDAQ)
elif cnt_index == ['Dow Jones']:
    data_path = os.path.join(os.getcwd(), "Finance_data", "DowJonesList.csv")
    cnt_list = fnc_data.get_data(data_path, fnc_data.DowJones)
elif cnt_index == ['S&P500 (no update)']: 
    # The S&P500 is not free from the finance API web, so scrap from the wikipedia
    data_path = os.path.join(os.getcwd(), "Finance_data", "SP500List.csv")
    if not os.path.exists(data_path):
        SP500_scrap(data_path)
    cnt_list = pd.read_csv(data_path)

# Filter for sector
if cnt_list.empty:
    sector = []
else:
    sector = st.sidebar.multiselect(":golf: Pick your Sector", cnt_list["sector"].unique())
if not sector:
    sector_list = cnt_list.copy()
else:
    sector_list = cnt_list[cnt_list["sector"].isin(sector)]

# Filter for sub-sector
if sector_list.empty:
    sub_sect = sector.copy()
else:
    sub_sect = st.sidebar.multiselect(":golf: Pick your Sub-Sector", sector_list["subSector"].unique())
if not sub_sect:
    sub_sect_list = sector_list.copy()
else:
    sub_sect_list = sector_list[sector_list["subSector"].isin(sub_sect)]
    
# Fiter our the symbol
if sub_sect_list.empty:
    syn_name2 = sub_sect.copy()
else:
    syn_name2 = st.sidebar.multiselect(" :rainbow-flag: Pick the Symbol (Only choose one)", sub_sect_list["symbol"].unique())

#print(syn_name)
if syn_name1:
    flt_syn = syn_name1[0]
elif syn_name2:
    flt_syn = syn_name2[0]
else:
    flt_syn = "AAPL"

# Get the stock full price history
data_path = os.path.join(os.getcwd(), "Finance_data", "dayend_price_"+flt_syn+".csv")
data_section = fnc_data.Historical_Price+flt_syn
sym_price = fnc_data.get_data(data_path, data_section, data_info=['historical']) # full data
if sym_price.empty:
    st.subheader("Sorry, no data found, only USA stock is free...")
else:
    cl1, cl2 = st.columns((2))
    # convert date to pd format
    sym_price["date"] = pd.to_datetime(sym_price["date"], format='mixed', dayfirst=True) 
    # Get the min and max date
    start_date = pd.to_datetime(sym_price["date"]).min()
    end_date = pd.to_datetime(sym_price["date"]).max()
    # Show the data under tha date control
    with cl1:
        date1 = pd.to_datetime(st.date_input("Start Date", start_date))
    with cl2:
        date2 = pd.to_datetime(st.date_input("End Date", end_date))
    sym_price = sym_price[(sym_price["date"] >= date1) & (sym_price["date"] <= date2)].copy()
    # Timeline selection for choosing start time
    start_date_index = st.slider("Choose start time", min_value=0, max_value=len(sym_price) - 1, step=1)
    # Filter data based on selected start time
    sym_price = sym_price.iloc[start_date_index:]
    # show the line chart for time series analysis
    st.subheader(f'{flt_syn} Time Series Analysis')
    linechart = pd.DataFrame(sym_price).reset_index()
    fig = px.line(linechart, x='date', y=['high', 'low', 'close'], title='Time series price analysis', labels={'Time': 'date', 'value': 'Price'},
                  color_discrete_map={'high': 'red', 'low': 'green', 'close': 'blue'})
    st.plotly_chart(fig, use_container_width=True)
    '''
    # show the symbol price table
    df_smp = sym_price[0:10]
    fig = ff.create_table(df_smp, colorscale="rainbow")
    st.plotly_chart(fig, use_container_width=True)
    '''

# Build the custom data
st.header("The customer share pirce")
custom_data = fnc_data.fetch_custom_data()
with st.expander("Customer data table"):
    if custom_data:
        custom_df = pd.DataFrame(custom_data).reset_index()
        syn_list = custom_df['symbol'].unique()
        if len(syn_list) == 1:
            st.dataframe(custom_df)
        else:
            customer_syn_name = st.multiselect("Pick the Symbol (Only choose one)", syn_list)
            custom_df = custom_df[custom_df['symbol'].isin(customer_syn_name)]
            st.dataframe(custom_df)

with st.expander("Customer data line chart"):    
    if custom_data:
        custom_df = pd.DataFrame(custom_data).reset_index()
        syn_list2 = custom_df['symbol'].unique()
        if len(syn_list2) == 1:
            fig = px.scatter(custom_df, x='date') # Build statter plot
            # Add scatter traces
            fig.add_scatter(x=custom_df['date'], y=custom_df['low'], mode='lines+markers', name = 'Low')
            fig.add_scatter(x=custom_df['date'], y=custom_df['high'], mode='lines+markers', name = 'High')
            fig.add_scatter(x=custom_df['date'], y=custom_df['close'], mode='lines+markers', name = 'Close')
            fig.update_layout(title='Customer share prices', xaxis_title='Date', yaxis_title='Prices', legend_title='Price Type')
            st.plotly_chart(fig, use_container_width=True)
        if len(syn_list2) >= 2:
            customer_syn_name = st.multiselect(" :rainbow-flag: Pick the Symbol (Only choose one)", syn_list2)
            custom_df = custom_df[custom_df['symbol'].isin(customer_syn_name)]
            fig = px.scatter(custom_df, x='date') # Build statter plot
            # Add scatter traces
            fig.add_scatter(x=custom_df['date'], y=custom_df['low'], mode='lines+markers', name = 'Low')
            fig.add_scatter(x=custom_df['date'], y=custom_df['high'], mode='lines+markers', name = 'High')
            fig.add_scatter(x=custom_df['date'], y=custom_df['close'], mode='lines+markers', name = 'Close')
            fig.update_layout(title='Customer share prices', xaxis_title='Date', yaxis_title='Prices', legend_title='Price Type')
            st.plotly_chart(fig, use_container_width=True)


with st.expander("Enter your share price"):
    date = st.date_input("Choose the price date") # date need to be json serialized
    open = st.number_input("Enter the open price")
    high = st.number_input("Enter the high price")
    low = st.number_input("Enter the low price")
    close = st.number_input("Enter the close price")
    volumn = st.number_input("Enter the volumn", step=1)
    symbol = st.text_input("Enter the symbol")

    if st.button("Submit"):
        response = fnc_data.send_custom_data(date, open, high, low, close, volumn, symbol)
        if response.status_code == 201:
            st.success("New customer data created")
        else:
            st.error("Something went wrong")

with st.expander("Delete one data"):
    id = st.number_input("Enter the data row id", step=1)
    if st.button("Delete submit"):
        response = fnc_data.delete_custom_data(id)
        if response.status_code == 204:
            st.success("Successfully delete the row")
        else:
            st.error("Something went wrong")
