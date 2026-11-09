"""Audits for cancellation exposure with explicit invoice-level denominators."""

from __future__ import annotations

import numpy as np
import pandas as pd


NON_MERCHANDISE_CODES = {
    "AMAZONFEE", "B", "BANK CHARGES", "C2", "CRUK", "D", "DOT", "M", "POST", "S",
    "gift_0001_10", "gift_0001_20", "gift_0001_30", "gift_0001_40", "gift_0001_50",
}


def _assert_close(actual: float, expected: float, label: str, tolerance: float = 0.01) -> None:
    if not np.isclose(actual, expected, atol=tolerance, rtol=0):
        raise AssertionError(f"Cancellation reconciliation failed for {label}: {actual} != {expected}")


def cancellation_audit(data: pd.DataFrame, minimum_country_invoices: int = 20) -> dict[str, pd.DataFrame | float]:
    """Return monthly, country and physical-product cancellation audit tables.

    A cancellation is an invoice whose identifier starts with ``C``. The tables do not claim that
    these records are customer returns; they describe the source coding and retain operational
    concepts separately from physical products.
    """
    cancellations = data.loc[data["IsCancellation"]].copy()
    gross_sales = data.loc[
        (~data["IsCancellation"]) & (data["Quantity"] > 0) & (data["UnitPrice"] > 0)
    ].copy()

    invoice_status = (
        data.groupby("InvoiceNo", as_index=False)
        .agg(CancelledInvoice=("IsCancellation", "max"), Country=("Country", "first"), Month=("Month", "first"))
    )

    monthly_value = (
        data.assign(
            GrossSales=np.where(
                (~data["IsCancellation"])
                & (data["Quantity"] > 0)
                & (data["UnitPrice"] > 0),
                data["Revenue"],
                0,
            ),
            CancelledValue=np.where(data["IsCancellation"], data["Revenue"].abs(), 0),
        )
        .groupby("Month", as_index=False)
        .agg(GrossSales=("GrossSales", "sum"), CancelledValue=("CancelledValue", "sum"))
    )
    monthly_invoices = (
        invoice_status.groupby("Month", as_index=False)
        .agg(TotalInvoices=("InvoiceNo", "nunique"), CancelledInvoices=("CancelledInvoice", "sum"))
    )
    monthly = monthly_value.merge(monthly_invoices, on="Month", how="left")
    monthly["InvoiceCancellationRatePct"] = monthly["CancelledInvoices"] / monthly["TotalInvoices"] * 100
    monthly["CancellationValueRatePct"] = monthly["CancelledValue"] / monthly["GrossSales"] * 100

    country_value = (
        data.assign(
            GrossSales=np.where(
                (~data["IsCancellation"])
                & (data["Quantity"] > 0)
                & (data["UnitPrice"] > 0),
                data["Revenue"],
                0,
            ),
            CancelledValue=np.where(data["IsCancellation"], data["Revenue"].abs(), 0),
        )
        .groupby("Country", as_index=False)
        .agg(GrossSales=("GrossSales", "sum"), CancelledValue=("CancelledValue", "sum"))
    )
    country_invoices = (
        invoice_status.groupby("Country", as_index=False)
        .agg(TotalInvoices=("InvoiceNo", "nunique"), CancelledInvoices=("CancelledInvoice", "sum"))
    )
    country = country_invoices.merge(country_value, on="Country", how="outer").fillna(0)
    country["InvoiceCancellationRatePct"] = country["CancelledInvoices"] / country["TotalInvoices"] * 100
    country["CancellationValueRatePct"] = country["CancelledValue"] / country["GrossSales"].replace(0, np.nan) * 100
    country["ComparableExposure"] = country["TotalInvoices"] >= minimum_country_invoices
    country = country.sort_values("CancelledValue", ascending=False)

    cancellations["IsOperationalConcept"] = cancellations["StockCode"].isin(NON_MERCHANDISE_CODES)
    operational = (
        cancellations.groupby("IsOperationalConcept", as_index=False)
        .agg(CancelledLines=("InvoiceNo", "size"), CancelledValue=("Revenue", lambda values: values.abs().sum()))
    )
    operational["CancelledValueSharePct"] = operational["CancelledValue"] / operational["CancelledValue"].sum() * 100

    physical_cancellations = cancellations.loc[~cancellations["IsOperationalConcept"]]
    physical_sales = gross_sales.loc[~gross_sales["StockCode"].isin(NON_MERCHANDISE_CODES)]
    product = (
        physical_sales.groupby(["StockCode", "Description"], dropna=False, as_index=False)
        .agg(GrossSales=("Revenue", "sum"), SalesInvoices=("InvoiceNo", "nunique"))
        .merge(
            physical_cancellations.groupby(["StockCode", "Description"], dropna=False, as_index=False)
            .agg(
                CancelledValue=("Revenue", lambda values: values.abs().sum()),
                CancellationLines=("InvoiceNo", "size"),
                CancellationInvoices=("InvoiceNo", "nunique"),
            ),
            on=["StockCode", "Description"],
            how="outer",
        )
        .fillna(0)
    )
    product["CancellationValueRatePct"] = product["CancelledValue"] / product["GrossSales"].replace(0, np.nan) * 100
    product["InvoiceCancellationRatePct"] = product["CancellationInvoices"] / product["SalesInvoices"].replace(0, np.nan) * 100
    product = product.sort_values("CancelledValue", ascending=False)

    _assert_close(monthly["CancelledValue"].sum(), cancellations["Revenue"].abs().sum(), "monthly value")
    _assert_close(country["CancelledValue"].sum(), cancellations["Revenue"].abs().sum(), "country value")
    _assert_close(
        product["CancelledValue"].sum(),
        physical_cancellations["Revenue"].abs().sum(),
        "physical-product value",
    )
    _assert_close(
        country["TotalInvoices"].sum(),
        data["InvoiceNo"].nunique(),
        "country invoice denominator",
    )

    return {
        "monthly": monthly,
        "country": country,
        "product": product,
        "operational": operational,
        "overall_invoice_rate_pct": invoice_status["CancelledInvoice"].mean() * 100,
        "overall_cancelled_value": cancellations["Revenue"].abs().sum(),
    }
