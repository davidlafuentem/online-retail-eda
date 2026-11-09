"""External context used to normalise country comparisons."""

from __future__ import annotations

import requests
import pandas as pd


WORLD_BANK_URL = (
    "https://api.worldbank.org/v2/country/all/indicator/"
    "SP.POP.TOTL?date=2011&format=json&per_page=400"
)


def fetch_country_population(year: int = 2011) -> pd.DataFrame:
    """Fetch World Bank population estimates for the dataset period."""
    url = WORLD_BANK_URL.replace("date=2011", f"date={year}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    payload = response.json()
    rows = [
        {
            "WorldBankCountry": item["country"]["value"],
            "Population": item["value"],
        }
        for item in payload[1]
        if item.get("value") is not None
    ]
    return pd.DataFrame(rows)


def country_name_for_merge(country: str) -> str:
    """Map source-specific labels to World Bank country names where needed."""
    return {"EIRE": "Ireland"}.get(country, country)
