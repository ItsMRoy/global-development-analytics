"""Tests verify coverage, arithmetic, and reproducibility."""
import sqlite3
from contextlib import closing
import tempfile
import unittest
from pathlib import Path
from src.analytics import load_data, annual_summary, regional_summary, country_change, weighted_mean, save_database

class TestAnalytics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = load_data()

    def test_expected_panel(self):
        self.assertEqual(len(self.df), 1704)
        self.assertEqual(self.df.country.nunique(), 142)
        self.assertEqual(self.df.year.nunique(), 12)
        self.assertFalse(self.df.duplicated(["country", "year"]).any())

    def test_weighted_mean(self):
        self.assertAlmostEqual(weighted_mean([10,20], [1,3]), 17.5)

    def test_annual_summary(self):
        report = annual_summary(self.df)
        self.assertEqual(len(report), 12)
        self.assertAlmostEqual(float(report.iloc[0].weighted_life_expectancy), 48.944237, places=4)
        self.assertAlmostEqual(float(report.iloc[-1].weighted_life_expectancy),68.919093,places=4)

    def test_region_groups(self):
        rep = regional_summary(self.df)
        self.assertEqual(len(rep),60)
        self.assertEqual(set(rep.continent),set(self.df.continent))

    def test_country_change(self):
        report=country_change(self.df)
        self.assertEqual(len(report),142)
        self.assertTrue(report.life_expectancy_change_years.notna().all())

    def test_all_sql_examples_run(self):
        statements = (Path(__file__).resolve().parents[1] / 'sql' / 'analyst_queries.sql').read_text()
        statements = '\n'.join(line for line in statements.splitlines() if not line.lstrip().startswith('--'))
        with tempfile.TemporaryDirectory() as p:
            db = Path(p) / 'example.sqlite'
            save_database(self.df, db)
            with closing(sqlite3.connect(db)) as conn:
                results = [conn.execute(s).fetchall() for s in statements.split(';') if s.strip()]
        self.assertEqual(len(results), 6)
        self.assertEqual(results[0][0][0], 1704)

    def test_sqlite_round_trip(self):
        with tempfile.TemporaryDirectory() as p:
            db=Path(p)/'test.sqlite'
            save_database(self.df, db)
            with closing(sqlite3.connect(db)) as c:
                self.assertEqual(c.execute('SELECT COUNT(*) FROM country_year').fetchone()[0],1704)
                result=c.execute('SELECT SUM(lifeExp*pop)*1.0/SUM(pop) FROM country_year WHERE year=2007').fetchone()[0]
            self.assertAlmostEqual(result,68.919093,places=4)

if __name__ == '__main__':
    unittest.main()
