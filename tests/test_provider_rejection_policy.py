"""Offline rejection-policy checks; no experiment execution or network calls."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scoped_generation import is_invalid_prompt, save_rejection
import resume_authorized_attempt as launcher


def error(status=400, code="invalid_prompt"):
    result = RuntimeError("offline rejection")
    result.status_code, result.code, result.request_id = status, code, "offline-request-id"
    return result


class ProviderRejectionTests(unittest.TestCase):
    def test_only_explicit_rejection_is_classified(self):
        self.assertTrue(is_invalid_prompt(error()))
        nested = error(code=None)
        nested.body = {"error": {"code": "invalid_prompt"}}
        self.assertTrue(is_invalid_prompt(nested))
        for candidate in (error(429), error(500), error(code="other"), ConnectionError(), TimeoutError()):
            self.assertFalse(is_invalid_prompt(candidate))

    def test_rejection_keeps_journal_evidence_and_reserve_without_response(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            path = directory / "requests/logical.json"
            path.parent.mkdir()
            request = {"task_id": "fixture", "method": "baseline", "sequence": 0,
                       "attempt_id": "attempt", "state": "started", "prompt": "unchanged prompt"}
            path.write_text(json.dumps(request))
            original = path.read_bytes()
            def save(target, value):
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(value))
            updated = save_rejection(directory, directory / "session", "logical", "attempt", error(), save)
            self.assertEqual(updated["state"], "provider_rejected")
            self.assertFalse(updated["successful_output"])
            self.assertNotIn("response", updated)
            self.assertEqual(updated["prompt"], request["prompt"])
            self.assertEqual(updated["request_id"], "offline-request-id")
            self.assertGreater(float(updated["reserved_cost_usd"]), 0)
            self.assertEqual((directory / "session/rejections/attempt/request.before.json").read_bytes(), original)
            with self.assertRaises(ValueError):
                save_rejection(directory, directory / "session", "logical", "attempt", error(429), save)

    def test_rejected_method_is_terminal_without_becoming_success(self):
        tasks = [{"task_id": str(i), "task_type": "test_case_generation"} for i in range(500)]
        boundary = launcher.UserStoryBoundary(tasks, [], task_type="test_case_generation")
        boundary.rejected.add(("0", "baseline"))
        for task in tasks:
            for method in ("baseline", "tavf"):
                if (task["task_id"], method) not in boundary.rejected:
                    boundary.saved.add((task["task_id"], method))
        self.assertTrue(boundary.complete)
        self.assertEqual(len(boundary.saved), 999)
        with self.assertRaises(RuntimeError):
            boundary.before_save(launcher.D / "requests/retry.json", {"task_id": "0", "method": "baseline"})
        self.assertIn(("0", "tavf"), boundary.saved)


if __name__ == "__main__":
    unittest.main()
