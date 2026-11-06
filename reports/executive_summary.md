# Resumen ejecutivo / Executive summary — Online Retail EDA

## Español

### Pregunta de negocio

¿Qué patrones de ventas, clientes y cancelaciones debería conocer la empresa para mejorar sus decisiones comerciales?

### Datos y alcance

El análisis utiliza líneas de factura del dataset Online Retail de UCI. Las ventas y cancelaciones se analizan por separado. `Revenue` significa `Quantity × UnitPrice`; no representa beneficio.

### Hallazgos principales

1. **La calidad de los datos condiciona la lectura comercial.** `CustomerID` falta en el 24,93 % de las filas y existen 5.268 duplicados exactos. Cantidades, precios y cancelaciones requieren reglas explícitas.
2. **Las cancelaciones tienen un impacto material.** Las ventas brutas positivas suman aproximadamente £10,67 millones y las cancelaciones identificadas representan aproximadamente £896.812 en valor absoluto. El 14,81 % de las facturas únicas aparece marcado como cancelado.
3. **Las operaciones extremas pueden distorsionar los rankings.** Una línea de +80.995 unidades es seguida por una reversión de -80.995 unidades 12 minutos después. Su cantidad e ingreso netos son cero.
4. **Los ingresos están concentrados geográficamente.** Reino Unido representa aproximadamente el 84 % de los ingresos netos calculados. Las comparaciones internacionales deben incorporar denominadores y costes.
5. **Los clientes recurrentes concentran el valor identificado.** Representan aproximadamente el 65,6 % de los clientes con `CustomerID` observado y el 93,1 % de los ingresos brutos de esa población. El resultado no se puede generalizar a las filas sin identificador.
6. **Las líneas de alto volumen son relevantes, pero no demuestran venta mayorista.** El 10 % superior de líneas por cantidad representa aproximadamente el 43,3 % de los ingresos brutos y tiene un precio unitario medio inferior. El dataset no permite establecer condición mayorista ni rentabilidad.

### Recomendaciones

- Conciliar cancelaciones y operaciones extremas antes de usar rankings para compras o inventario.
- Separar productos físicos de portes, descuentos, muestras y ajustes.
- Mejorar la captura de `CustomerID` para reforzar el análisis de retención y valor de cliente.
- Comparar países usando tasas de cancelación, pedidos, ticket medio y costes logísticos.
- Investigar las operaciones de alto volumen con datos de margen y segmentación antes de tratarlas como oportunidades mayoristas.

### Limitaciones

- No hay costes, márgenes ni gastos logísticos.
- `CustomerID` falta en una parte relevante de las filas.
- El dataset no identifica pedidos mayoristas ni motivos de cancelación.
- Los patrones descriptivos no demuestran causalidad.
- La unidad original es una línea de factura, no necesariamente un pedido completo.

---

## English

### Business question

What patterns in sales, customers and cancellations should the retailer understand to improve its commercial decisions?

### Data and scope

The analysis uses invoice-line records from UCI's Online Retail dataset. Sales and cancellations are analysed separately. `Revenue` means `Quantity × UnitPrice`; it is not profit.

### Key findings

1. **Data quality affects the commercial reading.** `CustomerID` is missing in 24.93% of rows and there are 5,268 exact duplicates. Quantities, prices and cancellations require explicit rules.
2. **Cancellations have material impact.** Gross positive sales total approximately £10.67M and identified cancellations represent approximately £896,812 in absolute value. The invoice-level cancellation rate is approximately 14.81%.
3. **Extreme operations can distort rankings.** A +80,995-unit line is followed by a -80,995 reversal 12 minutes later. Its net quantity and revenue are zero.
4. **Revenue is geographically concentrated.** The United Kingdom represents approximately 84% of calculated net revenue. International comparisons should include denominators and costs.
5. **Identified repeat customers concentrate value.** They represent approximately 65.6% of customers with an observed `CustomerID` and 93.1% of gross revenue within that population. This cannot be generalised to rows without an identifier.
6. **High-volume lines matter, but do not prove wholesale sales.** The top 10% of lines by quantity represent approximately 43.3% of gross revenue and have a lower average unit price. The dataset cannot establish wholesale status or profitability.

### Recommendations

- Reconcile cancellations and extreme-value operations before using product rankings for purchasing or inventory decisions.
- Separate physical products from postage, discounts, samples and administrative adjustments.
- Improve `CustomerID` capture to strengthen retention and customer-value analysis.
- Compare countries using cancellation rates, order counts, average order value and logistics costs.
- Investigate high-volume operations with margin and customer-segment data before treating them as wholesale opportunities.

### Limitations

- Costs, margins and logistics expenses are unavailable.
- Missing `CustomerID` values limit customer-level conclusions.
- The dataset does not identify wholesale orders or cancellation reasons.
- Descriptive patterns do not prove causality.
- The original grain is an invoice line, not necessarily a complete order.
