"""Offline tests for Windows replacement failures; no experiment execution."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_experiment as driver


def windows_error(code):
    error = PermissionError("simulated Windows replacement failure")
    error.winerror = code
    return error


class AtomicPersistenceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name)
        self.path = self.directory / "checkpoint.json"
        self.path.write_text('{"old": true}', encoding="utf-8")
        self.replace = driver.os.replace

    def test_windows_access_and_sharing_errors_recover(self):
        for code in (5, 32, 33):
            with self.subTest(winerror=code):
                with patch.object(driver.sys, "platform", "win32"), patch.object(driver.time, "sleep") as sleep:
                    with patch.object(driver.os, "replace", side_effect=[windows_error(code), windows_error(code), None]) as replace:
                        # Delegate the final successful replacement to the real filesystem.
                        def attempt(source, destination):
                            if replace.call_count <= 2:
                                raise windows_error(code)
                            self.replace(source, destination)
                        replace.side_effect = attempt
                        driver._save(self.path, {"new": code})
                self.assertEqual(replace.call_count, 3)
                self.assertEqual(sleep.call_count, 2)
                self.assertEqual(json.loads(self.path.read_text()), {"new": code})
                self.assertEqual(list(self.directory.glob("*.tmp")), [])

    def test_exhaustion_preserves_destination_and_complete_temp(self):
        with patch.object(driver.sys, "platform", "win32"), patch.object(driver.time, "sleep") as sleep:
            with patch.object(driver.os, "replace", side_effect=windows_error(32)) as replace:
                with self.assertRaises(PermissionError):
                    driver._save(self.path, {"response": "durable"})
        self.assertEqual(replace.call_count, 6)
        self.assertEqual(sleep.call_count, 5)
        self.assertLessEqual(sum(call.args[0] for call in sleep.call_args_list), 1.55)
        self.assertEqual(json.loads(self.path.read_text()), {"old": True})
        temps = list(self.directory.glob("*.tmp"))
        self.assertEqual(len(temps), 1)
        self.assertEqual(json.loads(temps[0].read_text()), {"response": "durable"})

    def test_other_errors_and_non_windows_fail_immediately(self):
        cases = [("win32", windows_error(112)), ("win32", PermissionError("no Windows code")),
                 ("linux", windows_error(32))]
        for platform, error in cases:
            with self.subTest(platform=platform, error=error):
                with patch.object(driver.sys, "platform", platform), patch.object(driver.time, "sleep") as sleep:
                    with patch.object(driver.os, "replace", side_effect=error) as replace:
                        with self.assertRaises(OSError):
                            driver._save(self.path, {"new": True})
                self.assertEqual(replace.call_count, 1)
                sleep.assert_not_called()

    def test_write_failure_does_not_retry_replacement(self):
        with patch.object(driver.os, "fsync", side_effect=OSError("disk failure")), patch.object(driver.os, "replace") as replace:
            with self.assertRaises(OSError):
                driver._save(self.path, {"new": True})
        replace.assert_not_called()

    def test_response_save_failure_never_retries_provider(self):
        manifest = {"model": driver.DEFAULT_MODEL, "reasoning_effort": "none", "max_output_tokens": 256}
        response = {"model": manifest["model"], "parameters": {"reasoning_effort": "none", "max_output_tokens": 256},
                    "output": "saved response", "input_tokens": 10, "output_tokens": 4, "cached_input_tokens": 0}
        provider = Mock()
        provider.generate.return_value = response
        journal = driver._JournalClient(provider, self.directory, manifest, {})
        journal.task, journal.method = {"task_id": "offline"}, "baseline"
        attempts = []

        def replace(source, destination):
            value = json.loads(source.read_text())
            if value.get("state") == "usage_unverified":
                attempts.append(source)
                raise windows_error(32)
            self.replace(source, destination)

        with patch.object(driver.sys, "platform", "win32"), patch.object(driver.time, "sleep"), \
                patch.object(driver.os, "replace", side_effect=replace), \
                patch.object(driver, "check_budget", return_value=True), \
                patch.object(driver, "calculate_spent", return_value=driver.calculate_cost(0, 0)):
            with self.assertRaises(PermissionError):
                journal.generate("offline prompt")
        provider.generate.assert_called_once_with("offline prompt")
        self.assertEqual(len(attempts), 6)
        self.assertEqual(len(set(attempts)), 1)
        self.assertEqual(json.loads(attempts[0].read_text())["response"], response)
        active = next((self.directory / "requests").glob("*.json"))
        self.assertEqual(json.loads(active.read_text())["state"], "started")


if __name__ == "__main__":
    unittest.main()
