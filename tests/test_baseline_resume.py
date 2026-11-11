
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts import run_baseline


class TestBaselineResume(unittest.TestCase):

    def test_resume_skips_completed_tasks(self):
        api_calls = []

        class FakeClient:
            def __init__(self, **kwargs):
                self.responses = self

            def create(self, **kwargs):
                api_calls.append(kwargs)

                return SimpleNamespace(
                    id="fake-response-001",
                    output_text="Simulated baseline output",
                    usage=SimpleNamespace(
                        input_tokens=100,
                        output_tokens=30,
                    ),
                )

        fake_openai = SimpleNamespace(OpenAI=FakeClient)

        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(temp)
            output_file = output_dir / "baseline_outputs.json"
            error_file = output_dir / "baseline_errors.jsonl"

            with (
                patch.object(run_baseline, "OUTPUT_DIR", output_dir),
                patch.object(run_baseline, "OUTPUT_FILE", output_file),
                patch.object(run_baseline, "ERROR_FILE", error_file),
                patch.dict(sys.modules, {"openai": fake_openai}),
                patch.dict(os.environ, {"OPENAI_API_KEY": "fake-test-key"}),
                patch.object(
                    sys,
                    "argv",
                    [
                        "run_baseline.py",
                        "--execute",
                        "--model",
                        "fake-test-model",
                        "--limit",
                        "1",
                    ],
                ),
            ):
                # First run: generate and save one result.
                run_baseline.main()

                self.assertEqual(len(api_calls), 1)
                self.assertTrue(output_file.exists())

                # Second run: resume without repeating the request.
                run_baseline.main()

                self.assertEqual(len(api_calls), 1)

                records = json.loads(
                    output_file.read_text(encoding="utf-8")
                )

                self.assertEqual(len(records), 1)
                self.assertEqual(records[0]["model"], "fake-test-model")
                self.assertEqual(
                    records[0]["output"],
                    "Simulated baseline output",
                )

        print("Resume test passed: no duplicate API requests.")


if __name__ == "__main__":
    unittest.main()
