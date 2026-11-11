import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from tavf.feedback import generate_feedback
from tavf.final_output import build_final_output
from tavf.refinement import refine_output
from tavf.validators.test_case import validate_test_case
from tavf.validators.user_story import validate_user_story


STORY = "As a reader, I want bookmarks, so that I can resume."


def version(output, attempt, task_type="user_story_refinement"):
    validation = (validate_test_case(output) if task_type == "test_case_generation"
                  else validate_user_story(output))
    return {"attempt": attempt, "generation": {"output": output, "model": "mock-model"},
            "validation": validation, "feedback": generate_feedback(task_type, validation)}


def history(*versions):
    return {"versions": list(versions), "attempts": [], "stop_reason": "attempt_limit"}


class TestTAVFFinalOutput(unittest.TestCase):
    def test_first_passing_version_wins_over_earlier_zero_fixable(self):
        result = build_final_output(history(
            version("As a reader, I want bookmarks.", 0),
            version(STORY, 1), version(STORY + " Later benefit.", 2),
        ))
        self.assertEqual(result["selected_attempt"], 1)
        self.assertEqual(result["artifact"], STORY)
        self.assertEqual(result["selection_reason"], "first_passing_version")
        self.assertTrue(result["valid"])

    def test_fewest_fixable_and_earliest_tie(self):
        initial = "```\nAs a reader, I want bookmarks.\n```"
        candidate = "As a reader, I want bookmarks."
        result = build_final_output(history(version(initial, 0), version(candidate, 1),
                                            version("As an editor, I want drafts.", 2)))
        self.assertEqual(result["selected_attempt"], 1)
        self.assertEqual(result["fixable_issue_count"], 0)
        self.assertFalse(result["valid"])
        self.assertTrue(result["missing_information"])

    def test_missing_information_count_does_not_affect_ranking(self):
        first = version("As a [role], I want [goal], so that [benefit].", 0)
        second = version("As a reader, I want bookmarks.", 1)
        self.assertGreater(len(first["validation"]["issues"]), len(second["validation"]["issues"]))
        result = build_final_output(history(first, second))
        self.assertEqual(result["selected_attempt"], 0)
        self.assertEqual(len(result["missing_information"]), 3)

    def test_multiple_stories_stay_in_one_artifact(self):
        artifact = STORY + "\nAs an editor, I want drafts, so that I can revise."
        result = build_final_output(history(version(artifact, 0)))
        self.assertEqual(result["artifact"], artifact)
        self.assertEqual(len(result["versions"]), 1)

    def test_unverified_checks_are_unresolved_not_passed(self):
        result = build_final_output(history(version("assert True", 0, "test_case_generation")))
        self.assertFalse(result["valid"])
        self.assertEqual(len(result["unresolved_checks"]), 3)
        self.assertTrue(all(e["status"] == "not_verified" for e in result["unresolved_checks"]))
        self.assertEqual(len(result["missing_information"]), 3)

    def test_inconsistent_valid_flag_does_not_override_unverified_evidence(self):
        candidate = version("assert True", 0, "test_case_generation")
        candidate["validation"]["valid"] = True
        candidate["validation"]["issues"] = []
        result = build_final_output(history(candidate))
        self.assertFalse(result["valid"])
        self.assertEqual(result["selection_reason"], "fewest_fixable_issues")
        self.assertTrue(result["unresolved_checks"])

    def test_all_history_feedback_failed_attempts_and_json_are_preserved(self):
        source = history(version("```\n" + STORY + "\n```", 0), version(STORY, 1))
        source["attempts"] = [{"attempt": 1, "prompt": "mock prompt", "status": "success"},
                              {"attempt": 2, "status": "failed", "error": "Generation failed."}]
        source["stop_reason"] = "generation_failed"
        original = copy.deepcopy(source)
        result = build_final_output(source)
        self.assertEqual(result["versions"], source["versions"])
        self.assertEqual(result["attempts"], source["attempts"])
        self.assertEqual(result["validation_history"], [v["validation"] for v in source["versions"]])
        self.assertEqual(result["feedback_history"], [v["feedback"] for v in source["versions"]])
        self.assertEqual(json.loads(json.dumps(result)), result)
        result["versions"][0]["generation"]["output"] = "changed"
        self.assertEqual(source, original)

    def test_actual_refinement_result_is_accepted_without_llm_calls(self):
        client = Mock(model="mock-model")
        refinement = refine_output("user_story_refinement", {"original_text": STORY},
                                   {"output": STORY, "model": "mock-model", "parameters": {}}, client)
        result = build_final_output(refinement)
        self.assertEqual(result["artifact"], STORY)
        self.assertTrue(result["valid"])
        client.generate.assert_not_called()

    def test_remaining_fixable_issues_are_preserved(self):
        result = build_final_output(history(version("```\n" + STORY + "\n```", 0)))
        self.assertFalse(result["valid"])
        self.assertEqual(result["fixable_issue_count"], 2)
        self.assertEqual(len(result["unresolved_issues"]), 2)

    def test_invalid_or_empty_history_is_rejected(self):
        with self.assertRaises(TypeError):
            build_final_output(None)
        for source in (history(), history({}), history(version(STORY, 1), version(STORY, 0))):
            with self.subTest(source=source), self.assertRaises(ValueError):
                build_final_output(source)


if __name__ == "__main__":
    unittest.main()
