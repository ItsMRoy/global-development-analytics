"""Run all analytics and create an offline interactive dashboard."""
from src.analytics import produce_outputs
from src.charts import make_figures

if __name__ == '__main__':
    df, annual, regional, changes, metrics = produce_outputs()
    make_figures(df, annual, regional, changes, metrics, __import__('pathlib').Path(__file__).resolve().parent)
    print("Complete. See dashboard/index.html, reports/figures/, reports/metrics.json")
    for k in ["countries", "rows", "start_population_weighted_life_expectancy", "end_population_weighted_life_expectancy", "cross_country_spearman_rho_last_year"]:
        print(f"{k}: {metrics[k]}")
