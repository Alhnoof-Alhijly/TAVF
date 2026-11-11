"""One offline integration test of the complete refinement-to-selection path."""

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from tavf.runner import run_task
from utils.llm_client import LLMClient


class TestRefinementIntegration(unittest.TestCase):
    def test_fixable_story_is_corrected_revalidated_and_selected(self):
        corrected = "As a reader, I want bookmarks, so that I can resume reading."
        initial = "```text\n" + corrected + "\n```"
        provider = Mock()
        provider.responses.create.side_effect = [
            SimpleNamespace(
                id=f"offline-{index}", output_text=output,
                usage=SimpleNamespace(input_tokens=10, output_tokens=10),
            ) for index, output in enumerate((initial, corrected))
        ]
        client = LLMClient(model="offline-model", client=provider)
        result = run_task({
            "task_id": "offline-refinement-integration",
            "task_type": "user_story_refinement",
            "input": {"original_text": corrected},
        }, client=client)

        # 1. Real internal validation detects fixable fence clutter.
        self.assertEqual(len(result["versions"]), 2)
        before, after = result["versions"]
        self.assertFalse(before["validation"]["valid"])
        self.assertEqual(len(before["validation"]["issues"]), 2)
        for issue in before["validation"]["issues"]:
            self.assertEqual(issue["criterion"], "Minimal")
            self.assertEqual(issue["classification"], "fixable")

        # 2. Real feedback provides the fence-specific correction instruction.
        for entry in before["feedback"]["feedback"]:
            self.assertIn("Remove only the reported standalone Markdown fences", entry["instruction"])
            self.assertTrue(entry["evidence"]["text"].startswith("```"))
        self.assertEqual(before["feedback"]["unmapped_issue_codes"], [])

        # 3. Real refinement sends feedback and receives the mocked correction.
        self.assertEqual(provider.responses.create.call_count, 2)
        revision_prompt = provider.responses.create.call_args_list[1].kwargs["input"]
        self.assertIn("Original Input (JSON):", revision_prompt)
        self.assertIn("Previous Output (JSON string):", revision_prompt)
        self.assertIn("Remove only the reported standalone Markdown fences", revision_prompt)
        self.assertEqual(after["generation"]["output"], corrected)
        self.assertEqual(len(result["attempts"]), 1)

        # 4. Real revalidation passes with no outstanding issues.
        self.assertTrue(after["validation"]["valid"])
        self.assertEqual(after["validation"]["issues"], [])
        self.assertEqual(result["stop_reason"], "validation_passed")

        # 5. Real final selection chooses the corrected version and keeps both.
        self.assertEqual(result["selected_attempt"], 1)
        self.assertEqual(result["selection_reason"], "first_passing_version")
        self.assertEqual(result["artifact"], corrected)
        self.assertEqual(before["generation"]["output"], initial)
        self.assertEqual(result["status"], "completed")
        self.assertTrue(result["valid"])


if __name__ == "__main__":
    unittest.main()
