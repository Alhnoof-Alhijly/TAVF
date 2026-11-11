
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import run_baseline_pilot


class TestBaselinePilot(unittest.TestCase):

    def test_pilot_execution_and_resume(self):
        api_calls = []

        class FakeClient:
            def __init__(self, **kwargs):
                self.responses = self

            def create(self, **kwargs):
                api_calls.append(kwargs)

                return SimpleNamespace(
                    id=f"fake-response-{len(api_calls)}",
                    output_text="Simulated pilot output",
                    usage=SimpleNamespace(
                        input_tokens=100,
                        output_tokens=50,
                    ),
                )

        fake_openai = SimpleNamespace(OpenAI=FakeClient)

        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(temp)
            output_file = output_dir / "pilot_outputs.json"
            error_file = output_dir / "pilot_errors.jsonl"

            with (
                patch.object(
                    run_baseline_pilot,
                    "OUTPUT_DIR",
                    output_dir,
                ),
                patch.object(
                    run_baseline_pilot,
                    "OUTPUT_FILE",
                    output_file,
                ),
                patch.object(
                    run_baseline_pilot,
                    "ERROR_FILE",
                    error_file,
                ),
                patch.dict(
                    sys.modules,
                    {"openai": fake_openai},
                ),
                patch.dict(
                    os.environ,
                    {"OPENAI_API_KEY": "fake-test-key"},
                ),
                patch.object(
                    sys,
                    "argv",
                    [
                        "run_baseline_pilot.py",
                        "--execute",
                        "--confirm-paid",
                    ],
                ),
            ):
                # First run: execute all three pilot tasks.
                run_baseline_pilot.main()

                self.assertEqual(len(api_calls), 3)
                self.assertTrue(output_file.exists())

                records = json.loads(
                    output_file.read_text(encoding="utf-8")
                )

                self.assertEqual(len(records), 3)
                self.assertEqual(
                    {r["task_id"] for r in records},
                    {"USC03", "BRC01", "TCC02"},
                )

                # Verify model and generation settings.
                for call in api_calls:
                    self.assertEqual(
                        call["model"],
                        run_baseline_pilot.MODEL,
                    )
                    self.assertEqual(
                        call["reasoning"],
                        {"effort": "none"},
                    )
                    self.assertEqual(
                        call["max_output_tokens"],
                        8192,
                    )

                # Second run: skip completed tasks.
                run_baseline_pilot.main()

                self.assertEqual(len(api_calls), 3)

                records = json.loads(
                    output_file.read_text(encoding="utf-8")
                )

                self.assertEqual(len(records), 3)
                self.assertFalse(error_file.exists())

        print(
            "Pilot test passed: "
            "3 saved outputs, correct settings, "
            "no duplicate requests."
        )


if __name__ == "__main__":
    unittest.main()
