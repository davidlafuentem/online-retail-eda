"""Country-level commercial and cancellation exposure analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _assert_close(actual: float, expected: float, label: str, tolerance: float = 0.01) -> None:
    if not np.isclose(actual, expected, atol=tolerance, rtol=0):
        raise AssertionError(f"Country reconciliation failed for {label}: {actual} != {expected}")


def country_performance(data: pd.DataFrame, minimum_invoices: int = 20) -> pd.DataFrame:
    """Build a country table with explicit revenue, invoice and cancellation populations."""
    net_lines = data.loc[data["UnitPrice"] > 0].copy()
    gross_sales = data.loc[
        (~data["IsCancellation"]) & (data["Quantity"] > 0) & (data["UnitPrice"] > 0)
    ].copy()
    cancellations = data.loc[data["IsCancellation"]].copy()

    invoice_status = (
        data.groupby(["Country", "InvoiceNo"], as_index=False)
        .agg(IsCancelled=("IsCancellation", "max"))
        .groupby("Country", as_index=False)
        .agg(
            TotalInvoices=("InvoiceNo", "nunique"),
            CancelledInvoices=("IsCancelled", "sum"),
        )
    )
    revenue = (
        net_lines.groupby("Country", as_index=False)
        .agg(NetRevenuePositivePriceLines=("Revenue", "sum"))
    )
    gross = gross_sales.groupby("Country", as_index=False).agg(GrossPositiveSales=("Revenue", "sum"))
    cancelled = cancellations.groupby("Country", as_index=False).agg(
        CancelledValue=("Revenue", lambda values: values.abs().sum())
    )

    result = invoice_status.merge(revenue, on="Country", how="outer")
    result = result.merge(gross, on="Country", how="outer").merge(cancelled, on="Country", how="outer").fillna(0)
    result["InvoiceCancellationRatePct"] = result["CancelledInvoices"] / result["TotalInvoices"] * 100
    result["CancellationValueRatePct"] = (
        result["CancelledValue"] / result["GrossPositiveSales"].replace(0, np.nan) * 100
    )
    result["NetRevenueSharePct"] = (
        result["NetRevenuePositivePriceLines"] / result["NetRevenuePositivePriceLines"].sum() * 100
    )
    result["NetRevenuePerInvoice"] = result["NetRevenuePositivePriceLines"] / result["TotalInvoices"].replace(0, np.nan)
    overall_invoice_rate = result["CancelledInvoices"].sum() / result["TotalInvoices"].sum() * 100
    overall_value_rate = result["CancelledValue"].sum() / result["GrossPositiveSales"].sum() * 100
    result["ExposureClass"] = np.select(
        [
            (result["InvoiceCancellationRatePct"] > overall_invoice_rate)
            & (result["CancellationValueRatePct"] > overall_value_rate),
            (result["InvoiceCancellationRatePct"] <= overall_invoice_rate)
            & (result["CancellationValueRatePct"] <= overall_value_rate),
        ],
        ["Above-average cancellation exposure", "Below-average cancellation exposure"],
        default="Mixed cancellation signals",
    )
    result["ComparableExposure"] = result["TotalInvoices"] >= minimum_invoices
    result = result.sort_values("NetRevenuePositivePriceLines", ascending=False).reset_index(drop=True)

    _assert_close(result["NetRevenuePositivePriceLines"].sum(), net_lines["Revenue"].sum(), "net revenue")
    _assert_close(result["GrossPositiveSales"].sum(), gross_sales["Revenue"].sum(), "gross sales")
    _assert_close(result["CancelledValue"].sum(), cancellations["Revenue"].abs().sum(), "cancelled value")
    _assert_close(result["TotalInvoices"].sum(), data["InvoiceNo"].nunique(), "invoice count")
    return result
