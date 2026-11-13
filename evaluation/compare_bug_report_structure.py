"""Analyze frozen Bug Report scores after anonymous scoring; never rescore."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def compare(scores_path, mapping_path, output):
    if output.exists():
        raise ValueError("Comparison already exists")
    score_bytes, map_bytes = scores_path.read_bytes(), mapping_path.read_bytes()
    scores = [json.loads(line) for line in score_bytes.decode().splitlines()]
    labels_list = [json.loads(line) for line in map_bytes.decode().splitlines()]
    labels = {r["artifact_id"]: r for r in labels_list}
    if len(scores) != 1000 or len({r["artifact_id"] for r in scores}) != 1000 or len(labels) != len(labels_list):
        raise ValueError("Duplicate IDs or wrong inventory")
    pairs, methods = {}, {"baseline": [], "tavf": []}
    for row in scores:
        label = labels[row["artifact_id"]]
        if (label["task_type"] != "bug_report_refinement" or row["task_id"] != label["task_id"]
                or row["pair_id"] != label["pair_id"] or row["procedure"] != "bug_report_structural_v1"):
            raise ValueError("Invalid method linkage")
        pair = pairs.setdefault(row["pair_id"], {})
        if label["method"] in pair:
            raise ValueError("Duplicate method in pair")
        pair[label["method"]] = row
        methods[label["method"]].append(row)
    if len(pairs) != 500 or any(set(pair) != {"baseline", "tavf"} for pair in pairs.values()):
        raise ValueError("Expected 500 complete pairs")

    def paired(value):
        differences, excluded = [], Counter()
        for pair in pairs.values():
            b, t = value(pair["baseline"]), value(pair["tavf"])
            if b is not None and t is not None:
                differences.append(t - b)
            else:
                excluded["neither_assessable" if b is None and t is None else
                         "tavf_only_assessable" if b is None else "baseline_only_assessable"] += 1
        return {"valid_pair_denominator": len(differences), "tavf_higher": sum(d > 0 for d in differences),
                "equal": sum(d == 0 for d in differences), "baseline_higher": sum(d < 0 for d in differences),
                "mean_difference": sum(differences) / len(differences) if differences else None,
                "excluded_pairs": dict(excluded)}

    components = {}
    for name in ("Summary", "Steps to Reproduce", "Expected Result", "Actual Result"):
        by_method = {}
        for method, rows in methods.items():
            counts = Counter(r["criteria"][name]["status"] for r in rows)
            by_method[method] = {status: counts[status] for status in ("pass", "fail", "unassessable")}
            by_method[method]["assessable_denominator"] = counts["pass"] + counts["fail"]
        difference = paired(lambda row: row["criteria"][name]["score"])
        difference["pass_rate_difference_percentage_points"] = 100 * difference["mean_difference"] if difference["mean_difference"] is not None else None
        components[name] = {"by_method": by_method, "paired": difference}
    totals = {}
    for method, rows in methods.items():
        values = [r["structural_score_100"] for r in rows if r["structural_score_100"] is not None]
        totals[method] = {"mean_score_100": sum(values) / len(values) if values else None,
                          "valid_artifact_denominator": len(values), "unassessable": len(rows) - len(values),
                          "score_distribution": dict(Counter(values))}
    report = {"procedure": "bug_report_structural_v1", "artifacts": 1000, "artifacts_per_method": 500,
              "task_pairs": 500, "components": components, "total_score": {"by_method": totals,
              "paired": paired(lambda row: row["structural_score_100"])},
              "difference_definition": "TAVF minus Baseline, jointly assessable pairs only; null never zero-filled",
              "scores_frozen_before_method_join": True, "rescoring_performed": False,
              "scores_sha256": hashlib.sha256(score_bytes).hexdigest(), "method_mapping_sha256": hashlib.sha256(map_bytes).hexdigest()}
    with output.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    assert scores_path.read_bytes() == score_bytes and mapping_path.read_bytes() == map_bytes
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scores", type=Path, default=ROOT / "results/final_evaluation/bug_report_structural_v1/scores.jsonl")
    parser.add_argument("--mapping", type=Path, default=ROOT / "results/final_evaluation/blinded_manifest/private/method_mapping.jsonl")
    parser.add_argument("--output", type=Path, default=ROOT / "results/final_evaluation/bug_report_structural_v1/method_comparison.json")
    args = parser.parse_args()
    print(json.dumps(compare(args.scores, args.mapping, args.output)))
