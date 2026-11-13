"""Offline v2 scoring tests; no framework validation dependencies."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evaluation"))
from score_user_story_structure_v2 import score_text, score_record

A = "As a reader, I want books, so that I can learn."
B = "As an editor, I want music, so that I can relax."


class StructuralV2Tests(unittest.TestCase):
    def scores(self, text):
        return {k: v["score"] for k, v in score_text(text)["criteria"].items()}

    def test_explicit_missing_is_form_present_not_populated(self):
        r = score_text("As a reader, I want books, so that Not provided.")
        self.assertEqual(r["stories"][0]["slots"]["benefit"]["state"], "explicitly_missing")
        self.assertEqual([v["score"] for v in r["criteria"].values()], [1, 0, 1, 1])

    def test_multiple_stories_and_presentation_are_valid(self):
        for text in (A + "\n" + B, A + " " + B, "```text\n1. " + A + "\n2. " + B + "\n```", A.replace(", I want", ",\nI want")):
            self.assertTrue(all(v == 1 for v in self.scores(text).values()))

    def test_atomic_and_minimal_are_independent_of_form_and_information(self):
        self.assertEqual(self.scores("As a reader, I want books.")["Atomic"], 1)
        self.assertEqual(self.scores("As a reader, I want books.")["Structural Form"], 0)
        self.assertEqual(self.scores("As a reader, I want books.")["Minimal"], 1)
        repeated = "As a reader, I want books and I want music, so that I can relax."
        self.assertEqual(self.scores(repeated)["Atomic"], 0)
        self.assertEqual(self.scores(repeated)["Minimal"], 1)
        self.assertEqual(self.scores("As a reader, I want books and music, so that I choose what I want.")["Atomic"], 1)

    def test_duplicate_and_commentary_fail_only_minimal(self):
        self.assertEqual(self.scores(A + "\n" + A)["Minimal"], 0)
        self.assertEqual(self.scores("Here is the story:\n" + A)["Minimal"], 0)
        self.assertEqual(self.scores(A + "\nExplanation.")["Minimal"], 0)

    def test_empty_slots_and_ambiguous_boundaries(self):
        scores = self.scores("As a reader, I want , so that I can learn.")
        self.assertEqual(scores["Structural Form"], 0)
        self.assertEqual(scores["Information Completeness"], 0)
        self.assertIsNone(scores["Atomic"])
        self.assertEqual(scores["Minimal"], 1)
        self.assertTrue(all(v is None for v in self.scores(A.rstrip(".") + " " + B).values()))

    def test_anonymous_record_ignores_method_and_internal_status(self):
        row = {"artifact_id": "anon", "pair_id": "pair", "task": {"task_id": "source"}, "artifact": A}
        before = score_record(row)
        row.update(method="tavf", validation_history=[False], status="failed")
        self.assertEqual(score_record(row), before)


if __name__ == "__main__":
    unittest.main()
