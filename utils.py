import streamlit as st
from urllib.error import URLError
from requests.exceptions import ConnectionError
import pandas as pd
import requests
from typing import Dict, List
from statistics import median, mean


# Constants
DAYS_RANGE = 90
API_URL = "https://api.nbp.pl/api/exchangerates/rates/A/{}/last/90/?format=json"

BASE_PAIRS = ["EUR/PLN", "USD/PLN", "CHF/PLN", "EUR/USD", "CHF/USD", "PLN/EUR"]

currency_to_pln = {}  # currency data in relation to PLN
currency_pair_data = {}  # currency pair data  from default config
user_currency_pairs = []  # currency pairs from user-added currencies
user_currency_pair_data = {}  # currency pair data from user-added currencies


def currency_statistics(currency_data: List) -> Dict:
    return {
        "avg": mean(currency_data),
        "min": min(currency_data),
        "max": max(currency_data),
        "median": median(currency_data),
    }


def refresh_currencies_from_api(currency_list: List[str]) -> Dict:
    data = {"Date": []}
    for currency in currency_list:
        url = API_URL.format(currency)
        try:
            response = requests.get(url)
            response.raise_for_status()
        except (requests.exceptions.HTTPError, ConnectionError) as err:
            st.error(f"Error connecting to NBP API")
            raise
        except URLError as err:
            st.error(f"Error: {err}")
            raise
        else:
            rates_raw = response.json()["rates"]
            data[f"{currency}"] = [rate["mid"] for rate in rates_raw]
            data["Date"] = [rate["effectiveDate"] for rate in rates_raw]
    return data


def calculate_intermediate_currencies(currency_pairs: List[str]) -> Dict:
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
    currency_to_pln.update(refresh_currencies_from_api(missing_currencies))

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


def add_user_currency_pair(currency_pair):
    global user_currency_pairs, user_currency_pair_data, all_currency_pairs
    user_currency_pairs.append(currency_pair)
    user_currency_pair_data = calculate_intermediate_currencies(user_currency_pairs)
    all_currency_pairs = user_currency_pair_data | currency_pair_data
    all_currency_pairs = collect_all(all_currency_pairs)


def collect_all(currency_pairs):
    # Collect currencies from both base data and collected pairs so far
    global currency_to_pln
    for curr in currency_to_pln.keys():
        if curr == "Date":
            continue
        currency_pairs[f"{curr}/PLN"] = currency_to_pln[curr]
    return currency_pairs


def initialize():
    global all_currency_pairs, currency_pair_data
    currency_pair_data = calculate_intermediate_currencies(BASE_PAIRS)
    all_currency_pairs = currency_pair_data | user_currency_pair_data
    all_currency_pairs = collect_all(all_currency_pairs)


initialize()
