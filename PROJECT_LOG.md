# Project log — Online Retail EDA

## Propósito y alcance

Esta bitácora resume la evolución del proyecto y las decisiones que afectan a la
reproducibilidad, la interpretación ejecutiva y la calidad numérica. Se ha reconstruido a
partir del historial Git, `tasks.md`, `design.md`, `AGENTS.md`, el notebook, los informes y el
registro de trabajo disponible después de varias compactaciones de conversación.

Cuando una fecha o una decisión no está directamente en Git, se identifica como **reconstruida**;
no se presenta como un evento remoto independiente verificable.

## Hitos verificados en el repositorio

| Fecha | Hito | Evidencia |
|---|---|---|
| 2026-11-06 | Creación del repositorio y primera versión del EDA | Commit `880e87b` |
| 2026-11-09 | Incorporación de funciones reutilizables, contexto de países y generador PDF | Commit `f4de7e6`; `src/`; informes PDF |
| 2026-11-09 | Documentación de estándares ejecutivos, poblaciones analíticas y reproducibilidad | Commit `0dd1b4c`; `AGENTS.md`, `design.md`, `README.md` |
| 2026-11-09 | Reconciliación de KPIs y actualización del notebook y resumen ejecutivo | Commit `d418654`; notebook y `reports/executive_summary.md` |
| 2026-11-09 | Regeneración final del PDF de prueba | Commit `194a814`; `reports/executive_report_with_interpretations.pdf` |

## Evolución analítica reconstruida

### 1. Fuente y preparación

- Se eligió el Excel original de UCI, `dataset/Online Retail.xlsx`, como fuente autoritativa.
- Se mantuvo el grano original: una fila es una línea de factura, no necesariamente un pedido
  completo.
- Se documentaron tipos, fechas, valores ausentes, duplicados, cantidades negativas, precios no
  positivos y valores extremos.
- Se creó `Revenue = Quantity × UnitPrice` y se identificaron cancelaciones mediante facturas cuyo
  número comienza por `C`.
- No se imputó `CustomerID`. Las filas sin identificador se conservan para ingresos, productos,
  países y cancelaciones, y se excluyen solo de las métricas de clientes.

### 2. Poblaciones y análisis EDA

Se separaron las poblaciones para evitar mezclar conceptos:

- ventas brutas positivas: líneas no canceladas con cantidad y precio positivos;
- valor cancelado: valor absoluto de las líneas con factura identificada como cancelación;
- facturas afectadas: denominador a nivel de factura, no de línea;
- balance registrado de todas las líneas;
- ingreso neto de líneas con `UnitPrice > 0`;
- clientes identificados: solo filas con `CustomerID` observado.

El EDA cubre evolución mensual, productos, países, clientes, cancelaciones, distribuciones,
valores extremos y relaciones descriptivas. Se añadieron contexto de población del Banco Mundial,
una media móvil de tres meses y una comparación interactiva por país.

### 3. Revisión ejecutiva de gráficos

Durante la revisión se corrigieron problemas de comunicación que eran relevantes para dirección:

- títulos explicativos dentro de cada gráfico;
- ejes, unidades y escalas explícitas (`£`, `£k`, `£M`, porcentajes);
- comparación mensual simultánea de ventas brutas y valor cancelado;
- lectura breve a pie de cada gráfico, con limitaciones y relevancia de gestión;
- separación entre riesgo de calidad de datos de `CustomerID` y posible concentración de cuentas;
- corrección de la interpretación de productos: los diez productos principales representan
  aproximadamente el 8% del ingreso físico, por lo que no se afirma una fuerte dependencia de
  pocas referencias;
- conservación del PDF anterior y creación de
  `reports/executive_report_with_interpretations.pdf` como versión de prueba mejorada.

### 4. Cancelaciones y recomendaciones

El informe distingue cancelaciones identificadas por el prefijo `C` de devoluciones reales: el
dataset no contiene el motivo y no demuestra que cada cancelación sea una devolución ni que tenga
un coste logístico concreto.

La recomendación es investigar y clasificar causas antes de endurecer la política de devoluciones.
Primero deben atacarse causas operativas evitables —stock, precios, descripción, preparación y
entrega— y cualquier cambio de política debe respetar la normativa, proteger la confianza del
cliente y probarse mediante un piloto controlado. Las métricas propuestas incluyen conversión,
reclamaciones, repetición, costes logísticos y margen, no solo el número de cancelaciones.

## Control numérico y corrección de la inconsistencia de ingresos

Durante la auditoría se detectó que dos poblaciones estaban recibiendo el mismo nombre genérico de
ingreso neto. Se corrigió antes de la publicación final:

| KPI publicado | Resultado | Definición |
|---|---:|---|
| Ventas brutas positivas | £10,666,684.54 | No canceladas; cantidad y precio positivos |
| Valor cancelado | £896,812.49 | Valor absoluto de líneas con factura `C` |
| Balance registrado — todas las líneas | £9,747,747.93 | Suma de `Revenue` en todas las filas |
| Ingreso neto — líneas con precio positivo | £9,769,872.05 | Suma de `Revenue` con `UnitPrice > 0` |

Se añadieron comprobaciones que detienen la generación del informe cuando no coinciden:

- agregación directa frente a totales mensuales;
- total por país frente al total de líneas con precio positivo;
- total de productos físicos frente a su población física agrupada;
- balance de todas las líneas frente a la suma mensual;
- notebook frente al generador del informe.

La diferencia entre £9,747,747.93 y £9,769,872.05 no es un error aritmético una vez corregida la
definición: son poblaciones distintas y ahora tienen nombres distintos.

## Validaciones realizadas

- Notebook ejecutado de principio a fin desde un kernel limpio con `nbconvert`.
- Generador PDF ejecutado correctamente desde `.venv`.
- `src/create_executive_pdf.py` validado con `py_compile`.
- `git diff --check` superado.
- PDF revisado después de la regeneración; el PDF anterior permanece como referencia.
- Los cuatro commits iniciales fueron publicados en `origin/main` el 2026-11-09.

## Estado actual y pendientes

- El análisis y el informe ejecutivo están publicados en GitHub.
- La bitácora formal se añade ahora como documento del proyecto.
- Siguen siendo limitaciones del dataset: ausencia de costes, margen, logística, stock, campañas y
  motivos de cancelación; por ello no se calcula beneficio ni se hace una previsión causal.
- La bitácora no sustituye un registro de incidencias externo: documenta decisiones y resultados
  verificables del repositorio.

---

# Project log — English summary

This log reconstructs the project history from Git, `tasks.md`, `design.md`, `AGENTS.md`, the
notebook, the reports and the available work record after conversation compaction. Reconstructed
decisions are labelled by their evidence level; no unverified event is presented as a remote fact.

The project uses UCI's original Excel file and keeps invoice-line grain explicit. It preserves rows
without `CustomerID`, separates gross sales, cancellations, all-lines recorded balance and
positive-price net revenue, and avoids calling revenue profit. The EDA covers monthly evolution,
products, countries, customers, cancellations, outliers and descriptive relationships. World Bank
population context, a three-month moving average and an interactive country view were added as
advanced extensions.

The executive review added explanatory chart titles, labelled axes, explicit units, chart-level
readings, monthly sales-versus-cancellation comparison, and a clearer distinction between customer
data quality and possible account concentration. Product concentration was corrected: the top ten
physical products represent approximately 8% of physical-product revenue, so the report does not
claim strong dependency on a few references.

Cancellation recommendations are deliberately conditional. The `C` prefix does not prove a
customer return or a specific logistics cost. The recommended order is to classify reasons, fix
avoidable operational causes, and only then test limited returns-policy changes with legal,
conversion, complaint, repeat-purchase, logistics-cost and margin safeguards.

The numerical audit found two differently filtered revenue totals that had been given an ambiguous
generic name. They are now explicitly named `Recorded balance — all lines` (£9,747,747.93) and
`Net revenue — positive-price lines` (£9,769,872.05). Automated reconciliations stop report
generation when direct, grouped, monthly, country, product or notebook totals do not tie out.

The notebook was executed end to end, the PDF generator and Python compilation checks passed, the
proof PDF was visually reviewed, and the four implementation commits were pushed to `origin/main`
on 2026-11-09. Remaining limitations are the absence of cost, margin, logistics, stock, campaign
and cancellation-reason data; therefore profit and causal forecasting are outside the evidence.
