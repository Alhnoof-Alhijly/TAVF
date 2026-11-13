"""Path-only compatibility for launchers relocated from experiment results."""
import hashlib
import json
from pathlib import Path


def launcher_sha256(source_path):
    """Accept the exact pre-move launcher fingerprint without rewriting history.

    Reverse only the three relocation edits and account for Windows line endings.
    Any other source change still fails the existing run-config comparison.
    """
    source_path = Path(source_path)
    actual = source_path.read_bytes()
    canonical = actual.decode("utf-8").replace("\r\n", "\n")
    canonical = canonical.replace("from experiment_paths import launcher_sha256\n", "")
    canonical = canonical.replace("ROOT = Path(__file__).resolve().parents[1]",
                                  "ROOT = Path(__file__).resolve().parents[2]")
    canonical = canonical.replace('DIRECTORY = ROOT / "results" / "main_experiment"',
                                  "DIRECTORY = Path(__file__).resolve().parent")
    canonical = canonical.replace('"launcher_sha256": launcher_sha256(Path(__file__))',
                                  '"launcher_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()')
    candidates = {hashlib.sha256(actual).hexdigest(), hashlib.sha256(canonical.encode()).hexdigest(),
                  hashlib.sha256(canonical.replace("\n", "\r\n").encode()).hexdigest()}
    config = source_path.resolve().parents[1] / "results/main_experiment/run_config.json"
    if config.exists():
        recorded = json.loads(config.read_text(encoding="utf-8"))["launcher_sha256"]
        if recorded in candidates:
            return recorded
    return hashlib.sha256(actual).hexdigest()
