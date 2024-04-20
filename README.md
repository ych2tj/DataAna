# DataAna
Learning of data analysis. Using financial dataset from [Finacial Modeling Prep | FMP](https://site.financialmodelingprep.com/) to build data dashboard to vistualize share market prices. Scraping S&P500 Constituents list from wikipedia [website](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).
## Run the code
`streamlit run dataDB_main.py`

The example the interface:
<p style="text-align:center;"><img src="images/data_dashboard.JPG" width="1600" alt="Original"/></p>

## Operatio of the data API to build customer data
These functions connect to data API from [DataAPI](https://github.com/ych2tj/DataAPI). The Operation includes four expanders:
<p style="text-align:center;"><img src="images/Custom_data_4expenders.JPG" width="1600" alt="Original"/></p>

Two expanders display the data table and scatter charts for similar symbol.
<p style="text-align:center;"><img src="images/Custom_data_table_scatter.JPG" width="1600" alt="Original"/></p>

The other two expanders operate the API to input and delete data.
<p style="text-align:center;"><img src="images/Custom_data_input_delete.JPG" width="1600" alt="Original"/></p>

## Acknowledgement
The streamlit tutorial is in [here](https://www.youtube.com/watch?v=7yAw1nPareM)
Source code and the CSV data is under the video caption.

`streamlit run dataDB_learn.py`
