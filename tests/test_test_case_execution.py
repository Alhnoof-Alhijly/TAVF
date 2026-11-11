"""Offline tests: all Docker calls are mocked; no generated source is run."""

import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from tavf.validators.execution import validate_execution
from tavf.validators.test_case import validate_test_case


class TestDockerExecution(unittest.TestCase):
    @patch("tavf.validators.execution.subprocess.run")
    def test_isolation_and_source_only_transport(self, run):
        run.return_value = Mock(returncode=0)
        result = validate_execution("assert target(1) == 1", "def target(x): return x")
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["exit_code"], 0)
        args, options = run.call_args_list[0]
        command = args[0]
        for flag, value in {
            "--network": "none", "--pull=never": None, "--read-only": None,
            "--cap-drop": "ALL", "--security-opt": "no-new-privileges",
            "--cpus": "0.5", "--memory": "128m", "--memory-swap": "128m",
            "--pids-limit": "16", "--user": "65534:65534",
            "--log-driver": "none",
        }.items():
            self.assertIn(flag, command)
            if value is not None:
                self.assertEqual(command[command.index(flag) + 1], value)
        self.assertIn("python:3.12-slim", command)
        self.assertEqual(command[-5:-1], ["python", "-I", "-B", "-c"])
        for forbidden in ("--volume", "-v", "--mount", "-e", "--env-file", "--privileged"):
            self.assertNotIn(forbidden, command)
        environment = [command[i + 1] for i, part in enumerate(command) if part == "--env"]
        self.assertEqual(set(environment), {
            key + "=" for proxy in ("HTTP_PROXY", "HTTPS_PROXY", "FTP_PROXY", "NO_PROXY", "ALL_PROXY")
            for key in (proxy, proxy.lower())
        })
        self.assertEqual(json.loads(options["input"]),
                         ["def target(x): return x", "assert target(1) == 1"])
        self.assertEqual(options["timeout"], 10)
        self.assertFalse(options["shell"])
        self.assertEqual(options["stdout"], subprocess.DEVNULL)
        self.assertEqual(options["stderr"], subprocess.DEVNULL)
        cleanup = run.call_args_list[1]
        self.assertEqual(cleanup.args[0], ["docker", "rm", "--force",
                                         command[command.index("--name") + 1]])
        self.assertEqual(cleanup.kwargs["timeout"], 5)

    @patch("tavf.validators.execution.subprocess.run")
    def test_exit_statuses(self, run):
        for code, expected in ((0, "passed"), (1, "failed"), (137, "failed"),
                               (125, "not_verified"), (126, "not_verified"), (127, "not_verified")):
            with self.subTest(code=code):
                run.side_effect = [Mock(returncode=code), Mock(returncode=0)]
                evidence = validate_execution("assert True")
                self.assertEqual(evidence["status"], expected)
                self.assertEqual(evidence["exit_code"], code)

    @patch("tavf.validators.execution.subprocess.run")
    def test_timeout_removes_container(self, run):
        run.side_effect = [subprocess.TimeoutExpired("docker", 10), Mock(returncode=0)]
        evidence = validate_execution("while True: pass")
        self.assertEqual(evidence["status"], "failed")
        self.assertTrue(evidence["timed_out"])
        self.assertEqual(run.call_count, 2)

    @patch("tavf.validators.execution.subprocess.run")
    def test_missing_docker_and_cleanup_errors_are_unverified(self, run):
        run.side_effect = FileNotFoundError()
        evidence = validate_execution("assert True")
        self.assertEqual(evidence["status"], "not_verified")
        self.assertEqual(evidence["error_type"], "FileNotFoundError")
        self.assertEqual(evidence["cleanup_error"], "FileNotFoundError")
        run.side_effect = [subprocess.TimeoutExpired("docker", 10), Mock(returncode=1)]
        self.assertEqual(validate_execution("pass")["status"], "not_verified")

    @patch("tavf.validators.test_case.validate_execution")
    def test_default_and_invalid_syntax_never_launch(self, execute):
        validate_test_case("assert True")
        validate_test_case("def broken(:", execute=True)
        execute.assert_not_called()

    @patch("tavf.validators.test_case.validate_execution")
    def test_integration_evidence_and_issue_classification(self, execute):
        for status in ("passed", "failed", "not_verified"):
            with self.subTest(status=status):
                execute.return_value = {"status": status, "message": "Evidence", "exit_code": 1}
                result = validate_test_case("assert target(1) == 1", {
                    "python_solution": "def target(x): return x", "secret": "never forwarded",
                }, execute=True)
                execute.assert_called_with("assert target(1) == 1", "def target(x): return x")
                evidence = result["evidence"][2]
                self.assertEqual(evidence["status"], status)
                self.assertEqual(evidence["exit_code"], 1)
                issues = [i for i in result["issues"] if i["check"] == "Execution Success"]
                if status == "passed":
                    self.assertEqual(issues, [])
                else:
                    self.assertEqual(issues[0]["classification"],
                                     "fixable" if status == "failed" else "missing_information")
                    self.assertEqual(issues[0]["evidence_index"], 2)
                self.assertFalse(result["valid"])


if __name__ == "__main__":
    unittest.main()
