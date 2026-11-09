# Online Retail EDA

## Español

### Descripción

Análisis exploratorio de datos (EDA) del dataset **Online Retail** de UCI. El proyecto estudia patrones de ventas, comportamiento de clientes y cancelaciones para apoyar decisiones comerciales.

### Pregunta de negocio

¿Qué patrones de ventas, clientes y cancelaciones debería conocer la empresa para mejorar sus decisiones comerciales?

### Fuente de datos

Fuente oficial: [UCI Machine Learning Repository — Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail)

Descarga el fichero Excel original y colócalo en:

```text
dataset/Online Retail.xlsx
```

El notebook utiliza este Excel como fuente oficial. El CSV que pueda existir en `dataset/` es opcional y no es necesario para reproducir el análisis. Los datasets están excluidos del control de versiones.

### Instalación y ejecución local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
.venv/bin/jupyter notebook
```

Si el comando `jupyter` no aparece después de activar el entorno, utiliza siempre la ruta explícita
`.venv/bin/jupyter`. La ejecución reproducible completa del notebook es:

```bash
.venv/bin/jupyter nbconvert \
  --to notebook \
  --execute \
  --inplace \
  notebooks/01_online_retail_eda.ipynb \
  --ExecutePreprocessor.timeout=300
```

La validación del código y la regeneración del informe son:

```bash
.venv/bin/python -m py_compile src/*.py
.venv/bin/python src/create_executive_pdf.py
```

Abre `notebooks/01_online_retail_eda.ipynb` y ejecuta las celdas de principio a fin. En Google Colab, sube `Online Retail.xlsx` y la carpeta `src/` al runtime; el notebook buscará `/content/Online Retail.xlsx`.

### Alcance

La unidad original es una línea de factura. Las ventas y las cancelaciones se analizan por separado. No se imputan valores ausentes de `CustomerID`: esas filas se conservan para productos, países e ingresos, pero se excluyen únicamente de las métricas de clientes.

`Revenue` significa `Quantity * UnitPrice`; no representa beneficio porque no hay costes ni márgenes.

### Estructura

```text
dataset/       fuente local y datos de trabajo (no versionados)
notebooks/     notebook de análisis
reports/       resumen ejecutivo
src/           reglas reutilizables y generación del informe
specs/         especificación OpenSpec
PROJECT_LOG.md bitácora bilingüe del desarrollo y las decisiones
proposal.md    propuesta del proyecto
design.md      diseño analítico y política de limpieza
tasks.md       checklist de implementación
```

### Limitaciones principales

- El dataset no contiene costes, márgenes ni gastos logísticos.
- Faltan valores de `CustomerID` en una parte relevante de las filas.
- Algunas líneas representan portes, descuentos, muestras o ajustes.
- Las cancelaciones no incluyen el motivo.
- Las relaciones descriptivas no demuestran causalidad.

Consulta el [resumen ejecutivo bilingüe](reports/executive_summary.md) para conocer los hallazgos y recomendaciones, y el [informe ejecutivo experto](reports/executive_report_expert.pdf) para la entrega no técnica actual. Se conservan `reports/executive_report.pdf` y `reports/executive_report_with_interpretations.pdf` como versiones anteriores de referencia.

### Extensiones del nivel avanzado

El análisis incorpora población de 2011 del [Banco Mundial](https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?date=2011&format=json&per_page=400) mediante `merge` para calcular ingresos por habitante. También incluye una media móvil de tres meses, una visualización interactiva con Plotly, una auditoría experta de cancelaciones, una matriz de exposición por país y un análisis de clientes identificados. Las métricas de clientes usan únicamente filas con `CustomerID` observado.

Para regenerar el informe ejecutivo experto:

```bash
.venv/bin/python src/create_executive_pdf.py
```

Resultados esperados de la auditoría de clientes: 4.338 clientes identificados, 75,1% de cobertura
de filas, 83,5% de cobertura de ventas brutas positivas y 65,6% de clientes con más de una factura.
Este último indicador describe repetición observada de facturas; no mide retención, churn ni causalidad.

### Asistencia de IA

Este proyecto se desarrolló con apoyo de **OpenCode**, un agente de IA utilizado para organizar el notebook, revisar el código, estructurar el análisis y mejorar la documentación.

- **Herramienta de agente:** OpenCode
- **Modelo de agente:** GPT-5.6 Luna
- **Motor/proveedor LLM:** OpenAI

Las decisiones analíticas, interpretaciones, comprobaciones de datos y validación final fueron revisadas por la persona autora del proyecto. La asistencia de IA no sustituye la verificación de las fuentes ni el criterio analítico.

---

## English

### Description

Exploratory data analysis (EDA) of UCI's **Online Retail** dataset. The project studies sales patterns, customer behaviour and cancellations to support commercial decisions.

### Business question

What patterns in sales, customers and cancellations should the retailer understand to improve its commercial decisions?

### Data source

Official source: [UCI Machine Learning Repository — Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail)

Download the original Excel file and place it at:

```text
dataset/Online Retail.xlsx
```

The notebook uses this Excel file as the authoritative source. Any CSV in `dataset/` is optional and is not required to reproduce the analysis. Dataset files are excluded from version control.

### Installation and local execution

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
.venv/bin/jupyter notebook
```

If `jupyter` is not available after activation, use the explicit `.venv/bin/jupyter` path. To execute
the complete notebook reproducibly:

```bash
.venv/bin/jupyter nbconvert \
  --to notebook \
  --execute \
  --inplace \
  notebooks/01_online_retail_eda.ipynb \
  --ExecutePreprocessor.timeout=300
```

Validate and regenerate the expert report with:

```bash
.venv/bin/python -m py_compile src/*.py
.venv/bin/python src/create_executive_pdf.py
```

Open `notebooks/01_online_retail_eda.ipynb` and run it from top to bottom. In Google Colab, upload `Online Retail.xlsx` and the `src/` directory to the runtime; the notebook will look for `/content/Online Retail.xlsx`.

### Scope

The original grain is an invoice line. Sales and cancellations are analysed separately. Missing `CustomerID` values are not imputed: those rows remain available for product, country and revenue analysis, but are excluded only from customer-level metrics.

`Revenue` means `Quantity * UnitPrice`; it is not profit because costs and margins are unavailable.

### Main limitations

- The dataset does not contain costs, margins or logistics expenses.
- A material share of rows has no `CustomerID`.
- Some lines represent postage, discounts, samples or adjustments.
- Cancellation reasons are not provided.
- Descriptive relationships do not establish causality.

See the [bilingual executive summary](reports/executive_summary.md) for findings and recommendations. The [expert executive PDF](reports/executive_report_expert.pdf) is the current non-technical version; `reports/executive_report.pdf` and `reports/executive_report_with_interpretations.pdf` are preserved as previous reference versions.

### Advanced-level extensions

The analysis enriches country results with 2011 population estimates from the [World Bank](https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?date=2011&format=json&per_page=400) through a documented merge. It also includes a justified three-month moving average, a Plotly interactive visualisation, an expert cancellation audit, a country exposure matrix and an identified-customer analysis. Customer metrics use only rows with an observed `CustomerID`.

To regenerate the expert executive report:

```bash
.venv/bin/python src/create_executive_pdf.py
```

Expected customer-audit results are 4,338 identified customers, 75.1% row coverage, 83.5% gross
positive-sales coverage and 65.6% of identified customers linked to more than one invoice. The last
metric describes observed repeat invoicing; it is not a retention, churn or causal measure.

### AI assistance

This project was developed with support from **OpenCode**, an AI agent used to organise the notebook, review code, structure the analysis and improve the documentation.

- **Agent tool:** OpenCode
- **Agent model:** GPT-5.6 Luna
- **LLM engine/provider:** OpenAI

The project's analytical decisions, interpretations, data checks and final validation were reviewed by the author. AI assistance does not replace source verification or analytical judgement.
