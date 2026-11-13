"""Adapter tests with fake Docker/evaluators only; never execute test source."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evaluation"))
import evaluate_testeval_blinded as adapter


def row(kind="line"):
    return {"artifact_id": "opaque-id", "pair_id": "opaque-pair", "artifact": "assert target(1) == 1",
            "task": {"task_id": "task", "task_type": "test_case_generation",
                     "input": {"python_solution": "def target(x):\n    return x\n"},
                     "reference": {"task_num": 1, "target_type": kind, "target": {"line": 2}}, "metadata": {"original": True}}}


class TestEvalAdapterTests(unittest.TestCase):
    def test_dry_run_never_constructs_docker_or_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest, output = Path(temp) / "manifest.jsonl", Path(temp) / "metrics"
            manifest.write_text(json.dumps(row()) + "\n")
            with patch.object(adapter.subprocess, "check_output", side_effect=AssertionError("No Docker")):
                result = adapter.run(manifest, output, expected_count=1)
            self.assertEqual(result["docker_runs"], 0)
            self.assertFalse(output.exists())

    def test_fresh_syntax_and_all_target_dispatch_preserve_metadata(self):
        for kind in ("line", "branch", "path"):
            artifact = row(kind)
            before = deepcopy(artifact)
            evaluator = Mock(return_value={"status": "covered", "evidence": {"image": "python:3.12-slim"}})
            with patch.object(adapter.execution, "validate_execution", return_value={"status": "passed", "image": "python:3.12-slim"}), \
                    patch.dict(adapter.COVERAGE, {kind: evaluator}):
                result = adapter.evaluate_one(artifact, adapter.VERIFIED_IMAGE)
            self.assertEqual(result["metrics"]["Syntax"]["status"], "passed")
            self.assertEqual(result["metrics"]["Assertion Correctness"]["status"], "not_verified")
            self.assertEqual(result["metrics"]["Target Coverage"]["evidence"]["image"], adapter.VERIFIED_IMAGE)
            evaluator.assert_called_once_with(artifact["artifact"], artifact["task"])
            self.assertEqual(artifact, before)
            self.assertEqual(result["task"], before["task"])

    def test_invalid_syntax_never_executes(self):
        artifact = row()
        artifact["artifact"] = "def broken(:"
        with patch.object(adapter.execution, "validate_execution", side_effect=AssertionError("No Docker")):
            result = adapter.evaluate_one(artifact, adapter.VERIFIED_IMAGE)
        self.assertEqual(result["metrics"]["Syntax"]["status"], "failed")
        self.assertEqual(result["metrics"]["Target Coverage"]["status"], "not_verified")

    def test_image_substitution_changes_no_other_flags_or_payload(self):
        command = ["docker", "run", "--rm", "--pull=never", "--network", "none", "--read-only",
                   "--cpus", "0.5", "--memory", "128m", "--pids-limit", "16", "python:3.12-slim", "python", "-I", "-B", "-c", "trusted harness"]
        expected = [adapter.VERIFIED_IMAGE if part == "python:3.12-slim" else part for part in command]
        with patch.object(adapter.subprocess, "run", return_value=Mock(returncode=0)) as run, \
                patch.object(adapter.subprocess, "Popen", return_value=Mock()) as popen:
            with adapter.selected_image(adapter.VERIFIED_IMAGE, []):
                adapter.execution.subprocess.run(command, input="unchanged payload", timeout=10)
                adapter.line_coverage.subprocess.Popen(command, stdin=-1)
        self.assertEqual(run.call_args.args[0], expected)
        self.assertEqual(run.call_args.kwargs, {"input": "unchanged payload", "timeout": 10})
        self.assertEqual(popen.call_args.args[0], expected)

    def test_resume_skips_saved_scores_and_refuses_incomplete_or_changed_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest, output = Path(temp) / "manifest.jsonl", Path(temp) / "metrics"
            artifact = row()
            manifest.write_text(json.dumps(artifact) + "\n")
            saved = {"artifact_id": artifact["artifact_id"], "pair_id": artifact["pair_id"], "task": artifact["task"],
                     "artifact_sha256": adapter.digest(artifact["artifact"].encode()), "metrics": {}, "infrastructure_stop": False}
            info = json.dumps([{"Os": "linux", "Config": {"User": "65534:65534"}}])
            with patch.object(adapter.subprocess, "check_output", return_value=info), patch.object(adapter, "evaluate_one", return_value=saved) as evaluate:
                first = adapter.run(manifest, output, execute=True, expected_count=1)
                second = adapter.run(manifest, output, execute=True, expected_count=1)
            self.assertEqual(first["saved_this_run"], 1)
            self.assertEqual(second["skipped_this_run"], 1)
            evaluate.assert_called_once()
            # Crash with only a started checkpoint must never trigger another run.
            (output / "scores/opaque-id.json").unlink()
            with patch.object(adapter.subprocess, "check_output", return_value=info), patch.object(adapter, "evaluate_one", side_effect=AssertionError("No rerun")):
                with self.assertRaisesRegex(ValueError, "Interrupted"):
                    adapter.run(manifest, output, execute=True, expected_count=1)
            artifact["artifact"] += "\n# changed"
            manifest.write_text(json.dumps(artifact) + "\n")
            with self.assertRaisesRegex(ValueError, "settings"):
                adapter.run(manifest, output, expected_count=1)


if __name__ == "__main__":
    unittest.main()
