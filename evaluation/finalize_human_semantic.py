"""Validate frozen human workbook before joining labels; never assign ratings."""
import argparse
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import csv

from human_semantic_workbook import read_workbook, load_csv, SHEETS, BASE, NOTES, col

ROOT = Path(__file__).resolve().parents[1]


def rating(value):
    if not value.strip():
        return None, "missing"
    try:
        number = Decimal(value.strip())
        if number not in {Decimal(n) for n in range(1, 6)}:
            return None, "invalid"
    except InvalidOperation:
        return None, "invalid"
    return int(number), "valid"


def lines(path, rows):
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")


def finalize(workbook, output):
    if output.exists():
        raise ValueError("Analysis already exists; refusing to overwrite")
    root = ROOT / "results/final_evaluation"
    source_csv = root / "human_semantic_final_v1_1/evaluator/scoring_sheet.csv"
    selection_path = workbook.with_suffix(".selection.json")
    original_bytes = workbook.read_bytes()
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    _, source_rows = load_csv(source_csv)
    lookup = {r["blinded_output_id"]: r for r in source_rows}
    expected = set(selection["blinded_output_ids"])
    book = read_workbook(workbook)
    if set(book) != set(SHEETS) or len(expected) != 100:
        raise ValueError("Expected two sheets and 100 selected outputs")
    validated, issues, seen, pair_labels = [], [], set(), defaultdict(set)
    for sheet, (kind, criteria) in SHEETS.items():
        rows = book[sheet]
        headers = list(BASE) + [title for title, _ in criteria] + [NOTES]
        if [rows[0].get(col(i), "") for i in range(1, len(headers) + 1)] != headers:
            raise ValueError("Workbook headers changed")
        data = [r for r in rows[1:] if any(r.values())]
        if len(data) != 50:
            raise ValueError("Expected exactly 50 output rows per task")
        for cells in data:
            raw = {header: cells.get(col(i), "") for i, header in enumerate(headers, 1)}
            ident = raw["Anonymous ID"]
            if ident not in expected or ident in seen:
                raise ValueError("Unknown, unselected or duplicate output ID")
            seen.add(ident)
            original = lookup[ident]
            if original["task_type"] != kind or any(original[k] != raw[h] for k, h in (
                    ("sample_id", "Sample ID"), ("output_label", "A/B"), ("source_input", "Original source"), ("output_text", "Output"))):
                raise ValueError("Original source/output text or anonymous identity changed")
            pair_labels[kind, raw["Sample ID"]].add(raw["A/B"])
            assessed = {}
            for title, key in criteria:
                value, status = rating(raw[title])
                assessed[key] = {"label": title, "raw_rating": raw[title], "rating": value, "validation": status}
                if status != "valid":
                    issues.append({"blinded_output_id": ident, "criterion": key, "raw_value": raw[title], "issue": status})
            validated.append({"blinded_output_id": ident, "sample_id": raw["Sample ID"], "output_label": raw["A/B"],
                              "task_type": kind, "criteria": assessed, "notes": raw[NOTES], "raw_workbook_row": raw})
    if seen != expected or any(labels != {"A", "B"} for labels in pair_labels.values()):
        raise ValueError("Incomplete or missing selected A/B pair")
    if Counter(kind for kind, _ in pair_labels) != {kind: 25 for kind, _ in SHEETS.values()}:
        raise ValueError("Expected 25 complete pairs per task")
    output.mkdir(parents=True)
    (output / "human_workbook.original.xlsx").write_bytes(original_bytes)
    lines(output / "validated_blinded_ratings.jsonl", validated)
    validation = {"outputs": 100, "outputs_per_task": 50, "complete_pairs_per_task": 25,
                  "rating_cells": sum(len(row["criteria"]) for row in validated),
                  "valid_ratings": sum(v["validation"] == "valid" for row in validated for v in row["criteria"].values()),
                  "issues": issues, "notes_preserved": sum(bool(row["notes"].strip()) for row in validated),
                  "workbook_sha256": hashlib.sha256(original_bytes).hexdigest(),
                  "validation_completed_before_private_mapping_read": True,
                  "ratings_generated_or_changed": False,
                  "note_policy": "Notes preserved verbatim; no semantic interpretation or inferred criterion status."}
    (output / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    # Private method labels are read only after validation and its blinded export.
    private_path = root / "human_samples_v1/private/method_mapping.jsonl"
    private_bytes = private_path.read_bytes()
    mapping = {r["sample_id"]: r for r in (json.loads(line) for line in private_bytes.decode().splitlines())}
    pairs, joined = defaultdict(dict), []
    for row in validated:
        key = mapping[row["sample_id"]]
        label = key["outputs"][row["output_label"]]
        if key["task_type"] != row["task_type"]:
            raise ValueError("Private mapping task mismatch")
        method = label["method"]
        if method not in {"baseline", "tavf"} or method in pairs[row["sample_id"]]:
            raise ValueError("Invalid method mapping")
        enriched = {**row, "method": method, "task_id": key["task_id"], "artifact_id": label["artifact_id"]}
        pairs[row["sample_id"]][method] = enriched
        joined.append(enriched)
    if any(set(p) != {"baseline", "tavf"} for p in pairs.values()):
        raise ValueError("Incomplete method pair")
    lines(output / "private_joined_ratings.jsonl", joined)
    comparisons = []
    for kind, criteria in SHEETS.values():
        group = [r for r in joined if r["task_type"] == kind]
        task_pairs = [p for p in pairs.values() if p["baseline"]["task_type"] == kind]
        for title, criterion in criteria:
            values = {m: [r["criteria"][criterion]["rating"] for r in group if r["method"] == m
                          and r["criteria"][criterion]["validation"] == "valid"] for m in ("baseline", "tavf")}
            differences = [p["tavf"]["criteria"][criterion]["rating"] - p["baseline"]["criteria"][criterion]["rating"]
                           for p in task_pairs if all(p[m]["criteria"][criterion]["validation"] == "valid" for m in ("baseline", "tavf"))]
            comparisons.append({"task_type": kind, "criterion": title,
                                "baseline_mean": sum(values["baseline"]) / len(values["baseline"]) if values["baseline"] else None,
                                "baseline_n": len(values["baseline"]),
                                "tavf_mean": sum(values["tavf"]) / len(values["tavf"]) if values["tavf"] else None,
                                "tavf_n": len(values["tavf"]), "paired_n": len(differences),
                                "paired_mean_difference": sum(differences) / len(differences) if differences else None,
                                "tavf_higher": sum(d > 0 for d in differences), "ties": sum(d == 0 for d in differences),
                                "baseline_higher": sum(d < 0 for d in differences)})
    report = {"procedure": "human_semantic_v1_1_final", "outputs": 100, "pairs_per_task": 25,
              "difference_definition": "TAVF minus Baseline on pairs with valid ratings; missing/invalid never imputed",
              "single_rater": True, "issues": issues, "comparisons": comparisons,
              "workbook_sha256": validation["workbook_sha256"], "private_mapping_sha256": hashlib.sha256(private_bytes).hexdigest()}
    (output / "comparison.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    with (output / "comparison.csv").open("x", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(comparisons[0]))
        writer.writeheader()
        writer.writerows(comparisons)
    assert workbook.read_bytes() == original_bytes and private_path.read_bytes() == private_bytes
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, default=ROOT / "results/final_evaluation/human_semantic_final_v1_1/evaluator/single_rater.xlsx")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/final_evaluation/human_semantic_comparison_v1_1")
    args = parser.parse_args()
    print(json.dumps(finalize(args.workbook, args.output_dir)))
