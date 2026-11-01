"""Reproducible, descriptive analytics for historical Gapminder country-year data."""
from pathlib import Path
import json
import sqlite3
from contextlib import closing
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "gapminder_1952_2007.csv"
EXPECTED = {"country", "continent", "year", "lifeExp", "pop", "gdpPercap", "iso_alpha", "iso_num"}


def load_data(path=RAW):
    df = pd.read_csv(path)
    absent = EXPECTED.difference(df.columns)
    if absent:
        raise ValueError(f"Missing required data columns: {sorted(absent)}")
    if df.duplicated(subset=["country", "year"]).any():
        raise ValueError("Duplicate country-year pairs")
    if df[list(EXPECTED)].isna().any().any():
        raise ValueError("Missing observations in required columns")
    if (df["pop"] <= 0).any() or (df["gdpPercap"] <= 0).any():
        raise ValueError("Non-positive populations or GDP per capita")
    if (~df["lifeExp"].between(0, 120)).any():
        raise ValueError("Life expectancy outside expected range")
    df["year"] = df["year"].astype(int)
    return df.sort_values(["country", "year"]).reset_index(drop=True)


def weighted_mean(values, weights):
    return float(np.average(np.asarray(values, dtype=float), weights=np.asarray(weights, dtype=float)))


def annual_summary(df):
    rows = []
    for year, part in df.groupby("year", sort=True):
        rows.append({
            "year": int(year), "countries": int(part["country"].nunique()),
            "represented_population": int(part["pop"].sum()),
            "weighted_life_expectancy": weighted_mean(part["lifeExp"], part["pop"]),
            "median_gdp_per_capita": float(part["gdpPercap"].median()),
        })
    return pd.DataFrame(rows)


def regional_summary(df):
    rows = []
    for (year, continent), part in df.groupby(["year", "continent"], sort=True):
        rows.append({
            "year": int(year), "continent": continent,
            "countries": int(part["country"].nunique()),
            "represented_population": int(part["pop"].sum()),
            "weighted_life_expectancy": weighted_mean(part["lifeExp"], part["pop"]),
            "unweighted_life_expectancy": float(part["lifeExp"].mean()),
            "median_gdp_per_capita": float(part["gdpPercap"].median()),
        })
    return pd.DataFrame(rows)


def country_change(df):
    first_year = int(df["year"].min())
    last_year = int(df["year"].max())
    start = df[df["year"] == first_year].set_index("country")
    end = df[df["year"] == last_year].set_index("country")
    shared = start.index.intersection(end.index)
    frame = pd.DataFrame({
        "country": shared,
        "continent": end.loc[shared, "continent"].values,
        "life_expectancy_start": start.loc[shared, "lifeExp"].values,
        "life_expectancy_end": end.loc[shared, "lifeExp"].values,
        "gdp_per_capita_start": start.loc[shared, "gdpPercap"].values,
        "gdp_per_capita_end": end.loc[shared, "gdpPercap"].values,
    })
    frame["life_expectancy_change_years"] = frame["life_expectancy_end"] - frame["life_expectancy_start"]
    frame["gdp_per_capita_ratio"] = frame["gdp_per_capita_end"] / frame["gdp_per_capita_start"]
    return frame.sort_values("life_expectancy_change_years", ascending=False).reset_index(drop=True)


def key_metrics(df, annual, regional):
    start, end = int(df["year"].min()), int(df["year"].max())
    a, b = annual.iloc[0], annual.iloc[-1]
    latest = df[df["year"] == end]
    rho, p = spearmanr(latest["gdpPercap"], latest["lifeExp"])
    summary = regional[regional["year"] == end]
    hi = summary.loc[summary["weighted_life_expectancy"].idxmax()]
    lo = summary.loc[summary["weighted_life_expectancy"].idxmin()]
    return {
        "source": "Gapminder data bundled with Plotly (historical country-year panel)",
        "first_year": start, "last_year": end,
        "rows": int(len(df)), "countries": int(df["country"].nunique()),
        "years_observed": int(df["year"].nunique()),
        "start_population_weighted_life_expectancy": round(float(a["weighted_life_expectancy"]), 2),
        "end_population_weighted_life_expectancy": round(float(b["weighted_life_expectancy"]), 2),
        "change_in_weighted_life_expectancy_years": round(float(b["weighted_life_expectancy"]-a["weighted_life_expectancy"]), 2),
        "highest_region_in_last_year": str(hi["continent"]),
        "highest_region_weighted_life_expectancy": round(float(hi["weighted_life_expectancy"]), 2),
        "lowest_region_in_last_year": str(lo["continent"]),
        "lowest_region_weighted_life_expectancy": round(float(lo["weighted_life_expectancy"]), 2),
        "cross_country_spearman_rho_last_year": round(float(rho), 3),
        "cross_country_spearman_p_last_year": float(p),
    }


def save_database(df, path):
    with closing(sqlite3.connect(path)) as conn:
        with conn:
            df.to_sql("country_year", conn, if_exists="replace", index=False)
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_country_year ON country_year (country, year)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_year_continent ON country_year (year, continent)")


def produce_outputs(root=ROOT):
    df = load_data(root / "data" / "gapminder_1952_2007.csv")
    annual = annual_summary(df)
    regional = regional_summary(df)
    changes = country_change(df)
    metrics = key_metrics(df, annual, regional)
    (root / "reports").mkdir(exist_ok=True)
    annual.to_csv(root / "reports" / "annual_summary.csv", index=False)
    regional.to_csv(root / "reports" / "regional_summary.csv", index=False)
    changes.to_csv(root / "reports" / "country_changes.csv", index=False)
    (root / "reports" / "metrics.json").write_text(json.dumps(metrics, indent=2)+"\n", encoding="utf-8")
    save_database(df, root / "data" / "development.sqlite")
    return df, annual, regional, changes, metrics
