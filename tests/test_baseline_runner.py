
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from baseline.baseline_runner import BaselineRunner, DATA_FILE


class TestBaselineRunner(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tasks = json.loads(
            DATA_FILE.read_text(encoding="utf-8")
        )

    def test_all_three_task_types(self):
        task_types = [
            "user_story_refinement",
            "bug_report_refinement",
            "test_case_generation",
        ]

        for task_type in task_types:
            with self.subTest(task_type=task_type):
                task = next(
                    t for t in self.tasks
                    if t["task_type"] == task_type
                )

                fake_client = Mock()
                fake_client.generate.return_value = {
                    "model": "fake-test-model",
                    "output": "Simulated baseline response",
                    "response_id": "fake-response-001",
                    "input_tokens": 100,
                    "output_tokens": 50,
                }

                runner = BaselineRunner(client=fake_client)
                result = runner.run_task(task)

                self.assertEqual(
                    result["task_id"],
                    task["task_id"],
                )
                self.assertEqual(
                    result["task_type"],
                    task_type,
                )
                self.assertEqual(
                    result["method"],
                    "baseline",
                )
                self.assertEqual(
                    result["output"],
                    "Simulated baseline response",
                )

                fake_client.generate.assert_called_once()

                sent_prompt = (
                    fake_client.generate.call_args.args[0]
                )

                self.assertTrue(sent_prompt.strip())
                self.assertEqual(
                    result["prompt"],
                    sent_prompt,
                )

    def test_missing_client(self):
        runner = BaselineRunner()

        with self.assertRaises(RuntimeError):
            runner.run_task(self.tasks[0])

    def test_unsupported_task_type(self):
        runner = BaselineRunner()

        invalid_task = {
            "task_id": "INVALID",
            "task_type": "unsupported_task",
            "input": {},
        }

        with self.assertRaises(ValueError):
            runner.build_prompt(invalid_task)


if __name__ == "__main__":
    unittest.main()
