"""Synthetic inference checks only; never rescore experimental outputs."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evaluation"))
import final_paired_statistics as stats


class PairedStatisticsTests(unittest.TestCase):
    def test_exact_two_sided_sign_and_flip(self):
        self.assertEqual(stats.sign_p(0, 0), 1)
        self.assertEqual(stats.sign_p(6, 0), .03125)
        self.assertEqual(stats.exact_flip([1] * 6), .03125)
        self.assertEqual(stats.exact_flip([1, -1, 0]), 1)
        self.assertEqual(stats.exact_flip([25, 25]), .5)

    def test_holm_is_global_and_monotone(self):
        rows = [{"p_value": p} for p in (.001, .02, .04)]
        stats.holm(rows)
        self.assertEqual([r["p_holm"] for r in rows], [.003, .04, .04])
        self.assertTrue(all(r["multiplicity_family_size"] == 3 for r in rows))

    def test_ordinal_direction_effect_does_not_use_rating_distances(self):
        pairs = [{"baseline": {"v": b}, "tavf": {"v": t}} for b, t in ((1, 5), (5, 4), (4, 4))]
        with patch.object(stats, "BOOTSTRAPS", 100):
            result = stats.endpoint("synthetic", "human", "fixture", "criterion", pairs,
                                    lambda row: (row["v"], "valid"), ordinal=True)
        self.assertEqual(result["effect"], 0)
        self.assertEqual(result["probability_of_superiority"], .5)
        self.assertEqual(result["valid_pair_n"], 3)
        self.assertEqual(result["discordant_pair_n"], 2)

    def test_unknown_excluded_conditionally_but_not_from_availability_denominator(self):
        pairs = [{"baseline": {"v": None}, "tavf": {"v": 1}}, {"baseline": {"v": 0}, "tavf": {"v": 1}}]
        with patch.object(stats, "BOOTSTRAPS", 100):
            conditional = stats.endpoint("conditional", "test", "fixture", "criterion", pairs, lambda r: (r["v"], "state"))
            available = stats.endpoint("available", "test", "fixture", "criterion", pairs, lambda r: (r["v"], "state"), yield_only=True)
        self.assertEqual(conditional["valid_pair_n"], 1)
        self.assertEqual(available["valid_pair_n"], 2)
        self.assertEqual(conditional["excluded_pair_patterns"], {"tavf_only_assessable": 1})

    def test_program_clustering_and_reproducible_intervals(self):
        pairs = [{"baseline": {"v": 0, "task": {"reference": {"task_num": 7}}}, "tavf": {"v": 1}} for _ in range(3)]
        with patch.object(stats, "BOOTSTRAPS", 100):
            a = stats.endpoint("cluster", "test", "fixture", "criterion", pairs, lambda r: (r["v"], "state"), cluster=True)
            b = stats.endpoint("cluster", "test", "fixture", "criterion", pairs, lambda r: (r["v"], "state"), cluster=True)
        self.assertEqual(a["independent_unit_n"], 1)
        self.assertEqual(a["p_value"], 1)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
