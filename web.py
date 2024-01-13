import streamlit as st
from urllib.error import URLError
from io import StringIO
import requests
import pandas as pd
from utils import all_currency_pairs, add_user_currency_pair, currency_statistics
import re
from typing import List, Dict
from streamlit.components.v1 import html
from random import randint

# Streamlit UI
st.title("Currency Data Analysis")

selected_currencies = st.multiselect(
    "Choose currency", [pair for pair in all_currency_pairs.keys() if pair != "Date"], key="selected_currencies"
)


# get data from selected currencies
data = {
    k: v for k, v in all_currency_pairs.items() if k in ["Date"] + selected_currencies
}
# order columns so that Date is first
data_columns_ordered = ["Date"] + list(
    [key for key in all_currency_pairs.keys() if key != "Date"]
)

# create dataframe
currencies_dataframe = st.dataframe(
    data, hide_index=True, column_order=data_columns_ordered
)


# display statistics for selected currencies
st.subheader("Statistics")
for currency in selected_currencies:
    st.write(f"Statistics for {currency}")
    st.write(currency_statistics(all_currency_pairs[currency]))


new_pair = st.text_input('Enter new currency pair in format "EUR/PLN"')
if st.button("Add"):
    if not re.search(r"([a-zA-Z]{3})/([a-zA-Z]{3})", new_pair) or len(new_pair) != 7:
        st.error("Invalid currency pair format")
    else:
        curr_one, curr_two = new_pair.split("/")
        if curr_one == curr_two:
            st.error("Currencies can't be the same")
        else:
            try:
                add_user_currency_pair(new_pair)
                st.success(f"Added {new_pair}")
            except:
                st.error("Cannot add new currency pair")
