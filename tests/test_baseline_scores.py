
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "evaluation"))

import calculate_baseline_scores as calculator


class TestBaselineScores(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        folder = Path(self.temp.name)
        self.input_file = folder / "scores.csv"
        self.output_file = folder / "calculated.csv"

        # Copy the original template into a temporary file.
        self.df = pd.read_csv(
            ROOT / "results/baseline/baseline_scores.csv",
            dtype=str,
            keep_default_na=False,
        )

        self.assertEqual(len(self.df), 60)

    def run_calculator(self):
        self.df.to_csv(self.input_file, index=False)

        with (
            patch.object(
                calculator, "INPUT_FILE", self.input_file
            ),
            patch.object(
                calculator, "OUTPUT_FILE", self.output_file
            ),
        ):
            calculator.main()

        return pd.read_csv(
            self.output_file,
            dtype=str,
            keep_default_na=False,
        )

    def test_correct_score(self):
        criteria = calculator.CRITERIA[
            "user_story_refinement"
        ]

        scores = [2, 2, 1, 2, 1, 2, 2, 2]

        self.df.loc[0, "output_available"] = "True"

        for criterion, score in zip(criteria, scores):
            self.df.loc[0, criterion] = str(score)

        result = self.run_calculator()

        self.assertEqual(
            result.loc[0, "quality_score"], "14"
        )
        self.assertEqual(
            float(result.loc[0, "normalized_quality"]),
            87.5,
        )
        self.assertEqual(
            result.loc[0, "evaluation_status"],
            "completed",
        )

    def test_invalid_score(self):
        self.df.loc[0, "output_available"] = "True"
        self.df.loc[0, "atomicity"] = "3"

        with self.assertRaises(ValueError):
            self.run_calculator()

        self.assertFalse(self.output_file.exists())

    def test_incomplete_evaluation(self):
        self.df.loc[0, "output_available"] = "True"
        self.df.loc[0, "atomicity"] = "2"

        result = self.run_calculator()

        self.assertEqual(
            result.loc[0, "evaluation_status"],
            "in_progress",
        )
        self.assertEqual(
            result.loc[0, "quality_score"],
            "",
        )

        # The remaining tasks must stay pending.
        self.assertEqual(
            (result["evaluation_status"] == "pending").sum(),
            59,
        )


if __name__ == "__main__":
    unittest.main()
