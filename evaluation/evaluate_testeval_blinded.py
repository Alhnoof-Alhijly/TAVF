"""Resumable opt-in TestEval evaluation; never reads private method labels."""
import argparse
from contextlib import contextmanager, ExitStack
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
from run_experiment import _lock, _save
from tavf.validators.test_case import validate_test_case
from tavf.validators import execution
from tavf.evaluation import line_coverage, branch_coverage, path_coverage
from testeval_diagnostics import capture
from testeval_module_harness import VERSION as HARNESS_VERSION, ALIASES, build_harnesses

VERIFIED_IMAGE = "sha256:acd3865aef3c1877be238341570499fb39ff2c72a2877a4b75649a9b9a00c1df"
VERSION = "testeval_final_adapter_v2"
COVERAGE = {"line": line_coverage.evaluate_line_target,
            "branch": branch_coverage.evaluate_branch_target, "path": path_coverage.evaluate_path_target}


def digest(value):
    return hashlib.sha256(value).hexdigest()


def load_manifest(path, expected_count=999):
    original = path.read_bytes()
    rows = [json.loads(line) for line in original.decode("utf-8").splitlines()]
    rows = [r for r in rows if r["task"]["task_type"] == "test_case_generation"]
    if len(rows) != expected_count or len({r["artifact_id"] for r in rows}) != expected_count:
        raise ValueError("Unexpected or duplicate TestEval artifact IDs")
    identities = set()
    for row in rows:
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", row["artifact_id"]):
            raise ValueError("Unsafe artifact ID")
        if not isinstance(row["artifact"], str) or not row["artifact"].strip():
            raise ValueError("Empty artifact")
        task = row["task"]
        if task["reference"]["target_type"] not in COVERAGE or not task["reference"]["target"]:
            raise ValueError("Missing selected target")
        if not task["input"]["python_solution"].strip():
            raise ValueError("Missing reference source")
        key = (row["pair_id"], row["artifact_id"])
        if key in identities:
            raise ValueError("Duplicate anonymous identity")
        identities.add(key)
    return rows, digest(original)


@contextmanager
def selected_image(image, commands, diagnostics=None):
    """Change only the Docker run image; preserve existing evaluator transports.

    Module-local subprocess proxies avoid altering the process-wide subprocess
    module. Shared line transport also serves branch and path evaluation.
    """
    def command(args):
        args = list(args)
        if args[:2] == ["docker", "run"]:
            if args.count("python:3.12-slim") != 1:
                raise ValueError("Unexpected evaluator Docker command")
            index = args.index("python:3.12-slim")
            args[index] = image
            commands.append(args[:index + 1] + ["python", "-I", "-B", "-c", "<existing trusted harness>"])
        return args

    class Proxy:
        def __getattr__(self, name):
            return getattr(subprocess, name)

        def run(self, args, **kwargs):
            selected = command(args)
            if diagnostics is not None and selected[:2] == ["docker", "run"]:
                payload = kwargs.get("input", "")
                if isinstance(payload, str):
                    payload = payload.encode("utf-8")
                try:
                    transport, detail = capture(selected, payload, kwargs["timeout"])
                except OSError as error:
                    diagnostics.append({"phase": "execution", "exit_code": None, "stdout": "", "stderr": str(error),
                                        "error_type": type(error).__name__, "failure_category": "infrastructure_failure"})
                    raise
                diagnostics.append({"phase": "execution", **detail})
                if transport["timed_out"]:
                    raise subprocess.TimeoutExpired(selected, kwargs["timeout"])
                return subprocess.CompletedProcess(selected, transport["exit_code"])
            return subprocess.run(selected, **kwargs)

        def Popen(self, args, **kwargs):
            return subprocess.Popen(command(args), **kwargs)

    def coverage_transport(args, payload):
        try:
            transport, detail = capture(command(args), payload, line_coverage.TIMEOUT_SECONDS,
                                        combined_limit=line_coverage.MAX_OUTPUT_BYTES)
        except OSError as error:
            diagnostics.append({"phase": "coverage", "exit_code": None, "stdout": "", "stderr": str(error),
                                "error_type": type(error).__name__, "failure_category": "infrastructure_failure"})
            raise
        diagnostics.append({"phase": "coverage", **detail})
        return transport

    with ExitStack() as stack:
        harnesses = build_harnesses(execution._HARNESS, line_coverage._COVERAGE_HARNESS,
                                    path_coverage._PATH_HARNESS, path_coverage._PATH_TEST_HARNESS)
        stack.enter_context(patch.object(execution, "_HARNESS", harnesses["execution"]))
        stack.enter_context(patch.object(line_coverage, "_COVERAGE_HARNESS", harnesses["line"]))
        stack.enter_context(patch.object(path_coverage, "_PATH_HARNESS", harnesses["path"]))
        stack.enter_context(patch.object(execution, "subprocess", Proxy()))
        stack.enter_context(patch.object(line_coverage, "subprocess", Proxy()))
        if diagnostics is not None:
            stack.enter_context(patch.object(line_coverage, "_run_container", coverage_transport))
        yield


def annotate_image(value, image):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "image" and child == "python:3.12-slim":
                value[key] = image
            else:
                annotate_image(child, image)
    elif isinstance(value, list):
        for child in value:
            annotate_image(child, image)


def evaluate_one(row, image):
    """Evaluate fresh artifact text, never consume saved internal validations."""
    commands = []
    diagnostics = []
    # Reuse only the existing syntax check, with execution explicitly disabled.
    static = validate_test_case(row["artifact"], row["task"]["input"], execute=False)
    syntax = deepcopy(next(e for e in static["evidence"] if e["check"] == "Syntax Validity"))
    assertion = {"status": "not_verified", "message": "No caller-trusted assertion oracle is available; execution success is not assertion correctness.",
                 "trusted_oracle": None}
    executed = {"status": "not_verified", "message": "Skipped because syntax did not pass."}
    coverage = {"status": "not_verified", "message": "Skipped because syntax or execution did not pass."}
    with selected_image(image, commands, diagnostics):
        if syntax["status"] == "passed":
            executed = execution.validate_execution(row["artifact"], row["task"]["input"]["python_solution"])
            if executed["status"] == "passed":
                coverage = COVERAGE[row["task"]["reference"]["target_type"]](row["artifact"], deepcopy(row["task"]))
    annotate_image(executed, image)
    annotate_image(coverage, image)
    execution_detail = next((d for d in diagnostics if d["phase"] == "execution"), None)
    if execution_detail is not None:
        if executed["status"] == "not_verified":
            execution_detail["failure_category"] = "infrastructure_failure"
        executed.update(diagnostics=execution_detail, failure_category=execution_detail["failure_category"],
                        output="bounded stdout/stderr in diagnostics")
    coverage_detail = next((d for d in diagnostics if d["phase"] == "coverage"), None)
    if coverage_detail is not None:
        coverage["diagnostics"] = coverage_detail
    return {"artifact_id": row["artifact_id"], "pair_id": row["pair_id"], "task": deepcopy(row["task"]),
            "artifact_sha256": digest(row["artifact"].encode()), "metrics": {
                "Syntax": syntax, "Execution": executed, "Assertion Correctness": assertion,
                "Target Coverage": {"target_type": row["task"]["reference"]["target_type"], **coverage}},
            "execution_evidence": {"image_id": image, "commands": commands, "docker_diagnostics": diagnostics,
                                   "harness_version": HARNESS_VERSION, "target_module_aliases": list(ALIASES)},
            "infrastructure_stop": syntax["status"] == "passed" and (
                executed["status"] == "not_verified" or "cleanup_error" in coverage.get("evidence", {}))}


def configuration(manifest_hash, image):
    source_paths = [Path(__file__), ROOT / "src/tavf/validators/test_case.py", ROOT / "src/tavf/validators/assertions.py",
                    ROOT / "src/tavf/validators/execution.py", ROOT / "src/tavf/evaluation/line_coverage.py",
                    ROOT / "src/tavf/evaluation/branch_coverage.py", ROOT / "src/tavf/evaluation/path_coverage.py"]
    source_paths.append(Path(__file__).with_name("testeval_diagnostics.py"))
    source_paths.append(Path(__file__).with_name("testeval_module_harness.py"))
    instrumentation = path_coverage.INSTRUMENTED_DATA
    return {"procedure": VERSION, "harness_version": HARNESS_VERSION, "target_module_aliases": list(ALIASES),
            "manifest_sha256": manifest_hash, "image_id": image,
            "assertion_oracle": None, "source_sha256": {p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for p in source_paths},
            "instrumentation_sha256": digest(instrumentation.read_bytes()) if instrumentation.exists() else None,
            "network": "none", "read_only": True, "cpus": 0.5, "memory_bytes": 134217728,
            "pids_limit": 16, "user": "65534:65534", "timeout_seconds": 10,
            "coverage_max_output_bytes": line_coverage.MAX_OUTPUT_BYTES, "private_mapping_read": False}


def run(manifest, output, *, execute=False, image=VERIFIED_IMAGE, limit=None, expected_count=999):
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", image):
        raise ValueError("An immutable verified image ID is required")
    if limit is not None and (type(limit) is not int or limit < 1):
        raise ValueError("Limit must be positive")
    rows, manifest_hash = load_manifest(manifest, expected_count)
    config = configuration(manifest_hash, image)
    config_path = output / "config.json"
    if config_path.exists() and json.loads(config_path.read_text(encoding="utf-8")) != config:
        raise ValueError("Evaluation settings, image, instrumentation or manifest changed")
    if not execute:
        return {"status": "dry_run", "artifacts": len(rows), "docker_runs": 0}
    with _lock(output):
        if config_path.exists() and json.loads(config_path.read_text(encoding="utf-8")) != config:
            raise ValueError("Evaluation config changed")
        if not config_path.exists() and (list(output.glob("scores/*.json")) or list(output.glob("checkpoints/*.json"))):
            raise ValueError("Existing evaluation records have no config")
        known_ids = {row["artifact_id"] for row in rows}
        if any(path.stem not in known_ids for path in output.glob("scores/*.json")):
            raise ValueError("Unknown saved evaluation artifact")
        info = json.loads(subprocess.check_output(["docker", "image", "inspect", image], text=True, timeout=10))[0]
        if info["Os"] != "linux" or info.get("Config", {}).get("User") != "65534:65534":
            raise ValueError("Image differs from verified non-root Linux setup")
        _save(config_path, config)
        saved = skipped = 0
        status = "completed"
        for row in rows:
            path = output / "scores" / (row["artifact_id"] + ".json")
            checkpoint = output / "checkpoints" / path.name
            artifact_hash = digest(row["artifact"].encode())
            if path.exists():
                previous = json.loads(path.read_text(encoding="utf-8"))
                if (previous.get("state") != "completed" or previous.get("procedure") != VERSION
                        or previous["artifact_id"] != row["artifact_id"] or previous["pair_id"] != row["pair_id"]
                        or previous["task"] != row["task"] or previous["artifact_sha256"] != artifact_hash):
                    raise ValueError("Saved evaluation identity mismatch")
                if checkpoint.exists():
                    prior_checkpoint = json.loads(checkpoint.read_text(encoding="utf-8"))
                    if prior_checkpoint.get("state") == "completed" and prior_checkpoint.get("score_sha256") != digest(path.read_bytes()):
                        raise ValueError("Saved score checksum mismatch")
                skipped += 1
                continue
            if checkpoint.exists():
                raise ValueError("Interrupted evaluation requires reconciliation; automatic rerun refused")
            _save(checkpoint, {"state": "started", "artifact_id": row["artifact_id"], "artifact_sha256": artifact_hash})
            try:
                result = evaluate_one(row, image)
            except Exception as error:
                _save(output / "errors" / path.name, {"error_type": type(error).__name__, "message": str(error)})
                raise
            _save(path, {"state": "completed", "procedure": VERSION, **result})
            _save(checkpoint, {"state": "completed", "artifact_id": row["artifact_id"], "score_sha256": digest(path.read_bytes())})
            saved += 1
            if result["infrastructure_stop"]:
                status = "infrastructure_stop"
                break
            if limit is not None and saved >= limit:
                status = "batch_limit"
                break
        if digest(manifest.read_bytes()) != manifest_hash:
            raise RuntimeError("Input manifest changed")
        summary = {"status": status, "saved_this_run": saved, "skipped_this_run": skipped,
                   "saved_records": len(list(output.glob("scores/*.json"))), "expected_artifacts": len(rows),
                   "image_id": image, "assertion_correctness": "not_verified_without_trusted_oracle"}
        _save(output / "summary.json", summary)
        return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "results/final_evaluation/blinded_manifest/evaluator/artifacts.jsonl")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/final_evaluation/testeval_metrics_v2")
    parser.add_argument("--image", default=VERIFIED_IMAGE)
    parser.add_argument("--execute", action="store_true", help="Explicitly authorize generated code inside isolated Docker")
    parser.add_argument("--limit", type=int, help="Stop after this many newly saved artifact evaluations")
    args = parser.parse_args()
    outcome = run(args.manifest, args.output_dir, execute=args.execute, image=args.image, limit=args.limit)
    print(json.dumps(outcome))
    if outcome["status"] == "infrastructure_stop":
        raise SystemExit(1)
