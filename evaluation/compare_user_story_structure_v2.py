"""Join frozen v2 scores to private labels for analysis only; never rescore."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def compare(score_path, mapping_path, output):
    if output.exists():
        raise ValueError("Comparison already exists")
    score_bytes, mapping_bytes = score_path.read_bytes(), mapping_path.read_bytes()
    scores = [json.loads(line) for line in score_bytes.decode().splitlines()]
    mapping_rows = [json.loads(line) for line in mapping_bytes.decode().splitlines()]
    mapping = {r["artifact_id"]: r for r in mapping_rows}
    if len(mapping) != len(mapping_rows) or len(scores) != 1000 or len({r["artifact_id"] for r in scores}) != 1000:
        raise ValueError("Duplicate IDs or wrong score count")
    pairs, method_rows = {}, {"baseline": [], "tavf": []}
    for row in scores:
        label = mapping[row["artifact_id"]]
        if (label["task_type"] != "user_story_refinement" or row["pair_id"] != label["pair_id"]
                or row["task_id"] != label["task_id"] or row["procedure"] != "user_story_structural_v2"):
            raise ValueError("Score-to-method linkage mismatch")
        method = label["method"]
        pair = pairs.setdefault(row["pair_id"], {})
        if method in pair:
            raise ValueError("Duplicate method in pair")
        pair[method] = row
        method_rows[method].append(row)
        for criterion in row["criteria"].values():
            if criterion["score"] != {"pass": 1, "fail": 0, "unassessable": None}[criterion["status"]]:
                raise ValueError("Inconsistent saved score/status")
    if len(pairs) != 500 or any(set(pair) != {"baseline", "tavf"} for pair in pairs.values()):
        raise ValueError("Expected 500 complete task pairs")
    criteria = {}
    for name in ("Structural Form", "Information Completeness", "Atomic", "Minimal"):
        by_method = {}
        for method, rows in method_rows.items():
            counts = Counter(row["criteria"][name]["status"] for row in rows)
            by_method[method] = {s: counts[s] for s in ("pass", "fail", "unassessable")}
            by_method[method]["assessable_denominator"] = counts["pass"] + counts["fail"]
        delta, excluded, transitions = Counter(), Counter(), Counter()
        for pair in pairs.values():
            b, t = (pair[m]["criteria"][name] for m in ("baseline", "tavf"))
            transitions[b["status"] + " -> " + t["status"]] += 1
            if b["score"] is not None and t["score"] is not None:
                delta[t["score"] - b["score"]] += 1
            else:
                excluded["neither_assessable" if b["score"] is None and t["score"] is None
                         else "tavf_only_assessable" if b["score"] is None else "baseline_only_assessable"] += 1
        n = sum(delta.values())
        difference = delta[1] - delta[-1]
        criteria[name] = {"by_method": by_method, "paired": {"valid_pair_denominator": n,
                          "tavf_higher": delta[1], "equal": delta[0], "baseline_higher": delta[-1],
                          "sum_score_difference": difference, "mean_score_difference": difference / n if n else None,
                          "pass_rate_difference_percentage_points": 100 * difference / n if n else None,
                          "excluded_pairs": dict(excluded), "status_transitions": dict(transitions)}}
    slot_counts = {}
    for method, rows in method_rows.items():
        counts = Counter()
        for row in rows:
            counts.update(row["slot_counts"])
        slot_counts[method] = {"states": dict(counts), "slot_denominator": sum(counts.values()),
                               "story_count": sum(row["story_count"] for row in rows)}
    report = {"procedure": "user_story_structural_v2", "artifacts": 1000, "artifacts_per_method": 500,
              "task_pairs": 500, "difference_definition": "TAVF minus Baseline; both-assessable pairs only; null never zero-filled",
              "criteria": criteria, "information_slot_counts_by_method": slot_counts,
              "scores_frozen_before_method_join": True, "rescoring_performed": False,
              "scores_sha256": hashlib.sha256(score_bytes).hexdigest(),
              "method_mapping_sha256": hashlib.sha256(mapping_bytes).hexdigest()}
    with output.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    assert score_path.read_bytes() == score_bytes and mapping_path.read_bytes() == mapping_bytes
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scores", type=Path, default=ROOT / "results/final_evaluation/user_story_structural_v2/scores.jsonl")
    parser.add_argument("--mapping", type=Path, default=ROOT / "results/final_evaluation/blinded_manifest/private/method_mapping.jsonl")
    parser.add_argument("--output", type=Path, default=ROOT / "results/final_evaluation/user_story_structural_v2/method_comparison.json")
    args = parser.parse_args()
    print(json.dumps(compare(args.scores, args.mapping, args.output)))
