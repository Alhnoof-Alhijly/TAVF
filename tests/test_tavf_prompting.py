import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from tavf.prompting import PROMPT_TEMPLATE_REGISTRY, build_prompt


class TestTAVFPrompting(unittest.TestCase):
    def test_registry_matches_schema(self):
        schema = json.loads(
            (ROOT / "data/task_schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            set(PROMPT_TEMPLATE_REGISTRY),
            set(schema["properties"]["task_type"]["enum"]),
        )

    def test_task_templates_and_required_sections(self):
        cases = (
            ("user_story_refinement", {"original_text": "As a reader, I want bookmarks."},
             "As a [role], I want [goal], so that [benefit]."),
            ("bug_report_refinement", {"original_text": "Save crashes on version 2."},
             "Summary\nSteps\nExpected\nActual"),
            ("test_case_generation", {
                "description": "Return the provided mapping.",
                "python_solution": "def identity(x): return {'value': x}",
            }, "unittest"),
        )
        for task_type, task_input, expected in cases:
            with self.subTest(task_type=task_type):
                original = task_input.copy()
                prompt = build_prompt(task_type, task_input)
                for heading in ("Role:", "Task Instruction:", "Context:", "Output Format:"):
                    self.assertIn(heading, prompt)
                for value in task_input.values():
                    self.assertIn(value, prompt)
                self.assertIn(expected, prompt)
                self.assertIn("Do not invent", prompt)
                self.assertEqual(task_input, original)

    def test_evaluation_fields_are_excluded(self):
        prompt = build_prompt("test_case_generation", {
            "description": "Return x.",
            "python_solution": "def identity(x): return x",
            "target_lines": "SECRET_TARGET",
            "blocks": "SECRET_BLOCKS",
            "reference": "SECRET_REFERENCE",
        })
        for value in ("SECRET_TARGET", "SECRET_BLOCKS", "SECRET_REFERENCE"):
            self.assertNotIn(value, prompt)

    def test_missing_or_invalid_input_fields(self):
        for task_type, (_, fields) in PROMPT_TEMPLATE_REGISTRY.items():
            for field in fields:
                valid = dict.fromkeys(fields, "source context")
                with self.subTest(task_type=task_type, field=field):
                    missing = valid.copy()
                    del missing[field]
                    with self.assertRaisesRegex(ValueError, f"Missing required input field: {field}"):
                        build_prompt(task_type, missing)
                    for value in (None, 1, "", "   "):
                        with self.assertRaisesRegex(ValueError, "non-empty string"):
                            build_prompt(task_type, {**valid, field: value})

    def test_invalid_task_type_and_input_container(self):
        for task_type in ("unknown", "User_Story_Refinement", None, []):
            with self.subTest(task_type=task_type):
                with self.assertRaisesRegex(ValueError, "Unsupported task_type"):
                    build_prompt(task_type, {})
        with self.assertRaisesRegex(TypeError, "must be a mapping"):
            build_prompt("user_story_refinement", None)


if __name__ == "__main__":
    unittest.main()
