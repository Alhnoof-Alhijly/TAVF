"""Reproducible inference on frozen paired scores; never evaluate artifacts."""
import argparse
from collections import defaultdict, Counter
from functools import reduce
import hashlib
import json
import math
from pathlib import Path
import platform

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SEED, BOOTSTRAPS, PERMUTATIONS = 42, 20000, 100000


def seed(label):
    return int.from_bytes(hashlib.sha256(f"{SEED}/{label}".encode()).digest()[:8], "big")


def sign_p(wins, losses):
    n = wins + losses
    return min(1., 2 * sum(math.comb(n, k) for k in range(min(wins, losses) + 1)) / (2 ** n)) if n else 1.


def exact_flip(sums):
    nonzero = [int(x) for x in sums if x != 0]
    if not nonzero:
        return 1.
    divisor = reduce(math.gcd, (abs(x) for x in nonzero))
    weights = [abs(x) // divisor for x in nonzero]
    target = abs(sum(nonzero)) // divisor
    distribution = {0: 1}
    for weight in weights:
        following = defaultdict(int)
        for total, count in distribution.items():
            following[total + weight] += count
            following[total - weight] += count
        distribution = following
    return sum(count for total, count in distribution.items() if abs(total) >= target) / (2 ** len(weights))


def holm(results):
    calculated = sorted((r for r in results if r.get("p_value") is not None), key=lambda r: r["p_value"])
    maximum = 0.
    for i, row in enumerate(calculated):
        maximum = max(maximum, min(1., row["p_value"] * (len(calculated) - i)))
        row.update(p_holm=maximum, holm_reject_0_05=maximum < .05, multiplicity_family_size=len(calculated))


def bootstrap(sums, counts, label):
    if not len(sums):
        return None
    rng = np.random.default_rng(seed(label + "/bootstrap"))
    values = []
    for start in range(0, BOOTSTRAPS, 500):
        indices = rng.integers(0, len(sums), size=(min(500, BOOTSTRAPS - start), len(sums)))
        values.extend((sums[indices].sum(axis=1) / counts[indices].sum(axis=1)).tolist())
    return np.quantile(values, [.025, .975], method="linear").tolist()


def endpoint(label, family, task_type, criterion, pairs, getter, *, ordinal=False, cluster=False, continuous=False, yield_only=False):
    data, transitions, excluded = [], Counter(), Counter()
    for pair in pairs:
        b, bs = getter(pair["baseline"])
        t, ts = getter(pair["tavf"])
        transitions[str(bs) + " -> " + str(ts)] += 1
        if yield_only:
            b, t = int(b == 1), int(t == 1)
        if b is None or t is None:
            excluded["neither_assessable" if b is None and t is None else "tavf_only_assessable" if b is None else "baseline_only_assessable"] += 1
            continue
        d = (int(t > b) - int(t < b)) if ordinal else t - b
        group = pair["baseline"]["task"]["reference"]["task_num"] if cluster else len(data)
        data.append((b, t, d, group))
    report = {"endpoint": label, "family": family, "task_type": task_type, "criterion": criterion,
              "estimand": "observed success yield" if yield_only else "ordinal net win fraction" if ordinal else "mean paired difference",
              "complete_pair_n": len(pairs), "valid_pair_n": len(data), "excluded_pair_patterns": dict(excluded),
              "status_transitions": dict(transitions), "independence_unit": "reference program" if cluster else "paired input",
              "effect_direction": "TAVF minus Baseline", "ci_level": .95, "ci_multiplicity_adjusted": False}
    if not data:
        report.update(effect=None, ci_95=None, p_value=None, test="not_applicable")
        return report
    grouped = defaultdict(list)
    for b, t, d, group in data:
        grouped[group].append(d)
    sums = np.array([sum(v) for v in grouped.values()], dtype=float)
    counts = np.array([len(v) for v in grouped.values()], dtype=int)
    differences = [v[2] for v in data]
    report.update(independent_unit_n=len(sums), effect=sum(differences) / len(data),
                  ci_95=bootstrap(sums, counts, label),
                  tavf_higher=sum(d > 0 for d in differences), ties=sum(d == 0 for d in differences), baseline_higher=sum(d < 0 for d in differences))
    if ordinal:
        report.update(baseline_median=float(np.median([r[0] for r in data])), tavf_median=float(np.median([r[1] for r in data])),
                      probability_of_superiority=(report["tavf_higher"] + .5 * report["ties"]) / len(data),
                      probability_of_superiority_ci_95=[(v + 1) / 2 for v in report["ci_95"]],
                      discordant_pair_n=report["tavf_higher"] + report["baseline_higher"],
                      test="exact two-sided paired sign test", p_value=sign_p(report["tavf_higher"], report["baseline_higher"]))
    elif continuous:
        rng = np.random.default_rng(seed(label + "/permutation"))
        observed, extreme = abs(sums.sum()), 0
        for start in range(0, PERMUTATIONS, 1000):
            signs = rng.integers(0, 2, size=(min(1000, PERMUTATIONS - start), len(sums))) * 2 - 1
            extreme += int(np.sum(np.abs(signs @ sums) >= observed - 1e-12))
        p = (extreme + 1) / (PERMUTATIONS + 1)
        report.update(test="seeded two-sided program-cluster sign-flip permutation", p_value=p,
                      permutation_draws=PERMUTATIONS, monte_carlo_standard_error=math.sqrt(p * (1 - p) / PERMUTATIONS))
    else:
        integer = np.all(np.abs(sums - np.round(sums)) < 1e-9)
        if not integer:
            raise ValueError("Exact flip endpoint must have integer differences")
        report.update(test="exact two-sided program-cluster sign-flip" if cluster else
                      "exact two-sided McNemar" if set(differences) <= {-1, 0, 1} else "exact two-sided paired sign-flip",
                      p_value=exact_flip(np.round(sums).astype(int)))
    if not ordinal:
        report.update(baseline_mean=sum(r[0] for r in data) / len(data), tavf_mean=sum(r[1] for r in data) / len(data))
    return report


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def pair_rows(rows, mapping, *, human=False):
    grouped, methods = defaultdict(dict), defaultdict(list)
    for row in rows:
        if human:
            method, pair_id = row["method"], row["sample_id"]
        else:
            key = mapping[row["artifact_id"]]
            method, pair_id = key["method"], row["pair_id"]
            task_id = row.get("task_id", row.get("task", {}).get("task_id"))
            if task_id != key["task_id"] or pair_id != key["pair_id"]:
                raise ValueError("Frozen score mapping mismatch")
        if method in grouped[pair_id]:
            raise ValueError("Duplicate method/pair")
        grouped[pair_id][method] = row
        methods[method].append(row)
    return [p for p in grouped.values() if set(p) == {"baseline", "tavf"}], methods, len(grouped)


def analyze(output):
    if output.exists():
        raise ValueError("Refusing to overwrite statistical analysis")
    root = ROOT / "results/final_evaluation"
    # Freeze all existing score, rating, mapping and protocol inputs by byte hash.
    paths = [p for folder in (root, ROOT / "evaluation") for p in folder.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    protected = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    mapping = {r["artifact_id"]: r for r in read_jsonl(root / "blinded_manifest/private/method_mapping.jsonl")}
    results, inventory = [], {}
    for directory, task, family in (("user_story_structural_v2", "user_story_refinement", "structural_v2"),
                                     ("bug_report_structural_v1", "bug_report_refinement", "structural"),
                                     ("user_story_structural_v1", "user_story_refinement", "structural_v1_sensitivity")):
        rows = read_jsonl(root / directory / "scores.jsonl")
        pairs, methods, total = pair_rows(rows, mapping)
        if len(pairs) != 500:
            raise ValueError("Expected 500 structural task pairs")
        inventory[directory] = {"pairs": total, "complete_pairs": len(pairs)}
        for criterion in rows[0]["criteria"]:
            def getter(row, criterion=criterion):
                value = row["criteria"][criterion]
                return value["score"], value["status"]
            results.append(endpoint(directory + "/" + criterion, family if criterion != "Information Completeness" else "information_completeness",
                                    task, criterion, pairs, getter))
        if directory == "bug_report_structural_v1":
            results.append(endpoint(directory + "/total_100", family, task, "Structural score /100", pairs,
                                    lambda row: (row["structural_score_100"], "assessable" if row["structural_score_100"] is not None else "unassessable")))
    human = read_jsonl(root / "human_semantic_comparison_v1_1/private_joined_ratings.jsonl")
    for task in ("user_story_refinement", "bug_report_refinement"):
        rows = [r for r in human if r["task_type"] == task]
        pairs, _, _ = pair_rows(rows, mapping, human=True)
        if len(pairs) != 25:
            raise ValueError("Expected 25 complete human pairs per task")
        for criterion in rows[0]["criteria"]:
            results.append(endpoint("human/" + task + "/" + criterion, "human_semantic", task, criterion, pairs,
                                    lambda row, c=criterion: (row["criteria"][c]["rating"] if row["criteria"][c]["validation"] == "valid" else None,
                                                             row["criteria"][c]["validation"]), ordinal=True))
    tests = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((root / "testeval_metrics_v2/scores").glob("*.json"))]
    pairs, methods, total = pair_rows(tests, mapping)
    if len(tests) != 999 or len(pairs) != 499:
        raise ValueError("Unexpected TestEval inventory")
    inventory["testeval"] = {"artifacts": 999, "baseline": len(methods["baseline"]), "tavf": len(methods["tavf"]),
                             "complete_pairs": 499, "incomplete_pairs": total - len(pairs),
                             "excluded_rejection": {"task_id": "testeval-2973-line", "method": "baseline", "state": "provider_rejected"},
                             "assertion_correctness": "999 not_verified; no statistical test"}
    for kind in ("overall", "line", "branch", "path"):
        selected = pairs if kind == "overall" else [p for p in pairs if p["baseline"]["task"]["reference"]["target_type"] == kind]
        for metric in ("Syntax", "Execution", "Target Coverage"):
            def getter(row, metric=metric):
                value = row["metrics"][metric]
                s = value["status"]
                return (1 if s in {"passed", "covered"} else 0 if s in {"failed", "not_covered"} else None), s
            label = "testeval/" + kind + "/" + metric
            family = "coverage" if metric == "Target Coverage" else "execution" if metric == "Execution" else "syntax"
            results.append(endpoint(label, family, "test_case_generation", kind + ": " + metric, selected, getter, cluster=True))
            if metric != "Syntax":
                results.append(endpoint(label + "/observed_yield", family + "_availability", "test_case_generation", kind + ": " + metric,
                                        selected, getter, cluster=True, yield_only=True))
        if kind == "path":
            def path_getter(row):
                m = row["metrics"]["Target Coverage"]
                return (m.get("evidence", {}).get("match_score") if m["status"] in {"covered", "not_covered"} else None), m["status"]
            results.append(endpoint("testeval/path/match_fraction", "coverage", "test_case_generation", "Path match fraction", selected,
                                    path_getter, cluster=True, continuous=True))
    holm(results)
    summary = {"analysis": "final_paired_statistics_v1", "master_seed": SEED, "bootstrap_resamples": BOOTSTRAPS,
               "permutation_draws_for_continuous_path": PERMUTATIONS, "python_version": platform.python_version(), "numpy_version": np.__version__,
               "multiplicity": {"method": "Holm–Bonferroni", "family_wise_alpha": .05, "tests": sum(r.get("p_value") is not None for r in results),
                                "scope": "All reported calculated endpoints including sensitivity and availability analyses", "confidence_intervals": "nominal 95%, not simultaneous"},
               "inventory": inventory, "results": results, "input_sha256": {p.relative_to(ROOT).as_posix(): h for p, h in protected.items()},
               "limitations": ["Single human rater; 25 paired inputs per semantic task; no inter-rater reliability estimate",
                               "Human ratings are ordinal; sign tests and direction effects do not assume interval spacing",
                               "Structural v2 is a post hoc revision; v1 is retained as sensitivity analysis",
                               "Conditional assessability can induce selection bias; availability yields are distinct endpoints",
                               "TestEval program clustering accounted for; project dependence in other tasks not separately modelled",
                               "No randomized method assignment; sign-flip assumptions do not establish causal effects",
                               "Single generated artifact per method/input; bootstrap intervals are nominal and may degenerate under ceiling/ties",
                               "No trusted assertion oracle; assertion correctness remains unverified"]}
    output.mkdir(parents=True)
    (output / "statistical_summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    import csv
    columns = ("endpoint", "family", "task_type", "criterion", "estimand", "complete_pair_n", "valid_pair_n", "independent_unit_n", "effect", "ci_95", "test", "p_value", "p_holm", "holm_reject_0_05")
    with (output / "statistical_summary.csv").open("x", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
    (output / "protocol.md").write_bytes(Path(__file__).with_name("paired_statistics_protocol.md").read_bytes())
    if any(hashlib.sha256(p.read_bytes()).hexdigest() != h for p, h in protected.items()):
        raise RuntimeError("An original evaluation input changed")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/final_evaluation/paired_statistics_v1")
    args = parser.parse_args()
    summary = analyze(args.output_dir)
    print(json.dumps({"output": str(args.output_dir), "tests": summary["multiplicity"]["tests"],
                      "holm_significant": [r["endpoint"] for r in summary["results"] if r.get("holm_reject_0_05")]}))
