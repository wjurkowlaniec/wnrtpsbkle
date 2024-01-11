import streamlit as st
from urllib.error import URLError
import pandas as pd
import requests

DAYS_RANGE = 90

API_URL = "https://api.nbp.pl/api/exchangerates/rates/A/{}/last/90/?format=json"

base_pairs = ["EUR/PLN", "USD/PLN", "CHF/PLN", "EUR/USD", "CHF/USD", "PLN/EUR"]

def refresh_currencies_api(currency_list):
    data = {"Date": []}
    for currency in currency_list:
        url = API_URL.format(currency)
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Erorr")
            st.error(f"Error: {err}")
        except URLError as err:
            st.error(f"Error: {err}")
            print("Erorr2")
        else:
            rates_raw = response.json()["rates"]
            data[f"{currency}"] = [rate["mid"] for rate in rates_raw]
            data["Date"] = [rate["effectiveDate"] for rate in rates_raw]
    return data


currency_to_pln = {}


def calculate_intermediate_currencies(currency_pairs):
    global currency_to_pln
    # get missing currencies to fetch
    pairs = {}
    currency_list = set(
        [
            currency
            for pair in currency_pairs
            for currency in pair.split("/")
            if currency != "PLN"
        ]
    )
    missing_currencies = list(currency_list) - currency_to_pln.keys()
    currency_to_pln.update(refresh_currencies_api(missing_currencies))
    # calculate intermediate currencies
    for currency_pair in currency_pairs:
        base_currency, target_currency = currency_pair.split("/")
        if target_currency == "PLN":
            continue
        if base_currency == "PLN":
            pairs[currency_pair] = pd.Series(
                [1 / x for x in currency_to_pln[target_currency]]
            )
        else:
            pairs[currency_pair] = pd.Series(
                currency_to_pln[base_currency]
            ) / pd.Series(currency_to_pln[target_currency])
        pairs["Date"] = currency_to_pln["Date"]
    return pairs


currency_pair_data = calculate_intermediate_currencies(base_pairs)
print(list(currency_pair_data.keys()))


user_currency_pairs = ["EUR/USD", "CHF/INR", "INR/CHF"]
user_currency_pair_data = calculate_intermediate_currencies(user_currency_pairs)
print(list(user_currency_pair_data.keys()) + list(currency_pair_data.keys()))


def collect_all(currency_pairs):
    # Collect currencies from both base data and collected pairs so far
    global currency_to_pln
    for curr in currency_to_pln.keys():
        if curr == "Date": 
            continue
        currency_pairs[f"{curr}/PLN"] = currency_to_pln[curr]
    return currency_pairs

print(collect_all(user_currency_pair_data | currency_pair_data).keys())
