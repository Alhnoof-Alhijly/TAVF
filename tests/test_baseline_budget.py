
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import run_baseline


class TestBaselineBudget(unittest.TestCase):

    def test_budget_limit_prevents_api_calls(self):
        api_calls = []

        class FakeClient:
            def __init__(self, **kwargs):
                self.responses = self

            def create(self, **kwargs):
                api_calls.append(kwargs)
                raise AssertionError(
                    "API request must not be sent."
                )

        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(temp)
            output_file = output_dir / "baseline_outputs.json"
            error_file = output_dir / "baseline_errors.jsonl"

            with (
                patch.object(
                    run_baseline,
                    "OUTPUT_DIR",
                    output_dir,
                ),
                patch.object(
                    run_baseline,
                    "OUTPUT_FILE",
                    output_file,
                ),
                patch.object(
                    run_baseline,
                    "ERROR_FILE",
                    error_file,
                ),
                patch.object(
                    run_baseline,
                    "check_budget",
                    return_value=False,
                ) as budget_check,
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
                        "run_baseline.py",
                        "--execute",
                        "--model",
                        "fake-test-model",
                        "--limit",
                        "2",
                    ],
                ),
            ):
                run_baseline.main()

            # The budget must be checked before an API request.
            budget_check.assert_called_once()

            # No requests or output records should be created.
            self.assertEqual(len(api_calls), 0)
            self.assertFalse(output_file.exists())
            self.assertFalse(error_file.exists())

        print(
            "Baseline budget test passed: "
            "0 API requests."
        )


if __name__ == "__main__":
    unittest.main()
