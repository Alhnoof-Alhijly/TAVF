"""Focused offline session lifecycle checks; all mutations use temporary copies."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from contextlib import ExitStack
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results/main_experiment"
sys.path.insert(0, str(ROOT / "scripts"))
import resume_authorized_attempt as launcher


class ResumeLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "experiment"
        shutil.copytree(SOURCE, self.directory, ignore=shutil.ignore_patterns("__pycache__", "resume_sessions"))
        # Each test checks finalization from the original stopped snapshot.
        (self.directory / "authorized_resume/status.json").unlink(missing_ok=True)
        self.patches = [patch.object(launcher, "D", self.directory),
                        patch.object(launcher, "SESSION", self.directory / "authorized_resume"),
                        patch.object(launcher.main.driver, "run_experiment", return_value={"status": "dry_run"}),
                        patch.object(launcher.main.driver, "load_tasks", return_value=[])]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)

    def test_preparation_preserves_all_history_and_reserves(self):
        before = {str(p.relative_to(self.directory)): launcher.sha(p)
                  for p in self.directory.rglob("*.json")}
        with patch.object(launcher.main, "LLMClient", side_effect=AssertionError("No API client")):
            session = launcher.prepare()
        self.assertTrue(all(launcher.sha(self.directory / p) == h for p, h in before.items()))
        plan = launcher.read(session / "plan.json")
        self.assertEqual(plan["historical_reserve_usd"], "0.1507125")
        self.assertNotEqual(plan["prior_attempt_id"], plan["new_attempt_id"])
        self.assertEqual(launcher.read(self.directory / "authorized_resume/status.json")["status"], "stopped")
        self.assertEqual(launcher.validate_session(session), plan)
        with self.assertRaisesRegex(RuntimeError, "Another prepared"):
            launcher.prepare()

    def test_changed_checkpoint_or_reserve_refuses_execution(self):
        session = launcher.prepare()
        summary = launcher.read(self.directory / "run_summary.json")
        summary["reserved_unknown_cost_usd"] = "0"
        launcher.main.SAVE(self.directory / "run_summary.json", summary)
        with self.assertRaisesRegex(RuntimeError, "changed"):
            launcher.validate_session(session)

    def test_sandbox_guard_does_not_touch_checkpoint(self):
        before = launcher.sha(self.directory / "requests" / (launcher.KEY + ".json"))
        with patch.dict(os.environ, {"CODEX_SANDBOX_NETWORK_DISABLED": "1"}):
            with self.assertRaisesRegex(RuntimeError, "outside"):
                launcher.run("a" * 32)
        self.assertEqual(before, launcher.sha(self.directory / "requests" / (launcher.KEY + ".json")))

    def test_stopped_session_cannot_be_reexecuted(self):
        session = launcher.prepare()
        launcher.main.SAVE(session / "status.json", {"status": "stopped"})
        with self.assertRaisesRegex(RuntimeError, "single-use"):
            launcher.validate_session(session)

    def test_execution_handoff_under_lock_without_network(self):
        session = launcher.prepare()
        m = launcher.main

        def fake_client(client):
            client.model = m.driver.DEFAULT_MODEL
            client.reasoning_effort = "none"
            client.max_output_tokens = m.driver.MAX_OUTPUT_TOKENS

        def offline_driver(tasks, directory, **kwargs):
            if not kwargs.get("execute"):
                return {"status": "dry_run"}
            with m.driver._lock(directory):
                self.assertFalse((self.directory / "requests" / (launcher.KEY + ".json")).exists())
                self.assertTrue((session / "retired_active_checkpoint.json").exists())
                self.assertEqual(launcher.read(session / "status.json")["status"], "running")
            return {"status": "completed", "saved": 0, "skipped": 43}

        with ExitStack() as stack:
            # run() installs wrappers; restore every patched global after this test.
            for obj, names in ((m, ("DIRECTORY", "REQUESTS", "RESULTS", "STATUS", "refresh_summary", "observed_save", "ObservedClient")),
                               (m.driver, ("_lock", "_save", "calculate_spent", "BUDGET", "SAFETY_LIMIT")),
                               (m.cost_tracker, ("calculate_spent", "BUDGET", "SAFETY_LIMIT"))):
                for name in names:
                    stack.enter_context(patch.object(obj, name, getattr(obj, name)))
            m.DIRECTORY, m.REQUESTS, m.RESULTS = self.directory, {}, {}
            stack.enter_context(patch.object(m.driver, "run_experiment", side_effect=offline_driver))
            stack.enter_context(patch.object(m.driver, "load_tasks", return_value=[{}] * 1500))
            stack.enter_context(patch.object(launcher.paced.PacedClient, "__init__", fake_client))
            stack.enter_context(patch.dict(os.environ, {"CODEX_SANDBOX_NETWORK_DISABLED": "0"}))
            launcher.run(session.name)
        self.assertEqual(launcher.read(session / "status.json")["status"], "stopped")
        summary = launcher.read(self.directory / "run_summary.json")
        self.assertEqual(summary["reserved_unknown_cost_usd"], "0.1507125")
        self.assertEqual(summary["final_outputs_saved"], 43)


if __name__ == "__main__":
    unittest.main()
