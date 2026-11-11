"""Offline path checks; Docker is mocked and no generated code is executed."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from tavf.evaluation.path_coverage import _PATH_HARNESS, evaluate_path_target, match_path


A, B = "BRANCH #1: Covered if branch at line 2-3\n", "BRANCH #2: Covered else branch at line 4-5\n"
SOURCE = "def target(x):\n    if x:\n        return 1\n    else:\n        return 0\n"
INSTRUMENTED = ("def target(x):\n    if x:\n        log_function(" + repr(A)
                + ")\n        return 1\n    else:\n        log_function(" + repr(B)
                + ")\n        return 0\ndef log_function(info):\n    raise RuntimeError('file logger must be replaced')\n")
ROW = {"task_num": 1, "python_solution": SOURCE, "python_solution_instrumented": INSTRUMENTED}
TASK = {"task_id": "offline-path", "task_type": "test_case_generation",
        "input": {"python_solution": SOURCE}, "reference": {"task_num": 1,
        "target_type": "path", "target": {"execution_path": [A], "condition_path": ["Line 2: x"]}}}


def transport(events, **changes):
    report = {"version": 1, "completed": True, "logger_intact": True, "truncated": False,
              "test_exit_code": 0, "observed_path": events}
    return {"exit_code": 0, "timed_out": False, "output_overflow": False,
            "transport_incomplete": False, "output": json.dumps(report).encode(), **changes}


class TestPathTargetCoverage(unittest.TestCase):
    def setUp(self):
        runner = patch("tavf.evaluation.line_coverage._run_container", return_value=transport([A]))
        cleanup = patch("tavf.evaluation.line_coverage.subprocess.run", return_value=Mock(returncode=0))
        guard = patch("tavf.evaluation.line_coverage.subprocess.Popen", side_effect=AssertionError("No real Docker"))
        self.runner, self.cleanup = runner.start(), cleanup.start()
        guard.start()
        self.addCleanup(runner.stop)
        self.addCleanup(cleanup.stop)
        self.addCleanup(guard.stop)

    def evaluate(self, task=TASK, row=ROW):
        return evaluate_path_target("assert target(1) == 1", task, instrumented_program=row)

    def test_covered_not_covered_and_empty_observed_stream(self):
        for events, expected in (([A], "covered"), ([B], "not_covered"), ([], "not_covered")):
            with self.subTest(events=events):
                self.runner.return_value = transport(events)
                result = self.evaluate()
                self.assertEqual(result["status"], expected)
                self.assertEqual(result["evidence"]["observed_path"], events)
                self.assertEqual(result["evidence"]["match_score"], 1 if expected == "covered" else 0)
                self.assertTrue(result["evidence"]["trace_completed"])
                self.assertEqual(result["evidence"]["assertion_correctness"], "not_verified")

    def test_order_repetition_extra_events_and_benchmark_contiguous_semantics(self):
        self.assertEqual(match_path([B, A, A, B], [A, A]), 1)
        self.assertEqual(match_path([A], [A, A]), 0.5)
        self.assertEqual(match_path([B, A], [A, B]), 0.5)
        # Distinguishes the actual TestEval implementation from subsequence LCS.
        self.assertEqual(match_path([A, "extra", B], [A, B]), 0.5)
        with self.assertRaises(ValueError):
            match_path([A], [])

    def test_source_identity_instrumentation_and_targets_must_match(self):
        for row in ({**ROW, "task_num": 2}, {**ROW, "python_solution": "pass"},
                    {**ROW, "python_solution_instrumented": INSTRUMENTED.replace("return 1", "return 999")},
                    {**ROW, "python_solution_instrumented": "def broken(:"}):
            self.assertEqual(self.evaluate(row=row)["status"], "not_verified")
        for target in ({"execution_path": [], "condition_path": []},
                       {"execution_path": ["unknown"], "condition_path": ["Line 2: x"]}):
            task = copy.deepcopy(TASK)
            task["reference"]["target"] = target
            self.assertEqual(self.evaluate(task=task)["status"], "not_verified")
        self.runner.assert_not_called()

    def test_missing_instrumentation_is_unverified(self):
        with patch("tavf.evaluation.path_coverage.INSTRUMENTED_DATA") as data:
            data.read_text.side_effect = FileNotFoundError()
            self.assertEqual(evaluate_path_target("pass", TASK)["status"], "not_verified")
        self.runner.assert_not_called()

    def test_instrumented_lookup_by_program_id_not_row_order(self):
        with patch("tavf.evaluation.path_coverage.INSTRUMENTED_DATA") as data:
            data.read_text.return_value = json.dumps({**ROW, "task_num": 999}) + "\n" + json.dumps(ROW)
            self.assertEqual(evaluate_path_target("pass", TASK)["status"], "covered")

    def test_timeout_failure_and_docker_unavailable(self):
        for changes in ({"timed_out": True}, {"exit_code": 125}, {"output_overflow": True}, {"transport_incomplete": True}):
            self.runner.return_value = transport([A], **changes)
            self.assertEqual(self.evaluate()["status"], "not_verified")
        self.runner.side_effect = FileNotFoundError()
        self.assertEqual(self.evaluate()["status"], "not_verified")
        self.cleanup.side_effect = subprocess.TimeoutExpired("docker rm", 5)
        self.runner.side_effect = None
        self.runner.return_value = transport([A])
        self.assertEqual(self.evaluate()["status"], "not_verified")

    def test_invalid_or_truncated_report_is_unverified(self):
        for output in (b"", b"invalid", b"{}", b"[]"):
            self.runner.return_value = transport([A], output=output)
            self.assertEqual(self.evaluate()["status"], "not_verified")
        for field, value in (("completed", False), ("logger_intact", False), ("truncated", True),
                             ("test_exit_code", 1), ("observed_path", [7])):
            report = json.loads(transport([A])["output"])
            report[field] = value
            self.runner.return_value = transport([A], output=json.dumps(report).encode())
            self.assertEqual(self.evaluate()["status"], "not_verified")

    def test_reuses_isolation_and_keeps_source_metadata_unchanged(self):
        before = copy.deepcopy(TASK)
        self.evaluate()
        command, payload = self.runner.call_args.args
        self.assertEqual(json.loads(payload), [INSTRUMENTED, "assert target(1) == 1"])
        self.assertEqual(command[-1], _PATH_HARNESS)
        for flag, value in {"--network": "none", "--cpus": "0.5", "--memory": "128m",
                            "--memory-swap": "128m", "--pids-limit": "16", "--cap-drop": "ALL",
                            "--security-opt": "no-new-privileges"}.items():
            self.assertEqual(command[command.index(flag) + 1], value)
        self.assertIn("--read-only", command)
        for flag in ("--mount", "--volume", "--env-file", "--privileged"):
            self.assertNotIn(flag, command)
        self.assertEqual(TASK, before)


class TestTrustedPathHarness(unittest.TestCase):
    def test_fixed_fixture_preserves_order_repeats_and_replaces_file_logger(self):
        # Fixed hand-written fixture only: no model output or dataset code runs.
        tests = ("import unittest\nclass Fixture(unittest.TestCase):\n"
                 "    def test_paths(self):\n"
                 "        self.assertEqual(target(0), 0)\n"
                 "        self.assertEqual(target(1), 1)\n"
                 "        self.assertEqual(target(1), 1)\n")
        completed = subprocess.run(
            [sys.executable, "-I", "-B", "-c", _PATH_HARNESS],
            input=json.dumps([INSTRUMENTED, tests]), text=True, capture_output=True,
            timeout=5, shell=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["observed_path"], [B, A, A])
        self.assertTrue(report["completed"])
        self.assertTrue(report["logger_intact"])
        self.assertFalse(report["truncated"])

    def test_incomplete_trusted_fixture_cannot_report_success(self):
        completed = subprocess.run(
            [sys.executable, "-I", "-B", "-c", _PATH_HARNESS],
            input=json.dumps([INSTRUMENTED, "assert target(1) == 999"]),
            text=True, capture_output=True, timeout=5, shell=False,
        )
        report = json.loads(completed.stdout)
        self.assertFalse(report["completed"])
        self.assertEqual(report["test_exit_code"], 1)


if __name__ == "__main__":
    unittest.main()
