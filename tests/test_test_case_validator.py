import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from tavf.validators.test_case import validate_test_case


def checks(result):
    return {item["check"]: item for item in result["evidence"]}


class TestTestCaseValidator(unittest.TestCase):
    def test_syntax_pass_is_not_full_validation(self):
        result = validate_test_case("assert identity(1) == 1")
        statuses = checks(result)
        self.assertEqual(statuses["Syntax Validity"]["status"], "passed")
        for check in ("Input Validity", "Execution Success", "Assertion Validity"):
            self.assertEqual(statuses[check]["status"], "not_verified")
        self.assertFalse(result["valid"])
        self.assertTrue(all(i["classification"] == "missing_information" for i in result["issues"]))

    def test_syntax_failures_are_fixable(self):
        for code in ("", "def broken(:", "return 1", "```python\nassert True\n```", "\x00"):
            with self.subTest(code=code):
                result = validate_test_case(code)
                self.assertEqual(checks(result)["Syntax Validity"]["status"], "failed")
                self.assertEqual(result["issues"][0]["classification"], "fixable")
                self.assertEqual(checks(result)["Execution Success"]["status"], "not_verified")

    def test_no_visible_assertion_is_structural_issue(self):
        result = validate_test_case("def test_value():\n    identity(1)")
        issue = next(i for i in result["issues"] if i["check"] == "Assertion Validity")
        self.assertEqual(issue["classification"], "fixable")
        self.assertEqual(result["evidence"][issue["evidence_index"]]["status"], "failed")

    def test_unittest_assertion_like_call_is_not_an_oracle(self):
        result = validate_test_case(
            "import unittest\nclass Tests(unittest.TestCase):\n"
            "    def test_value(self):\n        self.assertEqual(identity(1), 999)"
        )
        assertion = checks(result)["Assertion Validity"]
        self.assertEqual(assertion["status"], "not_verified")
        self.assertEqual(assertion["assertion_lines"], [4])

    def test_obviously_tautological_assertion_does_not_pass_correctness(self):
        result = validate_test_case("assert True")
        self.assertEqual(checks(result)["Assertion Validity"]["status"], "not_verified")
        self.assertFalse(result["valid"])

    def test_generated_and_reference_code_are_not_executed(self):
        code = "raise RuntimeError('must never execute')\nassert True"
        context = {
            "description": "Return input.",
            "python_solution": "raise RuntimeError('reference must never execute')",
        }
        original = context.copy()
        result = validate_test_case(code, context)
        self.assertEqual(checks(result)["Syntax Validity"]["status"], "passed")
        self.assertEqual(checks(result)["Execution Success"]["status"], "not_verified")
        self.assertEqual(context, original)

    def test_existing_testeval_context_is_not_treated_as_oracle(self):
        tasks = json.loads((ROOT / "data/processed/test_case_tasks.json").read_text(encoding="utf-8"))
        result = validate_test_case("assert True", tasks[0]["input"])
        evidence = checks(result)["Input Validity"]
        self.assertEqual(evidence["available_context_fields"], ["description", "python_solution"])
        self.assertEqual(evidence["status"], "not_verified")

    def test_deterministic_complete_evidence(self):
        result = validate_test_case("assert 1 == 1")
        self.assertEqual(result, validate_test_case("assert 1 == 1"))
        self.assertEqual(set(result), {"valid", "issues", "evidence"})
        self.assertEqual(len(result["evidence"]), 4)
        for issue in result["issues"]:
            self.assertEqual(issue["check"], result["evidence"][issue["evidence_index"]]["check"])

    def test_invalid_argument_types(self):
        for artifact, context in ((None, None), (1, {}), ("assert True", [])):
            with self.subTest(artifact=artifact, context=context):
                with self.assertRaises(TypeError):
                    validate_test_case(artifact, context)


if __name__ == "__main__":
    unittest.main()
