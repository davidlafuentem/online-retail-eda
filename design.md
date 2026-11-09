# Design — Online Retail EDA

## Data source

UCI Machine Learning Repository, Online Retail dataset:
https://archive.ics.uci.edu/dataset/352/online+retail

The authoritative local source is `dataset/Online Retail.xlsx`, the original Excel file downloaded
from UCI. The notebook reads this file directly so that the final analysis is reproducible from the
documented source. `dataset/online_retail.csv`, if present, is only an optional working copy and is
not the source used for the final results.

## Analytical grain

The source contains invoice-line records. A row is not necessarily a complete order: an invoice may contain several product lines. Analyses must state whether they operate at line, invoice, customer or country level.

## Derived fields

- `InvoiceDate`: parsed datetime.
- `Revenue`: `Quantity * UnitPrice`.
- `IsCancellation`: `InvoiceNo` starts with `C`.
- `Year`, `Month`, `DayOfWeek` and `Hour` from `InvoiceDate`.
- `Rolling3M`: three-month moving average of gross sales, used only to make the temporal trend easier to read.
- `Country`: the source label `EIRE` is harmonised to `Ireland` in the analytical copy so it matches the external context source; the raw Excel remains unchanged.
- `InvoicePrefix` or a similar documented field only if useful for quality checks.

## KPI dictionary and populations

The report uses distinct names for revenue measures that use different populations:

| KPI | Definition | Population | Grain | Interpretation |
|---|---|---|---|---|
| Gross positive sales | Sum of `Revenue` | Not cancelled, `Quantity > 0`, `UnitPrice > 0` | Invoice line | Recorded positive sales before cancellations |
| Cancelled value | Absolute sum of `Revenue` | `InvoiceNo` starts with `C` | Invoice line | Recorded cancellation value; not automatically a logistics cost |
| Invoice cancellation rate | Cancelled unique invoices / all unique invoices | Invoice-level status: any `C` line marks the invoice | Invoice | Share of invoices affected by an identified cancellation |
| Recorded balance — all lines | Sum of `Revenue` | All source rows | Invoice line | Descriptive balance including non-positive-price adjustments |
| Net revenue — positive-price lines | Sum of `Revenue` | `UnitPrice > 0`, positive and negative quantities retained | Invoice line | Comparable commercial view used for product and country rankings |
| Customer row coverage | Share of all source rows with non-null `CustomerID` | All source rows | Invoice line | Identifier availability; not customer or revenue coverage |
| Identified gross-sales coverage | Identified gross positive sales / all gross positive sales | Non-cancelled, `Quantity > 0`, `UnitPrice > 0`; numerator also requires non-null `CustomerID` | Invoice line | Economic coverage of observed customer identifiers |
| Repeat identified-customer rate | Identified customers with more than one unique invoice / identified customers | Gross positive sales with non-null `CustomerID` | Customer | Observed repeat-invoice pattern; not retention or churn |
| Repeat identified-revenue share | Gross positive sales from repeat identified customers / all identified gross positive sales | Same customer population; repeat means more than one unique invoice | Customer | Revenue concentration within identified customers; not whole-business concentration |

`Recorded balance — all lines` and `Net revenue — positive-price lines` must never be presented under the same generic label such as `NetRevenue`. Material KPIs are reconciled through direct totals and grouped totals before the executive report is generated.

## Cleaning policy

1. Keep the original data unchanged.
2. Standardise column names only in the analysis dataframe.
3. Parse dates and report parsing failures.
4. Do not impute `CustomerID` or `Description`.
5. Retain missing-customer rows for non-customer analyses.
6. Inspect exact duplicates and report their effect before removal.
7. Inspect negative quantities, zero/negative prices and cancellations separately.
8. Define the analysis population explicitly for each metric.

## Proposed analysis sections

1. Executive framing and data source.
2. Dataset structure and data-quality audit.
3. Sales and revenue evolution.
4. Product and country performance.
5. Cancellation patterns.
6. Customer coverage and repeat behaviour.
7. Findings, recommendations and limitations.

## Advanced-level extensions

- Country revenue is enriched with 2011 population estimates from the World Bank API. The year is
  aligned approximately with the Online Retail observation period, and unmatched labels are kept
  visible rather than imputed.
- Country revenue per inhabitant is used as a normalised comparison; it is descriptive and must not
  be interpreted as profitability or customer spending.
- Plotly is used for an interactive country comparison, while the three-month moving average is used
  to show the underlying temporal pattern without replacing the original monthly values.
- Reusable preparation rules live in `src/cleaning.py`.

## Reproducibility choice

The repository will not version the downloaded dataset files. The README links to UCI and explains
where to place the local Excel file. The notebook uses `Online Retail.xlsx` by default, looking for
it in `/content/` on Colab and in `dataset/` or `../dataset/` locally.
