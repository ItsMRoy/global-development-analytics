# Data dictionary

Each row is a `country` × `year` observation, at five-year intervals from 1952 through 2007.

| Field | Meaning |
| --- | --- |
| `country` | Country name in historical dataset |
| `continent` | Gapminder continent category |
| `year` | Observation year |
| `lifeExp` | Life expectancy at birth, years |
| `pop` | Population estimate in the given country-year |
| `gdpPercap` | GDP per capita in dataset units (often described as inflation-adjusted US dollars; check original documentation before economic comparisons) |
| `iso_alpha` | Three-character country code |
| `iso_num` | Numeric country code |

**Cleaning:** CSV parsing, required-column and duplicate-key validation, null checking and range checks. No imputation. Historical panel supplied with Plotly is already structured/clean. This project does not claim to have performed substantial missing-data cleaning.

**Weighting:** The overall/regional life expectancy is the sum of country life expectancy multiplied by population, divided by the sum of population. It is an approximation of the life expectancy of the represented population—not an independently calculated life table.

**Scope:** Only 142 countries included in this dataset; historical country coverage is not global. Each country-year contributes one observation. Countries are not a probability sample.
