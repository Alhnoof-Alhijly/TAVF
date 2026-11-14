"""Offline checks for blank human scoring rows and anonymous linkage."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evaluation"))
from prepare_human_semantic_sheet import blank_rows, CRITERIA, FIELDS, META


class HumanSemanticSheetTests(unittest.TestCase):
    def samples(self):
        return [{"sample_id": str(i), "presentation_index": i + 1, "task_type": kind,
                 "source_input": {"original_text": "source"}, "outputs": {"A": "first", "B": "second"}}
                for i, kind in enumerate(CRITERIA)]

    def test_blank_reproducible_rows_with_correct_criteria_and_no_method_fields(self):
        samples = self.samples()
        before = deepcopy(samples)
        rows = blank_rows(samples)
        self.assertEqual(rows, blank_rows(samples))
        self.assertEqual(len({r["blinded_output_id"] for r in rows}), 4)
        self.assertEqual({(r["sample_id"], r["output_label"]) for r in rows}, {("0", "A"), ("0", "B"), ("1", "A"), ("1", "B")})
        for row in rows:
            self.assertEqual(row["applicable_criteria"], ";".join(CRITERIA[row["task_type"]]))
            self.assertTrue(all(row[field] == "" for field in FIELDS if field not in META))
            self.assertNotIn("method", row)
        self.assertEqual(samples, before)

    def test_duplicate_or_incomplete_samples_refused(self):
        samples = self.samples()
        with self.assertRaises(ValueError):
            blank_rows(samples + [samples[0]])
        del samples[0]["outputs"]["B"]
        with self.assertRaises(ValueError):
            blank_rows(samples)


if __name__ == "__main__":
    unittest.main()
