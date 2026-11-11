"""Offline conversion checks; no generation, Docker or source execution."""

import ast
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from export_testeval_500_tasks import OUTPUT, PROGRAMS, SELECTION, convert
from tavf.task_identifier import identify_task


class TestTestEval500Tasks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = SELECTION.read_bytes()
        cls.digest = hashlib.sha256(raw).hexdigest()
        cls.selection = json.loads(raw)
        cls.programs = [json.loads(line) for line in PROGRAMS.read_text(encoding="utf-8").splitlines() if line.strip()]
        cls.tasks = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_schema_routing_and_prompt_inputs(self):
        validator = Draft202012Validator(json.loads((ROOT / "data/task_schema.json").read_text(encoding="utf-8")))
        self.assertEqual(len(self.tasks), 500)
        self.assertEqual(len({task["task_id"] for task in self.tasks}), 500)
        for task in self.tasks:
            validator.validate(task)
            self.assertEqual(identify_task(task), "test_case_generation")
            self.assertEqual(set(task["input"]), {"description", "python_solution"})
            self.assertTrue(all(value.strip() for value in task["input"].values()))

    def test_ids_targets_code_and_selection_metadata_preserved(self):
        indexed = {row["task_num"]: row for row in self.programs}
        for original, task in zip(self.selection["instances"], self.tasks):
            self.assertEqual(task["task_id"], original["instance_id"])
            self.assertEqual(task["input"]["python_solution"], original["input"]["python_solution"])
            self.assertEqual(task["input"]["description"], original["input"]["description"])
            for key in ("target_type", "source_target_index", "task_num"):
                self.assertEqual(task["reference"][key], original[key])
            self.assertEqual(task["reference"]["target"], original["input"]["target"])
            self.assertEqual(task["metadata"]["selection"], self.selection["metadata"])
            self.assertEqual(task["metadata"]["selection_sha256"], self.digest)
            row = indexed[original["task_num"]]
            for key in ("blocks", "target_lines"):
                self.assertEqual(ast.literal_eval(task["reference"][key]), row[key])
        self.assertEqual(Counter(t["reference"]["target_type"] for t in self.tasks),
                         {"line": 167, "branch": 167, "path": 166})
        self.assertEqual(len({t["reference"]["task_num"] for t in self.tasks}), 210)

    def test_deterministic_conversion_does_not_mutate_sources(self):
        before_selection, before_programs = copy.deepcopy(self.selection), copy.deepcopy(self.programs)
        self.assertEqual(convert(self.selection, self.programs, self.digest), self.tasks)
        self.assertEqual(self.selection, before_selection)
        self.assertEqual(self.programs, before_programs)
        self.assertEqual(hashlib.sha256(SELECTION.read_bytes()).hexdigest(), self.digest)

    def test_rejects_duplicate_ids_and_altered_target_or_program(self):
        for modification in ("id", "target", "code"):
            selection = copy.deepcopy(self.selection)
            if modification == "id":
                selection["instances"][1]["instance_id"] = selection["instances"][0]["instance_id"]
            elif modification == "target":
                selection["instances"][0]["input"]["target"] = {"line": 999999}
            else:
                selection["instances"][0]["input"]["python_solution"] = "pass"
            with self.subTest(modification=modification), self.assertRaises(ValueError):
                convert(selection, self.programs, self.digest)


if __name__ == "__main__":
    unittest.main()
