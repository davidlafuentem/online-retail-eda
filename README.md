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
jupyter notebook
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

Consulta el [resumen ejecutivo bilingüe](reports/executive_summary.md) para conocer los hallazgos y recomendaciones, y el [informe ejecutivo de prueba con interpretaciones](reports/executive_report_with_interpretations.pdf) para la entrega no técnica. Se conserva `reports/executive_report.pdf` como versión anterior de referencia.

### Extensiones del nivel avanzado

El análisis incorpora población de 2011 del [Banco Mundial](https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?date=2011&format=json&per_page=400) mediante `merge` para calcular ingresos por habitante. También incluye una media móvil de tres meses, una visualización interactiva con Plotly y reglas reutilizables en `src/cleaning.py`.

Para regenerar el informe ejecutivo de prueba:

```bash
cd src
../.venv/bin/python create_executive_pdf.py
```

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
jupyter notebook
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

See the [bilingual executive summary](reports/executive_summary.md) for findings and recommendations. The [executive proof PDF with chart interpretations](reports/executive_report_with_interpretations.pdf) is the current non-technical version; `reports/executive_report.pdf` is preserved as the previous reference version.
The non-technical [executive report PDF](reports/executive_report.pdf) is also included.

### Advanced-level extensions

The analysis enriches country results with 2011 population estimates from the [World Bank](https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?date=2011&format=json&per_page=400) through a documented merge. It also includes a justified three-month moving average, a Plotly interactive visualisation and reusable preparation rules in `src/cleaning.py`.

To regenerate the executive proof report:

```bash
cd src
../.venv/bin/python create_executive_pdf.py
```

### AI assistance

This project was developed with support from **OpenCode**, an AI agent used to organise the notebook, review code, structure the analysis and improve the documentation.

- **Agent tool:** OpenCode
- **Agent model:** GPT-5.6 Luna
- **LLM engine/provider:** OpenAI

The project's analytical decisions, interpretations, data checks and final validation were reviewed by the author. AI assistance does not replace source verification or analytical judgement.
