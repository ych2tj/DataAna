# Data dashboard from the finance API datasets
import os
import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import warnings

from Finance import finance_data
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
index_list = ["NASDAQ", "Dow Jones"]
cnt_index = st.sidebar.multiselect(":golf: Pick your Index ", index_list)
cnt_list = pd.DataFrame()
if cnt_index == ['NASDAQ']:
    data_path = os.path.join(os.getcwd(), "Finance_data", "NasdaqList.csv")
    cnt_list = fnc_data.get_data(data_path, fnc_data.NASDAQ)
elif cnt_index == ['Dow Jones']:
    data_path = os.path.join(os.getcwd(), "Finance_data", "DowJonesList.csv")
    cnt_list = fnc_data.get_data(data_path, fnc_data.DowJones)

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


