
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(ROOT / "experiments/baseline/pilot")
)

import run_pilot


class TestIntegratedPilot(unittest.TestCase):

    def test_execution_logging_and_resume(self):
        api_calls = []

        class FakeLLMClient:
            model = run_pilot.MODEL
            reasoning_effort = "none"
            max_output_tokens = 8192

            def __init__(self, **kwargs):
                self.settings = kwargs

            def generate(self, prompt):
                api_calls.append(prompt)

                return {
                    "model": self.model,
                    "output": "Simulated pilot output",
                    "response_id": (
                        f"fake-response-{len(api_calls)}"
                    ),
                    "parameters": {
                        "reasoning_effort": "none",
                        "max_output_tokens": 8192,
                    },
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "cached_input_tokens": 0,
                    "execution_time_seconds": 0.1,
                    "timestamp": "2026-09-26T12:00:00+00:00",
                }

        tasks = run_pilot.load_tasks()

        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            results_file = folder / "pilot_outputs.json"
            logs_dir = folder / "real_logs"

            with (
                patch.object(
                    run_pilot,
                    "LLMClient",
                    FakeLLMClient,
                ),
                patch.object(
                    run_pilot,
                    "RESULTS_FILE",
                    results_file,
                ),
                patch.object(
                    run_pilot,
                    "REAL_LOG_DIR",
                    logs_dir,
                ),
                patch.object(
                    run_pilot,
                    "check_budget",
                    return_value=True,
                ) as budget_check,
            ):
                # First run: execute all three tasks.
                run_pilot.run_real(tasks)

                self.assertEqual(len(api_calls), 3)
                self.assertEqual(
                    budget_check.call_count,
                    3,
                )
                self.assertTrue(results_file.exists())

                records = json.loads(
                    results_file.read_text(
                        encoding="utf-8"
                    )
                )

                self.assertEqual(len(records), 3)
                self.assertEqual(
                    {r["task_id"] for r in records},
                    {"USC03", "BRC01", "TCC02"},
                )

                # Verify the experiment logs.
                log_file = logs_dir / "results.jsonl"

                self.assertTrue(log_file.exists())

                logs = [
                    json.loads(line)
                    for line in log_file.read_text(
                        encoding="utf-8"
                    ).splitlines()
                ]

                self.assertEqual(len(logs), 3)
                self.assertTrue(
                    all(
                        log["status"] == "success"
                        for log in logs
                    )
                )

                # Second run: completed tasks are skipped.
                run_pilot.run_real(tasks)

                self.assertEqual(len(api_calls), 3)
                self.assertEqual(
                    budget_check.call_count,
                    3,
                )

                records = json.loads(
                    results_file.read_text(
                        encoding="utf-8"
                    )
                )

                self.assertEqual(len(records), 3)

                # No additional logs should be created.
                self.assertEqual(
                    len(
                        log_file.read_text(
                            encoding="utf-8"
                        ).splitlines()
                    ),
                    3,
                )

        print(
            "Integrated pilot passed: "
            "3 outputs, 3 logs, "
            "no duplicate requests."
        )


if __name__ == "__main__":
    unittest.main()
