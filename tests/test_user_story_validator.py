import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from tavf.validators.user_story import validate_user_story


STORY = "As a reader, I want bookmarks, so that I can resume reading."


class TestUserStoryValidator(unittest.TestCase):
    def test_well_formed_story(self):
        self.assertEqual(validate_user_story(STORY), {
            "valid": True, "issues": [], "evidence": [],
        })

    def test_multiple_numbered_bulleted_and_wrapped_stories(self):
        artifact = (
            "1. " + STORY + "\n\n"
            "- As an editor, I want drafts,\nso that I can revise articles."
        )
        self.assertTrue(validate_user_story(artifact)["valid"])

    def test_missing_information_and_placeholders(self):
        for artifact in (
            "", "   ", "I want bookmarks.",
            "As a reader, I want bookmarks.",
            "As a Not provided, I want bookmarks, so that I can resume.",
            "As a reader, I want , so that I can resume.",
            "As a reader, I want bookmarks, so that Not provided.",
            "As a [role], I want [goal], so that [benefit].",
        ):
            with self.subTest(artifact=artifact):
                result = validate_user_story(artifact)
                self.assertFalse(result["valid"])
                self.assertTrue(all(
                    issue["classification"] == "missing_information"
                    for issue in result["issues"]
                ))

    def test_repeated_request_clauses_have_atomic_evidence(self):
        artifact = "As a reader, I want bookmarks and I want alerts, so that I stay informed."
        result = validate_user_story(artifact)
        issue = next(i for i in result["issues"] if i["criterion"] == "Atomic")
        self.assertEqual(issue["classification"], "fixable")
        self.assertEqual(result["evidence"][issue["evidence_index"]], {
            "story": 1, "text": artifact,
        })

    def test_conjunctions_do_not_imply_multiple_requirements(self):
        self.assertTrue(validate_user_story(
            "As a reader, I want black and white display, so that I can read comfortably."
        )["valid"])

    def test_duplicate_story_is_minimal_issue_with_correct_story_number(self):
        result = validate_user_story(STORY + "\n" + STORY)
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["issues"][0]["criterion"], "Minimal")
        self.assertEqual(result["issues"][0]["classification"], "fixable")
        self.assertEqual(result["issues"][0]["story"], 2)

    def test_markdown_fences_are_surface_clutter(self):
        result = validate_user_story("```text\n" + STORY + "\n```")
        self.assertFalse(result["valid"])
        self.assertEqual(len(result["issues"]), 2)
        self.assertTrue(all(i["criterion"] == "Minimal" for i in result["issues"]))

    def test_deterministic_and_no_artifact_rewriting(self):
        artifact = STORY + "\nAs a reader, I want alerts."
        result = validate_user_story(artifact)
        self.assertEqual(result, validate_user_story(artifact))
        self.assertEqual(result["issues"][0]["story"], 2)
        self.assertEqual(set(result), {"valid", "issues", "evidence"})

    def test_non_string_is_rejected(self):
        with self.assertRaisesRegex(TypeError, "must be a string"):
            validate_user_story(None)


if __name__ == "__main__":
    unittest.main()
