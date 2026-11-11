"""Focused offline branch evaluation tests; no Docker or generated-code runs."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from tavf.evaluation.branch_coverage import evaluate_branch_target


SOURCE = "def target(x):\n    if x:\n        return 1\n    return 0\n"
TASK = {"task_id": "offline-branch", "task_type": "test_case_generation",
        "input": {"python_solution": SOURCE},
        "reference": {"target_type": "branch", "target": {"start": 2, "end": 3}}}


def transport(lines, **changes):
    report = {"version": 1, "completed": True, "tracer_intact": True,
              "test_exit_code": 0, "executed_lines": lines}
    return {"exit_code": 0, "timed_out": False, "output_overflow": False,
            "transport_incomplete": False, "output": json.dumps(report).encode(), **changes}


class TestBranchTargetCoverage(unittest.TestCase):
    def setUp(self):
        runner = patch("tavf.evaluation.line_coverage._run_container", return_value=transport([1, 2, 3]))
        cleanup = patch("tavf.evaluation.line_coverage.subprocess.run", return_value=Mock(returncode=0))
        guard = patch("tavf.evaluation.line_coverage.subprocess.Popen", side_effect=AssertionError("No real processes"))
        self.runner, self.cleanup = runner.start(), cleanup.start()
        guard.start()
        self.addCleanup(runner.stop)
        self.addCleanup(cleanup.stop)
        self.addCleanup(guard.stop)

    def test_entered_block_requires_start_plus_one(self):
        for lines, status in (([1, 2, 3], "covered"), ([1, 2, 4], "not_covered")):
            with self.subTest(lines=lines):
                self.runner.return_value = transport(lines)
                result = evaluate_branch_target("assert target(1) == 1", TASK)
                self.assertEqual(result["status"], status)
                self.assertEqual(result["evidence"]["entry_line"], 3)
                self.assertEqual(result["evidence"]["target"], {"start": 2, "end": 3})
                self.assertEqual(result["evidence"]["executed_lines"], lines)
                self.assertEqual(result["evidence"]["test_exit_code"], 0)
                self.assertEqual(result["evidence"]["assertion_correctness"], "not_verified")

    def test_passing_exit_code_without_trace_is_unverified(self):
        for output in (b"", b"{}", b"invalid"):
            self.runner.return_value = transport([1], output=output)
            self.assertEqual(evaluate_branch_target("pass", TASK)["status"], "not_verified")

    def test_timeout_failure_and_missing_docker_are_unverified(self):
        for changes in ({"timed_out": True}, {"exit_code": 1}, {"exit_code": 125},
                        {"output_overflow": True}, {"transport_incomplete": True}):
            with self.subTest(changes=changes):
                self.runner.return_value = transport([1, 2, 3], **changes)
                self.assertEqual(evaluate_branch_target("pass", TASK)["status"], "not_verified")
        self.runner.side_effect = FileNotFoundError()
        result = evaluate_branch_target("pass", TASK)
        self.assertEqual(result["status"], "not_verified")
        self.assertEqual(result["evidence"]["error_type"], "FileNotFoundError")

    def test_invalid_bounds_and_other_target_types_never_launch(self):
        for target in ({}, {"start": True, "end": 3}, {"start": 0, "end": 3},
                       {"start": 3, "end": 2}, {"start": 2, "end": 2}, {"start": 2, "end": 99}):
            task = copy.deepcopy(TASK)
            task["reference"]["target"] = target
            self.assertEqual(evaluate_branch_target("pass", task)["status"], "not_verified")
        for task in (None, {}, {**TASK, "reference": {"target_type": "line", "target": {"line": 3}}}):
            self.assertEqual(evaluate_branch_target("pass", task)["status"], "not_verified")
        self.runner.assert_not_called()
        self.cleanup.assert_not_called()

    def test_reuses_docker_isolation_and_preserves_input(self):
        before = copy.deepcopy(TASK)
        result = evaluate_branch_target("assert target(1) == 1", TASK)
        self.assertEqual(result["status"], "covered")
        command, payload = self.runner.call_args.args
        self.assertEqual(json.loads(payload), [SOURCE, "assert target(1) == 1"])
        for flag, value in {"--network": "none", "--cpus": "0.5", "--memory": "128m",
                            "--memory-swap": "128m", "--pids-limit": "16",
                            "--cap-drop": "ALL", "--security-opt": "no-new-privileges"}.items():
            self.assertEqual(command[command.index(flag) + 1], value)
        for flag in ("--read-only", "--pull=never", "python:3.12-slim"):
            self.assertIn(flag, command)
        for flag in ("--mount", "--volume", "--env-file", "--privileged"):
            self.assertNotIn(flag, command)
        self.assertEqual(result["evidence"]["timeout_seconds"], 10)
        self.assertEqual(result["evidence"]["max_output_bytes"], 65536)
        self.assertEqual(TASK, before)
        self.cleanup.assert_called_once()

    def test_cleanup_failure_propagates(self):
        self.cleanup.side_effect = subprocess.TimeoutExpired("docker rm", 5)
        self.assertEqual(evaluate_branch_target("pass", TASK)["status"], "not_verified")


if __name__ == "__main__":
    unittest.main()
