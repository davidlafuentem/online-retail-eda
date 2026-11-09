# Tasks — Online Retail EDA

## Specification

- [x] Select and download the UCI Online Retail dataset.
- [x] Retain the original Excel file as the documented analysis source.
- [x] Record the initial shape, columns, missing values and duplicate count.
- [x] Review and approve the business questions.

## Data preparation

- [x] Load the Excel file with pandas.
- [x] Standardise column names.
- [x] Parse `InvoiceDate` and validate failures.
- [x] Profile missing values and duplicates.
- [x] Profile negative quantities and non-positive prices.
- [x] Define and validate cancellation logic.
- [x] Create documented derived fields.
- [x] Define a non-imputing strategy for missing identifiers and descriptions.
- [x] Create transaction-level and customer-level analytical views.
- [x] Investigate extreme quantities and possible reversals.
- [x] Compare gross and net product revenue.

## EDA

- [x] Analyse monthly revenue and invoice activity.
- [x] Analyse product contribution.
- [x] Analyse countries.
- [x] Analyse cancellations with invoice-level denominators.
- [x] Analyse customer coverage and repeat customers.
- [x] Add outlier distributions and a correlation heatmap.
- [x] Select and interpret the final visualisations.

## Communication

- [x] Write an executive summary.
- [x] Add recommendations with evidence and limitations.
- [x] Complete README and requirements.
- [x] Execute the notebook from a clean kernel.
- [x] Add World Bank population context and document the country merge.
- [x] Add a justified three-month moving average transformation.
- [x] Add an interactive Plotly country comparison.
- [x] Extract reusable preparation functions to `src/cleaning.py`.
- [x] Generate the project-specific executive report PDF.
- [ ] Remove accidental outputs or sensitive/local files before publication.
