"""Independent scorer tests using synthetic text and blinded records only."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evaluation"))
from score_user_story_structure import score_record, score_text

STORY = "As a reader, I want to browse and bookmark books, so that I can choose which one I want later."


class StructuralScoringTests(unittest.TestCase):
    def test_single_story_conjunction_and_benefit_request_are_not_semantically_split(self):
        result = score_text(STORY)
        self.assertEqual(result["structural_total"], 3)
        self.assertTrue(all(v["score"] == 1 for v in result["criteria"].values()))

    def test_multiple_stories_and_repeated_goal_markers(self):
        scores = score_text(STORY + "\n" + STORY)["criteria"]
        self.assertEqual([scores[k]["score"] for k in scores], [0, 0, 0])
        repeated = score_text("As a reader, I want books and I want music, so that I can relax.")
        self.assertEqual(repeated["criteria"]["Atomic"]["score"], 0)

    def test_formatting_and_extra_sentence_have_preserved_evidence(self):
        result = score_text("```text\n- " + STORY + "\n```")
        self.assertEqual(result["criteria"]["Well-formed"]["score"], 1)
        self.assertEqual(result["criteria"]["Minimal"]["score"], 0)
        self.assertTrue(result["criteria"]["Minimal"]["evidence"]["fences"])
        self.assertEqual(score_text(STORY + " Additional explanation.")["criteria"]["Minimal"]["score"], 0)

    def test_missing_structure_is_unassessable_not_zero_for_other_criteria(self):
        result = score_text("")
        self.assertEqual(result["criteria"]["Well-formed"]["score"], 0)
        self.assertIsNone(result["criteria"]["Atomic"]["score"])
        self.assertIsNone(result["criteria"]["Minimal"]["score"])
        self.assertIsNone(result["structural_total"])
        self.assertEqual(score_text("As a reader, I want books, so that Not provided.")["criteria"]["Well-formed"]["score"], 0)

    def test_wrapped_text_determinism_and_no_method_or_validation_dependency(self):
        row = {"artifact_id": "anon", "pair_id": "pair", "task": {"task_id": "task"}, "artifact": STORY}
        original = deepcopy(row)
        score = score_record(row)
        row.update(method="tavf", status="unresolved", validation_history=[{"valid": False}])
        self.assertEqual(score_record(row), score)
        self.assertEqual(score_record(original), score)
        self.assertEqual(score_text(STORY.replace(", I want", ",\nI want"))["structural_total"], 3)


if __name__ == "__main__":
    unittest.main()
