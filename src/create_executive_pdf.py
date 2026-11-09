"""Generate the fixed-layout executive PDF and its Markdown companion."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FuncFormatter

from cleaning import prepare_transaction_data
from cancellation_analysis import cancellation_audit
from country_analysis import country_performance
from customer_analysis import customer_performance


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dataset" / "Online Retail.xlsx"
PDF_OUTPUT = ROOT / "reports" / "executive_report_with_interpretations.pdf"
EXPERT_PDF_OUTPUT = ROOT / "reports" / "executive_report_expert.pdf"
MD_OUTPUT = ROOT / "reports" / "executive_summary.md"
BLUE = "#17365D"
MID_BLUE = "#4472C4"
GREEN = "#70AD47"
RED = "#C00000"
GREY = "#666666"


def money(value: float) -> str:
    return f"£{value:,.0f}"


def pct(value: float) -> str:
    return f"{value:.1f}%"


def money_axis(ax: plt.Axes) -> None:
    """Format money axes so a manager can read thousands and millions directly."""
    ax.yaxis.set_major_formatter(FuncFormatter(
        lambda value, _: f"£{value / 1_000_000:.1f}M" if abs(value) >= 1_000_000
        else f"£{value / 1_000:.0f}k" if abs(value) >= 1_000
        else f"£{value:.0f}"
    ))


def assert_close(actual: float, expected: float, label: str, tolerance: float = 0.01) -> None:
    """Fail report generation when a material reconciliation does not tie out."""
    if not np.isclose(actual, expected, atol=tolerance, rtol=0):
        raise AssertionError(
            f"Reconciliation failed for {label}: actual={actual:.6f}, expected={expected:.6f}"
        )


def validate_reconciliations(
    data: pd.DataFrame,
    valid_sales: pd.DataFrame,
    cancellations: pd.DataFrame,
    net_lines: pd.DataFrame,
    monthly: pd.DataFrame,
    product: pd.DataFrame,
    country: pd.DataFrame,
) -> None:
    """Cross-check published totals through direct and grouped aggregations."""
    gross_direct = valid_sales["Revenue"].sum()
    cancelled_direct = cancellations["Revenue"].abs().sum()
    balance_all_lines = data["Revenue"].sum()
    net_positive_price = net_lines["Revenue"].sum()

    assert_close(monthly["GrossRevenue"].sum(), gross_direct, "gross positive sales")
    assert_close(monthly["CancellationValue"].sum(), cancelled_direct, "cancelled value")
    assert_close(product["Revenue"].sum(), product.attrs["source_total"], "physical-product total")
    assert_close(country["Revenue"].sum(), net_positive_price, "country total")
    assert_close(
        data.groupby("Month")["Revenue"].sum().sum(),
        balance_all_lines,
        "recorded balance — all lines",
    )
    assert_close(
        data.loc[data["UnitPrice"] > 0].groupby("Month")["Revenue"].sum().sum(),
        net_positive_price,
        "net revenue — positive-price lines",
    )


def base_data() -> dict[str, object]:
    data = prepare_transaction_data(pd.read_excel(SOURCE, engine="openpyxl"))
    valid_sales = data.loc[
        (~data["IsCancellation"]) & (data["Quantity"] > 0) & (data["UnitPrice"] > 0)
    ].copy()
    cancellations = data.loc[data["IsCancellation"]].copy()
    identified = valid_sales.dropna(subset=["CustomerID"]).copy()
    invoice_status = data.groupby("InvoiceNo")["IsCancellation"].max()
    net_lines = data.loc[data["UnitPrice"] > 0].copy()
    monthly = (
        data.assign(
            Gross=np.where(
                (~data["IsCancellation"])
                & (data["Quantity"] > 0)
                & (data["UnitPrice"] > 0),
                data["Revenue"],
                0,
            ),
            Cancelled=np.where(data["IsCancellation"], data["Revenue"].abs(), 0),
        )
        .groupby("Month", as_index=False)
        .agg(GrossRevenue=("Gross", "sum"), CancellationValue=("Cancelled", "sum"), Invoices=("InvoiceNo", "nunique"))
    )
    monthly["Rolling3M"] = monthly["GrossRevenue"].rolling(3, min_periods=1).mean()
    monthly["CancellationSharePct"] = monthly["CancellationValue"] / monthly["GrossRevenue"] * 100
    # These are descriptive checks across only 13 months; they are not a causal model.
    monthly_pearson = monthly["GrossRevenue"].corr(monthly["CancellationValue"])
    monthly_spearman = monthly["GrossRevenue"].rank().corr(monthly["CancellationValue"].rank())
    audit = cancellation_audit(data)
    country_expert = country_performance(data, minimum_invoices=20)
    customer_expert = customer_performance(data)
    # Product rankings use net lines and exclude operational concepts already
    # documented in the notebook (postage, discounts, fees and samples).
    non_merchandise_codes = {
        "AMAZONFEE", "B", "BANK CHARGES", "C2", "CRUK", "D", "DOT", "M", "POST", "S",
        "gift_0001_10", "gift_0001_20", "gift_0001_30", "gift_0001_40", "gift_0001_50",
    }
    merchandise = data.loc[
        (data["UnitPrice"] > 0) & (~data["StockCode"].isin(non_merchandise_codes))
    ].copy()
    product = (
        merchandise.groupby(["StockCode", "Description"], dropna=False, as_index=False)
        .agg(Revenue=("Revenue", "sum"), Quantity=("Quantity", "sum"), Invoices=("InvoiceNo", "nunique"))
        .sort_values("Revenue", ascending=False)
    )
    product.attrs["source_total"] = merchandise["Revenue"].sum()
    country = (
        net_lines
        .groupby("Country", as_index=False)
        .agg(Revenue=("Revenue", "sum"), Invoices=("InvoiceNo", "nunique"))
        .sort_values("Revenue", ascending=False)
    )
    customer = (
        identified.groupby("CustomerID", as_index=False)
        .agg(Revenue=("Revenue", "sum"), Invoices=("InvoiceNo", "nunique"))
        .sort_values("Revenue", ascending=False)
    )
    repeat = customer["Invoices"].gt(1)
    validate_reconciliations(data, valid_sales, cancellations, net_lines, monthly, product, country)
    return {
        "data": data,
        "sales": valid_sales,
        "cancellations": cancellations,
        "identified": identified,
        "monthly": monthly,
        "product": product,
        "country": country,
        "customer": customer,
        "gross": valid_sales["Revenue"].sum(),
        "cancelled": cancellations["Revenue"].abs().sum(),
        "recorded_balance_all_lines": data["Revenue"].sum(),
        "net_revenue_positive_price_lines": net_lines["Revenue"].sum(),
        "cancel_rate": invoice_status.mean() * 100,
        "cancelled_invoices": int(invoice_status.sum()),
        "uk_share": country.loc[country["Country"].eq("United Kingdom"), "Revenue"].sum() / country["Revenue"].sum() * 100,
        "customer_coverage": data["CustomerID"].notna().mean() * 100,
        "repeat_customer_share": repeat.mean() * 100,
        "repeat_revenue_share": customer.loc[repeat, "Revenue"].sum() / customer["Revenue"].sum() * 100,
        "top_product_share": product.head(1)["Revenue"].sum() / product["Revenue"].sum() * 100,
        "top10_product_share": product.head(10)["Revenue"].sum() / product["Revenue"].sum() * 100,
        "monthly_pearson": monthly_pearson,
        "monthly_spearman": monthly_spearman,
        "peak_cancellation_share": monthly["CancellationSharePct"].max(),
        "best_month": monthly.loc[monthly["GrossRevenue"].idxmax()],
        "worst_month": monthly.loc[monthly["GrossRevenue"].idxmin()],
        "cancellation_audit": audit,
        "country_expert": country_expert,
        "customer_expert": customer_expert,
    }


def page(pdf: PdfPages, title: str, subtitle: str = "") -> tuple[plt.Figure, plt.Figure]:
    fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
    fig.text(0.07, 0.955, title, fontsize=20, weight="bold", color=BLUE)
    if subtitle:
        fig.text(0.07, 0.925, subtitle, fontsize=9.5, color=GREY)
    fig.text(0.07, 0.035, "Online Retail EDA · UCI Online Retail · Revenue = Quantity × UnitPrice (no es beneficio)", fontsize=7.5, color=GREY)
    return fig, fig


def finish(pdf: PdfPages, fig: plt.Figure) -> None:
    pdf.savefig(fig)  # Deliberately no bbox_inches='tight': every page is identical A4 size.
    plt.close(fig)


def caption(fig: plt.Figure, text: str, y: float) -> None:
    """Add a short business interpretation below a chart."""
    fig.text(0.10, y, f"Lectura: {text}", fontsize=7.2, color=GREY, wrap=False)


def generate_markdown(stats: dict[str, object]) -> None:
    data = stats["data"]
    sales = stats["sales"]
    cancellations = stats["cancellations"]
    monthly = stats["monthly"]
    audit = stats["cancellation_audit"]
    country_expert = stats["country_expert"]
    customer_expert = stats["customer_expert"]
    product = stats["product"]
    country = stats["country"]
    best = stats["best_month"]
    worst = stats["worst_month"]
    period = f"{data['InvoiceDate'].min():%B %Y}–{data['InvoiceDate'].max():%B %Y}"
    top_countries = country.head(5)
    top_products = product.head(5)
    audit_monthly = audit["monthly"]
    audit_country = audit["country"]
    audit_product = audit["product"]
    audit_operational = audit["operational"]
    operational_share = audit_operational.loc[
        audit_operational["IsOperationalConcept"], "CancelledValueSharePct"
    ].iloc[0]
    comparable_country = audit_country.loc[audit_country["ComparableExposure"]]
    top_cancel_country = comparable_country.sort_values("CancelledValue", ascending=False).iloc[0]
    top_cancel_product = audit_product.iloc[0]
    comparable_country_expert = country_expert.loc[country_expert["ComparableExposure"]]
    highest_country_rate = comparable_country_expert.sort_values("InvoiceCancellationRatePct", ascending=False).iloc[0]
    customer_metrics = customer_expert["metrics"]
    md = f"""# Informe ejecutivo — Online Retail EDA

## 1. Lectura para gerencia

Este informe resume la situación comercial observada en las líneas de factura del dataset UCI Online Retail durante **{period}**. La unidad original es una línea de factura; `Revenue = Quantity × UnitPrice` y no representa beneficio porque no hay costes, margen ni gastos logísticos.

### Cuadro de mando

| Indicador | Resultado | Lectura gerencial |
|---|---:|---|
| Ventas brutas positivas | {money(stats['gross'])} | Volumen comercial registrado antes de cancelaciones. |
| Valor identificado como cancelado | {money(stats['cancelled'])} ({stats['cancelled']/stats['gross']*100:.1f}% de ventas brutas) | Riesgo material que requiere conciliación. |
| Balance registrado — todas las líneas | {money(stats['recorded_balance_all_lines'])} | Suma de `Revenue` en todas las filas, incluidos ajustes y líneas con precio no positivo; no es beneficio. |
| Ingreso neto — líneas con precio positivo | {money(stats['net_revenue_positive_price_lines'])} | Suma de `Revenue` con `UnitPrice > 0`, usada para rankings de productos y países; no es beneficio. |
| Facturas con alguna cancelación | {pct(stats['cancel_rate'])} | Tasa sobre facturas, no sobre líneas. |
| Peso del Reino Unido | {pct(stats['uk_share'])} | Alta dependencia geográfica. |
| Filas con CustomerID | {pct(stats['customer_coverage'])} | La lectura de clientes no cubre todo el negocio. |

**Mensaje principal:** la empresa muestra un volumen comercial relevante, pero la lectura de rendimiento está condicionada por cancelaciones, concentración en Reino Unido y cobertura incompleta de clientes. Antes de optimizar productos o mercados conviene asegurar la conciliación de ingresos y la calidad de la identificación de clientes.

## 2. Evolución del negocio

Las ventas brutas alcanzan su máximo en **{best['Month']}** ({money(best['GrossRevenue'])}) y su mínimo en **{worst['Month']}** ({money(worst['GrossRevenue'])}). El mes de mayor actividad no demuestra por sí solo una causa concreta: no hay datos de campañas, stock, precios, costes ni calendario comercial comparable.

La media móvil de tres meses ayuda a distinguir movimientos puntuales de la evolución reciente. El periodo cubre aproximadamente un año, por lo que permite observar estacionalidad potencial, pero no comparar crecimiento interanual.

La correlación mensual entre ventas brutas y valor cancelado es **{stats['monthly_pearson']:.2f}** (Pearson) y **{stats['monthly_spearman']:.2f}** (Spearman), calculada sobre solo 13 meses. No aparece una relación conjunta estable que permita anticipar cancelaciones a partir de las ventas; conviene gestionar las cancelaciones como un proceso operativo separado. La mayor proporción mensual de valor cancelado es **{stats['peak_cancellation_share']:.1f}%** de las ventas brutas del mes, por lo que el seguimiento debe usar tanto importes absolutos como proporciones.

## 3. Cancelaciones y riesgo operativo

Se identifican {len(cancellations):,} líneas de cancelación y {stats['cancelled_invoices']:,} facturas afectadas. El valor cancelado equivale al **{stats['cancelled']/stats['gross']*100:.1f}%** de las ventas brutas positivas. Esta magnitud debe revisarse junto con devoluciones, reversiones y posibles ajustes administrativos antes de usar ingresos para objetivos o previsiones.

### Diagnóstico experto de exposición

La tasa mensual de facturas afectadas oscila entre **{audit_monthly['InvoiceCancellationRatePct'].min():.1f}%** y **{audit_monthly['InvoiceCancellationRatePct'].max():.1f}%**, mientras que el valor cancelado sobre ventas brutas oscila entre **{audit_monthly['CancellationValueRatePct'].min():.1f}%** y **{audit_monthly['CancellationValueRatePct'].max():.1f}%**. Diciembre de 2011 alcanza el máximo monetario relativo, pero termina el día 9 y no es directamente comparable con meses completos. La existencia de una tasa recurrente no demuestra que sea una tasa normal o aceptable.

El **{operational_share:.1f}%** del valor cancelado identificado corresponde a códigos clasificados como conceptos operativos, no a productos físicos. Esta clasificación no revela la causa, pero demuestra que no es riguroso interpretar todo el importe como devolución de cliente. En países con al menos 20 facturas, **{top_cancel_country['Country']}** presenta el mayor valor cancelado (**{money(top_cancel_country['CancelledValue'])}**) entre los mercados comparables; los países pequeños deben analizarse con cautela por su denominador.

El producto físico con mayor valor cancelado identificado es **{top_cancel_product['Description']}** ({money(top_cancel_product['CancelledValue'])}). Su tasa debe investigarse junto con el número de facturas y el contexto de la operación; no prueba por sí sola un problema general de producto o una preferencia negativa del cliente.

### Línea de actuación: descubrir y reducir cancelaciones evitables

Reducir las cancelaciones evitables puede mejorar la contribución económica al disminuir trabajo administrativo, costes logísticos y pérdida de ventas, pero el dataset no demuestra todavía el importe de esos costes. El prefijo `C` tampoco demuestra que todas sean devoluciones de clientes. Antes de endurecer la política de devoluciones, la empresa debería clasificar los casos por motivo: devolución, error de pedido, falta de stock, precio, entrega o ajuste administrativo.

La prioridad inicial debería ser entender qué ocurre y corregir causas operativas evitables —stock, precios, descripciones, preparación y entrega— sin deteriorar la confianza del cliente. Los casos claros y repetitivos pueden automatizarse para reducir fricción y backoffice sin impedir derechos legítimos. Cualquier cambio en la política de devoluciones debe respetar la normativa, probarse de forma controlada y evaluarse con ventas, conversión, reclamaciones, repetición de compra, costes logísticos y margen. El objetivo no es minimizar cancelaciones a cualquier coste, sino reducir coste y fricción manteniendo la relación a largo plazo con el cliente.

## 4. Clientes y concentración de valor

Los clientes recurrentes —definidos aquí como `CustomerID` asociado a más de una factura única— representan el **{pct(stats['repeat_customer_share'])}** de los clientes identificados y concentran el **{pct(stats['repeat_revenue_share'])}** del ingreso dentro de esa población. `CustomerID` está disponible en el **{stats['customer_coverage']:.1f}%** de las filas, pero cubre el **{customer_metrics['gross_sales_customer_coverage_pct']:.1f}%** de las ventas brutas positivas; ambas coberturas deben distinguirse. No puede extrapolarse la concentración identificada a las filas sin identificador.

Esta observación tiene dos lecturas gerenciales distintas: es primero un **riesgo operativo de información**, porque la cobertura de clientes impide medir el negocio completo; y, dentro de la población identificada, una señal de posible **concentración de cuentas**, útil para priorizar retención y continuidad de servicio. La cobertura de `CustomerID` en las líneas de cancelación es del **{customer_metrics['cancellation_row_customer_coverage_pct']:.1f}%**, pero esto no revela el motivo de esas cancelaciones. No permite decidir inversiones en fidelización sin margen, costes y cobertura completa.

## 5. Productos y mercados

Los diez productos físicos principales concentran aproximadamente el **{pct(stats['top10_product_share'])}** del ingreso neto de productos físicos y el primero representa aproximadamente el **{pct(stats['top_product_share'])}**. Esto no demuestra una dependencia fuerte de pocas referencias; sí justifica revisar las referencias de mayor ingreso junto con disponibilidad, margen y riesgo de sustitución.

Los cinco países con mayor **ingreso neto de líneas con precio positivo** son:

""" + "\n".join(f"- **{row.Country}:** {money(row.Revenue)} en {int(row.Invoices):,} facturas" for row in top_countries.itertuples()) + f"""

El Reino Unido representa el **{pct(stats['uk_share'])}** del ingreso neto de líneas con precio positivo. Las comparaciones internacionales deben incorporar facturas, cancelaciones, costes logísticos y margen; el ingreso por habitante solo aporta contexto y no mide cuota de mercado.

La matriz país prioriza exposición observada, no oportunidad de mercado: entre países con al menos 20 facturas, **{highest_country_rate['Country']}** presenta la mayor tasa de facturas afectadas (**{highest_country_rate['InvoiceCancellationRatePct']:.1f}%**), mientras que Reino Unido concentra el mayor impacto absoluto por su volumen. Ninguna de estas señales identifica una causa ni justifica expansión o retirada sin costes, tamaño de mercado y motivos de cancelación.

## 6. Prioridades de gestión

1. **En 0–30 días, Finanzas y Operaciones:** conciliar ventas y cancelaciones semanalmente. KPI: valor cancelado/ventas brutas y tasa de facturas afectadas.
2. **En 30–60 días, Comercial y Supply:** revisar las referencias que concentran el ingreso junto con disponibilidad y margen antes de aumentar compras.
3. **En 60–90 días, Dirección Comercial:** comparar países por ingreso, facturas, cancelaciones, costes logísticos y rentabilidad antes de invertir en expansión.
4. **En 0–30 días, Operaciones y CRM:** mejorar la captura de `CustomerID`. KPI: cobertura de filas identificadas; después, medir repetición, retención y concentración de cuentas.
5. **En el siguiente ciclo de datos, Finanzas y BI:** incorporar costes, margen, logística, campañas, stock y motivos de cancelación para pasar de facturación descriptiva a decisiones económicas.

## Anexo: principales productos por ingreso neto de líneas con precio positivo

| Producto | Ingreso | Facturas |
|---|---:|---:|
""" + "\n".join(f"| {str(row.Description)[:55]} | {money(row.Revenue)} | {int(row.Invoices):,} |" for row in top_products.itertuples()) + f"""

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

This report uses invoice-line records from UCI's Online Retail dataset during **{period}**. `Revenue = Quantity × UnitPrice`; it is recorded revenue, not profit, because costs, margins and logistics expenses are unavailable.

### Management reading

The business shows substantial recorded activity, but management interpretation is constrained by cancellations, strong UK concentration and incomplete customer identification. Gross sales, cancelled value, the all-lines recorded balance and positive-price net revenue must remain separate.

Gross sales peak in **{best['Month']}** ({money(best['GrossRevenue'])}) and reach their minimum in **{worst['Month']}** ({money(worst['GrossRevenue'])}). The monthly Pearson correlation between gross sales and cancelled value is **{stats['monthly_pearson']:.2f}**, and the rank correlation is **{stats['monthly_spearman']:.2f}**, based on only 13 months. This does not show a stable co-movement that can forecast cancellations from sales; cancellation control should be managed as a separate operational process.

Repeat customers—defined here as an observed `CustomerID` linked to more than one unique invoice—account for **{pct(stats['repeat_customer_share'])}** of identified customers and **{pct(stats['repeat_revenue_share'])}** of revenue within that identified population. This is first a data-quality issue because `CustomerID` is missing from **{100-stats['customer_coverage']:.1f}%** of rows; within the identified population it may also indicate account concentration relevant to retention and service continuity. It is not a retention or churn measure, and it is not enough to justify loyalty investment without margin and cost data.

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
"""
    MD_OUTPUT.write_text(md, encoding="utf-8")


def generate_pdf(stats: dict[str, object], output_path: Path = EXPERT_PDF_OUTPUT) -> None:
    data = stats["data"]
    monthly = stats["monthly"]
    country = stats["country"]
    country_expert = stats["country_expert"]
    product = stats["product"]
    customer = stats["customer"]
    audit = stats["cancellation_audit"]
    customer_expert = stats["customer_expert"]
    audit_monthly = audit["monthly"]
    audit_country = audit["country"]
    audit_product = audit["product"]
    audit_operational = audit["operational"]
    with PdfPages(output_path) as pdf:
        # 1. Dashboard
        fig, _ = page(pdf, "Online Retail EDA", "Informe ejecutivo · situación comercial, evolución y prioridades")
        fig.text(0.07, 0.875, "Situación actual", fontsize=12, weight="bold", color=MID_BLUE)
        fig.text(0.07, 0.845, "El negocio registra un volumen relevante, pero la lectura de rendimiento está condicionada por cancelaciones, concentración geográfica y cobertura incompleta de clientes.", fontsize=10, wrap=True)
        metrics = [("Ventas brutas (£)", money(stats["gross"])), ("Valor cancelado (£)", money(stats["cancelled"])), ("Balance todas las líneas (£)", money(stats["recorded_balance_all_lines"])), ("Neto precio positivo (£)", money(stats["net_revenue_positive_price_lines"])), ("Facturas canceladas (%)", pct(stats["cancel_rate"])), ("Peso de Reino Unido (%)", pct(stats["uk_share"])), ("Filas con CustomerID (%)", pct(stats["customer_coverage"])), ("Top 10 productos físicos (%)", pct(stats["top10_product_share"]))]
        for i, (label, value) in enumerate(metrics):
            x = 0.07 + (i % 4) * 0.23
            y = 0.75 - (i // 4) * 0.13
            fig.text(x, y, label, fontsize=9, color=GREY)
            fig.text(x, y - 0.04, value, fontsize=16, weight="bold", color=BLUE)
        fig.text(0.07, 0.44, "Qué debe saber la dirección", fontsize=12, weight="bold", color=MID_BLUE)
        bullets = [
            f"El valor cancelado equivale al {stats['cancelled']/stats['gross']*100:.1f}% de las ventas brutas positivas; el {stats['cancel_rate']:.1f}% de las facturas contiene alguna cancelación.",
            f"El Reino Unido aporta {stats['uk_share']:.1f}% del ingreso neto de líneas con precio positivo: existe dependencia de un mercado principal.",
            f"Los clientes con más de una factura concentran {stats['repeat_revenue_share']:.1f}% del ingreso identificado, pero CustomerID solo cubre {stats['customer_coverage']:.1f}% de las filas.",
            "La facturación no permite conocer beneficio sin costes, margen y gastos logísticos.",
        ]
        for i, text in enumerate(bullets):
            fig.text(0.09, 0.38 - i * 0.075, "•", fontsize=14, color=RED)
            fig.text(0.115, 0.382 - i * 0.075, text, fontsize=9.5, wrap=True)
        fig.text(0.07, 0.10, "Alcance: líneas de factura UCI Online Retail, aproximadamente diciembre de 2010 a diciembre de 2011.", fontsize=9, color=GREY)
        finish(pdf, fig)

        # 2. Evolution: both panels use explicit monetary units and explanatory titles.
        fig, _ = page(pdf, "1 · Evolución del negocio", "Ventas, cancelaciones y actividad mensual; lectura descriptiva, no causal")
        fig.text(
            0.10,
            0.885,
            f"Comprobación sobre 13 meses: correlación Pearson {stats['monthly_pearson']:.2f} · Spearman {stats['monthly_spearman']:.2f}; no se observa una relación estable.",
            fontsize=8.5,
            color=GREY,
        )
        ax1 = fig.add_axes([0.10, 0.58, 0.82, 0.24])
        ax1.plot(monthly["Month"], monthly["GrossRevenue"], marker="o", color=MID_BLUE, label="Ventas brutas")
        ax1.plot(monthly["Month"], monthly["Rolling3M"], color="#ED7D31", linewidth=2.5, label="Media móvil 3 meses")
        ax1.set_xlabel("Mes de la factura")
        ax1.set_ylabel("Ventas registradas (£)")
        ax1.set_title("Ventas brutas mensuales y media móvil de tres meses", loc="left", weight="bold")
        money_axis(ax1)
        ax1.tick_params(axis="x", rotation=65, labelsize=7)
        ax1.grid(axis="y", alpha=.25)
        ax1.legend(frameon=False, fontsize=8)
        caption(
            fig,
            "ventas suben entre septiembre y noviembre; 13 meses no permiten afirmar crecimiento interanual.",
            0.465,
        )
        ax2 = fig.add_axes([0.10, 0.21, 0.82, 0.17])
        ax2.plot(monthly["Month"], monthly["GrossRevenue"], marker="o", color=MID_BLUE, label="Ventas brutas")
        ax2.plot(monthly["Month"], monthly["CancellationValue"], marker="o", color=RED, label="Valor cancelado")
        ax2.set_xlabel("Mes de la factura")
        ax2.set_ylabel("Valor registrado (£)")
        ax2.set_title("Ventas brutas y valor cancelado: comparación mensual", loc="left", weight="bold")
        money_axis(ax2)
        ax2.tick_params(axis="x", rotation=65, labelsize=7)
        ax2.grid(axis="y", alpha=.25)
        ax2.legend(frameon=False, fontsize=8)
        caption(
            fig,
            "cancelaciones no siguen las ventas; octubre supera septiembre/noviembre y diciembre es excepcional.",
            0.085,
        )
        finish(pdf, fig)

        # 3. Cancellations and customers.
        fig, _ = page(pdf, "2 · Riesgo de cancelación y clientes", "Dos señales macro para la estabilidad comercial")
        ax1 = fig.add_axes([0.10, 0.56, 0.82, 0.25])
        ax1.bar(["Ventas brutas", "Valor cancelado"], [stats["gross"], stats["cancelled"]], color=[MID_BLUE, RED])
        ax1.set_xlabel("Indicador")
        ax1.set_ylabel("Valor registrado (£)")
        ax1.set_title("El valor cancelado es material frente a las ventas brutas", loc="left", weight="bold")
        money_axis(ax1)
        for i, value in enumerate([stats["gross"], stats["cancelled"]]):
            ax1.text(i, value, money(value), ha="center", va="bottom", fontsize=9)
        caption(
            fig,
            f"cancelaciones = {stats['cancelled']/stats['gross']*100:.1f}% de ventas brutas; indicador de conciliación, no de beneficio.",
            0.465,
        )
        ax2 = fig.add_axes([0.10, 0.22, 0.82, 0.19])
        customer_sorted = customer.sort_values("Revenue", ascending=False)
        cumulative = customer_sorted["Revenue"].cumsum() / customer_sorted["Revenue"].sum() * 100
        customer_share = np.arange(1, len(cumulative) + 1) / len(cumulative) * 100
        customers_for_80 = int((cumulative < 80).sum() + 1)
        customer_share_for_80 = customers_for_80 / len(cumulative) * 100
        ax2.plot(customer_share, cumulative, color=GREEN)
        ax2.axhline(80, linestyle="--", color=GREY, linewidth=1, label="80% del ingreso")
        ax2.axvline(customer_share_for_80, linestyle=":", color=GREY, linewidth=1)
        ax2.set(xlabel="Porcentaje acumulado de clientes identificados (de mayor a menor ingreso)", ylabel="Ingreso acumulado (%)", title=f"El {customer_share_for_80:.1f}% de clientes identificados aporta el 80% del ingreso")
        ax2.legend(frameon=False, fontsize=8)
        ax2.grid(alpha=.25)
        caption(
            fig,
            f"{customer_share_for_80:.1f}% de clientes identificados aporta 80%; CustomerID cubre {customer_expert['metrics']['gross_sales_customer_coverage_pct']:.1f}% de ventas brutas positivas.",
            0.085,
        )
        finish(pdf, fig)

        # 4. Products and markets: only the two macro views.
        fig, _ = page(pdf, "3 · Productos y mercados principales", "Dónde se genera el ingreso de líneas con UnitPrice > 0 y qué debe revisarse antes de asignar recursos")
        ax1 = fig.add_axes([0.27, 0.56, 0.63, 0.25])
        top_products = product.head(8).sort_values("Revenue")
        labels = [str(value)[:22] for value in top_products["Description"]]
        ax1.barh(labels, top_products["Revenue"], color=MID_BLUE)
        ax1.set_xlabel("Ingreso neto — líneas con precio positivo (£)")
        ax1.set_ylabel("Producto físico")
        ax1.set_title("Top 8 productos físicos · ingreso neto (UnitPrice > 0)", loc="left", weight="bold")
        ax1.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"£{value/1000:.0f}k"))
        caption(
            fig,
            f"top 10 = {stats['top10_product_share']:.1f}% del ingreso físico; no hay fuerte dependencia de pocas referencias.",
            0.465,
        )
        ax2 = fig.add_axes([0.27, 0.20, 0.63, 0.22])
        top_countries = country.head(8).sort_values("Revenue")
        ax2.barh(top_countries["Country"], top_countries["Revenue"], color=GREEN)
        ax2.set_xlabel("Ingreso neto — líneas con precio positivo (£)")
        ax2.set_ylabel("País")
        ax2.set_title("Top 8 países · ingreso neto (UnitPrice > 0)", loc="left", weight="bold")
        ax2.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"£{value/1_000_000:.1f}M" if abs(value) >= 1_000_000 else f"£{value/1000:.0f}k"))
        caption(
            fig,
            f"Reino Unido = {stats['uk_share']:.1f}% del ingreso neto con precio positivo; no es cuota de mercado ni rentabilidad.",
            0.075,
        )
        finish(pdf, fig)

        # 5. Expert country exposure matrix.
        fig, _ = page(
            pdf,
            "4 · Matriz experta de países",
            "Dónde priorizar investigación combinando peso económico y exposición a cancelaciones",
        )
        fig.text(
            0.10,
            0.885,
            "Países con ≥20 facturas · tamaño = valor cancelado · color = señal relativa de exposición.",
            fontsize=8.5,
            color=GREY,
        )
        ax1 = fig.add_axes([0.12, 0.28, 0.76, 0.48])
        comparable_expert = country_expert.loc[country_expert["ComparableExposure"]].copy()
        exposure_colors = {
            "Above-average cancellation exposure": RED,
            "Below-average cancellation exposure": GREEN,
            "Mixed cancellation signals": "#ED7D31",
        }
        point_colors = comparable_expert["ExposureClass"].map(exposure_colors).fillna("#ED7D31")
        point_sizes = 60 + comparable_expert["CancelledValue"] / comparable_expert["CancelledValue"].max() * 700
        ax1.scatter(
            comparable_expert["NetRevenuePositivePriceLines"],
            comparable_expert["InvoiceCancellationRatePct"],
            s=point_sizes,
            c=point_colors,
            alpha=.75,
            edgecolor="white",
            linewidth=.7,
        )
        labelled_countries = {"United Kingdom", "Japan", "Germany", "Netherlands", "Ireland"}
        for row in comparable_expert.itertuples():
            if row.Country not in labelled_countries:
                continue
            label = "UK" if row.Country == "United Kingdom" else str(row.Country)
            ax1.annotate(label, (row.NetRevenuePositivePriceLines, row.InvoiceCancellationRatePct), fontsize=6.5, xytext=(3, 3), textcoords="offset points")
        ax1.set_xscale("log")
        ax1.set_xlabel("Ingreso neto — líneas con precio positivo (£, escala logarítmica)")
        ax1.set_ylabel("Facturas afectadas (%)")
        ax1.set_title("Peso económico y exposición operativa por país", loc="left", weight="bold")
        ax1.grid(alpha=.25)
        for label, color in exposure_colors.items():
            ax1.scatter([], [], s=70, color=color, label=label)
        ax1.legend().remove()
        fig.text(
            0.13,
            0.785,
            "Color: rojo = ambas tasas altas · verde = ambas bajas · naranja = señales mixtas",
            fontsize=7.5,
            color=GREY,
        )
        caption(
            fig,
            "prioriza investigación; no mide cuota, margen ni causa.",
            0.15,
        )
        finish(pdf, fig)

        # 6. Identified-customer concentration and priority accounts.
        fig, _ = page(
            pdf,
            "5 · Clientes identificados",
            "Concentración del ingreso observado y cuentas que requieren continuidad de servicio",
        )
        customer_metrics = customer_expert["metrics"]
        fig.text(
            0.10,
            0.885,
            f"{customer_metrics['identified_customer_count']:,} clientes identificados · {customer_metrics['gross_sales_customer_coverage_pct']:.1f}% de ventas brutas positivas cubiertas por CustomerID.",
            fontsize=8.5,
            color=GREY,
        )
        ax1 = fig.add_axes([0.28, 0.52, 0.62, 0.27])
        top_customers = customer_expert["customers"].head(10).copy().sort_values("Revenue")
        top_customers["CustomerRank"] = np.arange(len(top_customers), 0, -1)
        labels = [f"Cliente {rank}" for rank in top_customers["CustomerRank"]]
        ax1.barh(labels, top_customers["Revenue"], color=GREEN)
        ax1.set_xlabel("Ingreso bruto positivo (£)")
        ax1.set_ylabel("Ranking por ingreso")
        ax1.set_title("Top 10 clientes identificados por ingreso", loc="left", weight="bold")
        ax1.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"£{value / 1000:.0f}k"))
        ax1.grid(axis="x", alpha=.25)
        ax1.tick_params(axis="y", labelsize=8)
        caption(
            fig,
            "el ranking ayuda a localizar cuentas prioritarias, pero no prueba rentabilidad ni permite medir retención con este dataset.",
            0.43,
        )
        ax2 = fig.add_axes([0.12, 0.14, 0.76, 0.20])
        customer_sorted = customer_expert["customers"].sort_values("Revenue", ascending=False)
        cumulative = customer_sorted["Revenue"].cumsum() / customer_sorted["Revenue"].sum() * 100
        customer_share = np.arange(1, len(cumulative) + 1) / len(cumulative) * 100
        ax2.plot(customer_share, cumulative, color=GREEN)
        ax2.axhline(80, linestyle="--", color=GREY, linewidth=1, label="80% del ingreso")
        ax2.axvline(customer_metrics["customers_for_80_share_pct"], linestyle=":", color=GREY, linewidth=1)
        ax2.set_xlabel("Porcentaje acumulado de clientes identificados (ordenados por ingreso)")
        ax2.set_ylabel("Ingreso acumulado (%)")
        ax2.set_title("Concentración acumulada del ingreso identificado", loc="left", weight="bold", fontsize=10)
        ax2.legend(frameon=False, fontsize=7)
        ax2.grid(alpha=.25)
        caption(
            fig,
            f"{customer_metrics['customers_for_80_share_pct']:.1f}% de los clientes identificados aporta 80% del ingreso identificado; no se extrapola a filas sin CustomerID.",
            0.075,
        )
        finish(pdf, fig)

        # 7. Expert cancellation audit.
        fig, _ = page(
            pdf,
            "6 · Diagnóstico experto de cancelaciones",
            "Exposición por tiempo, país y producto; la clasificación C no demuestra una devolución",
        )
        fig.text(
            0.10,
            0.885,
            f"Valor cancelado identificado: {money(stats['cancelled'])} · {audit_operational.loc[audit_operational['IsOperationalConcept'], 'CancelledValueSharePct'].iloc[0]:.1f}% corresponde a códigos operativos.",
            fontsize=8.5,
            color=GREY,
        )
        ax1 = fig.add_axes([0.10, 0.57, 0.82, 0.24])
        ax1.plot(
            audit_monthly["Month"],
            audit_monthly["InvoiceCancellationRatePct"],
            marker="o",
            color=RED,
            label="Facturas afectadas (%)",
        )
        ax1.plot(
            audit_monthly["Month"],
            audit_monthly["CancellationValueRatePct"],
            marker="o",
            color="#ED7D31",
            label="Valor cancelado / ventas (%)",
        )
        ax1.set_xlabel("Mes de la factura")
        ax1.set_ylabel("Tasa (%)")
        ax1.set_title("La extensión y el impacto económico de las cancelaciones no son lo mismo", loc="left", weight="bold")
        ax1.set_ylim(bottom=0)
        ax1.tick_params(axis="x", rotation=65, labelsize=7)
        ax1.grid(axis="y", alpha=.25)
        ax1.legend(frameon=False, fontsize=8)
        peak_value_month = audit_monthly.loc[audit_monthly["CancellationValueRatePct"].idxmax(), "Month"]
        caption(
            fig,
            f"tasa de facturas afectadas; impacto monetario máximo en {peak_value_month}. Diciembre es incompleto.",
            0.485,
        )

        ax2 = fig.add_axes([0.18, 0.18, 0.29, 0.22])
        comparable = audit_country.loc[audit_country["ComparableExposure"]].copy()
        comparable = comparable.sort_values("CancelledValue", ascending=False).head(12).sort_values("InvoiceCancellationRatePct")
        comparable["CountryDisplay"] = comparable["Country"].replace({"United Kingdom": "UK"})
        ax2.barh(comparable["CountryDisplay"], comparable["InvoiceCancellationRatePct"], color=RED)
        ax2.set_xlabel("Facturas afectadas (%)")
        ax2.set_ylabel("País · mínimo 20 facturas")
        ax2.set_title("Tasa por factura y exposición suficiente", loc="left", weight="bold", fontsize=10)
        ax2.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0f}%"))
        ax2.tick_params(axis="y", labelsize=7)
        ax2.grid(axis="x", alpha=.25)

        ax3 = fig.add_axes([0.64, 0.18, 0.28, 0.22])
        physical_products = audit_product.head(8).sort_values("CancelledValue")
        physical_products["DescriptionDisplay"] = physical_products["Description"].astype(str).str[:17]
        ax3.barh(physical_products["DescriptionDisplay"], physical_products["CancelledValue"], color=RED)
        ax3.set_xlabel("Valor cancelado identificado (£)")
        ax3.set_ylabel("Producto físico")
        ax3.set_title("Top físicos por cancelado", loc="left", weight="bold", fontsize=10)
        ax3.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"£{value / 1000:.0f}k"))
        ax3.tick_params(axis="y", labelsize=6.5)
        ax3.grid(axis="x", alpha=.25)
        caption(
            fig,
            "países pequeños: tasas inestables. Productos extremos y códigos operativos requieren investigar causas.",
            0.085,
        )
        finish(pdf, fig)

        # 8. Decisions and limitations, no chart overload.
        fig, _ = page(pdf, "7 · Prioridades para la dirección", "Qué decisiones están respaldadas por los datos y cuáles requieren información adicional")
        sections = [
            ("Actuar en 0–30 días", ["Finanzas y Operaciones: conciliar ventas y cancelaciones semanalmente; KPI: valor cancelado/ventas y tasa de facturas afectadas.", "Operaciones y Atención al Cliente: clasificar el motivo de cada cancelación y automatizar casos claros y repetitivos.", "Operaciones y CRM: mejorar la captura de CustomerID; KPI: cobertura de filas identificadas."]),
            ("Decidir en 30–90 días", ["Comercial y Supply: revisar referencias de mayor ingreso y casos extremos de cancelación con disponibilidad y margen.", "Dirección Comercial: comparar países con ingreso, facturas, cancelaciones, logística y rentabilidad.", "Legal y Atención al Cliente: pilotar cambios limitados en devoluciones solo con métricas de conversión, reclamaciones, repetición, coste y margen."]),
            ("Información que falta", ["Coste y margen por producto y país.", "Motivo de cancelación, devolución o ajuste.", "Gastos logísticos, campañas, stock y canales de adquisición."]),
        ]
        y = 0.83
        for title, items in sections:
            fig.text(0.09, y, title, fontsize=12, weight="bold", color=MID_BLUE)
            y -= 0.045
            for item in items:
                fig.text(0.11, y, "•", fontsize=13, color=RED)
                fig.text(0.14, y, item, fontsize=10, wrap=True)
                y -= 0.055
            y -= 0.045
        fig.text(0.09, 0.10, "Conclusión: reducir cancelaciones evitables puede mejorar la contribución, pero primero hay que medir causas y costes; el dataset no permite atribuir causas ni calcular rentabilidad.", fontsize=10, weight="bold", color=BLUE, wrap=True)
        finish(pdf, fig)


def main() -> None:
    stats = base_data()
    PDF_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    generate_markdown(stats)
    generate_pdf(stats, EXPERT_PDF_OUTPUT)
    print(f"Generated {EXPERT_PDF_OUTPUT}")
    print(f"Generated {MD_OUTPUT}")


if __name__ == "__main__":
    main()
