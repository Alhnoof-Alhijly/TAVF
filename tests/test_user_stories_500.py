"""Offline validation of prepared user-story inputs and source preservation."""

import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_user_stories_500 import OUTPUT, SOURCE, exclusion_reason, load_source, select, validate


class TestUserStories500(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.digest = load_source()
        cls.tasks = json.loads(OUTPUT.read_text(encoding="utf-8"))
        cls.schema = json.loads((ROOT / "data/task_schema.json").read_text(encoding="utf-8"))

    def test_saved_tasks_schema_uniqueness_and_source_fidelity(self):
        validate(self.tasks, self.rows, self.schema)
        self.assertEqual(len(self.tasks), 500)
        self.assertEqual(len({task["reference"]["original_source_file"] for task in self.tasks}), 22)
        for task in self.tasks:
            selection = task["metadata"]["selection"]
            self.assertEqual(selection["seed"], 42)
            self.assertEqual(selection["source_sha256"], self.digest)
            self.assertTrue(selection["criteria"])
            self.assertIsNone(task["expected_output"]["gold_reference"])

    def test_reproducible_without_mutation(self):
        before = copy.deepcopy(self.rows)
        tasks, summary = select(self.rows, self.digest)
        self.assertEqual(tasks, self.tasks)
        self.assertEqual(self.rows, before)
        self.assertEqual(summary["raw_records"], 1680)
        self.assertEqual(summary["selected"], 500)
        self.assertEqual(summary["raw_records"], summary["eligible_unique"] + sum(summary["excluded"].values()))
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), self.digest)

    def test_unusable_records_and_incomplete_benefit(self):
        for text, reason in (("", "empty"), ("As a user", "word_count"),
                             ("As a user " + "word " * 40, "word_count"),
                             ("As a user, I want to save my bookmarks.\x00", "encoding_or_control"),
                             ("ï»¿As a user, I want to save my bookmarks.", "encoding_or_control"),
                             ("This is a continuation fragment with enough words to pass length filtering.", "non_story_fragment")):
            with self.subTest(reason=reason, text=text):
                self.assertEqual(exclusion_reason(text), reason)
        self.assertIsNone(exclusion_reason("As a user, I want to save all of my bookmarks."))

    def test_normalized_duplicates_excluded_without_rewriting(self):
        rows = copy.deepcopy(self.rows)
        original = self.tasks[0]["input"]["original_text"]
        duplicate = {"source_file": "duplicate.txt", "line_number": "1",
                     "original_story": "  ".join(original.upper().split())}
        _, before = select(rows, self.digest)
        rows.append(duplicate)
        tasks, after = select(rows, self.digest)
        self.assertEqual(tasks, self.tasks)
        self.assertEqual(after["excluded"]["duplicate"], before["excluded"]["duplicate"] + 1)

    def test_rejects_duplicate_altered_and_insufficient_inputs(self):
        duplicate = copy.deepcopy(self.tasks)
        duplicate[1] = copy.deepcopy(duplicate[0])
        with self.assertRaises(ValueError):
            validate(duplicate, self.rows, self.schema)
        altered = copy.deepcopy(self.tasks)
        altered[0]["input"]["original_text"] += " changed"
        with self.assertRaises(ValueError):
            validate(altered, self.rows, self.schema)
        with self.assertRaises(ValueError):
            select(self.rows[:10], self.digest)


if __name__ == "__main__":
    unittest.main()
