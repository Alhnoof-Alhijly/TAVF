"""Offline selected-target prompt checks; no dataset code or API is executed."""

import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from tavf.prompting import build_prompt
from tavf.generation import GenerationError
from tavf.runner import run_task


class TestTargetPrompting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks = json.loads((ROOT / "data/processed/test_cases_500.json").read_text(encoding="utf-8"))

    def test_actual_line_branch_and_path_details_and_original_code(self):
        for kind in ("line", "branch", "path"):
            task = copy.deepcopy(next(t for t in self.tasks if t["reference"]["target_type"] == kind))
            original = copy.deepcopy(task)
            task["reference"]["evaluation_secret"] = "EXCLUDED_EVALUATION_METADATA"
            with self.subTest(kind=kind):
                prompt = build_prompt(task["task_type"], task["input"], task_reference=task["reference"])
                self.assertIn("Selected Target Type: " + kind, prompt)
                self.assertIn(json.dumps(task["reference"]["target"], ensure_ascii=False, indent=2), prompt)
                self.assertIn(task["input"]["python_solution"], prompt)
                self.assertIn(task["input"]["description"], prompt)
                self.assertNotIn("EXCLUDED_EVALUATION_METADATA", prompt)
                del task["reference"]["evaluation_secret"]
                self.assertEqual(task, original)

    def test_all_500_targets_render_without_rewriting_source(self):
        for task in self.tasks:
            prompt = build_prompt(task["task_type"], task["input"], task_reference=task["reference"])
            code = prompt.split("Reference Implementation:\n", 1)[1].split("\n\nSelected Target Type:", 1)[0]
            self.assertEqual(code, task["input"]["python_solution"])

    def test_runner_passes_reference_to_prompt_builder_for_each_type(self):
        for kind in ("line", "branch", "path"):
            task = next(t for t in self.tasks if t["reference"]["target_type"] == kind)
            with self.subTest(kind=kind), patch("tavf.runner.generate_initial_output", side_effect=GenerationError):
                result = run_task(task, client=object())
                self.assertEqual(result["stop_reason"], "initial_generation_failed")
                self.assertIn("Selected Target Type: " + kind, result["initial_prompt"])
                self.assertIn(json.dumps(task["reference"]["target"], ensure_ascii=False, indent=2), result["initial_prompt"])

    def test_legacy_reference_adds_no_target_and_other_task_prompts_ignore_it(self):
        task = self.tasks[0]
        default = build_prompt(task["task_type"], task["input"])
        legacy = build_prompt(task["task_type"], task["input"], task_reference={"blocks": "SECRET", "target_lines": "SECRET"})
        self.assertEqual(default, legacy)
        self.assertNotIn("Selected Target", legacy)
        for kind in ("user_story_refinement", "bug_report_refinement"):
            self.assertEqual(build_prompt(kind, {"original_text": "Source"}),
                             build_prompt(kind, {"original_text": "Source"}, task_reference=task["reference"]))

    def test_invalid_or_incomplete_targets_are_rejected(self):
        task = self.tasks[0]
        for reference in ({"target_type": "line"}, {"target": {"line": 1}},
                          {"target_type": "line", "target": {"line": True}},
                          {"target_type": "branch", "target": {"start": 3, "end": 2}},
                          {"target_type": "path", "target": {"execution_path": [], "condition_path": []}}):
            with self.subTest(reference=reference), self.assertRaises(ValueError):
                build_prompt(task["task_type"], task["input"], task_reference=reference)


if __name__ == "__main__":
    unittest.main()
