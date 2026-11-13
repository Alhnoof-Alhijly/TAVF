"""Offline import/path checks; no client construction or experiment execution."""
import hashlib
import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from experiment_paths import launcher_sha256


class ResumeRelocationTests(unittest.TestCase):
    def test_all_moved_modules_import_without_network_and_keep_runtime_paths(self):
        with patch("socket.socket.connect", side_effect=AssertionError("No network")):
            modules = {name: importlib.import_module(name) for name in (
                "main_run", "resume_build", "resume_updated_build", "resume_authorized_attempt",
                "retry_one", "connection_diagnostics")}
        for module in modules.values():
            self.assertEqual(Path(module.__file__).resolve().parent, ROOT / "scripts")
        runtime = ROOT / "results/main_experiment"
        self.assertEqual(modules["main_run"].ROOT, ROOT)
        for name in ("main_run", "resume_build", "resume_updated_build"):
            self.assertEqual(modules[name].DIRECTORY, runtime)
        for name in ("resume_authorized_attempt", "retry_one"):
            self.assertEqual(modules[name].D, runtime)

    def fingerprint_fixture(self, line_ending):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        source = root / "scripts/main_run.py"
        source.parent.mkdir()
        old = ('ROOT = Path(__file__).resolve().parents[2]\n'
               'DIRECTORY = Path(__file__).resolve().parent\n'
               'config = {"launcher_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}\n')
        new = ('from experiment_paths import launcher_sha256\n'
               'ROOT = Path(__file__).resolve().parents[1]\n'
               'DIRECTORY = ROOT / "results" / "main_experiment"\n'
               'config = {"launcher_sha256": launcher_sha256(Path(__file__))}\n')
        expected = hashlib.sha256(old.replace("\n", line_ending).encode()).hexdigest()
        source.write_bytes(new.encode())
        config = root / "results/main_experiment/run_config.json"
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps({"launcher_sha256": expected}))
        return source, config, expected

    def test_legacy_fingerprint_survives_relocation_and_line_endings(self):
        for newline in ("\n", "\r\n"):
            with self.subTest(newline=repr(newline)):
                source, config, expected = self.fingerprint_fixture(newline)
                before = config.read_bytes()
                self.assertEqual(launcher_sha256(source), expected)
                self.assertEqual(config.read_bytes(), before)

    def test_other_source_changes_do_not_inherit_legacy_fingerprint(self):
        source, _, expected = self.fingerprint_fixture("\r\n")
        source.write_bytes(source.read_bytes() + b'CAP = "changed"\n')
        self.assertNotEqual(launcher_sha256(source), expected)

    def test_new_runs_use_current_source_fingerprint(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "scripts/main_run.py"
            source.parent.mkdir()
            source.write_bytes(b"# new launcher\n")
            self.assertEqual(launcher_sha256(source), hashlib.sha256(source.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
