import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from tavf.task_identifier import identify_task


class TestTaskIdentifier(unittest.TestCase):
    def test_accepts_exact_schema_task_types(self):
        schema = json.loads(
            (ROOT / "data/task_schema.json").read_text(encoding="utf-8")
        )
        for task_type in schema["properties"]["task_type"]["enum"]:
            with self.subTest(task_type=task_type):
                self.assertEqual(identify_task({"task_type": task_type}), task_type)

    def test_missing_type_is_not_inferred_from_content(self):
        with self.assertRaisesRegex(ValueError, "Missing required field: task_type"):
            identify_task({"input": {"original_text": "As a user, I want tests."}})

    def test_rejects_unsupported_and_malformed_types(self):
        for task_type in (
            "unsupported", "User_Story_Refinement", "user_story_refinement ",
            "", None, 1, [], {},
        ):
            with self.subTest(task_type=task_type):
                with self.assertRaisesRegex(ValueError, "Unsupported task_type"):
                    identify_task({"task_type": task_type})

    def test_supplied_type_takes_precedence_and_input_is_unchanged(self):
        task = {
            "task_type": "bug_report_refinement",
            "input": {"description": "Generate unit tests"},
        }
        original = json.loads(json.dumps(task))
        self.assertEqual(identify_task(task), "bug_report_refinement")
        self.assertEqual(task, original)

    def test_rejects_non_mapping_tasks(self):
        for task in (None, [], "user_story_refinement"):
            with self.subTest(task=task):
                with self.assertRaisesRegex(TypeError, "Task must be a mapping"):
                    identify_task(task)


if __name__ == "__main__":
    unittest.main()
