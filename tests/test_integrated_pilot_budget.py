
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(
    0, str(ROOT / "experiments/baseline/pilot")
)

import run_pilot


class TestIntegratedPilotBudget(unittest.TestCase):

    def test_budget_limit_blocks_requests(self):
        api_calls = []

        class FakeLLMClient:
            model = run_pilot.MODEL
            reasoning_effort = "none"
            max_output_tokens = 8192

            def __init__(self, **kwargs):
                pass

            def generate(self, prompt):
                api_calls.append(prompt)
                raise AssertionError(
                    "No API request should be made."
                )

        tasks = run_pilot.load_tasks()

        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            results_file = folder / "pilot_outputs.json"
            logs_dir = folder / "real_logs"

            with (
                patch.object(
                    run_pilot, "LLMClient", FakeLLMClient
                ),
                patch.object(
                    run_pilot, "RESULTS_FILE", results_file
                ),
                patch.object(
                    run_pilot, "REAL_LOG_DIR", logs_dir
                ),
                patch.object(
                    run_pilot,
                    "check_budget",
                    return_value=False,
                ) as budget_check,
            ):
                run_pilot.run_real(tasks)

                budget_check.assert_called_once()
                self.assertEqual(len(api_calls), 0)
                self.assertFalse(results_file.exists())

                log_file = logs_dir / "results.jsonl"
                self.assertFalse(log_file.exists())

        print(
            "Integrated pilot budget test passed: "
            "0 API requests, 0 saved outputs."
        )


if __name__ == "__main__":
    unittest.main()
