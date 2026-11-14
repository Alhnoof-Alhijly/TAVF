"""Run trusted synthetic fixtures only; no Docker or saved generated artifacts."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evaluation"))
import evaluate_testeval_blinded as adapter
from testeval_module_harness import build_harnesses

SOURCE = "def target(x):\n    return x + 1\n"
TESTS = """import unittest
from solution import target
from main import target as other
from __main__ import target as third
class TestSyntheticTarget(unittest.TestCase):
    def test_aliases(self):
        self.assertIs(target, other)
        self.assertIs(target, third)
        self.assertEqual(target(1), 2)
"""


def trusted_run(harness, source=SOURCE, tests=TESTS):
    stdout, stderr = io.StringIO(), io.StringIO()
    with patch.dict(sys.modules), patch.object(sys, "stdin", io.StringIO(json.dumps([source, tests]))), \
            contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            exec(compile(harness, "<trusted synthetic harness>", "exec"), {})
        except SystemExit as error:
            if error.code != 0:
                raise AssertionError(stderr.getvalue())
    return stdout.getvalue()


class TargetModuleHarnessTests(unittest.TestCase):
    def harnesses(self):
        return build_harnesses(adapter.execution._HARNESS, adapter.line_coverage._COVERAGE_HARNESS,
                               adapter.path_coverage._PATH_HARNESS, adapter.path_coverage._PATH_TEST_HARNESS)

    def test_execution_aliases_share_unchanged_reference_implementation(self):
        trusted_run(self.harnesses()["execution"])
        # Original shared-namespace access remains supported too.
        trusted_run(self.harnesses()["execution"], tests="assert target(2) == 3")

    def test_imported_reference_is_observed_by_line_tracer(self):
        report = json.loads(trusted_run(self.harnesses()["line"]))
        self.assertTrue(report["completed"])
        self.assertTrue(report["tracer_intact"])
        self.assertIn(2, report["executed_lines"])

    def test_imported_instrumented_reference_uses_path_recorder(self):
        instrumented = "def log_function(event):\n    pass\ndef target(x):\n    log_function('target-hit')\n    return x + 1\n"
        report = json.loads(trusted_run(self.harnesses()["path"], source=instrumented))
        self.assertTrue(report["completed"])
        self.assertTrue(report["logger_intact"])
        self.assertEqual(report["observed_path"], ["target-hit"])

    def test_harness_overrides_are_scoped_and_branch_uses_line_transport(self):
        originals = (adapter.execution._HARNESS, adapter.line_coverage._COVERAGE_HARNESS, adapter.path_coverage._PATH_HARNESS)
        with adapter.selected_image(adapter.VERIFIED_IMAGE, []):
            self.assertNotEqual(adapter.execution._HARNESS, originals[0])
            self.assertIn("target_module", adapter.line_coverage._COVERAGE_HARNESS)
            self.assertIn("target_module", adapter.path_coverage._PATH_HARNESS)
            self.assertIs(adapter.branch_coverage.evaluate_line_target, adapter.line_coverage.evaluate_line_target)
        self.assertEqual((adapter.execution._HARNESS, adapter.line_coverage._COVERAGE_HARNESS, adapter.path_coverage._PATH_HARNESS), originals)


if __name__ == "__main__":
    unittest.main()
