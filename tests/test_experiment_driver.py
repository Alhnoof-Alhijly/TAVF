"""Offline driver tests: fake model client, temporary journals, no Docker/API."""

import copy
from decimal import Decimal
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import run_experiment as driver


STORY = "As a reader, I want bookmarks, so that I can resume."
TASK = {"task_id": "offline-story", "task_type": "user_story_refinement", "source": "fixture",
        "input": {"original_text": STORY}, "reference": {"original_source_file": "fixture.txt", "original_line_number": 1},
        "metadata": {}, "expected_output": {"type": "refined_user_story", "gold_reference": None}}


def client_for(*outputs):
    client = Mock(model=driver.DEFAULT_MODEL, reasoning_effort="none", max_output_tokens=256)
    client.generate.side_effect = [output if isinstance(output, Exception) else {
        "model": driver.DEFAULT_MODEL, "output": output, "input_tokens": 100, "output_tokens": 30,
        "cached_input_tokens": 0, "response_id": "offline-" + str(index),
        "parameters": {"reasoning_effort": "none", "max_output_tokens": 256},
    } for index, output in enumerate(outputs)]
    return client


class TestExperimentDriver(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.output = Path(temporary.name) / "run"
        budget = patch("run_experiment.check_budget", return_value=True)
        spent = patch("run_experiment.calculate_spent", return_value=Decimal("0"))
        docker = patch("tavf.validators.execution.subprocess.run", side_effect=AssertionError("No Docker"))
        self.guard = budget.start()
        spent.start()
        docker.start()
        self.addCleanup(budget.stop)
        self.addCleanup(spent.stop)
        self.addCleanup(docker.stop)

    def run_driver(self, client, tasks=None):
        return driver.run_experiment(tasks or [TASK], self.output, execute=True, client=client, max_output_tokens=256)

    def test_all_1500_dry_run_no_client_no_files(self):
        with patch("run_experiment.LLMClient", side_effect=AssertionError("No client initialization")):
            tasks = driver.load_tasks()
            result = driver.run_experiment(tasks, self.output)
        self.assertEqual(result, {"status": "dry_run", "tasks": 1500, "method_tasks": 3000, "api_calls": 0})
        self.assertFalse(self.output.exists())
        self.guard.assert_not_called()

    def test_paired_results_saved_and_resume_makes_no_calls(self):
        before = copy.deepcopy(TASK)
        first = client_for(STORY, STORY)
        self.assertEqual(self.run_driver(first)["saved"], 2)
        self.assertEqual(len(list((self.output / "results").glob("*.json"))), 2)
        saved = [json.loads(p.read_text()) for p in (self.output / "results").glob("*.json")]
        self.assertEqual({record["method"] for record in saved}, {"baseline", "tavf"})
        self.assertTrue(all(record["task"] == TASK for record in saved))
        second = client_for()
        self.assertEqual(self.run_driver(second)["skipped"], 2)
        second.generate.assert_not_called()
        self.assertEqual(TASK, before)

    def test_replay_durable_response_after_crash_before_result_save(self):
        save = driver._save

        def crash(path, value):
            if path.parent.name == "results":
                raise OSError("simulated interruption")
            save(path, value)

        first = client_for(STORY)
        with patch("run_experiment._save", side_effect=crash), self.assertRaises(OSError):
            self.run_driver(first)
        self.assertEqual(first.generate.call_count, 1)
        second = client_for(STORY)
        self.assertEqual(self.run_driver(second)["saved"], 2)
        # Baseline replays its response; only the pending TAVF call is new.
        self.assertEqual(second.generate.call_count, 1)

    def test_budget_applies_to_refinements_and_replay_keeps_initial_response(self):
        self.guard.side_effect = [True, True, False]
        first = client_for(STORY, "```\n" + STORY + "\n```")
        self.assertEqual(self.run_driver(first)["status"], "budget_limit")
        self.assertEqual(first.generate.call_count, 2)
        self.assertEqual(len(list((self.output / "results").glob("*.json"))), 1)
        self.guard.side_effect = None
        self.guard.return_value = True
        second = client_for(STORY)
        self.assertEqual(self.run_driver(second)["status"], "completed")
        self.assertEqual(second.generate.call_count, 1)

    def test_uncertain_request_never_retries_automatically(self):
        first = client_for(ConnectionError("secret-provider-detail"))
        self.assertEqual(self.run_driver(first)["status"], "request_requires_reconciliation")
        second = client_for(STORY)
        with self.assertRaisesRegex(ValueError, "reconciliation"):
            self.run_driver(second)
        second.generate.assert_not_called()
        journal = next((self.output / "requests").glob("*.json")).read_text()
        self.assertNotIn("secret-provider-detail", journal)

    def test_new_run_usage_counts_toward_existing_limit(self):
        # Legacy guard alone approves, but the driver's aggregate guard refuses.
        with patch("run_experiment.SAFETY_LIMIT", Decimal("0.000001")):
            client = client_for(STORY)
            self.assertEqual(self.run_driver(client)["status"], "budget_limit")
            client.generate.assert_not_called()

    def test_saved_request_cost_is_added_before_next_request(self):
        prompt = driver.build_prompt(TASK["task_type"], TASK["input"])
        reserve = driver.calculate_cost(len(prompt.encode("utf-8")) + 512, 256)
        first_cost = driver.calculate_cost(100, 30)
        # The next request fits alone, but not together with the saved response.
        with patch("run_experiment.SAFETY_LIMIT", reserve + first_cost / 2):
            client = client_for(STORY, STORY)
            result = self.run_driver(client)
        self.assertEqual(result["status"], "budget_limit")
        self.assertEqual(client.generate.call_count, 1)

    def test_missing_usage_is_saved_and_blocks_resume(self):
        client = client_for(STORY)
        client.generate.side_effect = None
        client.generate.return_value = {"model": driver.DEFAULT_MODEL, "output": STORY, "parameters": {}, "input_tokens": None}
        self.assertEqual(self.run_driver(client)["status"], "response_requires_reconciliation")
        journal = json.loads(next((self.output / "requests").glob("*.json")).read_text())
        self.assertEqual(journal["response"]["output"], STORY)
        with self.assertRaisesRegex(ValueError, "reconciliation"):
            self.run_driver(client_for())

    def test_changed_inputs_or_configuration_refuse_resume(self):
        self.run_driver(client_for(STORY, STORY))
        changed = copy.deepcopy(TASK)
        changed["input"]["original_text"] += " Changed."
        client = client_for()
        with self.assertRaisesRegex(ValueError, "resume refused"):
            self.run_driver(client, [changed])
        with self.assertRaisesRegex(ValueError, "resume refused"):
            driver.run_experiment([TASK], self.output, execute=True, client=client, max_output_tokens=128)
        client.generate.assert_not_called()

    def test_line_branch_path_targets_preserved_in_both_methods_and_revisions(self):
        tasks = driver.load_tasks()
        for kind in ("line", "branch", "path"):
            task = next(t for t in tasks if t["task_type"] == "test_case_generation" and t["reference"]["target_type"] == kind)
            self.output = self.output.parent / kind
            client = client_for("assert True", "def broken(:", "assert True")
            self.assertEqual(self.run_driver(client, [task])["status"], "completed")
            self.assertEqual(client.generate.call_count, 3)
            section = driver._target_context(task["reference"])
            for call in client.generate.call_args_list:
                self.assertIn(section, call.args[0])
            for call in client.generate.call_args_list[:2]:
                self.assertIn(task["input"]["python_solution"], call.args[0])
            saved = [json.loads(p.read_text(encoding="utf-8")) for p in (self.output / "results").glob("*.json")]
            self.assertTrue(all(record["task"] == task for record in saved))

    def test_lock_rejects_concurrent_writer(self):
        with driver._lock(self.output), self.assertRaises(OSError):
            with driver._lock(self.output):
                self.fail("Concurrent writer acquired the lock")


if __name__ == "__main__":
    unittest.main()
