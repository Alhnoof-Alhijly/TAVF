"""Offline runner/refinement integration; Docker and generation are mocked."""

import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from tavf.refinement import refine_output
from tavf.runner import run_task
from tavf.validators.test_case import validate_test_case


TASK = {"task_id": "offline-options", "task_type": "test_case_generation", "input": {
    "description": "Return the input.", "python_solution": "def identity(x): return x",
}}
ORACLE = {"source": "curated offline example", "cases": [{"call": "identity(1)", "expected": 1}]}
CORRECT = "assert identity(1) == 1"
INCORRECT = "assert identity(1) == 999"


def generation(code):
    return {"output": code, "model": "offline-model", "parameters": {}}


def client_for(*outputs):
    client = Mock(model="offline-model")
    client.generate.side_effect = [generation(code) for code in outputs]
    return client


class TestValidationOptions(unittest.TestCase):
    def setUp(self):
        guard = patch("tavf.validators.execution.subprocess.run",
                      side_effect=AssertionError("Real Docker execution is forbidden"))
        self.process = guard.start()
        self.addCleanup(guard.stop)

    @patch("tavf.validators.test_case.validate_execution")
    def test_runner_forwards_same_options_to_initial_and_revisions(self, execute):
        execute.side_effect = lambda *args: {
            "status": "passed", "message": "Mock Docker evidence", "exit_code": 0,
        }
        original_task, original_oracle = copy.deepcopy(TASK), copy.deepcopy(ORACLE)
        with patch("tavf.refinement.validate_test_case", wraps=validate_test_case) as validator:
            result = run_task(TASK, client_for(INCORRECT, INCORRECT, CORRECT),
                              execute=True, trusted_oracle=ORACLE)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["selected_attempt"], 2)
        self.assertEqual(len(result["validation_history"]), 3)
        self.assertEqual(execute.call_count, 3)
        for call in validator.call_args_list:
            self.assertTrue(call.kwargs["execute"])
            self.assertIs(call.kwargs["trusted_oracle"], ORACLE)
        self.assertEqual(validator.call_count, 3)
        assertions = [validation["evidence"][3]["status"] for validation in result["validation_history"]]
        self.assertEqual(assertions, ["failed", "failed", "passed"])
        self.assertTrue(all(v["evidence"][2]["exit_code"] == 0 for v in result["validation_history"]))
        self.assertEqual(TASK, original_task)
        self.assertEqual(ORACLE, original_oracle)

    def test_defaults_disable_execution_on_initial_and_revalidation(self):
        with patch("tavf.refinement.validate_test_case", wraps=validate_test_case) as validator:
            result = run_task(TASK, client_for("def broken(:", CORRECT))
        self.assertEqual(validator.call_count, 2)
        for call in validator.call_args_list:
            self.assertIs(call.kwargs["execute"], False)
            self.assertIsNone(call.kwargs["trusted_oracle"])
        self.process.assert_not_called()
        self.assertEqual(result["status"], "unresolved")
        for validation in result["validation_history"]:
            self.assertEqual(validation["evidence"][2]["status"], "not_verified")
            self.assertEqual(validation["evidence"][3]["status"], "not_verified")

    def test_direct_refinement_accepts_oracle_with_execution_disabled(self):
        result = refine_output("test_case_generation", TASK["input"],
                               generation(INCORRECT), client_for(CORRECT), trusted_oracle=ORACLE)
        self.process.assert_not_called()
        self.assertEqual(len(result["versions"]), 2)
        self.assertEqual(result["versions"][0]["validation"]["evidence"][3]["status"], "failed")
        final = result["versions"][1]["validation"]
        self.assertEqual(final["evidence"][3]["status"], "passed")
        self.assertEqual(final["evidence"][2]["status"], "not_verified")
        self.assertFalse(final["valid"])

    @patch("tavf.validators.test_case.validate_execution")
    def test_unavailable_docker_remains_unverified_with_trusted_oracle(self, execute):
        execute.return_value = {"status": "not_verified", "message": "Docker unavailable"}
        result = run_task(TASK, client_for(CORRECT), execute=True, trusted_oracle=ORACLE)
        self.assertEqual(result["status"], "unresolved")
        final = result["validation_history"][0]
        self.assertEqual(final["evidence"][2]["status"], "not_verified")
        self.assertEqual(final["evidence"][3]["status"], "passed")

    @patch("tavf.validators.test_case.validate_execution")
    def test_docker_success_without_oracle_remains_unverified(self, execute):
        execute.return_value = {"status": "passed", "message": "Mock Docker success", "exit_code": 0}
        # Neither task metadata nor input fields implicitly enable trust/execution.
        source = copy.deepcopy(TASK)
        source["input"]["trusted_oracle"] = ORACLE
        result = run_task(source, client_for(CORRECT), execute=True)
        self.assertEqual(result["status"], "unresolved")
        final = result["validation_history"][0]
        self.assertEqual(final["evidence"][2]["status"], "passed")
        self.assertEqual(final["evidence"][3]["status"], "not_verified")

    def test_options_do_not_reach_other_validators(self):
        for task_type, text, validator_name in (
            ("user_story_refinement", "As a reader, I want bookmarks, so that I can resume.", "validate_user_story"),
            ("bug_report_refinement", "Summary: Crash\nSteps: Save\nExpected: Saved\nActual: Exits", "validate_bug_report"),
        ):
            with self.subTest(task_type=task_type), patch("tavf.refinement." + validator_name) as validator:
                validator.return_value = {"valid": True, "issues": [], "evidence": []}
                result = run_task({"task_type": task_type, "input": {"original_text": text}},
                                  client_for(text), execute=True, trusted_oracle=ORACLE)
                self.assertEqual(result["status"], "completed")
                expected_args = (text,) if task_type == "user_story_refinement" else (text, text)
                validator.assert_called_once_with(*expected_args)
        self.process.assert_not_called()


if __name__ == "__main__":
    unittest.main()
