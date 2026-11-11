"""Resumable paired generation. Dry-run by default; no Final Evaluation here."""

import argparse
from contextlib import contextmanager
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
from uuid import uuid4

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from baseline.baseline_runner import BaselineRunner
from cost_tracker import BUDGET, SAFETY_LIMIT, calculate_cost, calculate_spent, check_budget
from tavf.prompting import _target_context, build_prompt
from tavf.runner import run_task as run_tavf
from utils.llm_client import DEFAULT_MODEL, MAX_OUTPUT_TOKENS, LLMClient


DATASETS = {"user_stories_500.json": "user_story_refinement",
            "bug_reports_500.json": "bug_report_refinement",
            "test_cases_500.json": "test_case_generation"}


def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     allow_nan=False).encode("utf-8")).hexdigest()


def _save(path, value):
    """Flush a complete record before atomic replacement; ignore orphan temps."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid4().hex + ".tmp")
    with temporary.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


@contextmanager
def _lock(directory):
    """OS lock releases after crashes; concurrent writers fail without requests."""
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / ".lock").open("a+b") as handle:
        handle.seek(0, 2)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


class TargetBaselineRunner(BaselineRunner):
    """Retain direct prompting while exposing the same selected target as TAVF."""
    def build_prompt(self, task):
        prompt = super().build_prompt(task)
        if task["task_type"] == "test_case_generation":
            prompt += "\n\n" + _target_context(task.get("reference"))
        return prompt


def _validate_tasks(tasks):
    validator = Draft202012Validator(json.loads((ROOT / "data/task_schema.json").read_text(encoding="utf-8")))
    if not tasks or len({task["task_id"] for task in tasks}) != len(tasks):
        raise ValueError("Tasks must have unique IDs")
    baseline = TargetBaselineRunner()
    for task in tasks:
        validator.validate(task)
        if task["task_type"] == "test_case_generation" and not _target_context(task.get("reference")):
            raise ValueError("Selected TestEval target metadata is required")
        baseline.build_prompt(task)
        build_prompt(task["task_type"], task["input"], task_reference=task.get("reference"))


def load_tasks(directory=ROOT / "data/processed"):
    tasks = []
    for filename, task_type in DATASETS.items():
        rows = json.loads((Path(directory) / filename).read_text(encoding="utf-8"))
        if not isinstance(rows, list) or len(rows) != 500 or any(row.get("task_type") != task_type for row in rows):
            raise ValueError("Expected 500 correctly routed tasks in " + filename)
        tasks.extend(rows)
    _validate_tasks(tasks)
    return tasks


def _manifest(tasks, max_output_tokens):
    files = [ROOT / "data/task_schema.json", Path(__file__), ROOT / "scripts/cost_tracker.py"]
    for directory in ("prompts/baseline", "prompts/tavf", "src/baseline", "src/tavf", "src/utils"):
        files.extend(path for path in (ROOT / directory).rglob("*") if path.suffix in {".txt", ".py"})
    return {"version": 1, "tasks_sha256": _hash(tasks), "task_count": len(tasks),
            "model": DEFAULT_MODEL, "reasoning_effort": "none", "max_output_tokens": max_output_tokens,
            "source_hashes": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in sorted(set(files))},
            "docker_execution": False, "final_evaluation": "separate"}


class _JournalClient:
    def __init__(self, provider, directory, manifest, records):
        self.provider, self.directory, self.manifest, self.records = provider, directory, manifest, records
        self.model = manifest["model"]
        self.reasoning_effort = manifest["reasoning_effort"]
        self.max_output_tokens = manifest["max_output_tokens"]
        self.halted = None
        self.task, self.method, self.sequence = None, None, 0

    def generate(self, prompt):
        if self.halted:
            raise RuntimeError("Experiment halted")
        if self.method == "tavf" and self.task["task_type"] == "test_case_generation":
            initial = build_prompt(self.task["task_type"], self.task["input"], task_reference=self.task["reference"])
            if prompt != initial:
                prompt += "\n\n" + _target_context(self.task["reference"])
        key = _hash([self.task["task_id"], self.method, self.sequence])
        self.sequence += 1
        path = self.directory / "requests" / (key + ".json")
        request = {"task_id": self.task["task_id"], "method": self.method,
                   "sequence": self.sequence - 1, "prompt": prompt, "prompt_sha256": _hash(prompt)}
        if key in self.records:
            saved = self.records[key]
            if any(saved.get(field) != value for field, value in request.items()):
                self.halted = "replay_mismatch"
                raise ValueError("Saved request does not match replay")
            return deepcopy(saved["response"])
        # One token per UTF-8 byte plus request overhead is conservative. Both
        # the legacy guard and this run's durable usage apply to EVERY request.
        estimate = len(prompt.encode("utf-8")) + 512
        spent = sum((calculate_cost(r["response"]["input_tokens"], r["response"]["output_tokens"],
                                    r["response"].get("cached_input_tokens", 0) or 0)
                     for r in self.records.values()), start=calculate_cost(0, 0))
        projected = calculate_spent() + spent + calculate_cost(estimate, self.max_output_tokens)
        if not check_budget(estimate, self.max_output_tokens) or projected > min(BUDGET, SAFETY_LIMIT):
            self.halted = "budget_limit"
            raise RuntimeError("Budget limit")
        request["state"] = "started"
        _save(path, request)
        try:
            response = self.provider.generate(prompt)
        except Exception:
            request["state"] = "uncertain"
            _save(path, request)
            self.halted = "request_requires_reconciliation"
            raise RuntimeError("Request outcome requires reconciliation") from None
        # Persist every response immediately, even if its usage is incomplete.
        request.update(state="usage_unverified", response=response)
        _save(path, request)
        try:
            if (response.get("model") != self.model or response.get("parameters") != {
                    "reasoning_effort": self.reasoning_effort, "max_output_tokens": self.max_output_tokens}
                    or not isinstance(response.get("output"), str) or not response["output"].strip()
                    or any(type(response.get(k)) is not int or response[k] < 0 for k in ("input_tokens", "output_tokens"))):
                raise ValueError("Response metadata unavailable")
            calculate_cost(response["input_tokens"], response["output_tokens"], response.get("cached_input_tokens", 0) or 0)
        except (TypeError, ValueError):
            self.halted = "response_requires_reconciliation"
            raise RuntimeError("Response metadata requires reconciliation") from None
        request["state"] = "completed"
        _save(path, request)
        self.records[key] = request
        return deepcopy(response)


def run_experiment(tasks, output_dir, *, execute=False, client=None, max_output_tokens=MAX_OUTPUT_TOKENS):
    """Dry-run is read-only; execute must be explicit even with an injected client.

    Completed outputs skip; interrupted tasks replay durable responses before
    making new requests. An interrupted/uncertain API request is never retried
    automatically: its billing/outcome must first be reconciled.
    """
    _validate_tasks(tasks)
    if type(max_output_tokens) is not int or not 1 <= max_output_tokens <= MAX_OUTPUT_TOKENS:
        raise ValueError("Invalid output token cap")
    directory = Path(output_dir)
    manifest = _manifest(tasks, max_output_tokens)
    manifest_path = directory / "manifest.json"
    if manifest_path.exists() and json.loads(manifest_path.read_text(encoding="utf-8")) != manifest:
        raise ValueError("Experiment configuration, inputs or source changed; resume refused")
    if not execute:
        return {"status": "dry_run", "tasks": len(tasks), "method_tasks": 2 * len(tasks), "api_calls": 0}
    with _lock(directory):
        if manifest_path.exists():
            if json.loads(manifest_path.read_text(encoding="utf-8")) != manifest:
                raise ValueError("Experiment manifest changed")
        elif list(directory.glob("requests/*.json")) or list(directory.glob("results/*.json")):
            raise ValueError("Existing results lack an experiment manifest")
        else:
            _save(manifest_path, manifest)
        records = {path.stem: json.loads(path.read_text(encoding="utf-8")) for path in directory.glob("requests/*.json")}
        if any(record.get("state") != "completed" for record in records.values()):
            raise ValueError("Unfinished API request requires reconciliation; automatic retry refused")
        if client is None:
            client = LLMClient(max_output_tokens=max_output_tokens)
        if any(getattr(client, key, None) != manifest[key] for key in ("model", "reasoning_effort", "max_output_tokens")):
            raise ValueError("Client configuration differs from experiment manifest")
        journal = _JournalClient(client, directory, manifest, records)
        baseline = TargetBaselineRunner(client=journal)
        completed = skipped = 0
        for task in tasks:
            for method in ("baseline", "tavf"):
                path = directory / "results" / (_hash([task["task_id"], method]) + ".json")
                if path.exists():
                    saved = json.loads(path.read_text(encoding="utf-8"))
                    if saved["task"] != task or saved["method"] != method:
                        raise ValueError("Saved result identity mismatch")
                    skipped += 1
                    continue
                journal.task, journal.method, journal.sequence = task, method, 0
                try:
                    outcome = baseline.run_task(deepcopy(task)) if method == "baseline" else run_tavf(deepcopy(task), client=journal)
                except Exception:
                    if journal.halted:
                        return {"status": journal.halted, "saved": completed, "skipped": skipped}
                    raise
                if journal.halted:
                    return {"status": journal.halted, "saved": completed, "skipped": skipped}
                _save(path, {"task": task, "method": method, "result": outcome,
                             "final_evaluation": {"status": "not_verified", "message": "Not run by generation driver."}})
                completed += 1
        return {"status": "completed", "saved": completed, "skipped": skipped}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--execute", action="store_true", help="Explicitly enable paid requests.")
    mode.add_argument("--dry-run", action="store_true", help="Validate/prepare only (the default).")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/main_experiment")
    args = parser.parse_args()
    print(json.dumps(run_experiment(load_tasks(), args.output_dir, execute=args.execute)))


if __name__ == "__main__":
    main()
