"""Fake pipe/process tests only; no Docker or generated source execution."""
import io
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evaluation"))
from testeval_diagnostics import MAX_STREAM_BYTES, capture, classify
import evaluate_testeval_blinded as adapter


def process(stdout=b"", stderr=b"", code=0):
    fake = Mock(stdin=io.BytesIO(), stdout=io.BytesIO(stdout), stderr=io.BytesIO(stderr), returncode=code)
    fake.wait.return_value = code
    return fake


class TestEvalDiagnosticsTests(unittest.TestCase):
    def test_both_streams_are_bounded_and_excess_is_drained_without_changing_exit(self):
        fake = process(b"a" * (MAX_STREAM_BYTES + 400), b"b" * (MAX_STREAM_BYTES + 300))
        transport, detail = capture(["docker", "run"], b"payload", 10, popen=Mock(return_value=fake))
        self.assertEqual(len(detail["stdout"]), MAX_STREAM_BYTES)
        self.assertEqual(len(detail["stderr"]), MAX_STREAM_BYTES)
        self.assertEqual(detail["truncated"], {"stdout": True, "stderr": True})
        self.assertEqual(detail["bytes_observed"]["stderr"], MAX_STREAM_BYTES + 300)
        self.assertEqual(transport["exit_code"], 0)
        fake.kill.assert_not_called()

    def test_failure_categories_distinguish_assertion_import_runtime_and_infrastructure(self):
        cases = [(1, "AssertionError: wrong\nFAILED (failures=1)", "test_assertion_failure"),
                 (1, "ModuleNotFoundError: No module named solution\nFAILED (errors=1)", "import_error"),
                 (1, "ValueError: invalid\nFAILED (errors=1)", "runtime_error"),
                 (125, "daemon error", "infrastructure_failure"),
                 (1, "", "unclassified_failure"), (0, "", "none")]
        for code, stderr, expected in cases:
            self.assertEqual(classify(code, "", stderr), expected)
        self.assertEqual(classify(-9, "", "", timed_out=True), "timeout")

    def test_timeout_preserves_partial_output_and_coverage_preserves_overflow_policy(self):
        fake = process(b"partial", b"trace", -9)
        fake.wait.side_effect = [subprocess.TimeoutExpired("docker", 10), -9]
        transport, detail = capture(["docker", "run"], b"", 10, popen=Mock(return_value=fake))
        self.assertTrue(transport["timed_out"])
        self.assertEqual(detail["stdout"], "partial")
        self.assertEqual(detail["failure_category"], "timeout")
        fake.kill.assert_called_once()
        noisy = process(b"x" * 100, b"y" * 100)
        transport, detail = capture(["docker", "run"], b"", 10, combined_limit=128, popen=Mock(return_value=noisy))
        self.assertTrue(transport["output_overflow"])
        self.assertEqual(len(transport["output"]), 128)
        noisy.kill.assert_called()

    def test_adapter_retains_diagnostics_and_original_failure_rule_and_limits(self):
        row = {"artifact_id": "anon", "pair_id": "pair", "artifact": "import nonexistent_module",
               "task": {"task_id": "task", "task_type": "test_case_generation", "input": {"python_solution": "x = 1"},
                        "reference": {"target_type": "line", "target": {"line": 1}}}}
        detail = {"stdout": "", "stderr": "ModuleNotFoundError: nonexistent_module", "exit_code": 1,
                  "failure_category": "import_error", "truncated": {"stdout": False, "stderr": False}}
        with patch.object(adapter, "capture", return_value=({"exit_code": 1, "timed_out": False}, detail)) as bounded, \
                patch.object(adapter.subprocess, "run", return_value=Mock(returncode=0)):
            result = adapter.evaluate_one(row, adapter.VERIFIED_IMAGE)
        metric = result["metrics"]["Execution"]
        self.assertEqual(metric["status"], "failed")
        self.assertEqual(metric["failure_category"], "import_error")
        self.assertEqual(metric["diagnostics"]["stderr"], detail["stderr"])
        self.assertEqual(result["metrics"]["Assertion Correctness"]["status"], "not_verified")
        command = bounded.call_args.args[0]
        for flag, value in {"--network": "none", "--memory": "128m", "--memory-swap": "128m", "--cpus": "0.5",
                            "--pids-limit": "16", "--user": "65534:65534", "--cap-drop": "ALL"}.items():
            self.assertEqual(command[command.index(flag) + 1], value)
        self.assertIn("--read-only", command)
        self.assertEqual(bounded.call_args.args[2], 10)


if __name__ == "__main__":
    unittest.main()
