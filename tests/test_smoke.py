"""Regression checks for all three format filters and ranking invariants."""
import unittest
import numpy as np
from analytics import load, formats, calculate, unreliable_chase_ids
from bowling_analytics import calculate_bowling_final

class DashboardSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, *_ = load()

    def test_format_partition(self):
        all_rows = formats(self.source, "All")
        ipl = formats(self.source, "IPL")
        intl = formats(self.source, "T20Is")
        self.assertEqual(len(all_rows), len(self.source))
        self.assertLessEqual(len(ipl) + len(intl), len(all_rows))
        self.assertEqual(len(ipl), int(ipl.comp_name.str.match(r"^IPL\\s+20\\d\\d$", case=False).sum()))
        self.assertTrue(intl.match_format.eq("T20I").all())

    def test_rankings_and_pressure(self):
        for choice in ("All", "T20Is", "IPL"):
            with self.subTest(choice=choice):
                bat, _, raw, _ = calculate(choice)
                bowl, _, bowling_raw = calculate_bowling_final(choice)
                self.assertEqual(len(raw), len(formats(self.source, choice)))
                self.assertTrue(raw.pressure_flag.notna().all())
                self.assertFalse(raw.loc[raw.innings.isin([3, 4]), "pressure_flag"].any())
                self.assertTrue(bowling_raw.innings.isin([1, 2]).all())
                for ranked in (bat, bowl):
                    self.assertFalse(ranked.empty, "No eligible ranked players")
                    scores = ranked.final_score_200.astype(float)
                    self.assertTrue(np.isfinite(scores).all())
                    self.assertTrue(scores.between(0, 200).all())
                    self.assertTrue(scores.is_monotonic_decreasing)
                bad = unreliable_chase_ids()
                self.assertFalse(raw.loc[raw.match_id.isin(bad), "pressure_chase"].any())
                self.assertFalse(bowling_raw.loc[bowling_raw.match_id.isin(bad), "pressure"].any())

if __name__ == "__main__":
    unittest.main()
