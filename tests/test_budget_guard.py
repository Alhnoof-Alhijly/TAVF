
import os
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import cost_tracker
import run_baseline_pilot


class TestBudgetGuard(unittest.TestCase):

    def test_budget_limit_prevents_api_calls(self):
        api_calls = []

        class FakeClient:
            def __init__(self, **kwargs):
                self.responses = self

            def create(self, **kwargs):
                api_calls.append(kwargs)
                raise AssertionError(
                    "API must not be called when budget is exceeded."
                )

        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(temp)

            with (
                patch.object(
                    run_baseline_pilot,
                    "OUTPUT_DIR",
                    output_dir,
                ),
                patch.object(
                    run_baseline_pilot,
                    "OUTPUT_FILE",
                    output_dir / "pilot_outputs.json",
                ),
                patch.object(
                    run_baseline_pilot,
                    "ERROR_FILE",
                    output_dir / "pilot_errors.jsonl",
                ),
                patch.object(
                    cost_tracker,
                    "calculate_spent",
                    return_value=Decimal("1.50"),
                ),
                patch.dict(
                    sys.modules,
                    {
                        "openai": type(
                            "FakeOpenAI",
                            (),
                            {"OpenAI": FakeClient},
                        )
                    },
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
                run_baseline_pilot.main()

            self.assertEqual(len(api_calls), 0)

            self.assertFalse(
                (output_dir / "pilot_outputs.json").exists()
            )

        print(
            "Budget guard passed: "
            "pilot stopped before any API request."
        )


if __name__ == "__main__":
    unittest.main()
