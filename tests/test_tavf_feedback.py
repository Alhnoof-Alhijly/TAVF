import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from tavf.feedback import generate_feedback
from tavf.validators.bug_report import validate_bug_report
from tavf.validators.test_case import validate_test_case
from tavf.validators.user_story import validate_user_story


class TestTAVFFeedback(unittest.TestCase):
    def test_user_story_multiple_issues_and_story_evidence(self):
        story = "As a reader, I want bookmarks and I want alerts, so that I stay informed."
        result = validate_user_story("```\n" + story + "\n" + story + "\n```")
        feedback = generate_feedback("user_story_refinement", result)
        self.assertGreater(len(feedback["feedback"]), 1)
        self.assertEqual(feedback["unmapped_issue_codes"], [])
        for entry, issue in zip(feedback["feedback"], result["issues"]):
            self.assertEqual(entry["issue"], issue)
            self.assertEqual(entry["evidence"], result["evidence"][issue["evidence_index"]])
            self.assertTrue(entry["instruction"])

    def test_well_formed_identifier_mapping(self):
        # This validator branch is fixable when markers exist but the role slot
        # cannot match (no whitespace after the article).
        result = validate_user_story("As a, I want bookmarks, so that I can resume.")
        feedback = generate_feedback("user_story_refinement", result)
        self.assertEqual(feedback["feedback"][0]["issue"]["criterion"], "Well-formed")
        self.assertIn("Format the existing role", feedback["feedback"][0]["instruction"])

    def test_bug_report_all_sections_and_duplicate_heading(self):
        source = "Summary: Crash\nSteps: Save\nExpected: Saved\nActual: Exits"
        result = validate_bug_report("", source)
        feedback = generate_feedback("bug_report_refinement", result)
        self.assertEqual(len(feedback["feedback"]), 4)
        self.assertEqual(feedback["unmapped_issue_codes"], [])
        for entry in feedback["feedback"]:
            self.assertIn(entry["issue"]["section"], entry["instruction"])
            self.assertTrue(entry["evidence"]["source_content_available"])
        duplicate = validate_bug_report(source + "\nSummary: Crash", source)
        self.assertIn("consolidate", generate_feedback(
            "bug_report_refinement", duplicate
        )["feedback"][0]["instruction"])

    def test_test_case_fixable_checks_and_unverified_reporting(self):
        for artifact, expected in (("def broken(:", "Syntax Validity"),
                                   ("def test_value():\n    value = 1", "Assertion Validity")):
            with self.subTest(artifact=artifact):
                result = validate_test_case(artifact)
                feedback = generate_feedback("test_case_generation", result)
                self.assertEqual(feedback["unmapped_issue_codes"], [])
                corrections = [e for e in feedback["feedback"] if e["instruction"] is not None]
                self.assertEqual([e["issue"]["check"] for e in corrections], [expected])
                for entry in feedback["feedback"]:
                    if entry["issue"]["classification"] == "missing_information":
                        self.assertIsNone(entry["instruction"])
                        self.assertEqual(entry["evidence"]["status"], "not_verified")

    def test_missing_information_preserved_for_all_task_types(self):
        for task_type, result in (
            ("user_story_refinement", validate_user_story("")),
            ("bug_report_refinement", validate_bug_report("", "")),
            ("test_case_generation", validate_test_case("assert True")),
        ):
            with self.subTest(task_type=task_type):
                feedback = generate_feedback(task_type, result)
                self.assertEqual(len(feedback["feedback"]), len(result["issues"]))
                self.assertTrue(all(e["instruction"] is None for e in feedback["feedback"]))

    def test_empty_and_unmapped_issues(self):
        self.assertEqual(generate_feedback("user_story_refinement", {
            "issues": [], "evidence": [],
        }), {"feedback": [], "unmapped_issue_codes": []})
        # Unknown identifiers are supplied only as a forward-compatibility fixture.
        result = {"issues": [{"criterion": "unknown", "classification": "fixable",
                              "evidence_index": 0}], "evidence": [{"text": "source"}]}
        feedback = generate_feedback("user_story_refinement", result)
        self.assertEqual(feedback["unmapped_issue_codes"], ["unknown"])
        self.assertIsNone(feedback["feedback"][0]["instruction"])

    def test_results_are_independent_copies(self):
        result = validate_user_story("As a reader, I want bookmarks.")
        original = copy.deepcopy(result)
        feedback = generate_feedback("user_story_refinement", result)
        feedback["feedback"][0]["issue"]["message"] = "changed"
        feedback["feedback"][0]["evidence"]["text"] = "changed"
        self.assertEqual(result, original)

    def test_malformed_inputs_and_evidence_links(self):
        with self.assertRaises(ValueError):
            generate_feedback("unknown", {})
        with self.assertRaises(TypeError):
            generate_feedback("user_story_refinement", None)
        for index in (-1, 1, None, True):
            with self.subTest(index=index):
                with self.assertRaisesRegex(ValueError, "evidence_index"):
                    generate_feedback("user_story_refinement", {
                        "issues": [{"criterion": "Minimal", "classification": "fixable",
                                    "evidence_index": index}], "evidence": [{}],
                    })


if __name__ == "__main__":
    unittest.main()
