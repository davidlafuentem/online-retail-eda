# Capability: Online Retail EDA

## Requirements

### Requirement: reproducible data loading

The project SHALL load the documented Excel source, `Online Retail.xlsx`, with pandas and SHALL
report its shape and column names before transformation.

#### Scenario: source is available

- **WHEN** the user follows the README setup instructions and places `Online Retail.xlsx` in `dataset/`
- **THEN** the notebook loads the data without hard-coded machine-specific paths.

#### Scenario: source is missing

- **WHEN** the source file is not present
- **THEN** the notebook reports the expected Excel filename and the UCI download URL rather than failing with an opaque error.

### Requirement: data-quality assessment

The analysis SHALL quantify missing values, exact duplicates, invalid or suspicious quantities/prices and date parsing failures.

#### Scenario: missing customer identifiers

- **WHEN** `CustomerID` is missing
- **THEN** the row remains available for product, country and revenue analysis and is excluded only from customer-level metrics.

#### Scenario: duplicate records

- **WHEN** exact duplicate rows are detected
- **THEN** the notebook reports their count and explains whether they are retained or removed before aggregating results.

### Requirement: cancellation analysis

The analysis SHALL identify cancellations from the invoice identifier and SHALL keep cancellation metrics separate from completed-sales metrics.

#### Scenario: cancellation invoice

- **WHEN** `InvoiceNo` starts with `C`
- **THEN** the row is marked as a cancellation and included in cancellation analysis.

### Requirement: business analysis

The notebook SHALL answer at least three business questions using labelled visualisations and written interpretations.

#### Scenario: sales performance

- **WHEN** monthly sales are aggregated
- **THEN** the notebook shows revenue and activity trends and explains the aggregation grain.

#### Scenario: product or country contribution

- **WHEN** revenue is grouped by product or country
- **THEN** the notebook identifies the leading contributors and states the limitations of using transaction revenue as business profit.

#### Scenario: cancellation patterns

- **WHEN** cancellations are grouped by time, product or country
- **THEN** the notebook reports patterns without claiming that a group causes cancellations.

### Requirement: recruiter-readable communication

The repository SHALL include a README, requirements file and executive summary written for a non-technical reader.

#### Scenario: notebook review

- **WHEN** a recruiter opens the repository
- **THEN** the project purpose, source, setup, key findings and limitations are visible without inspecting implementation details first.
