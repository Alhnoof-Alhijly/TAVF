import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from tavf.refinement import refine_output


STORY = "As a reader, I want bookmarks, so that I can resume."
PARAMETERS = {"reasoning_effort": "none", "max_output_tokens": 256}


def generation(output):
    return {"output": output, "model": "mock-model", "parameters": PARAMETERS.copy(),
            "input_tokens": 10, "output_tokens": 5, "execution_time_seconds": 0.1}


def client_for(*outputs):
    client = Mock(model="mock-model", reasoning_effort="none", max_output_tokens=256)
    client.generate.side_effect = [generation(output) for output in outputs]
    return client


class TestTAVFRefinement(unittest.TestCase):
    def test_initial_validation_pass_makes_no_call(self):
        client = client_for()
        result = refine_output("user_story_refinement", {"original_text": STORY}, generation(STORY), client)
        self.assertEqual(result["stop_reason"], "validation_passed")
        self.assertEqual(len(result["versions"]), 1)
        client.generate.assert_not_called()

    def test_revalidates_and_preserves_successful_revision(self):
        initial = generation("```\n" + STORY + "\n```")
        original = copy.deepcopy(initial)
        client = client_for(STORY)
        result = refine_output("user_story_refinement", {"original_text": STORY}, initial, client)
        self.assertEqual(result["stop_reason"], "validation_passed")
        self.assertEqual(len(result["versions"]), 2)
        self.assertFalse(result["versions"][0]["validation"]["valid"])
        self.assertTrue(result["versions"][1]["validation"]["valid"])
        self.assertEqual(result["versions"][1]["generation"]["input_tokens"], 10)
        client.generate.assert_called_once()
        self.assertEqual(initial, original)

    def test_two_attempt_limit_and_previous_output_in_prompt(self):
        initial = "```\n" + STORY + "\n```"
        revision = STORY + "\n" + STORY
        client = client_for(revision, initial, STORY)
        result = refine_output("user_story_refinement", {"original_text": STORY}, generation(initial), client)
        self.assertEqual(result["stop_reason"], "attempt_limit")
        self.assertEqual(client.generate.call_count, 2)
        self.assertEqual(len(result["versions"]), 3)
        self.assertIn("Exact duplicate story", result["attempts"][1]["prompt"])
        self.assertEqual([v["attempt"] for v in result["versions"]], [0, 1, 2])

    def test_missing_information_is_reported_but_not_corrected(self):
        story = "As a reader, I want bookmarks."
        client = client_for(story)
        result = refine_output("user_story_refinement", {"original_text": story},
                               generation("```\n" + story + "\n```"), client)
        self.assertEqual(result["stop_reason"], "no_fixable_issues")
        self.assertNotIn('"classification": "missing_information"', result["attempts"][0]["prompt"])
        self.assertEqual(result["versions"][-1]["feedback"]["feedback"][0]["issue"]["classification"],
                         "missing_information")
        self.assertFalse(result["versions"][-1]["validation"]["valid"])

    def test_bug_report_original_source_and_evaluation_field_exclusion(self):
        source = "Summary: Crash\nSteps: Save\nExpected: Saved\nActual: Exits"
        client = client_for(source)
        result = refine_output("bug_report_refinement", {
            "original_text": source, "reference": "SECRET_EVALUATION",
        }, generation("Summary: Crash"), client)
        self.assertEqual(result["stop_reason"], "validation_passed")
        prompt = result["attempts"][0]["prompt"]
        self.assertIn("Expected: Saved", prompt)
        self.assertNotIn("SECRET_EVALUATION", prompt)

    def test_unverified_test_case_checks_remain_unresolved(self):
        client = client_for("assert True")
        result = refine_output("test_case_generation", {
            "description": "Return input.", "python_solution": "def identity(x): return x",
        }, generation("def broken(:"), client)
        self.assertEqual(result["stop_reason"], "no_fixable_issues")
        self.assertFalse(result["versions"][-1]["validation"]["valid"])
        statuses = [e["status"] for e in result["versions"][-1]["validation"]["evidence"]]
        self.assertIn("not_verified", statuses)
        client.generate.assert_called_once()

    def test_only_missing_information_stops_without_call(self):
        client = client_for()
        result = refine_output("bug_report_refinement", {"original_text": "Save crashes."},
                               generation("Summary: Save crashes."), client)
        self.assertEqual(result["stop_reason"], "no_fixable_issues")
        client.generate.assert_not_called()

    def test_api_failure_preserves_history_and_sanitizes_error(self):
        client = client_for()
        client.generate.side_effect = RuntimeError("secret-api-key")
        result = refine_output("user_story_refinement", {"original_text": STORY},
                               generation("```\n" + STORY + "\n```"), client)
        self.assertEqual(result["stop_reason"], "generation_failed")
        self.assertEqual(len(result["versions"]), 1)
        self.assertEqual(len(result["attempts"]), 1)
        self.assertNotIn("secret-api-key", str(result))

    def test_model_and_parameter_mismatch_rejected_before_generation(self):
        for attribute, value in (("model", "different-model"), ("max_output_tokens", 999)):
            client = client_for()
            setattr(client, attribute, value)
            with self.subTest(attribute=attribute), self.assertRaises(ValueError):
                refine_output("user_story_refinement", {"original_text": STORY}, generation(STORY), client)
            client.generate.assert_not_called()

    def test_response_model_mismatch_is_preserved_as_failed_attempt(self):
        client = client_for(STORY)
        client.generate.side_effect = None
        client.generate.return_value = {**generation(STORY), "model": "different-model"}
        result = refine_output("user_story_refinement", {"original_text": STORY},
                               generation("```\n" + STORY + "\n```"), client)
        self.assertEqual(result["stop_reason"], "configuration_mismatch")
        self.assertEqual(len(result["versions"]), 1)
        self.assertEqual(result["attempts"][0]["generation"]["model"], "different-model")


if __name__ == "__main__":
    unittest.main()
