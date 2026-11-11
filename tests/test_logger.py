
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from utils.logger import ExperimentLogger


class TestExperimentLogger(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.logger = ExperimentLogger(
            log_dir=self.temp.name
        )

        self.task = {
            "task_id": "USC03",
            "task_type": "user_story_refinement",
        }

        self.prompt = "Refine this user story."

    def test_success_log(self):
        response = {
            "model": "fake-test-model",
            "output": "Refined user story",
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

        record = self.logger.log_success(
            self.task,
            self.prompt,
            response,
        )

        self.assertTrue(self.logger.results_file.exists())
        self.assertEqual(record["status"], "success")

        saved = json.loads(
            self.logger.results_file.read_text(
                encoding="utf-8"
            ).strip()
        )

        self.assertEqual(saved["task_id"], "USC03")
        self.assertEqual(
            saved["response"],
            "Refined user story",
        )
        self.assertEqual(saved["input_tokens"], 100)
        self.assertEqual(
            saved["parameters"]["max_output_tokens"],
            8192,
        )
        self.assertTrue(saved["run_id"])

    def test_error_log(self):
        error = RuntimeError("Simulated API failure")

        record = self.logger.log_error(
            task=self.task,
            prompt=self.prompt,
            error=error,
            model="fake-test-model",
            parameters={"reasoning_effort": "none"},
        )

        self.assertTrue(self.logger.errors_file.exists())
        self.assertEqual(record["status"], "error")

        saved = json.loads(
            self.logger.errors_file.read_text(
                encoding="utf-8"
            ).strip()
        )

        self.assertEqual(
            saved["error_type"],
            "RuntimeError",
        )
        self.assertEqual(
            saved["error_message"],
            "Simulated API failure",
        )
        self.assertEqual(saved["task_id"], "USC03")

    def test_multiple_records(self):
        response = {
            "model": "fake-test-model",
            "output": "Simulated output",
        }

        self.logger.log_success(
            self.task, self.prompt, response
        )
        self.logger.log_success(
            self.task, self.prompt, response
        )

        lines = self.logger.results_file.read_text(
            encoding="utf-8"
        ).splitlines()

        self.assertEqual(len(lines), 2)

        records = [json.loads(line) for line in lines]

        self.assertNotEqual(
            records[0]["run_id"],
            records[1]["run_id"],
        )


if __name__ == "__main__":
    unittest.main()
