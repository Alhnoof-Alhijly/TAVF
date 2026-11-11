
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts import run_baseline


class TestBaselineRecovery(unittest.TestCase):

    def test_recovery_after_failure(self):
        api_calls = []

        class FakeClient:
            def __init__(self, **kwargs):
                self.responses = self

            def create(self, **kwargs):
                api_calls.append(kwargs)

                # Simulate an API failure on the second request.
                if len(api_calls) == 2:
                    raise RuntimeError("Simulated API failure")

                return SimpleNamespace(
                    id=f"fake-response-{len(api_calls)}",
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
                        "2",
                    ],
                ),
            ):
                # First run: one success followed by one failure.
                run_baseline.main()

                records = json.loads(
                    output_file.read_text(encoding="utf-8")
                )

                self.assertEqual(len(records), 1)
                self.assertEqual(len(api_calls), 2)
                self.assertTrue(error_file.exists())

                # Second run: skip the saved task and retry the failed one.
                run_baseline.main()

                records = json.loads(
                    output_file.read_text(encoding="utf-8")
                )

                self.assertEqual(len(records), 2)
                self.assertEqual(len(api_calls), 3)

                ids = [record["task_id"] for record in records]
                self.assertEqual(len(set(ids)), 2)

        print("Recovery test passed: saved task was not repeated.")


if __name__ == "__main__":
    unittest.main()
