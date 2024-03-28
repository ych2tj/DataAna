# learing of using Streamlit, plotly and pandas to build data dashboard
import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Data Dash Board", page_icon=":sparkles:", layout="wide")

st.title(" :bar_chart: SuperStore Data Dashboard")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

file = st.file_uploader(":file_folder: Upload a file", type=(["csv","xlsx","xls","json"]))
if file is not None:
    file_name = file.name
    st.write(file_name)
    dfl = pd.read_csv(file_name, encoding = "ISO-8859-1")
else:
    os.chdir(r"E:\Work\Projects\DataAna")
    dfl = pd.read_csv("Superstore.csv", encoding = "ISO-8859-1")

cl1, cl2 = st.columns((2))
dfl["Order Date"] = pd.to_datetime(dfl["Order Date"], format='mixed', dayfirst=True)
# Get the min and max date
start_date = pd.to_datetime(dfl["Order Date"]).min()
end_date = pd.to_datetime(dfl["Order Date"]).max()
# Show the data under tha date control
with cl1:
    date1 = pd.to_datetime(st.date_input("Start Date", start_date))
with cl2:
    date2 = pd.to_datetime(st.date_input("End Date", end_date))
dfl = dfl[(dfl["Order Date"] >= date1) & (dfl["Order Date"] <= date2)].copy()

# Create a side bar for filter
st.sidebar.header(" :receipt: Choose your filter: ")
# Filter for region
region = st.sidebar.multiselect(":golf: Pick your Region", dfl["Region"].unique())
if not region:
    dfl2 = dfl.copy()
else:
    dfl2 = dfl[dfl["Region"].isin(region)]
# Filter for state (.unique() is for removing the duplicate info.)
state = st.sidebar.multiselect(" :rainbow-flag: Pick the State", dfl2["State"].unique())
if not state:
    dfl3 = dfl2.copy()
else:
    dfl3 = dfl2[dfl2["State"].isin(state)]
# Filter for city
city = st.sidebar.multiselect(" :city_sunset: Pick the City", dfl3["City"].unique())

# Filter out the data based on region, state and city
if not region and not state and not city:
    flt_df = dfl
elif not state and not city:
    flt_df = dfl[dfl["Region"].isin(region)]
elif not region and not city:
    flt_df = dfl[dfl["State"].isin(state)]
elif state and city:
    flt_df = dfl3[dfl["State"].isin(state) & dfl3["City"].isin(city)]
elif region and city:
    flt_df = dfl3[dfl["Region"].isin(region) & dfl3["City"].isin(city)]
elif region and state:
    flt_df = dfl3[dfl["Region"].isin(region) & dfl3["State"].isin(state)]
elif city:
    flt_df = dfl3[dfl3["City"].isin(city)]
else:
    flt_df = dfl3[dfl3["Region"].isin(region) & dfl3["State"].isin(state) & dfl3["City"].isin(city)]

ctg_df = flt_df.groupby(by=["Category"], as_index = False)["Sales"].sum()
with cl1:
    st.subheader("Category wise Salses")
    fig = px.bar(ctg_df, x = "Category", y = "Sales", text = ['{:,.2f}'.format(x) for x in ctg_df["Sales"]], 
                 template = "seaborn")
                 
    st.plotly_chart(fig, use_container_width=True, height = 200)
with cl2:
    st.subheader("Region wise Salses")
    fig = px.pie(flt_df, values = "Sales", names = "Region", hole = 0.1)
    fig.update_traces(text = flt_df["Region"], textposition = "outside")
    st.plotly_chart(fig, use_container_width=True)

# View and download data with different expander
clm1, clm2 = st.columns(2)
with clm1:
    with st.expander("Category_ViewData"):
        st.write(ctg_df.style.background_gradient(cmap="Blues"))
        csv = ctg_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name = "Category.csv", mime = "text/csv",
                           help = "Click here to download the data as a CSV file")
with clm2:
    with st.expander("Region_ViewData"):
        rg_view = flt_df.groupby(by = "Region", as_index = False)["Sales"].sum()
        st.write(rg_view.style.background_gradient(cmap="Oranges"))
        csv = rg_view.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name = "Region.csv", mime = "text/csv",
                           help = "Click here to download the data as a CSV file")    

# Add time series analysis
flt_df["year_month"] = flt_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')
linechart = pd.DataFrame(flt_df.groupby(flt_df["year_month"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x = "year_month", y="Sales", labels = {"Sales": "Amount"}, height=500, width=1000,
               template="gridon")
st.plotly_chart(fig2, use_container_width=True)
# set a bar to download the data
with st.expander("Get data of timeseries:"):
    st.write(linechart.T.style.background_gradient(cmap="Oranges")) # an warning: Serialization of dataframe to arrow
    csv = linechart.to_csv(index = False).encode('utf-8')
    st.download_button("Download Data", data=csv, file_name = "Timeseries.csv", mime = "text/csv",
                           help = "Click here to download the data as a CSV file") 

# Crate a tree map based on Region, Category and sub-category 
st.subheader("Hierarchical view of Sales using Treemap")
fig3 = px.treemap(flt_df, path = ["Region", "Category", "Sub-Category"], values="Sales", hover_data=["Sales"],
                  color="Sub-Category")
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

# chart for segment and category
cht1, cht2 = st.columns((2))
with cht1:
    st.subheader('Segment wise Sales')
    fig = px.pie(flt_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(text=flt_df["Segment"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)
with cht2:
    st.subheader('Category wise Sales')
    fig = px.pie(flt_df, values="Sales", names="Category", template="gridon")
    fig.update_traces(text=flt_df["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)    

# Create table to show some samples
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary Table"):
    df_smp = dfl[0:10][["Region","State","City","Category","Sales","Profit","Quantity"]]
    fig = ff.create_table(df_smp, colorscale="rainbow")
    st.plotly_chart(fig, use_container_width=True)
 
    st.markdown("Month wise Sub-Category Table")
    flt_df["month"] = flt_df["Order Date"].dt.month_name()
    sub_ctg_year = pd.pivot_table(data=flt_df, values="Sales", index=["Sub-Category"], columns="month")
    st.write(sub_ctg_year.style.background_gradient(cmap="Blues"))

# Build a scatter plot
sct_chart = px.scatter(flt_df, x="Sales", y="Profit", size="Quantity")
sct_chart['layout'].update(title="Relationship between Sales and Profits using Scatter Plot.",
                           titlefont=dict(size=22), xaxis=dict(title="Sales", titlefont=dict(size=18)),
                           yaxis=dict(title="Profit", titlefont=dict(size=18)))
st.plotly_chart(sct_chart, use_container_width=True)

# View the whole data
with st.expander("View Data"):
    st.write(flt_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))

# Download the whole datset
csv = dfl.to_csv(index = False).encode('utf-8')
st.download_button('Download Data', data=csv, file_name="Data.csv", mime="text/csv")