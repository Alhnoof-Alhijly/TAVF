"""Prepare blinded artifacts and a separate private key; never score or execute."""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from random import SystemRandom
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
DATA_FILES = ("user_stories_500.json", "bug_reports_500.json", "test_cases_500.json")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare_records(tasks, records, rejections):
    """Pure assembly with strict identity checks and no invented missing output."""
    lookup = {t["task_id"]: t for t in tasks}
    if len(lookup) != len(tasks):
        raise ValueError("Duplicate task ID")
    expected = {(task_id, method) for task_id in lookup for method in ("baseline", "tavf")}
    observed, rejected = set(), set()
    evaluator, mapping, rejection_rows = [], [], []
    pairs = defaultdict(list)
    pair_ids = {task_id: uuid4().hex for task_id in lookup}
    for source, source_sha256, record in records:
        task, method, result = record["task"], record["method"], record["result"]
        identity = task["task_id"], method
        if identity not in expected or identity in observed or task != lookup.get(task["task_id"]):
            raise ValueError("Duplicate, unknown or mismatched output metadata")
        if any(result.get(k) != v for k, v in (("task_id", identity[0]), ("method", method), ("task_type", task["task_type"]))):
            raise ValueError("Inner result identity mismatch")
        if method == "tavf" and result.get("task") != task:
            raise ValueError("TAVF task snapshot mismatch")
        artifact = result.get("output") if method == "baseline" else result.get("artifact")
        if not isinstance(artifact, str) or not artifact.strip():
            raise ValueError("Missing artifact")
        observed.add(identity)
        anonymous_id = uuid4().hex
        pair_id = pair_ids[task["task_id"]]
        evaluator.append({"artifact_id": anonymous_id, "pair_id": pair_id,
                          "task": deepcopy(task), "artifact": artifact})
        mapping.append({"artifact_id": anonymous_id, "pair_id": pair_id, "task_id": task["task_id"],
                        "task_type": task["task_type"], "method": method,
                        "source_file": source, "source_sha256": source_sha256,
                        "artifact_sha256": hashlib.sha256(artifact.encode("utf-8")).hexdigest()})
        pairs[task["task_id"]].append(anonymous_id)
    for source, source_sha256, record in rejections:
        identity = record["task_id"], record["method"]
        if (identity not in expected or identity in observed or identity in rejected
                or record.get("state") != "provider_rejected" or record.get("http_status") != 400
                or record.get("provider_code") != "invalid_prompt" or not record.get("request_id")):
            raise ValueError("Invalid or conflicting provider rejection")
        rejected.add(identity)
        rejection_rows.append({"task": deepcopy(lookup[identity[0]]), "pair_id": pair_ids[identity[0]],
                               "source_file": source, "source_sha256": source_sha256,
                               "request": deepcopy(record), "successful_output": False})
    if observed | rejected != expected:
        raise ValueError("Missing output lacks a documented provider rejection")
    rng = SystemRandom()
    rng.shuffle(evaluator)
    pair_rows = []
    for task_id, ids in pairs.items():
        rng.shuffle(ids)
        pair_rows.append({"pair_id": pair_ids[task_id], "task_id": task_id,
                          "artifact_ids": ids, "complete_pair": len(ids) == 2})
    rng.shuffle(pair_rows)
    counts = Counter((row["task_type"], row["method"]) for row in mapping)
    summary = {"artifacts": len(evaluator), "complete_pairs": sum(row["complete_pair"] for row in pair_rows),
               "incomplete_pairs": sum(not row["complete_pair"] for row in pair_rows),
               "provider_rejections": len(rejection_rows), "scoring": "not_started",
               "counts_by_task_and_method": {kind: {m: counts[kind, m] for m in ("baseline", "tavf")}
                                            for kind in sorted({t["task_type"] for t in tasks})}}
    return evaluator, pair_rows, mapping, rejection_rows, summary


def write_jsonl(path, rows):
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")


def build(output):
    if output.exists():
        raise ValueError("Destination exists; refusing to overwrite an evaluation manifest")
    data_paths = [ROOT / "data/processed" / name for name in DATA_FILES]
    tasks = [t for path in data_paths for t in read(path)]
    directory = ROOT / "results/main_experiment"
    paths = sorted((directory / "results").glob("*.json"))
    request_paths = sorted((directory / "requests").glob("*.json"))
    rejected_paths = [path for path in request_paths if read(path)["state"] == "provider_rejected"]
    if any(read(path)["state"] not in {"completed", "provider_rejected"} for path in request_paths):
        raise ValueError("Unresolved request blocks evaluation preparation")
    protected = {path: sha(path) for path in data_paths + paths + request_paths}
    records = [(path.relative_to(ROOT).as_posix(), protected[path], read(path)) for path in paths]
    rejections = [(path.relative_to(ROOT).as_posix(), protected[path], read(path)) for path in rejected_paths]
    evaluator, pairs, mapping, rejected, summary = prepare_records(tasks, records, rejections)
    if (len(tasks), summary["artifacts"], summary["complete_pairs"], summary["provider_rejections"]) != (1500, 2999, 1499, 1):
        raise ValueError("Unexpected completed experiment inventory")
    if {(r["request"]["task_id"], r["request"]["method"]) for r in rejected} != {("testeval-2973-line", "baseline")}:
        raise ValueError("Unexpected rejected task")
    output.mkdir(parents=True)
    evaluator_dir, private_dir = output / "evaluator", output / "private"
    evaluator_dir.mkdir()
    private_dir.mkdir()
    write_jsonl(evaluator_dir / "artifacts.jsonl", evaluator)
    write_jsonl(evaluator_dir / "pairs.jsonl", pairs)
    write_jsonl(private_dir / "method_mapping.jsonl", mapping)
    write_jsonl(private_dir / "provider_rejections.jsonl", rejected)
    (private_dir / "inventory.json").write_text(json.dumps({**summary, "dataset_sha256": {
        path.relative_to(ROOT).as_posix(): protected[path] for path in data_paths}}, indent=2) + "\n", encoding="utf-8")
    (output / "README.md").write_text(
        "Share only evaluator/ with independent scorers. Keep private/ and original experiment records hidden.\n"
        "Opaque IDs and randomized ordering conceal method labels; artifact text is unchanged.\n"
        "Original task metadata is retained. Pair membership is visible. No scores have been calculated.\n"
        "One incomplete pair remains; the private rejection ledger records its missing artifact.\n",
        encoding="utf-8")
    if any(sha(path) != value for path, value in protected.items()):
        raise RuntimeError("Original data or experiment record changed")
    # Read back serialized artifacts and verify every anonymous link.
    loaded = [json.loads(line) for line in (evaluator_dir / "artifacts.jsonl").read_text(encoding="utf-8").splitlines()]
    if len({row["artifact_id"] for row in loaded}) != 2999:
        raise RuntimeError("Anonymous ID collision")
    by_id = {row["artifact_id"]: row for row in loaded}
    if any(hashlib.sha256(by_id[row["artifact_id"]]["artifact"].encode()).hexdigest() != row["artifact_sha256"] for row in mapping):
        raise RuntimeError("Artifact linkage mismatch")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/final_evaluation/blinded_manifest")
    args = parser.parse_args()
    print(json.dumps({"output_dir": str(args.output_dir), **build(args.output_dir)}))
