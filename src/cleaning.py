"""Reusable, non-destructive preparation rules for the Online Retail dataset."""

from __future__ import annotations

import pandas as pd


def prepare_transaction_data(frame: pd.DataFrame) -> pd.DataFrame:
    """Return an analysis copy with documented transaction-level fields.

    The input is never mutated. Missing identifiers and descriptions are kept;
    customer-level filtering is intentionally handled separately.
    """
    data = frame.copy()
    data.columns = [column.strip() for column in data.columns]
    # Harmonise the source label with the external context source; the raw Excel is untouched.
    data["Country"] = data["Country"].replace({"EIRE": "Ireland"})
    data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"], errors="coerce")
    data["IsCancellation"] = data["InvoiceNo"].astype(str).str.startswith("C")
    data["Revenue"] = data["Quantity"] * data["UnitPrice"]
    data["Year"] = data["InvoiceDate"].dt.year
    data["Month"] = data["InvoiceDate"].dt.to_period("M").astype(str)
    data["DayOfWeek"] = data["InvoiceDate"].dt.day_name()
    data["Hour"] = data["InvoiceDate"].dt.hour
    return data


def customer_view(transaction_data: pd.DataFrame) -> pd.DataFrame:
    """Create the identified-customer view without imputing CustomerID."""
    customer_data = transaction_data.dropna(subset=["CustomerID"]).copy()
    customer_data["CustomerID"] = customer_data["CustomerID"].astype("int64")
    return customer_data
