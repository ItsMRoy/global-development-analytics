# Case study: How did development indicators differ by region, 1952–2007?

**Business/research question.** How did country-level life expectancy change over the historical observation period? How much variation existed between regions by 2007, and how strongly was GDP per capita associated with life expectancy across the included countries?

**Dataset.** Gapminder/Plotly country-year panel: 1,704 records, 142 countries, 12 five-year observations, 1952–2007. This is a retrospective analytical exercise, not current country-level monitoring.

## Analytical workflow

1. Load and validate a primary-key structure of country and year; inspect missingness and value ranges.
2. Compute population-weighted regional and overall mean life expectancy, plus country-average values for comparison.
3. Calculate median country GDP per capita by region/year, avoiding presentation of it as GDP-weighted output.
4. Compare countries' absolute improvements in life expectancy between 1952 and 2007.
5. Evaluate rank-based association between GDP per capita and life expectancy across countries in 2007 (Spearman rho). This is descriptive/ecological and does not imply causation.
6. Reproduce key aggregates with SQL and deliver a standalone interactive HTML dashboard.

## Results

<!-- Values are validated using src/analytics.py. -->
- Observed country-year rows: **1,704**, with **142 countries**.
- Population-weighted life expectancy among the included countries increased from **48.94 years (1952)** to **68.92 years (2007)**, an increase of **19.97 years**.
- In 2007, **Oceania (81.06 years)** had the highest population-weighted regional figure and **Africa (54.56 years)** the lowest in this panel. **Caution:** Oceania includes only two countries here, so it is not representative of all Oceania.
- Across 142 countries in 2007, the Spearman rank correlation between GDP per capita and life expectancy was approximately **0.857**. Higher GDP per capita was associated with longer lifespan, but this cannot establish cause or account for historical confounding.

## Decision relevance

For a development organization, the region-level comparison can motivate more targeted investigation of historical health gaps. For a commercial analytics employer, the same workflow demonstrates reproducible extraction, weighted KPI definition, SQL queries and interactive stakeholder reporting. It is *not* evidence for contemporary policy or business decisions.

## Limitations

- Data are historical (1952–2007); **do not** label as recent or current.
- Country samples/coverage and geography definitions differ from full world coverage; region-level conclusions are limited accordingly.
- Population-weighted averages can mask within-country inequalities and uncertainty.
- GDP per capita and life expectancy are not randomized exposures; correlation is not causation.
- Panel observations every **five years**, not annual. Never apply monthly or yearly churn analogies to this dataset.
- Due to two-country Oceania coverage, be particularly cautious with that region's values.

## What I would do next

Refresh this framework using verified World Bank API data and compare population-weighted results with household-level survey outcomes when appropriate. This would require a new dataset and metadata review—not simply relabeling the historical figures.
