import copy
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from tavf.runner import run_task
from utils.llm_client import LLMClient


STORY = "As a reader, I want bookmarks, so that I can resume."
REPORT = "Summary: Crash\nSteps: Save\nExpected: Saved\nActual: Exits"


def task(task_type="user_story_refinement", **task_input):
    return {"task_id": "offline-1", "task_type": task_type, "input": task_input,
            "reference": {"target_lines": "EVALUATION_ONLY"}, "metadata": {"source": "offline"}}


def mocked_client(*outputs):
    provider = Mock()
    provider.responses.create.side_effect = [
        output if isinstance(output, Exception) else SimpleNamespace(
            id=f"mock-{index}", output_text=output,
            usage=SimpleNamespace(input_tokens=100, output_tokens=20),
        ) for index, output in enumerate(outputs)
    ]
    return LLMClient(model="mock-model", max_output_tokens=256, client=provider), provider


class TestTAVFRunner(unittest.TestCase):
    def test_success_routes_all_three_task_types(self):
        cases = (
            (task(original_text=STORY), STORY, "completed"),
            (task("bug_report_refinement", original_text=REPORT), REPORT, "completed"),
            (task("test_case_generation", description="Return input.",
                  python_solution="def identity(x): return x"), "assert identity(1) == 1", "unresolved"),
        )
        for source, output, status in cases:
            with self.subTest(task_type=source["task_type"]):
                client, provider = mocked_client(output)
                result = run_task(source, client)
                self.assertEqual(result["status"], status)
                self.assertEqual(result["artifact"], output)
                self.assertEqual(result["task"], source)
                self.assertEqual(len(result["versions"]), 1)
                self.assertEqual(len(result["generation_history"]), 1)
                self.assertEqual(json.loads(json.dumps(result)), result)
                provider.responses.create.assert_called_once()
                self.assertNotIn("EVALUATION_ONLY", provider.responses.create.call_args.kwargs["input"])

    def test_refinement_reuses_model_and_keeps_all_history(self):
        client, provider = mocked_client("```\n" + STORY + "\n```", STORY)
        source = task(original_text=STORY)
        original = copy.deepcopy(source)
        result = run_task(source, client)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["selected_attempt"], 1)
        for key in ("versions", "validation_history", "feedback_history", "generation_history"):
            self.assertEqual(len(result[key]), 2)
        self.assertEqual(result["versions"][0]["generation"]["input_tokens"], 100)
        self.assertIn("Standalone Markdown fence", result["attempts"][0]["prompt"])
        self.assertEqual(provider.responses.create.call_count, 2)
        for call in provider.responses.create.call_args_list:
            self.assertEqual(call.kwargs["model"], "mock-model")
            self.assertEqual(call.kwargs["max_output_tokens"], 256)
        self.assertEqual(source, original)

    def test_bug_report_refinement_uses_original_source(self):
        client, provider = mocked_client("Summary: Crash", REPORT)
        result = run_task(task("bug_report_refinement", original_text=REPORT), client)
        self.assertEqual(result["status"], "completed")
        self.assertIn("Expected: Saved", result["attempts"][0]["prompt"])
        self.assertEqual(provider.responses.create.call_count, 2)

    def test_test_case_revision_never_passes_unverified_checks(self):
        client, provider = mocked_client("def broken(:", "assert True")
        result = run_task(task("test_case_generation", description="Return input.",
                               python_solution="def identity(x): return x"), client)
        self.assertEqual(result["status"], "unresolved")
        self.assertFalse(result["valid"])
        self.assertEqual(len(result["unresolved_checks"]), 3)
        self.assertEqual(provider.responses.create.call_count, 2)

    def test_attempt_limit_and_earliest_best_selection(self):
        output = "```\n" + STORY + "\n```"
        client, provider = mocked_client(output, output, output)
        result = run_task(task(original_text=STORY), client)
        self.assertEqual(result["stop_reason"], "attempt_limit")
        self.assertEqual(result["selected_attempt"], 0)
        self.assertEqual(len(result["versions"]), 3)
        self.assertEqual(provider.responses.create.call_count, 3)

    def test_generation_failure_and_empty_response_keep_task_and_prompt(self):
        for response in (RuntimeError("secret-provider-details"), ""):
            with self.subTest(response=response):
                client, provider = mocked_client(response)
                source = task(original_text=STORY)
                result = run_task(source, client)
                self.assertEqual(result["status"], "failed")
                self.assertEqual(result["task"], source)
                self.assertIn(STORY, result["initial_prompt"])
                self.assertIsNone(result["artifact"])
                self.assertEqual(result["versions"], [])
                self.assertNotIn("secret-provider-details", json.dumps(result))
                provider.responses.create.assert_called_once()

    def test_refinement_failure_preserves_initial_artifact_and_failed_attempt(self):
        output = "```\n" + STORY + "\n```"
        client, provider = mocked_client(output, RuntimeError("secret-provider-details"))
        result = run_task(task(original_text=STORY), client)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["artifact"], output)
        self.assertEqual(len(result["versions"]), 1)
        self.assertEqual(result["attempts"][0]["status"], "failed")
        self.assertTrue(result["errors"])
        self.assertNotIn("secret-provider-details", json.dumps(result))
        self.assertEqual(provider.responses.create.call_count, 2)

    def test_invalid_tasks_never_construct_client(self):
        with patch("tavf.runner.LLMClient") as factory:
            for source in ({}, {"task_type": "unknown"}, task(original_text="")):
                with self.subTest(source=source), self.assertRaises(ValueError):
                    run_task(source)
            factory.assert_not_called()

    def test_client_initialization_failure_is_reported_safely(self):
        with patch("tavf.runner.LLMClient", side_effect=RuntimeError("secret")):
            result = run_task(task(original_text=STORY))
        self.assertEqual(result["stop_reason"], "client_initialization_failed")
        self.assertNotIn("secret", json.dumps(result))

    def test_multiple_user_stories_remain_one_artifact(self):
        output = STORY + "\nAs an editor, I want drafts, so that I can revise."
        client, provider = mocked_client(output)
        result = run_task(task(original_text=output), client)
        self.assertEqual(result["artifact"], output)
        self.assertEqual(len(result["versions"]), 1)
        provider.responses.create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
