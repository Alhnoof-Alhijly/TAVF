"""Prepare target-level inputs only; never import or execute dataset code."""

import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import re


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data/raw/testeval/data/leetcode-py-all.jsonl"
OUTPUT = ROOT / "data/processed/testeval_targets_500.json"
QUOTAS = {"line": 167, "branch": 167, "path": 166}
SEED = 42


def eligible_targets(row):
    """Conservative syntax/bounds checks, not a proof of runtime reachability."""
    pools = {kind: [] for kind in QUOTAS}
    rejected = Counter()
    source = row["python_solution"]
    lines = source.splitlines()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        rejected["program_syntax"] += 1
        return pools, rejected
    statements = {node.lineno for node in ast.walk(tree) if isinstance(node, ast.stmt)}
    dead = set()
    for node in ast.walk(tree):
        for _, suite in ast.iter_fields(node):
            if isinstance(suite, list) and suite and all(isinstance(n, ast.stmt) for n in suite):
                terminated = False
                for statement in suite:
                    if terminated:
                        dead.update(range(statement.lineno, statement.end_lineno + 1))
                    if isinstance(statement, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                        terminated = True
        if isinstance(node, (ast.If, ast.While)) and isinstance(node.test, ast.Constant):
            suite = node.orelse if bool(node.test.value) else node.body
            for statement in suite:
                dead.update(range(statement.lineno, statement.end_lineno + 1))

    def bounded(line):
        return type(line) is int and 1 <= line <= len(lines)

    seen = {kind: set() for kind in QUOTAS}

    def accept(kind, target, index):
        key = json.dumps(target, sort_keys=True)
        if key in seen[kind]:
            rejected[kind + "_duplicate"] += 1
        else:
            seen[kind].add(key)
            pools[kind].append({"target": target, "source_target_index": index})

    for index, line in enumerate(row["target_lines"]):
        if not bounded(line) or line not in statements or line in dead:
            rejected["line_questionable"] += 1
        else:
            accept("line", {"line": line}, index)
    for index, block in enumerate(row["blocks"]):
        start, end = block["start"], block["end"]
        if (not bounded(start) or not bounded(end) or start > end
                or start in dead or start + 1 in dead or start + 1 not in statements):
            rejected["branch_questionable"] += 1
        else:
            accept("branch", {"start": start, "end": end}, index)
    logs, conditions = row["sampled_paths"], row["sampled_condition_paths"]
    if len(logs) != len(conditions):
        rejected["path_unpaired"] += max(len(logs), len(conditions))
        return pools, rejected
    for index, (log, condition) in enumerate(zip(logs, conditions)):
        if not log or not condition:
            rejected["path_empty"] += 1
            continue
        if (not isinstance(log, list) or not isinstance(condition, list)
                or any(not isinstance(entry, str) or not entry.strip() for entry in log + condition)):
            rejected["path_questionable"] += 1
            continue
        refs = [re.match(r"^Line (\d+):", entry) for entry in condition]
        log_refs = [re.search(r" at line (\d+)-(\d+)", entry) for entry in log]
        if (any(match is None for match in refs + log_refs)
                or any(not bounded(int(match[1])) or int(match[1]) in dead for match in refs)
                or any(not bounded(int(match[1])) or not bounded(int(match[2]))
                       or int(match[1]) > int(match[2]) or int(match[1]) in dead for match in log_refs)):
            rejected["path_questionable"] += 1
        else:
            accept("path", {"execution_path": log, "condition_path": condition}, index)
    return pools, rejected


def difficulty_quotas(groups, count):
    total = sum(len(group) for group in groups.values())
    allocation = {key: count * len(group) // total for key, group in groups.items()}
    order = sorted(groups, key=lambda key: (-(count * len(groups[key]) % total), key))
    for key in order[:count - sum(allocation.values())]:
        allocation[key] += 1
    return allocation


def prepare(rows, source_hash):
    if len({row["task_num"] for row in rows}) != len(rows):
        raise ValueError("Duplicate program IDs")
    rng = random.Random(SEED)
    rows = sorted(rows, key=lambda row: row["task_num"])
    by_id = {row["task_num"]: row for row in rows}
    candidates, excluded = {}, Counter()
    for row in rows:
        if not row["description"].strip() or not row["python_solution"].strip():
            raise ValueError("Missing program input")
        candidates[row["task_num"]], rejected = eligible_targets(row)
        excluded.update(rejected)
    instances, coverage, stratification = [], Counter(), {}
    for kind, count in QUOTAS.items():
        groups = {}
        for program, pool in candidates.items():
            if pool[kind]:
                groups.setdefault(by_id[program]["difficulty"], []).append(program)
        if sum(map(len, groups.values())) < count:
            raise ValueError("Insufficient eligible programs for " + kind)
        allocation = difficulty_quotas(groups, count)
        stratification[kind] = allocation
        for difficulty in sorted(groups):
            programs = groups[difficulty][:]
            rng.shuffle(programs)
            # Random tie-breaking, then prefer programs used least so far.
            programs.sort(key=lambda program: coverage[program])
            for program in programs[:allocation[difficulty]]:
                row = by_id[program]
                chosen = rng.choice(candidates[program][kind])
                instances.append({
                    "instance_id": f"testeval-{program}-{kind}",
                    "task_num": program, "task_title": row["task_title"],
                    "target_type": kind, "difficulty": difficulty,
                    "input": {"description": row["description"],
                              "python_solution": row["python_solution"],
                              "func_name": row["func_name"], "target_type": kind,
                              "target": chosen["target"]},
                    "source_target_index": chosen["source_target_index"],
                })
                coverage[program] += 1
    metadata = {
        "seed": SEED, "source_file": SOURCE.relative_to(ROOT).as_posix(),
        "source_sha256": source_hash, "program_count": len(rows),
        "quotas": QUOTAS, "selected_program_count": len(coverage),
        "selected_difficulty_counts": stratification,
        "instances_per_program": dict(sorted(Counter(coverage.values()).items())),
        "eligible_target_counts": {kind: sum(len(pool[kind]) for pool in candidates.values()) for kind in QUOTAS},
        "excluded_counts": dict(sorted(excluded.items())),
        "selection": "Proportional difficulty quotas (largest remainder); least-used programs first; seeded random ties and targets.",
        "static_policy": "Exclude nonstatement/dead line targets, invalid block bounds/probes, empty/unpaired/invalid paths and duplicate targets.",
        "runtime_reachability": "not_verified", "schema": "testeval_target_sampling_v1",
        "integration": "Standalone target-level inputs; existing TAVF prompts do not consume target fields.",
    }
    bundle = {"metadata": metadata, "instances": instances}
    validate(bundle, rows)
    return bundle


def validate(bundle, rows):
    """Validate quotas, provenance, eligibility and per-program caps offline."""
    items = bundle["instances"]
    if Counter(item["target_type"] for item in items) != Counter(QUOTAS):
        raise ValueError("Incorrect target quotas")
    pairs = [(item["task_num"], item["target_type"]) for item in items]
    if len(set(pairs)) != len(items) or len({item["instance_id"] for item in items}) != len(items):
        raise ValueError("Duplicate instance or program/type pair")
    indexed = {row["task_num"]: row for row in rows}
    pools = {program: eligible_targets(row)[0] for program, row in indexed.items()}
    if set(program for program, _ in pairs) != set(indexed):
        raise ValueError("All-program coverage was not achieved")
    for item in items:
        row = indexed[item["task_num"]]
        data = item["input"]
        if any(data[key] != row[key] for key in ("description", "python_solution", "func_name")):
            raise ValueError("Source input mismatch")
        if item["difficulty"] != row["difficulty"] or data["target_type"] != item["target_type"]:
            raise ValueError("Instance metadata mismatch")
        candidate = {"target": data["target"], "source_target_index": item["source_target_index"]}
        if candidate not in pools[item["task_num"]][item["target_type"]]:
            raise ValueError("Ineligible or mismatched source target")


def main():
    raw = SOURCE.read_bytes()
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    bundle = prepare(rows, hashlib.sha256(raw).hexdigest())
    # Exclusive creation protects previous selections as well as original data.
    with OUTPUT.open("x", encoding="utf-8") as handle:
        json.dump(bundle, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(json.dumps(bundle["metadata"], sort_keys=True))


if __name__ == "__main__":
    main()
