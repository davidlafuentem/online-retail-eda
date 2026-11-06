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
- `InvoicePrefix` or a similar documented field only if useful for quality checks.

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

## Reproducibility choice

The repository will not version the downloaded dataset files. The README links to UCI and explains
where to place the local Excel file. The notebook uses `Online Retail.xlsx` by default, looking for
it in `/content/` on Colab and in `dataset/` or `../dataset/` locally.
