# AGENTS.md

## Project purpose

This repository contains an exploratory data analysis (EDA) of the UCI Online Retail dataset.
The audience is a non-technical business stakeholder and a data-analyst recruiter.

## Scope

- Analyse sales and cancellations separately.
- Preserve the original dataset and document every cleaning decision.
- Do not impute `CustomerID`; it is an identifier, not a measurement.
- Keep rows without `CustomerID` for product, country and revenue analysis.
- Exclude rows without `CustomerID` only from customer-level metrics.
- Investigate exact duplicates before deciding whether to remove them.
- Treat negative quantities and zero prices as quality/business signals, not as automatic errors.
- Do not claim causality from correlations or descriptive comparisons.

## Reproducibility

- Use the local virtual environment in `.venv` when available.
- Keep raw data out of version control.
- Use the documented Excel file as the authoritative analysis source when the project specifies it.
  Treat any CSV working copy as optional and do not describe it as the final source unless the
  notebook actually uses it.
- The notebook must run from top to bottom after dependencies are installed.

## Presentation

- Every chart must have a meaningful title, labelled axes and units where applicable.
- Every chart must be followed by a short interpretation in Markdown.
- Conclusions must distinguish observed patterns, hypotheses and limitations.
- Use English for code identifiers and Spanish or English consistently for the narrative; the final choice must be consistent throughout the notebook and README.

### Executive-report chart standard

Apply these rules to every chart included in an executive report or presentation:

- The title must explain the business question or decision relevance, not only repeat a variable
  name. A page heading is not a substitute for a title inside the chart.
- Label both axes, including the unit and the aggregation grain where relevant: for example,
  `Revenue (£ millions)`, `Cancellation rate (%)`, `Invoices (unique)` or `Month of invoice`.
- Never leave scientific notation, unexplained decimals or ambiguous `k`/`M` scales on a chart
  intended for a CEO, country manager or other non-technical reader. Format values explicitly as
  £, £k, £M, units, invoices or percentages.
- State the period, population and metric definition when they materially affect interpretation.
  Distinguish gross sales, cancelled value, net recorded revenue and profit.
- When comparing two measures over time, display both measures in the same figure when their units
  are comparable, and quantify the apparent pattern in the accompanying text. Do not infer a cause
  from visual co-movement.
- Every chart must answer a management question: what should be monitored, decided, investigated or
  changed? Replace decorative charts with a KPI, denominator, benchmark or action where possible.
- Treat data-coverage charts as operational controls. If customer identifiers are incomplete,
  explain both the information-quality risk and the limited commercial planning implication; do not
  present incomplete customer coverage as a standalone growth opportunity.
- Add an accompanying interpretation with the observed fact, decision relevance, limitation and
  recommended next check. Recommendations should identify a reasonable action, owner or process,
  time horizon and KPI when the available data supports it.

## Validation

Before considering the project complete, verify:

1. dataset shape and column types;
2. missing values and duplicates;
3. cancellation identification;
4. invalid quantities/prices and revenue calculations;
5. notebook execution from a clean kernel;
6. README reproduction instructions.

## Critical thinking and missing-data policy

The analysis must be critical, evidence-based and explicit about uncertainty. Do not invent
business meaning, identifiers, causes or conclusions that the data cannot support.

- Never impute `CustomerID`: it is an identifier, not a measured variable. Invented customer IDs
  would falsify customer counts, repeat-purchase metrics and customer revenue.
- Keep a full transaction-level analytical view for sales, products, countries, cancellations and
  data-quality analysis. Do not delete rows only because `CustomerID` is missing.
- Use a separate customer-level analytical view containing only rows with an observed `CustomerID`.
  Report its coverage and limitations whenever customer metrics are shown.
- Do not impute `Description` as factual data. A display-only label such as `Unknown description`
  is allowed, while `StockCode` remains the product key.
- Do not silently drop rows, columns, outliers or business-looking records. Each exclusion must be
  justified, quantified and compared with the corresponding inclusive result when material.
- Treat missingness as a potential data-quality or business-process signal, not automatically as a
  nuisance to remove.
- Distinguish observed facts, hypotheses and unresolved questions. Descriptive relationships do not
  establish causality.

## Strict numerical certainty and cross-validation

Every number presented in a notebook, report, dashboard or recommendation must be traceable to a
documented definition, source column, analytical population and unit. Numerical correctness is not
enough if two different populations are given the same KPI name.

- Define every KPI before using it, including filters, denominator, aggregation grain and whether
  it represents a line, invoice, customer, country, gross value, net recorded value or profit.
- Use distinct names for distinct populations. For example, do not call both `sum(Revenue)` across
  all rows and `sum(Revenue)` after a positive-price filter `NetRevenue` without qualification.
- Before publication, cross-check important metrics through at least two independent routes where
  practical: direct aggregation versus grouped totals, report values versus notebook values, and
  source-row totals versus derived monthly/country/product totals.
- Add automated reconciliation checks for material KPIs. A failed check must stop report generation,
  not be hidden or rounded away.
- Investigate every discrepancy, even when it is caused by a legitimate population difference.
  Either unify the population or give the metrics different names and explain the difference next to
  the result.
- Never present a rounded value as more precise than its source or imply that a descriptive revenue
  metric is profit when costs and margins are unavailable.
- Preserve a KPI dictionary in the analytical design or report so another analyst can reproduce and
  challenge each published number.

## Reusable EDA structure

Use the following structure for future exploratory data analyses, unless the project explicitly
requires another approach. The objective is to make the reasoning traceable from the first data
inspection to the final business recommendations.

### 1. Business context and analytical question

- Explain the business context, the decision to support and the main question.
- Define the scope and state what the dataset cannot measure.
- Avoid starting with charts that are not connected to a question.

### 2. Data source and unit of analysis

- Identify the source, period, number of rows and columns, and relevant access or licensing notes.
- Explain the grain of the data: for example, a line of invoice, an order, a customer or a daily
  observation. Do not treat one row as a complete business event without verifying it.

### 3. Load and initial structure

- Load the data reproducibly and preserve the original source.
- Inspect sample rows, dimensions, column names, data types, date ranges and basic descriptive
  statistics.
- Add a short Markdown interpretation immediately after the initial summary. Explain what the
  first inspection suggests and which questions it creates for the next steps.

### 4. Data-quality audit

- Measure missing values, duplicates, invalid types, impossible or suspicious ranges, inconsistent
  categories and derived-field risks.
- Treat unusual values as investigation signals, not automatic errors.
- Quantify the impact of any proposed exclusion, correction or deduplication before applying it.

### 5. Analytical populations and transformations

- Define the populations used for each metric, such as all transactions, positive sales,
  cancellations or identified customers.
- Document every derived variable and business rule in plain language.
- Keep alternative views separate when they answer different questions; do not silently mix gross,
  net, cancelled, adjusted or customer-identified populations.

### 6. Progressive exploration

Explore in a logical order:

1. Univariate distributions and category frequencies.
2. Time evolution when dates are available.
3. Comparisons between relevant groups, such as countries, products or customer types.
4. Relationships between numerical variables.
5. Segments, concentrations, extremes and representative cases.

Each chart or table must be followed immediately by a concise Markdown reading that includes:

- what is observed;
- why it matters for the business question;
- what cannot be concluded from it;
- the next analysis or validation it motivates.

### 7. Critical interpretation

- Separate observed facts, reasonable hypotheses and unresolved questions.
- Do not infer causality from correlation, ordering or visual similarity.
- Do not call revenue profit or margin without cost data.
- Do not assign business labels such as wholesale, fraud, error or customer churn unless the data
  contains a defensible definition.
- Use denominators and coverage information when comparing groups.

### 8. Business synthesis and limitations

- End with a short synthesis that connects each conclusion to the analysis that supports it.
- Prioritize practical recommendations and specify what additional data would validate them.
- State limitations next to the affected conclusion, not only in a final generic list.
- Ensure the final report can be understood without reading the code.

### 9. Code and reproducibility standard

- Use clear English identifiers and comments that explain the business purpose of a calculation,
  not only its Python syntax.
- Keep code cells focused: one analytical task per cell where practical.
- Explain filters, thresholds, denominators and exclusions in comments or Markdown.
- Run the notebook from a clean kernel from top to bottom before delivery and record the result.
