import unittest
from datetime import date
import pandas as pd
from analysis import metrics, project

class Calculations(unittest.TestCase):
    def test_known_growth_and_drawdown(self):
        series = pd.Series([100., 120., 90., 110.], index=pd.to_datetime(['2020-01-01','2020-05-01','2020-09-01','2021-01-01']))
        total, cagr, vol, drawdown = metrics(series)
        self.assertAlmostEqual(total, .1)
        self.assertAlmostEqual(cagr, 1.1 ** (365.25 / 366) - 1)
        self.assertAlmostEqual(drawdown, -.25)
        self.assertGreater(vol, 0)

    def test_zero_return_contributions_and_partial_month(self):
        path = project(1000, 100, 0, date(2026,1,31), date(2026,4,15))
        self.assertEqual(path['Projected value'].iloc[-1], 1200)
        self.assertEqual(path['Contributed'].iloc[-1], 1200)
        self.assertEqual(path['Date'].iloc[1], pd.Timestamp('2026-02-28'))

    def test_compound_growth_without_contributions(self):
        path = project(1000, 0, .08, date(2026,1,1), date(2035,12,31))
        self.assertAlmostEqual(path['Projected value'].iloc[-1], 1000 * 1.08 ** ((date(2035,12,31)-date(2026,1,1)).days / 365.25))

    def test_negative_return_and_zero_purchase(self):
        self.assertLess(project(1000, 0, -.2, date(2026,1,1), date(2027,1,1))['Projected value'].iloc[-1], 1000)
        self.assertEqual(project(0, 0, .08, date(2026,1,1), date(2035,12,31))['Projected value'].iloc[-1], 0)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            project(100, 0, -1, date(2026,1,1), date(2035,1,1))

if __name__ == '__main__':
    unittest.main()
