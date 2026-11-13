"""Small synthetic offline tests for evaluation blinding and linkage."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from prepare_final_evaluation_manifest import prepare_records


class BlindedManifestTests(unittest.TestCase):
    def fixtures(self):
        tasks = [{"task_id": str(i), "task_type": "test_case_generation", "input": {"python_solution": "source"},
                  "reference": {"target_type": "line", "target": {"line": i + 1}}, "metadata": {"original": True}}
                 for i in range(2)]
        records = []
        for task in tasks:
            for method in ("baseline", "tavf"):
                if task["task_id"] == "1" and method == "baseline":
                    continue
                result = {"task_id": task["task_id"], "task_type": task["task_type"], "method": method}
                result.update({"output": "exact artifact"} if method == "baseline"
                              else {"task": deepcopy(task), "artifact": "exact artifact"})
                records.append(("private/original.json", "source-hash", {"task": deepcopy(task), "method": method, "result": result}))
        rejection = {"task_id": "1", "method": "baseline", "state": "provider_rejected", "http_status": 400,
                     "provider_code": "invalid_prompt", "request_id": "evidence-id"}
        return tasks, records, [("private/request.json", "rejection-hash", rejection)]

    def test_blinding_pairing_metadata_and_missing_artifact(self):
        tasks, records, rejected = self.fixtures()
        before = deepcopy((tasks, records, rejected))
        artifacts, pairs, mapping, rejections, summary = prepare_records(tasks, records, rejected)
        self.assertEqual(summary["artifacts"], 3)
        self.assertEqual(summary["complete_pairs"], 1)
        self.assertEqual(summary["incomplete_pairs"], 1)
        self.assertEqual(summary["provider_rejections"], 1)
        self.assertEqual(len({a["artifact_id"] for a in artifacts}), 3)
        for artifact in artifacts:
            self.assertEqual(set(artifact), {"artifact_id", "pair_id", "task", "artifact"})
            self.assertEqual(artifact["task"], tasks[int(artifact["task"]["task_id"])])
        self.assertEqual({a["artifact_id"] for a in artifacts}, {m["artifact_id"] for m in mapping})
        self.assertFalse(rejections[0]["successful_output"])
        self.assertEqual((tasks, records, rejected), before)

    def test_duplicates_metadata_changes_and_unexplained_missing_output_refused(self):
        tasks, records, rejected = self.fixtures()
        with self.assertRaises(ValueError):
            prepare_records(tasks, records + [records[0]], rejected)
        changed = deepcopy(records)
        changed[0][2]["task"]["reference"]["target"]["line"] = 999
        with self.assertRaises(ValueError):
            prepare_records(tasks, changed, rejected)
        with self.assertRaises(ValueError):
            prepare_records(tasks, records, [])


if __name__ == "__main__":
    unittest.main()
