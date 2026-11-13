"""One offline image/configuration check; never invoke Docker."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TestEvalDockerConfigTests(unittest.TestCase):
    def test_pinned_image_dependency_and_existing_isolation_contract(self):
        directory = ROOT / "evaluation/docker/testeval"
        dockerfile = (directory / "Dockerfile").read_text()
        requirements = (directory / "requirements.txt").read_text()
        doc = (directory / "README.md").read_text()
        self.assertIn("ARG PYTHON_BASE=python:3.12-slim", dockerfile)
        self.assertIn("FROM ${PYTHON_BASE}", dockerfile)
        self.assertIn("USER 65534:65534", dockerfile)
        for flag in ("--no-deps", "--only-binary=:all:", "--require-hashes", "--no-cache-dir"):
            self.assertIn(flag, dockerfile)
        dependencies = [line for line in requirements.splitlines() if line and not line.startswith("#")]
        self.assertEqual(dependencies, ["sortedcontainers==2.4.0 --hash=sha256:a163dcaede0f1c021485e957a39245190e74249897e2ae4b2aa38595db237ee0"])
        self.assertEqual(re.findall(r"^COPY (.+)$", dockerfile, re.M), ["requirements.txt /opt/testeval/requirements.txt"])
        self.assertNotIn("ENTRYPOINT", dockerfile)
        self.assertIn("docker build --tag tavf-testeval:py312-sortedcontainers-2.4.0", doc)
        self.assertIn("<recorded-base-digest>", doc)
        for name in ("src/tavf/validators/execution.py", "src/tavf/evaluation/line_coverage.py"):
            source = (ROOT / name).read_text()
            for fragment in ('"--network", "none"', '"--read-only"', '"--cap-drop", "ALL"',
                             '"--security-opt", "no-new-privileges"', '"--cpus", "0.5"',
                             '"--memory", "128m"', '"--memory-swap", "128m"',
                             '"--pids-limit", "16"', '"--user", "65534:65534"', '"--pull=never"'):
                self.assertIn(fragment, source)


if __name__ == "__main__":
    unittest.main()
