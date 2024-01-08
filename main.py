import streamlit as st
from urllib.error import URLError
from io import StringIO
import requests

DAYS_RANGE = 90

API_URL = "https://api.nbp.pl/api/exchangerates/rates/A/{}/last/90/?format=json"
currencies = ["EUR/PLN", "USD/PLN", "CHF/PLN"]


def refresh_currencies():
    data = {}
    for pair in currencies:
        url = API_URL.format(pair[:3])
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
            
            data[pair] = sorted(rates, key=lambda x: x[1])
            
    return data


currencies_data = refresh_currencies()
print(currencies_data)
# currencies_data = 

user_currencies = []

select_value = st.selectbox("Choose currency", currencies)


column_config = {
    'Rate': {'width': 150},
    'Date': {'backgroundColor': '#90ee90'},
}

st.dataframe(currencies_data[select_value], column_config=column_config)



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