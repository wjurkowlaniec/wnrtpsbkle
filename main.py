import streamlit as st
from urllib.error import URLError
from io import StringIO
import requests
import pandas as pd

DAYS_RANGE = 90

API_URL = "https://api.nbp.pl/api/exchangerates/rates/A/{}/last/90/?format=json"

currency_list  = ["EUR", "USD", "CHF"]
currency_select = ["EUR/PLN", "USD/PLN", "CHF/PLN"]
currency_convert = ["EUR/USD", "CHF/USD"]

def save_currencies(currency_data):
    for currency in currency_select:
         data_csv = currency_data[currency].to_csv(index=False)
         currency_file_name = currency.replace('/', '_')
         with open(f"data/{currency_file_name}.csv", "w") as f:
             f.write(data_csv)
        
def load_currencies():
    data = {}
    for pair in currency_select:
        pair_filename = pair.replace('/', '_')
        data[pair] = pd.read_csv(f"data/{pair_filename}.csv")
    return data



def refresh_currencies():
    data = {}
    for currency in currency_list:
        url = API_URL.format(currency[:3])
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            st.error(f"Error: {err}")
        except URLError as err:
            st.error(f"Error: {err}")
        else:
            rates_raw = response.json()["rates"]
            rates = [(rate["mid"], rate["effectiveDate"]) for rate in rates_raw]
            data[f"{currency}/PLN"] = pd.DataFrame(rates, columns=["Rate","Date"])
            
    
    return data

try:
    currencies_data = load_currencies()
except:
    currencies_data = refresh_currencies()
    save_currencies(currencies_data)

    
# refresh_currencies()

user_currencies = []

select_value = st.selectbox("Choose currency", currency_select)


currencies_dataframe = st.dataframe(currencies_data[select_value], hide_index=True)
# st.dataframe(currencies_dataframe.style.hide(axis="index"))
# st.dataframe(currencies_dataframe, hide_index=True)

if st.button("Refresh data"):
    refresh_currencies()
    save_currencies()


# "
# try:
    
#     # df = 
#     countries = st.multiselect(
#         "Choose countries", list(df.index), ["China", "United States of America"]
#     )
#     if not countries:
#         st.error("Please select at least one country.")
#     else:
#         data = df.loc[countries]
#         data /= 1000000.0
#         st.write("### Gross Agricultural Production ($B)", data.sort_index())

#         data = data.T.reset_index()
#         data = pd.melt(data, id_vars=["index"]).rename(
#             columns={"index": "year", "value": "Gross Agricultural Product ($B)"}
#         )
#         chart = (
#             alt.Chart(data)
#             .mark_area(opacity=0.3)
#             .encode(
#                 x="year:T",
#                 y=alt.Y("Gross Agricultural Product ($B):Q", stack=None),
#                 color="Region:N",
#             )
#         )
#         st.altair_chart(chart, use_container_width=True)
# except URLError as e:
#     st.error(
#         """
#         **This demo requires internet access.**
#         Connection error: %s
#     """
#         % e.reason
#     )"