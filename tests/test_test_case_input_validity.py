import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from tavf.validators.test_case import validate_test_case


def validate(code, reference):
    result = validate_test_case(code, {"python_solution": reference})
    evidence = next(e for e in result["evidence"] if e["check"] == "Input Validity")
    return result, evidence


class TestStaticInputValidity(unittest.TestCase):
    def test_direct_function_valid_arguments(self):
        result, evidence = validate("assert target(1, limit=2) == 1",
                                    "def target(value, *, limit=10): return value")
        self.assertEqual(evidence["status"], "passed")
        self.assertEqual(evidence["scope"], "signature_only")
        self.assertEqual(evidence["domain_status"], "not_verified")
        self.assertFalse(result["valid"])

    def test_missing_extra_and_invalid_keyword_arguments(self):
        for call in ("target()", "target(1, 2)", "target(1, wrong=2)",
                     "target(1, value=2)"):
            with self.subTest(call=call):
                result, evidence = validate(call, "def target(value): return value")
                self.assertEqual(evidence["status"], "failed")
                issue = next(i for i in result["issues"] if i["check"] == "Input Validity")
                self.assertEqual(issue["classification"], "fixable")
                self.assertEqual(result["evidence"][issue["evidence_index"]], evidence)

    def test_positional_only_keyword_only_defaults_and_variadics(self):
        reference = "def target(a, /, b=2, *items, required, **options): pass"
        for call, status in (("target(1, required=3)", "passed"),
                             ("target(1, 2, 3, required=4, extra=5)", "passed"),
                             ("target(1)", "failed"), ("target(a=1, required=3)", "failed")):
            with self.subTest(call=call):
                self.assertEqual(validate(call, reference)[1]["status"], status)
        self.assertEqual(validate("target(a=1)", "def target(a, /): pass")[1]["status"], "failed")

    def test_testeval_solution_method_inline_and_local_instance(self):
        reference = "class Solution:\n    def solve(self, values, *, limit=2): return values"
        for code in ("assert Solution().solve([1]) == [1]",
                     "def test_solve():\n    solution = Solution()\n    assert solution.solve([1], limit=3) == [1]"):
            with self.subTest(code=code):
                self.assertEqual(validate(code, reference)[1]["status"], "passed")
        self.assertEqual(validate("Solution().solve()", reference)[1]["status"], "failed")

    def test_ambiguous_calls_remain_unverified(self):
        reference = "def target(value): return value"
        for code in ("target(*values)", "target(**options)", "alias = target\nalias(1)",
                     "target = other\ntarget()", "def test_x(target):\n    target()",
                     "from somewhere import target\ntarget()", "helper(1)", "assert True",
                     "target(1)\nhelper(1)", "exec('pass')\ntarget()"):
            with self.subTest(code=code):
                result, evidence = validate(code, reference)
                self.assertEqual(evidence["status"], "not_verified")
                issue = next(i for i in result["issues"] if i["check"] == "Input Validity")
                self.assertEqual(issue["classification"], "missing_information")

    def test_decorated_duplicate_and_reassigned_reference_targets(self):
        for reference in ("@wrapper\ndef target(value): pass",
                          "def target(value): pass\ndef target(): pass",
                          "def target(value): pass\ntarget = other"):
            with self.subTest(reference=reference):
                self.assertEqual(validate("target()", reference)[1]["status"], "not_verified")

    def test_ambiguous_receivers_are_not_resolved(self):
        reference = "class Solution:\n    def solve(self, value): return value"
        for code in ("solution.solve()", "solution = Solution()\nsolution = other\nsolution.solve()",
                     "if flag:\n    solution = Solution()\nsolution.solve()",
                     "solution = Solution()\nsolution.solve = other\nsolution.solve()"):
            with self.subTest(code=code):
                self.assertEqual(validate(code, reference)[1]["status"], "not_verified")

    def test_missing_and_invalid_reference_syntax(self):
        for reference in ("", "def broken(:", "def target(value, value): pass"):
            with self.subTest(reference=reference):
                self.assertEqual(validate("target(1)", reference)[1]["status"], "not_verified")

    def test_replaced_and_dynamic_reference_methods_remain_unverified(self):
        for reference in (
            "class Solution:\n    def solve(self, value): pass\n    solve = other",
            "class Solution:\n    def __getattribute__(self, name): pass\n    def solve(self, value): pass",
        ):
            with self.subTest(reference=reference):
                self.assertEqual(validate("Solution().solve()", reference)[1]["status"], "not_verified")

    def test_other_checks_preserved_and_source_not_executed(self):
        reference = "raise RuntimeError('never run')\ndef target(value=explode()): return value"
        result, evidence = validate("assert target() == 1", reference)
        self.assertEqual(evidence["status"], "passed")
        checks = {e["check"]: e["status"] for e in result["evidence"]}
        self.assertEqual(checks["Syntax Validity"], "passed")
        self.assertEqual(checks["Execution Success"], "not_verified")
        self.assertEqual(checks["Assertion Validity"], "not_verified")
        self.assertEqual(len(result["evidence"]), 4)

    def test_no_domain_constraints_inferred(self):
        _, evidence = validate("target(-999)", "def target(positive: int): return positive")
        self.assertEqual(evidence["status"], "passed")
        self.assertEqual(evidence["domain_status"], "not_verified")


if __name__ == "__main__":
    unittest.main()
