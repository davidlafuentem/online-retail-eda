# Informe ejecutivo — Online Retail EDA

## 1. Lectura para gerencia

Este informe resume la situación comercial observada en las líneas de factura del dataset UCI Online Retail durante **December 2010–December 2011**. La unidad original es una línea de factura; `Revenue = Quantity × UnitPrice` y no representa beneficio porque no hay costes, margen ni gastos logísticos.

### Cuadro de mando

| Indicador | Resultado | Lectura gerencial |
|---|---:|---|
| Ventas brutas positivas | £10,666,685 | Volumen comercial registrado antes de cancelaciones. |
| Valor identificado como cancelado | £896,812 (8.4% de ventas brutas) | Riesgo material que requiere conciliación. |
| Balance registrado — todas las líneas | £9,747,748 | Suma de `Revenue` en todas las filas, incluidos ajustes y líneas con precio no positivo; no es beneficio. |
| Ingreso neto — líneas con precio positivo | £9,769,872 | Suma de `Revenue` con `UnitPrice > 0`, usada para rankings de productos y países; no es beneficio. |
| Facturas con alguna cancelación | 14.8% | Tasa sobre facturas, no sobre líneas. |
| Peso del Reino Unido | 84.0% | Alta dependencia geográfica. |
| Filas con CustomerID | 75.1% | La lectura de clientes no cubre todo el negocio. |

**Mensaje principal:** la empresa muestra un volumen comercial relevante, pero la lectura de rendimiento está condicionada por cancelaciones, concentración en Reino Unido y cobertura incompleta de clientes. Antes de optimizar productos o mercados conviene asegurar la conciliación de ingresos y la calidad de la identificación de clientes.

## 2. Evolución del negocio

Las ventas brutas alcanzan su máximo en **2011-11** (£1,509,496) y su mínimo en **2011-02** (£523,632). El mes de mayor actividad no demuestra por sí solo una causa concreta: no hay datos de campañas, stock, precios, costes ni calendario comercial comparable.

La media móvil de tres meses ayuda a distinguir movimientos puntuales de la evolución reciente. El periodo cubre aproximadamente un año, por lo que permite observar estacionalidad potencial, pero no comparar crecimiento interanual.

La correlación mensual entre ventas brutas y valor cancelado es **-0.13** (Pearson) y **0.21** (Spearman), calculada sobre solo 13 meses. No aparece una relación conjunta estable que permita anticipar cancelaciones a partir de las ventas; conviene gestionar las cancelaciones como un proceso operativo separado. La mayor proporción mensual de valor cancelado es **32.1%** de las ventas brutas del mes, por lo que el seguimiento debe usar tanto importes absolutos como proporciones.

## 3. Cancelaciones y riesgo operativo

Se identifican 9,288 líneas de cancelación y 3,836 facturas afectadas. El valor cancelado equivale al **8.4%** de las ventas brutas positivas. Esta magnitud debe revisarse junto con devoluciones, reversiones y posibles ajustes administrativos antes de usar ingresos para objetivos o previsiones.

### Diagnóstico experto de exposición

La tasa mensual de facturas afectadas oscila entre **12.7%** y **17.6%**, mientras que el valor cancelado sobre ventas brutas oscila entre **3.2%** y **32.1%**. Diciembre de 2011 alcanza el máximo monetario relativo, pero termina el día 9 y no es directamente comparable con meses completos. La existencia de una tasa recurrente no demuestra que sea una tasa normal o aceptable.

El **46.6%** del valor cancelado identificado corresponde a códigos clasificados como conceptos operativos, no a productos físicos. Esta clasificación no revela la causa, pero demuestra que no es riguroso interpretar todo el importe como devolución de cliente. En países con al menos 20 facturas, **United Kingdom** presenta el mayor valor cancelado (**£815,292**) entre los mercados comparables; los países pequeños deben analizarse con cautela por su denominador.

El producto físico con mayor valor cancelado identificado es **PAPER CRAFT , LITTLE BIRDIE** (£168,470). Su tasa debe investigarse junto con el número de facturas y el contexto de la operación; no prueba por sí sola un problema general de producto o una preferencia negativa del cliente.

### Línea de actuación: descubrir y reducir cancelaciones evitables

Reducir las cancelaciones evitables puede mejorar la contribución económica al disminuir trabajo administrativo, costes logísticos y pérdida de ventas, pero el dataset no demuestra todavía el importe de esos costes. El prefijo `C` tampoco demuestra que todas sean devoluciones de clientes. Antes de endurecer la política de devoluciones, la empresa debería clasificar los casos por motivo: devolución, error de pedido, falta de stock, precio, entrega o ajuste administrativo.

La prioridad inicial debería ser entender qué ocurre y corregir causas operativas evitables —stock, precios, descripciones, preparación y entrega— sin deteriorar la confianza del cliente. Los casos claros y repetitivos pueden automatizarse para reducir fricción y backoffice sin impedir derechos legítimos. Cualquier cambio en la política de devoluciones debe respetar la normativa, probarse de forma controlada y evaluarse con ventas, conversión, reclamaciones, repetición de compra, costes logísticos y margen. El objetivo no es minimizar cancelaciones a cualquier coste, sino reducir coste y fricción manteniendo la relación a largo plazo con el cliente.

## 4. Clientes y concentración de valor

Los clientes recurrentes —definidos aquí como `CustomerID` asociado a más de una factura única— representan el **65.6%** de los clientes identificados y concentran el **93.1%** del ingreso dentro de esa población. `CustomerID` está disponible en el **75.1%** de las filas, pero cubre el **83.5%** de las ventas brutas positivas; ambas coberturas deben distinguirse. No puede extrapolarse la concentración identificada a las filas sin identificador.

Esta observación tiene dos lecturas gerenciales distintas: es primero un **riesgo operativo de información**, porque la cobertura de clientes impide medir el negocio completo; y, dentro de la población identificada, una señal de posible **concentración de cuentas**, útil para priorizar retención y continuidad de servicio. La cobertura de `CustomerID` en las líneas de cancelación es del **95.9%**, pero esto no revela el motivo de esas cancelaciones. No permite decidir inversiones en fidelización sin margen, costes y cobertura completa.

## 5. Productos y mercados

Los diez productos físicos principales concentran aproximadamente el **8.0%** del ingreso neto de productos físicos y el primero representa aproximadamente el **1.7%**. Esto no demuestra una dependencia fuerte de pocas referencias; sí justifica revisar las referencias de mayor ingreso junto con disponibilidad, margen y riesgo de sustitución.

Los cinco países con mayor **ingreso neto de líneas con precio positivo** son:

- **United Kingdom:** £8,209,930 en 21,391 facturas
- **Netherlands:** £284,662 en 100 facturas
- **Ireland:** £263,277 en 360 facturas
- **Germany:** £221,698 en 603 facturas
- **France:** £197,404 en 461 facturas

El Reino Unido representa el **84.0%** del ingreso neto de líneas con precio positivo. Las comparaciones internacionales deben incorporar facturas, cancelaciones, costes logísticos y margen; el ingreso por habitante solo aporta contexto y no mide cuota de mercado.

La matriz país prioriza exposición observada, no oportunidad de mercado: entre países con al menos 20 facturas, **Japan** presenta la mayor tasa de facturas afectadas (**32.1%**), mientras que Reino Unido concentra el mayor impacto absoluto por su volumen. Ninguna de estas señales identifica una causa ni justifica expansión o retirada sin costes, tamaño de mercado y motivos de cancelación.

## 6. Prioridades de gestión

1. **En 0–30 días, Finanzas y Operaciones:** conciliar ventas y cancelaciones semanalmente. KPI: valor cancelado/ventas brutas y tasa de facturas afectadas.
2. **En 30–60 días, Comercial y Supply:** revisar las referencias que concentran el ingreso junto con disponibilidad y margen antes de aumentar compras.
3. **En 60–90 días, Dirección Comercial:** comparar países por ingreso, facturas, cancelaciones, costes logísticos y rentabilidad antes de invertir en expansión.
4. **En 0–30 días, Operaciones y CRM:** mejorar la captura de `CustomerID`. KPI: cobertura de filas identificadas; después, medir repetición, retención y concentración de cuentas.
5. **En el siguiente ciclo de datos, Finanzas y BI:** incorporar costes, margen, logística, campañas, stock y motivos de cancelación para pasar de facturación descriptiva a decisiones económicas.

## Anexo: principales productos por ingreso neto de líneas con precio positivo

| Producto | Ingreso | Facturas |
|---|---:|---:|
| REGENCY CAKESTAND 3 TIER | £164,762 | 2,168 |
| PARTY BUNTING | £98,303 | 1,705 |
| WHITE HANGING HEART T-LIGHT HOLDER | £97,716 | 2,231 |
| JUMBO BAG RED RETROSPOT | £92,356 | 2,132 |
| RABBIT NIGHT LIGHT | £66,757 | 1,009 |

## Limitaciones

- El análisis trabaja con líneas de factura, no necesariamente con pedidos completos.
- `Revenue` no es beneficio: faltan costes, márgenes, logística y gastos comerciales.
- No se imputa `CustomerID`; las métricas de clientes cubren solo la población identificada.
- Las cancelaciones no incluyen su motivo.
- Los duplicados, precios cero, cantidades negativas y operaciones extremas son señales que deben investigarse, no conclusiones automáticas.
- Las relaciones descriptivas no demuestran causalidad.

## English

### Business question

What patterns in sales, customers and cancellations should the retailer understand to improve its commercial decisions?

### Data and scope

This report uses invoice-line records from UCI's Online Retail dataset during **December 2010–December 2011**. `Revenue = Quantity × UnitPrice`; it is recorded revenue, not profit, because costs, margins and logistics expenses are unavailable.

### Management reading

The business shows substantial recorded activity, but management interpretation is constrained by cancellations, strong UK concentration and incomplete customer identification. Gross sales, cancelled value, the all-lines recorded balance and positive-price net revenue must remain separate.

Gross sales peak in **2011-11** (£1,509,496) and reach their minimum in **2011-02** (£523,632). The monthly Pearson correlation between gross sales and cancelled value is **-0.13**, and the rank correlation is **0.21**, based on only 13 months. This does not show a stable co-movement that can forecast cancellations from sales; cancellation control should be managed as a separate operational process.

Repeat customers—defined here as an observed `CustomerID` linked to more than one unique invoice—account for **65.6%** of identified customers and **93.1%** of revenue within that identified population. This is first a data-quality issue because `CustomerID` is missing from **24.9%** of rows; within the identified population it may also indicate account concentration relevant to retention and service continuity. It is not a retention or churn measure, and it is not enough to justify loyalty investment without margin and cost data.

### Action line: identify and reduce avoidable cancellations

Cancelling avoidable transactions may improve contribution by reducing administrative work, logistics costs and lost sales, but the dataset does not yet quantify those costs. The `C` prefix does not prove that every case is a customer return. Before tightening the returns policy, the business should classify cases by reason: return, order error, stock issue, price, delivery or administrative adjustment.

The first priority should be understanding and correcting avoidable operational causes—stock, prices, descriptions, fulfilment and delivery—without damaging customer trust. Clear, repetitive cases may be automated to reduce friction and back-office work without restricting legitimate rights. Any returns-policy change should comply with applicable law, be tested in a controlled pilot and be evaluated using sales, conversion, complaints, repeat purchase, logistics cost and margin. The objective is not to minimise cancellations at any cost, but to reduce cost and friction while protecting long-term customer relationships.

### Priorities

1. **Within 0–30 days, Finance and Operations:** reconcile sales and cancellations weekly. KPI: cancelled value/gross sales and affected-invoice rate.
2. **Within 30–60 days, Commercial and Supply:** review concentrated product references together with availability and margin.
3. **Within 60–90 days, Commercial leadership:** compare countries using revenue, orders, cancellation rates, logistics costs and profitability rather than revenue alone.
4. **Within 0–30 days, Operations and CRM:** improve `CustomerID` capture as an operational data-quality KPI; then measure retention and account concentration.
5. **In the next data cycle, Finance and BI:** add cost, margin, logistics, campaign, stock and cancellation-reason data before building forecasts or profitability decisions.

### Limitations

- The original grain is an invoice line, not necessarily a complete order.
- The dataset does not identify wholesale orders or cancellation reasons.
- Descriptive relationships do not establish causality.
