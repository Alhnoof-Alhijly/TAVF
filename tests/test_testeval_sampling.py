"""Offline sampling checks; dataset programs are parsed, never executed."""

from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_testeval_500 import OUTPUT, QUOTAS, SOURCE, eligible_targets, prepare, validate


class TestTestEvalSampling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = SOURCE.read_bytes()
        cls.digest = hashlib.sha256(raw).hexdigest()
        cls.rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
        cls.bundle = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_saved_selection_quotas_coverage_and_caps(self):
        validate(self.bundle, self.rows)
        items = self.bundle["instances"]
        self.assertEqual(len(items), 500)
        self.assertEqual(Counter(i["target_type"] for i in items), Counter(QUOTAS))
        self.assertEqual(len({i["task_num"] for i in items}), 210)
        self.assertEqual(len({(i["task_num"], i["target_type"]) for i in items}), 500)
        self.assertEqual(self.bundle["metadata"]["source_sha256"], self.digest)
        self.assertEqual(self.bundle["metadata"]["runtime_reachability"], "not_verified")

    def test_seeded_selection_is_reproducible_without_source_mutation(self):
        before = copy.deepcopy(self.rows)
        rebuilt = prepare(self.rows, self.digest)
        # JSON normalizes integer metadata keys to strings.
        self.assertEqual(json.loads(json.dumps(rebuilt)), self.bundle)
        self.assertEqual(self.rows, before)
        for kind, count in QUOTAS.items():
            actual = Counter(str(i["difficulty"]) for i in self.bundle["instances"] if i["target_type"] == kind)
            self.assertEqual(dict(actual), self.bundle["metadata"]["selected_difficulty_counts"][kind])
            self.assertEqual(sum(actual.values()), count)

    def test_validation_rejects_duplicates_and_source_mismatch(self):
        duplicate = copy.deepcopy(self.bundle)
        duplicate["instances"][1] = copy.deepcopy(duplicate["instances"][0])
        with self.assertRaises(ValueError):
            validate(duplicate, self.rows)
        altered = copy.deepcopy(self.bundle)
        altered["instances"][0]["input"]["target"] = {"line": 999999}
        with self.assertRaises(ValueError):
            validate(altered, self.rows)
        altered = copy.deepcopy(self.bundle)
        altered["instances"][0]["input"]["python_solution"] = "pass"
        with self.assertRaises(ValueError):
            validate(altered, self.rows)

    def test_static_exclusions_and_deduplication(self):
        row = {
            "python_solution": "def target(x):\n    if x:\n        return 1\n    else:\n        return 0\n        x = 99\n",
            "target_lines": [2, 3, 3, 4, 6, 999],
            "blocks": [{"start": 2, "end": 3}, {"start": 3, "end": 4}],
            "sampled_paths": [[], ["BRANCH #1: Covered if branch at line 2-3\n"],
                              ["BRANCH #2: Covered if branch at line 999-1000\n"]],
            "sampled_condition_paths": [[], ["Line 2: x"], ["Line 999: x"]],
        }
        pools, rejected = eligible_targets(row)
        self.assertEqual([i["target"]["line"] for i in pools["line"]], [2, 3])
        self.assertEqual(len(pools["branch"]), 1)
        self.assertEqual(len(pools["path"]), 1)
        self.assertEqual(rejected, {"line_duplicate": 1, "line_questionable": 3,
                                    "branch_questionable": 1, "path_empty": 1, "path_questionable": 1})

    def test_syntax_constant_dead_branches_and_unpaired_paths(self):
        row = {"python_solution": "def target():\n    if False:\n        return 1\n    return 0",
               "target_lines": [3, 4], "blocks": [],
               "sampled_paths": [[]], "sampled_condition_paths": []}
        pools, rejected = eligible_targets(row)
        self.assertEqual([i["target"]["line"] for i in pools["line"]], [4])
        self.assertEqual(rejected["path_unpaired"], 1)
        row["python_solution"] = "def broken(:"
        pools, rejected = eligible_targets(row)
        self.assertTrue(all(not pool for pool in pools.values()))
        self.assertEqual(rejected["program_syntax"], 1)


if __name__ == "__main__":
    unittest.main()
