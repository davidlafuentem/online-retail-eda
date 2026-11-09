"""Customer coverage, repeat behaviour and concentration metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _assert_close(actual: float, expected: float, label: str, tolerance: float = 0.01) -> None:
    if not np.isclose(actual, expected, atol=tolerance, rtol=0):
        raise AssertionError(f"Customer reconciliation failed for {label}: {actual} != {expected}")


def customer_performance(data: pd.DataFrame) -> dict[str, object]:
    """Return customer metrics using only observed identifiers and positive sales."""
    gross_sales = data.loc[
        (~data["IsCancellation"]) & (data["Quantity"] > 0) & (data["UnitPrice"] > 0)
    ].copy()
    identified_sales = gross_sales.dropna(subset=["CustomerID"]).copy()
    customers = (
        identified_sales.groupby("CustomerID", as_index=False)
        .agg(Revenue=("Revenue", "sum"), Invoices=("InvoiceNo", "nunique"), Rows=("InvoiceNo", "size"))
        .sort_values("Revenue", ascending=False)
        .reset_index(drop=True)
    )
    customers["RevenueSharePct"] = customers["Revenue"] / customers["Revenue"].sum() * 100
    customers["CumulativeRevenuePct"] = customers["RevenueSharePct"].cumsum()
    customers["CustomerSharePct"] = (np.arange(len(customers)) + 1) / len(customers) * 100
    customers["IsRepeatCustomer"] = customers["Invoices"] > 1

    top20_count = max(1, int(np.ceil(len(customers) * 0.20)))
    customers_for_80 = int((customers["CumulativeRevenuePct"] < 80).sum() + 1)
    cancellation_rows = data.loc[data["IsCancellation"]]
    cancellation_invoices = cancellation_rows.groupby("InvoiceNo")["CustomerID"].apply(lambda values: values.notna().any())

    metrics = {
        "source_row_customer_coverage_pct": data["CustomerID"].notna().mean() * 100,
        "gross_sales_customer_coverage_pct": identified_sales["Revenue"].sum() / gross_sales["Revenue"].sum() * 100,
        "identified_customer_count": int(len(customers)),
        "repeat_customer_rate_pct": customers["IsRepeatCustomer"].mean() * 100,
        "repeat_revenue_share_pct": customers.loc[customers["IsRepeatCustomer"], "Revenue"].sum() / customers["Revenue"].sum() * 100,
        "top20_revenue_share_pct": customers.head(top20_count)["Revenue"].sum() / customers["Revenue"].sum() * 100,
        "customers_for_80_count": customers_for_80,
        "customers_for_80_share_pct": customers_for_80 / len(customers) * 100,
        "cancellation_row_customer_coverage_pct": cancellation_rows["CustomerID"].notna().mean() * 100,
        "cancellation_invoice_customer_coverage_pct": cancellation_invoices.mean() * 100,
    }

    _assert_close(
        identified_sales["Revenue"].sum(),
        customers["Revenue"].sum(),
        "identified gross sales",
    )
    _assert_close(
        customers["RevenueSharePct"].sum(),
        100,
        "customer revenue shares",
        tolerance=1e-8,
    )
    return {"customers": customers, "metrics": metrics}
