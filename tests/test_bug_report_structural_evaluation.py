from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evaluation"))
from score_bug_report_structure import score_text, score_record

FULL = "Summary: Problem\nSteps: Open app\nExpected: It opens\nActual: It crashes"


class BugReportStructuralTests(unittest.TestCase):
    def test_aliases_and_formatting_are_equivalent(self):
        self.assertEqual(score_text(FULL)["structural_score_100"], 100)
        formatted = "## Summary\nProblem\n**Steps to Reproduce:**\n1. Open app\n## Expected Behavior\nIt opens\n## Actual Behaviour\nIt crashes"
        self.assertEqual(score_text(formatted)["structural_score_100"], 100)

    def test_missing_values_are_not_populated_and_no_semantic_inference(self):
        result = score_text("Summary: Problem\nSteps: Not provided\nExpected:\nActual: Unverified claim")
        self.assertEqual(result["structural_score_100"], 50)
        self.assertEqual(result["criteria"]["Steps to Reproduce"]["state"], "explicitly_missing")
        self.assertEqual(result["criteria"]["Expected Result"]["state"], "empty")
        self.assertEqual(score_text("plain prose")["structural_score_100"], 0)

    def test_duplicate_sections_are_unassessable_not_zero(self):
        result = score_text(FULL + "\nSummary: Again")
        self.assertIsNone(result["structural_score_100"])
        self.assertIsNone(result["criteria"]["Summary"]["score"])
        self.assertEqual(result["criteria"]["Summary"]["evidence"]["section_count"], 2)

    def test_context_heading_does_not_populate_empty_component(self):
        result = score_text("Summary:\n## Technical Context\nFirefox\nSteps: Open\nExpected: Works\nActual: Fails")
        self.assertEqual(result["criteria"]["Summary"]["state"], "empty")
        self.assertEqual(result["structural_score_100"], 75)

    def test_identical_text_has_identical_score_regardless_of_private_fields(self):
        row = {"artifact_id": "anonymous", "pair_id": "pair", "task": {"task_id": "task"}, "artifact": FULL}
        original = score_record(row)
        row.update(method="tavf", status="failed", validation_history=[False])
        self.assertEqual(score_record(row), original)


if __name__ == "__main__":
    unittest.main()
