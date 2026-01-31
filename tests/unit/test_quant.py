import unittest
import pandas as pd
from core.engines.quantitative.performance import max_drawdown

class TestQuant(unittest.TestCase):
    def test_max_drawdown(self):
        s = pd.Series([100, 120, 90, 95, 80, 130])
        dd = max_drawdown(s)
        self.assertAlmostEqual(dd, 80/120 - 1)

if __name__ == '__main__':
    unittest.main()
