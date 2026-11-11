"""Prepare reproducible Bug Report Refinement inputs from local Parquet only."""

from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import unicodedata

from jsonschema import Draft202012Validator
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data/raw/bugsrepo/train-00000-of-00001.parquet"
OUTPUT = ROOT / "data/processed/bug_reports_500.json"
DATASET = "jag2023/Bug_report_Final_new_dataset_2024"
SEED, SIZE = 42, 500
REFERENCE_FIELDS = {"bug_id": "Bug ID", "product": "Product",
                    "steps_to_reproduce": "Steps to Reproduce",
                    "expected_result": "Expected_Res", "actual_result": "Actual_Res"}
CRITERIA = [
    "Nonempty original Comment Text; 40-250 whitespace-delimited words inclusive.",
    "Exclude placeholder-only text, replacement/BOM artifacts and controls except newline, carriage return and tab.",
    "Require a source bug ID, product and nonempty source reference fields.",
    "Deduplicate bug IDs and casefolded whitespace-collapsed comments; retain first eligible source occurrence.",
    "Preserve original comments and reference annotations verbatim; do not infer missing facts.",
]


def identity(text):
    return " ".join(text.split()).casefold()


def exclusion_reason(row):
    text = row.get("Comment Text")
    if not isinstance(text, str) or identity(text) in {"", "nan", "none", "null", "n/a", "not provided"}:
        return "empty_or_placeholder"
    if (any(unicodedata.category(c) == "Cc" and c not in "\n\r\t" for c in text)
            or any(marker in text for marker in ("\ufffd", "\ufeff", "\u00ef\u00bb\u00bf"))):
        return "encoding_or_control"
    if not 40 <= len(text.split()) <= 250:
        return "word_count"
    for field in REFERENCE_FIELDS.values():
        value = row.get(field)
        if value is None or pd.isna(value) or str(value).strip().casefold() in {"", "nan", "none", "null", "n/a"}:
            return "missing_reference"
    return None


def select(rows, digest):
    eligible, seen_ids, seen_comments, excluded = [], set(), set(), Counter()
    for index, row in enumerate(rows):
        reason = exclusion_reason(row)
        if reason:
            excluded[reason] += 1
            continue
        bug_id, key = str(row["Bug ID"]).strip(), identity(row["Comment Text"])
        if bug_id in seen_ids or key in seen_comments:
            excluded["duplicate"] += 1
            continue
        seen_ids.add(bug_id)
        seen_comments.add(key)
        eligible.append((index, row))
    if len(eligible) < SIZE:
        raise ValueError("Fewer than 500 eligible unique bug reports")
    summary = {"raw_records": len(rows), "eligible_unique": len(eligible),
               "excluded": dict(sorted(excluded.items())), "selected": SIZE}
    tasks = []
    for rank, (index, row) in enumerate(random.Random(SEED).sample(eligible, SIZE), 1):
        tasks.append({
            "task_id": "BR500-" + str(row["Bug ID"]),
            "task_type": "bug_report_refinement", "source": DATASET,
            "input": {"original_text": row["Comment Text"]},
            "reference": {key: str(row[field]) for key, field in REFERENCE_FIELDS.items()},
            "metadata": {
                "difficulty": None, "word_count": len(row["Comment Text"].split()),
                "selection": {"seed": SEED, "sample_rank": rank, "source_row_index": index,
                              "source_file": SOURCE.relative_to(ROOT).as_posix(),
                              "source_sha256": digest, "method": "random.Random(42).sample; Parquet row order",
                              "criteria": CRITERIA.copy(), "exclusions": summary["excluded"].copy(),
                              "raw_records": len(rows), "eligible_unique": len(eligible)},
                "reference_status": "source_annotations_not_verified",
            },
            "expected_output": {"type": "refined_bug_report", "gold_reference": None},
        })
    summary["products_selected"] = len({task["reference"]["product"] for task in tasks})
    return tasks, summary


def validate(tasks, rows, schema):
    validator = Draft202012Validator(schema)
    if len(tasks) != SIZE or len({task["task_id"] for task in tasks}) != SIZE:
        raise ValueError("Expected 500 distinct task IDs")
    if len({identity(task["input"]["original_text"]) for task in tasks}) != SIZE:
        raise ValueError("Duplicate report text")
    if len({task["reference"]["bug_id"] for task in tasks}) != SIZE:
        raise ValueError("Duplicate bug IDs")
    for rank, task in enumerate(tasks, 1):
        validator.validate(task)
        selection = task["metadata"]["selection"]
        index = selection["source_row_index"]
        if type(index) is not int or not 0 <= index < len(rows):
            raise ValueError("Invalid source row")
        row = rows[index]
        if exclusion_reason(row) or task["input"]["original_text"] != row["Comment Text"]:
            raise ValueError("Unusable or changed source text")
        if task["reference"] != {key: str(row[field]) for key, field in REFERENCE_FIELDS.items()}:
            raise ValueError("Changed reference facts")
        if (task["task_type"] != "bug_report_refinement" or task["source"] != DATASET
                or task["metadata"]["word_count"] != len(row["Comment Text"].split())
                or selection["seed"] != SEED or selection["sample_rank"] != rank):
            raise ValueError("Invalid task metadata")


def load_source():
    return pd.read_parquet(SOURCE).to_dict("records"), hashlib.sha256(SOURCE.read_bytes()).hexdigest()


def main():
    rows, digest = load_source()
    tasks, summary = select(rows, digest)
    schema = json.loads((ROOT / "data/task_schema.json").read_text(encoding="utf-8"))
    validate(tasks, rows, schema)
    with OUTPUT.open("x", encoding="utf-8") as handle:
        json.dump(tasks, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
