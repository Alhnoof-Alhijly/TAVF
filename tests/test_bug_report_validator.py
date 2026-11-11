import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from tavf.validators.bug_report import validate_bug_report


REPORT = (
    "Summary: Save crashes.\n"
    "Steps to Reproduce:\n1. Open editor.\n2. Click Save.\n"
    "Expected Result: Document is saved.\n"
    "Actual Result: Application exits."
)


class TestBugReportValidator(unittest.TestCase):
    def test_complete_report_passes(self):
        self.assertEqual(validate_bug_report(REPORT, REPORT), {
            "valid": True, "issues": [], "evidence": [],
        })

    def test_short_prompt_headings_and_markdown_aliases(self):
        for report in (
            "Summary\nSave crashes.\nSteps\nClick Save.\nExpected\nSaved.\nActual\nExits.",
            "## SUMMARY\nSave crashes.\n**Steps to Reproduce:**\nClick Save.\n"
            "**Expected Behavior**: Saved.\n__Actual Behaviour:__ Exits.",
        ):
            with self.subTest(report=report):
                self.assertTrue(validate_bug_report(report, REPORT)["valid"])

    def test_missing_section_with_source_content_is_fixable(self):
        output = REPORT.split("Expected Result:")[0] + "Actual Result: Application exits."
        result = validate_bug_report(output, REPORT)
        self.assertFalse(result["valid"])
        self.assertEqual(len(result["issues"]), 1)
        issue = result["issues"][0]
        self.assertEqual(issue["section"], "Expected Result")
        self.assertEqual(issue["classification"], "fixable")
        evidence = result["evidence"][issue["evidence_index"]]
        self.assertFalse(evidence["output_present"])
        self.assertIn("Document is saved.", evidence["source_text"])
        self.assertTrue(evidence["source_content_available"])

    def test_placeholder_output_uses_original_input_for_classification(self):
        output = REPORT.replace("Document is saved.", "Not provided.")
        for source, classification in ((REPORT, "fixable"), (output, "missing_information")):
            with self.subTest(classification=classification):
                result = validate_bug_report(output, source)
                self.assertEqual(len(result["issues"]), 1)
                self.assertEqual(result["issues"][0]["classification"], classification)

    def test_empty_punctuation_numbering_and_placeholder_content(self):
        for content in ("", "---", "1.\n2.", "N/A", "[Not provided]", "TBD", "...", "1. Not provided."):
            with self.subTest(content=content):
                report = REPORT.replace("Document is saved.", content)
                result = validate_bug_report(report, "")
                self.assertFalse(result["valid"])
                self.assertEqual(result["issues"][0]["section"], "Expected Result")
                self.assertEqual(result["issues"][0]["classification"], "missing_information")

    def test_unlabeled_prose_is_not_interpreted_as_source_details(self):
        result = validate_bug_report("", "Click Save and the application exits.")
        self.assertEqual(len(result["issues"]), 4)
        self.assertTrue(all(i["classification"] == "missing_information" for i in result["issues"]))
        self.assertTrue(all(not e["source_content_available"] for e in result["evidence"]))

    def test_repeated_sections_are_fixable(self):
        result = validate_bug_report(REPORT + "\nSummary: Save crashes.", REPORT)
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["issues"][0]["classification"], "fixable")
        self.assertIn("Repeated", result["issues"][0]["message"])

    def test_other_markdown_section_does_not_fill_empty_section(self):
        report = REPORT.replace("Document is saved.", "\n## Environment\nDesktop editor")
        result = validate_bug_report(report, REPORT)
        self.assertEqual(result["issues"][0]["section"], "Expected Result")

    def test_deterministic_and_no_semantic_claim(self):
        report = REPORT.replace("Document is saved.", "Application exits.")
        self.assertTrue(validate_bug_report(report, REPORT)["valid"])
        self.assertEqual(validate_bug_report("", REPORT), validate_bug_report("", REPORT))

    def test_invalid_input_types(self):
        for artifact, source in ((None, REPORT), (REPORT, {}), (123, "")):
            with self.subTest(artifact=artifact, source=source):
                with self.assertRaisesRegex(TypeError, "must be strings"):
                    validate_bug_report(artifact, source)


if __name__ == "__main__":
    unittest.main()
