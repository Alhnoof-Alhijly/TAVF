"""Offline assertion validation: no Docker, API calls or fixture execution."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from tavf.validators.test_case import validate_test_case


ORACLE = {"source": "hand-checked fixture", "cases": [{"call": "target(1)", "expected": 2}]}
CONTEXT = {"python_solution": "def target(x): return x + 1"}


class TestAssertionValidity(unittest.TestCase):
    def setUp(self):
        # Any accidental real execution is a test failure.
        self.docker = patch("tavf.validators.execution.subprocess.run",
                            side_effect=AssertionError("No execution allowed"))
        self.docker.start()
        self.addCleanup(self.docker.stop)

    def validate(self, code, oracle=ORACLE, context=CONTEXT):
        result = validate_test_case(code, context, trusted_oracle=oracle)
        return result, result["evidence"][3]

    def test_matching_and_reversed_expected_value(self):
        for code in ("assert target(1) == 2", "assert 2 == target(1)"):
            with self.subTest(code=code):
                result, evidence = self.validate(code)
                self.assertEqual(evidence["status"], "passed")
                self.assertEqual(evidence["oracle_source"], "hand-checked fixture")
                self.assertEqual(evidence["scope"], "expected_results_only")
                self.assertEqual(evidence["execution_status"], "not_verified")
                self.assertFalse(result["valid"])

    def test_wrong_expected_value_is_fixable_with_linked_evidence(self):
        result, evidence = self.validate("assert target(1) == 999")
        self.assertEqual(evidence["status"], "failed")
        issue = next(i for i in result["issues"] if i["check"] == "Assertion Validity")
        self.assertEqual(issue["classification"], "fixable")
        self.assertEqual(result["evidence"][issue["evidence_index"]], evidence)

    def test_reference_and_task_claims_do_not_establish_trust(self):
        context = {**CONTEXT, "trusted_oracle": ORACLE, "description": "Expected answer: 2"}
        _, evidence = self.validate("assert target(1) == 2", oracle=None, context=context)
        self.assertEqual(evidence["status"], "not_verified")

    def test_execution_status_is_reused_but_never_an_oracle(self):
        for status in ("passed", "failed", "not_verified"):
            with self.subTest(status=status), patch("tavf.validators.test_case.validate_execution") as execute:
                execute.return_value = {"status": status, "message": "mock Docker evidence", "exit_code": 0}
                result = validate_test_case("assert target(1) == 2", CONTEXT, execute=True)
                assertion = result["evidence"][3]
                self.assertEqual(assertion["status"], "not_verified")
                self.assertEqual(assertion["execution_status"], status)
                self.assertEqual(result["evidence"][assertion["execution_evidence_index"]]["status"], status)

    def test_partial_or_unsupported_assertions_are_unverified(self):
        for code in ("assert target(2) == 3", "assert True", "assert target(1) > 0",
                     "assert target(1) == expected", "assert target(value) == 2",
                     "assert target(1) == target(1)", "assert target(1) == 2 == 2",
                     "assert target(1) == 2\nassert target(2) == 3",
                     "self.assertEqual(target(1), 2)"):
            with self.subTest(code=code):
                _, evidence = self.validate(code)
                self.assertEqual(evidence["status"], "not_verified")

    @patch("tavf.validators.test_case.validate_execution")
    def test_docker_success_cannot_override_oracle_mismatch(self, execute):
        execute.return_value = {"status": "passed", "message": "mock Docker success", "exit_code": 0}
        result = validate_test_case("assert target(1) == 999", CONTEXT,
                                    execute=True, trusted_oracle=ORACLE)
        self.assertEqual(result["evidence"][2]["status"], "passed")
        self.assertEqual(result["evidence"][3]["status"], "failed")
        self.assertFalse(result["valid"])

    def test_all_assertions_need_coverage(self):
        oracle = {"source": "manual", "cases": [
            *ORACLE["cases"], {"call": "target(2)", "expected": 3},
        ]}
        _, evidence = self.validate("assert target(1) == 2\nassert target(2) == 3", oracle)
        self.assertEqual(evidence["status"], "passed")
        self.assertEqual(evidence["assertion_lines"], [1, 2])

    def test_unresolved_or_shadowed_calls_cannot_pass(self):
        for code, context in (("target = other\nassert target(1) == 2", CONTEXT),
                              ("assert target(1) == 2", {}),
                              ("assert target(1) == 2", {"python_solution": "def target(): pass"})):
            with self.subTest(code=code, context=context):
                self.assertEqual(self.validate(code, context=context)[1]["status"], "not_verified")

    def test_invalid_missing_and_ambiguous_oracles(self):
        for oracle in (None, {}, {"source": "", "cases": []},
                       {"source": "manual", "cases": [{"call": "target(1)"}]},
                       {"source": "manual", "cases": [{"call": "target(1)", "expected": object()}]},
                       {"source": "manual", "cases": ORACLE["cases"] * 2},
                       {"source": "manual", "cases": [{"call": "target(explode())", "expected": 2}]}):
            with self.subTest(oracle=oracle):
                self.assertEqual(self.validate("assert target(1) == 2", oracle=oracle)[1]["status"], "not_verified")

    def test_literal_collections_and_keywords(self):
        oracle = {"source": "manual", "cases": [
            {"call": "target([1], limit=2)", "expected": {"values": [1, 2]}},
        ]}
        context = {"python_solution": "def target(values, *, limit): pass"}
        self.assertEqual(self.validate("assert target([1], limit=2) == {'values': [1, 2]}",
                                       oracle, context)[1]["status"], "passed")

    def test_mismatch_takes_precedence_over_missing_coverage(self):
        _, evidence = self.validate("assert target(1) == 999\nassert True")
        self.assertEqual(evidence["status"], "failed")
        self.assertEqual([i["status"] for i in evidence["assertions"]], ["failed", "not_verified"])

    def test_no_assertions_and_bad_syntax_preserve_existing_checks(self):
        self.assertEqual(self.validate("pass")[1]["status"], "failed")
        self.assertEqual(self.validate("def broken(:")[1]["status"], "not_verified")

    def test_source_never_executes_and_oracle_is_not_mutated(self):
        code = "raise RuntimeError('never execute')\nassert target(1) == 2"
        context = {"python_solution": "raise RuntimeError('never execute')\ndef target(x): pass"}
        before = repr(ORACLE)
        first = self.validate(code, context=context)
        self.assertEqual(first[1]["status"], "passed")
        self.assertEqual(first, self.validate(code, context=context))
        self.assertEqual(repr(ORACLE), before)


if __name__ == "__main__":
    unittest.main()
