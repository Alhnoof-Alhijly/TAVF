"""Offline checks for the local Bug Report Refinement selection."""

import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_bug_reports_500 import OUTPUT, SOURCE, exclusion_reason, load_source, select, validate


class TestBugReports500(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.digest = load_source()
        cls.tasks = json.loads(OUTPUT.read_text(encoding="utf-8"))
        cls.schema = json.loads((ROOT / "data/task_schema.json").read_text(encoding="utf-8"))

    def test_saved_tasks_schema_and_verbatim_source_facts(self):
        validate(self.tasks, self.rows, self.schema)
        self.assertEqual(len(self.tasks), 500)
        for task in self.tasks:
            selection = task["metadata"]["selection"]
            self.assertEqual(selection["source_sha256"], self.digest)
            self.assertEqual(selection["seed"], 42)
            self.assertTrue(selection["criteria"])
            self.assertIn("exclusions", selection)
            self.assertIsNone(task["expected_output"]["gold_reference"])

    def test_deterministic_selection_and_source_unchanged(self):
        tasks, summary = select(self.rows, self.digest)
        self.assertEqual(tasks, self.tasks)
        self.assertEqual(summary["raw_records"], 3158)
        self.assertEqual(summary["selected"], 500)
        self.assertEqual(summary["raw_records"], summary["eligible_unique"] + sum(summary["excluded"].values()))
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), self.digest)

    def test_duplicates_deduplicated_without_mutation(self):
        rows = copy.deepcopy(self.rows)
        duplicate = copy.deepcopy(rows[self.tasks[0]["metadata"]["selection"]["source_row_index"]])
        duplicate["Comment Text"] = "  ".join(duplicate["Comment Text"].upper().split())
        duplicate["Bug ID"] = "duplicate-id"
        rows.append(duplicate)
        before = copy.deepcopy(rows)
        tasks, summary = select(rows, self.digest)
        self.assertEqual(tasks[0]["input"], self.tasks[0]["input"])
        self.assertEqual(summary["excluded"]["duplicate"], 1)
        # Original rows contain NaNs; compare their JSON representations.
        self.assertEqual(json.dumps(rows, sort_keys=True), json.dumps(before, sort_keys=True))

    def test_unusable_records_and_multiline_input(self):
        row = copy.deepcopy(self.rows[self.tasks[0]["metadata"]["selection"]["source_row_index"]])
        for text, reason in ((None, "empty_or_placeholder"), ("N/A", "empty_or_placeholder"),
                             ("short report", "word_count"), ("word " * 251, "word_count"),
                             ("word " * 40 + "\x00", "encoding_or_control")):
            with self.subTest(reason=reason):
                self.assertEqual(exclusion_reason({**row, "Comment Text": text}), reason)
        self.assertIsNone(exclusion_reason({**row, "Comment Text": "word\n" * 40}))
        self.assertEqual(exclusion_reason({**row, "Product": None}), "missing_reference")

    def test_rejects_duplicate_changed_facts_and_small_pool(self):
        duplicate = copy.deepcopy(self.tasks)
        duplicate[1] = copy.deepcopy(duplicate[0])
        with self.assertRaises(ValueError):
            validate(duplicate, self.rows, self.schema)
        altered = copy.deepcopy(self.tasks)
        altered[0]["reference"]["actual_result"] = "invented"
        with self.assertRaises(ValueError):
            validate(altered, self.rows, self.schema)
        with self.assertRaises(ValueError):
            select(self.rows[:10], self.digest)


if __name__ == "__main__":
    unittest.main()
