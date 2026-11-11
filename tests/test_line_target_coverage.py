"""Offline line coverage tests: all Docker processes are mocked."""

import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from tavf.evaluation.line_coverage import MAX_OUTPUT_BYTES, _COVERAGE_HARNESS, _run_container, evaluate_line_target


SOURCE = "def target(x):\n    if x:\n        return 1\n    return 0\n"
TASK = {"task_id": "offline-line", "task_type": "test_case_generation",
        "input": {"python_solution": SOURCE},
        "reference": {"target_type": "line", "target": {"line": 3}}}


def transport(lines=(1, 2, 3), **changes):
    report = {"version": 1, "completed": True, "tracer_intact": True,
              "test_exit_code": 0, "executed_lines": list(lines)}
    return {"exit_code": 0, "timed_out": False, "output_overflow": False,
            "transport_incomplete": False, "output": json.dumps(report).encode(), **changes}


class TestLineTargetCoverage(unittest.TestCase):
    def setUp(self):
        runner = patch("tavf.evaluation.line_coverage._run_container", return_value=transport())
        cleanup = patch("tavf.evaluation.line_coverage.subprocess.run", return_value=Mock(returncode=0))
        guard = patch("tavf.evaluation.line_coverage.subprocess.Popen", side_effect=AssertionError("No real processes"))
        self.runner, self.cleanup = runner.start(), cleanup.start()
        guard.start()
        self.addCleanup(runner.stop)
        self.addCleanup(cleanup.stop)
        self.addCleanup(guard.stop)

    def test_covered_and_not_covered_with_evidence(self):
        for lines, status in (((1, 2, 3), "covered"), ((1, 2, 4), "not_covered")):
            with self.subTest(status=status):
                self.runner.return_value = transport(lines)
                result = evaluate_line_target("assert target(1) == 1", TASK)
                self.assertEqual(result["status"], status)
                self.assertEqual(result["evidence"]["executed_lines"], list(lines))
                self.assertEqual(result["evidence"]["target_line"], 3)
                self.assertEqual(result["evidence"]["task_id"], "offline-line")
                self.assertEqual(result["evidence"]["assertion_correctness"], "not_verified")

    def test_isolation_source_transport_and_cleanup(self):
        original = copy.deepcopy(TASK)
        evaluate_line_target("assert target(1) == 1", TASK)
        command, payload = self.runner.call_args.args
        self.assertEqual(json.loads(payload), [SOURCE, "assert target(1) == 1"])
        for flag, value in {"--network": "none", "--cpus": "0.5", "--memory": "128m",
                            "--memory-swap": "128m", "--pids-limit": "16", "--user": "65534:65534",
                            "--cap-drop": "ALL", "--security-opt": "no-new-privileges"}.items():
            self.assertEqual(command[command.index(flag) + 1], value)
        for flag in ("--read-only", "--pull=never", "python:3.12-slim", "-I", "-B"):
            self.assertIn(flag, command)
        for flag in ("--mount", "--volume", "-v", "--env-file", "--privileged"):
            self.assertNotIn(flag, command)
        env = [command[i + 1] for i, value in enumerate(command) if value == "--env"]
        self.assertEqual(len(env), 10)
        self.assertTrue(all(value.endswith("=") for value in env))
        self.assertEqual(self.cleanup.call_args.args[0],
                         ["docker", "rm", "--force", command[command.index("--name") + 1]])
        self.assertEqual(self.cleanup.call_args.kwargs["timeout"], 5)
        self.assertEqual(TASK, original)

    def test_unavailable_docker_and_timeout_cleanup(self):
        for error in (FileNotFoundError(), PermissionError(), subprocess.TimeoutExpired("docker", 10)):
            with self.subTest(error=type(error).__name__):
                self.runner.side_effect = error
                self.assertEqual(evaluate_line_target("pass", TASK)["status"], "not_verified")
                self.assertEqual(self.cleanup.call_count, 1)
                self.cleanup.reset_mock()

    def test_transport_errors_never_mean_not_covered(self):
        for changes in ({"exit_code": 125}, {"exit_code": 1}, {"exit_code": 137},
                        {"timed_out": True}, {"output_overflow": True}, {"transport_incomplete": True}):
            with self.subTest(changes=changes):
                self.runner.return_value = transport(**changes)
                self.assertEqual(evaluate_line_target("pass", TASK)["status"], "not_verified")

    def test_missing_malformed_or_incomplete_reports(self):
        for output in (b"", b"garbage", b"[]", b"{}", b"x" * (MAX_OUTPUT_BYTES + 1)):
            self.runner.return_value = transport(output=output)
            self.assertEqual(evaluate_line_target("pass", TASK)["status"], "not_verified")
        for field, value in (("completed", False), ("tracer_intact", False), ("test_exit_code", 1),
                             ("executed_lines", []), ("executed_lines", [True]),
                             ("executed_lines", [999]), ("version", 2)):
            report = json.loads(transport()["output"])
            report[field] = value
            self.runner.return_value = transport(output=json.dumps(report).encode())
            self.assertEqual(evaluate_line_target("pass", TASK)["status"], "not_verified")

    def test_invalid_target_never_launches_docker(self):
        for target in ({"line": 0}, {"line": True}, {"line": 999}, {}, {"line": 3, "extra": 1}):
            task = copy.deepcopy(TASK)
            task["reference"]["target"] = target
            self.assertEqual(evaluate_line_target("pass", task)["status"], "not_verified")
        task = copy.deepcopy(TASK)
        task["reference"]["target_type"] = "branch"
        self.assertEqual(evaluate_line_target("pass", task)["status"], "not_verified")
        self.assertEqual(evaluate_line_target("", TASK)["status"], "not_verified")
        self.runner.assert_not_called()
        self.cleanup.assert_not_called()

    def test_cleanup_timeout_leaves_result_unverified(self):
        self.cleanup.side_effect = subprocess.TimeoutExpired("docker rm", 5)
        result = evaluate_line_target("pass", TASK)
        self.assertEqual(result["status"], "not_verified")
        self.assertIn("cleanup_error", result["evidence"])


class TestBoundedDockerTransport(unittest.TestCase):
    @patch("tavf.evaluation.line_coverage.subprocess.Popen")
    def test_capture_cap_and_cli_kill(self, popen):
        process = popen.return_value
        process.stdout = io.BytesIO(b"x" * (MAX_OUTPUT_BYTES + 100))
        process.stdin = io.BytesIO()
        process.returncode = -9
        result = _run_container(["docker", "run"], b"[]")
        self.assertEqual(len(result["output"]), MAX_OUTPUT_BYTES)
        self.assertTrue(result["output_overflow"])
        process.kill.assert_called_once()
        process.wait.assert_called_once_with(timeout=10)

    @patch("tavf.evaluation.line_coverage.subprocess.Popen")
    def test_timeout_kills_cli_and_bounds_wait(self, popen):
        process = popen.return_value
        process.stdout, process.stdin = io.BytesIO(b"{}"), io.BytesIO()
        process.returncode = -9
        process.wait.side_effect = [subprocess.TimeoutExpired("docker", 10), None]
        result = _run_container(["docker", "run"], b"[]")
        self.assertTrue(result["timed_out"])
        process.kill.assert_called_once()
        self.assertEqual(process.wait.call_args_list[-1].kwargs, {"timeout": 5})


class TestTrustedTracingFixture(unittest.TestCase):
    def test_traces_only_program_and_runs_unittest(self):
        # These fixed trusted fixtures exercise the harness offline. No data from
        # datasets, model output, environment or project code is executed.
        tests = ("import unittest\nclass Fixture(unittest.TestCase):\n"
                 "    def test_zero(self):\n        self.assertEqual(target(0), 0)\n")
        completed = subprocess.run(
            [sys.executable, "-I", "-B", "-c", _COVERAGE_HARNESS],
            input=json.dumps([SOURCE, tests]), text=True, capture_output=True,
            timeout=5, shell=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["executed_lines"], [1, 2, 4])
        self.assertTrue(report["completed"])
        self.assertTrue(report["tracer_intact"])

    def test_failed_trusted_fixture_is_incomplete(self):
        completed = subprocess.run(
            [sys.executable, "-I", "-B", "-c", _COVERAGE_HARNESS],
            input=json.dumps([SOURCE, "assert target(1) == 999"]),
            text=True, capture_output=True, timeout=5, shell=False,
        )
        report = json.loads(completed.stdout)
        self.assertFalse(report["completed"])
        self.assertEqual(report["test_exit_code"], 1)


if __name__ == "__main__":
    unittest.main()
