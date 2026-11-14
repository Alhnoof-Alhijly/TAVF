"""Small synthetic checks; no ratings, model calls, or execution."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evaluation"))
from prepare_human_evaluation_samples import assemble, KINDS


class HumanSampleTests(unittest.TestCase):
    def fixture(self):
        artifacts, mapping = [], []
        for kind in KINDS:
            for i in range(4):
                for method in ("baseline", "tavf"):
                    ident, task = f"{kind}-{i}-{method}", {"task_id": f"{kind}-{i}", "task_type": kind, "input": {"original_text": f"source {i}"}}
                    artifacts.append({"artifact_id": ident, "pair_id": task["task_id"], "task": task,
                                      "artifact": f"exact output {i} {method}", "validation_status": "must not leak"})
                    mapping.append({"artifact_id": ident, "pair_id": task["task_id"], "task_id": task["task_id"], "task_type": kind, "method": method})
        return artifacts, mapping

    def test_reproducible_pairs_exact_text_and_blinded_fields(self):
        artifacts, mapping = self.fixture()
        original = deepcopy((artifacts, mapping))
        packet, private, info = assemble(artifacts, mapping, seed=42, per_type=2)
        self.assertEqual((packet, private, info), assemble(list(reversed(artifacts)), list(reversed(mapping)), seed=42, per_type=2))
        self.assertEqual(info["selected_pairs"], {kind: 2 for kind in KINDS})
        lookup = {r["artifact_id"]: r for r in artifacts}
        key = {r["sample_id"]: r for r in private}
        for row in packet:
            self.assertEqual(set(row), {"sample_id", "presentation_index", "task_type", "source_input", "outputs"})
            self.assertEqual({r["method"] for r in key[row["sample_id"]]["outputs"].values()}, {"baseline", "tavf"})
            for label, text in row["outputs"].items():
                self.assertEqual(text, lookup[key[row["sample_id"]]["outputs"][label]["artifact_id"]]["artifact"])
        self.assertEqual((artifacts, mapping), original)

    def test_incomplete_pair_excluded_and_conflicting_mapping_refused(self):
        artifacts, mapping = self.fixture()
        packet, _, info = assemble(artifacts[:-1], mapping, per_type=2)
        self.assertEqual(info["eligible_complete_pairs"][KINDS[1]], 3)
        mapping[0]["method"] = "tavf"
        with self.assertRaises(ValueError):
            assemble(artifacts, mapping, per_type=2)


if __name__ == "__main__":
    unittest.main()
