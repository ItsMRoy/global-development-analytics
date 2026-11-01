-- SQLite SQL queries for development analytics.
-- Data comes from country_year table created by: python run_all.py
-- All measures are descriptive. An aggregated regional "global" claim
-- applies ONLY to the 142 countries included in the Gapminder panel.

-- Q1. Dataset quality and scope
SELECT COUNT(*) AS records, COUNT(DISTINCT country) AS countries,
       MIN(year) AS first_year, MAX(year) AS last_year
FROM country_year;

-- Q2. Country-year weighted regional life expectancy, 2007
SELECT continent, COUNT(*) AS countries,
       ROUND(SUM(lifeExp * pop) / SUM(pop), 2) AS weighted_life_expectancy,
       ROUND(AVG(lifeExp), 2) AS country_average_life_expectancy
FROM country_year
WHERE year = 2007
GROUP BY continent
ORDER BY weighted_life_expectancy DESC;

-- Q3. Changes between observations; five-year intervals, NOT annual trends
WITH change_over_time AS (
  SELECT country, continent, year, lifeExp,
         LAG(lifeExp) OVER (PARTITION BY country ORDER BY year) AS prior_life_exp
  FROM country_year
)
SELECT country, continent, year,
       ROUND(lifeExp-prior_life_exp, 2) AS change_since_prior_observation
FROM change_over_time
WHERE prior_life_exp IS NOT NULL
ORDER BY change_since_prior_observation DESC
LIMIT 20;

-- Q4. Top 10 countries by absolute life expectancy change, 1952 to 2007
WITH endpoints AS (
  SELECT country, continent,
         MAX(CASE WHEN year=1952 THEN lifeExp END) AS life_1952,
         MAX(CASE WHEN year=2007 THEN lifeExp END) AS life_2007
  FROM country_year
  GROUP BY country, continent
)
SELECT country, continent, ROUND(life_1952,2) AS life_1952,
       ROUND(life_2007,2) AS life_2007,
       ROUND(life_2007-life_1952,2) AS improvement_years
FROM endpoints
WHERE life_1952 IS NOT NULL AND life_2007 IS NOT NULL
ORDER BY improvement_years DESC LIMIT 10;

-- Q5. Country rankings by per-capita GDP, 2007; does not measure total GDP
SELECT country, continent,
       ROUND(gdpPercap,0) AS gdp_per_capita,
       ROUND(lifeExp,1) AS life_expectancy
FROM country_year
WHERE year=2007
ORDER BY gdpPercap DESC
LIMIT 15;

-- Q6. 1952 vs 2007, region-level population-weighted life expectancy
SELECT continent, year,
       ROUND(SUM(lifeExp*pop)/SUM(pop),2) AS weighted_life_exp
FROM country_year
WHERE year IN (1952,2007)
GROUP BY continent,year
ORDER BY continent,year;
