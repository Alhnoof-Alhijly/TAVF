
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from baseline.baseline_runner import BaselineRunner, DATA_FILE
from utils.logger import ExperimentLogger


class TestBaselineLogging(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        tasks = json.loads(
            DATA_FILE.read_text(encoding="utf-8")
        )
        cls.task = tasks[0]

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.logger = ExperimentLogger(
            log_dir=self.temp.name
        )

        self.client = Mock()
        self.client.model = "fake-test-model"
        self.client.reasoning_effort = "none"
        self.client.max_output_tokens = 8192

        self.runner = BaselineRunner(
            client=self.client,
            logger=self.logger,
        )

    def test_successful_generation_is_logged(self):
        self.client.generate.return_value = {
            "model": "fake-test-model",
            "output": "Simulated baseline output",
            "response_id": "fake-response-001",
            "parameters": {
                "reasoning_effort": "none",
                "max_output_tokens": 8192,
            },
            "input_tokens": 100,
            "output_tokens": 50,
            "cached_input_tokens": 0,
            "execution_time_seconds": 0.5,
            "timestamp": "2026-09-26T12:00:00+00:00",
        }

        result = self.runner.run_task(self.task)

        self.assertEqual(
            result["output"],
            "Simulated baseline output",
        )
        self.assertTrue(
            self.logger.results_file.exists()
        )

        records = [
            json.loads(line)
            for line in self.logger.results_file.read_text(
                encoding="utf-8"
            ).splitlines()
        ]

        self.assertEqual(len(records), 1)

        saved = records[0]

        self.assertEqual(
            saved["task_id"],
            self.task["task_id"],
        )
        self.assertEqual(saved["status"], "success")
        self.assertEqual(
            saved["response"],
            "Simulated baseline output",
        )
        self.assertEqual(saved["prompt"], result["prompt"])
        self.assertEqual(saved["input_tokens"], 100)
        self.assertEqual(saved["output_tokens"], 50)
        self.assertTrue(saved["run_id"])

        self.assertFalse(
            self.logger.errors_file.exists()
        )

    def test_failed_generation_is_logged(self):
        self.client.generate.side_effect = RuntimeError(
            "Simulated API failure"
        )

        with self.assertRaisesRegex(
            RuntimeError,
            "Simulated API failure",
        ):
            self.runner.run_task(self.task)

        self.assertTrue(
            self.logger.errors_file.exists()
        )

        records = [
            json.loads(line)
            for line in self.logger.errors_file.read_text(
                encoding="utf-8"
            ).splitlines()
        ]

        self.assertEqual(len(records), 1)

        saved = records[0]

        self.assertEqual(
            saved["task_id"],
            self.task["task_id"],
        )
        self.assertEqual(saved["status"], "error")
        self.assertEqual(
            saved["error_type"],
            "RuntimeError",
        )
        self.assertEqual(
            saved["error_message"],
            "Simulated API failure",
        )
        self.assertEqual(
            saved["model"],
            "fake-test-model",
        )
        self.assertTrue(saved["prompt"])
        self.assertTrue(saved["run_id"])

        self.assertFalse(
            self.logger.results_file.exists()
        )


if __name__ == "__main__":
    unittest.main()
