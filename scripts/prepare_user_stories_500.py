"""Select local user-story inputs without rewriting source text or calling APIs."""

from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import random
import re
import unicodedata

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data/processed/userstories_candidates.csv"
RAW = ROOT / "data/raw/dalpiaz_userstories"
OUTPUT = ROOT / "data/processed/user_stories_500.json"
SEED = 42
SIZE = 500
CRITERIA = [
    "Nonempty role-led story beginning with 'As ' (case insensitive).",
    "10-40 whitespace-delimited words inclusive; at least one alphabetic character.",
    "No control characters or obvious BOM/replacement/mojibake artifacts.",
    "Deduplicate using casefolded, whitespace-collapsed text; retain first source occurrence.",
    "Preserve selected original text verbatim; do not require a complete benefit clause.",
]


def exclusion_reason(text):
    if not isinstance(text, str) or not text.strip():
        return "empty"
    if (any(unicodedata.category(char) == "Cc" for char in text)
            or any(marker in text for marker in ("\ufeff", "\ufffd", "ï»¿", "â€", "Ã"))):
        return "encoding_or_control"
    if not 10 <= len(text.split()) <= 40:
        return "word_count"
    if not re.match(r"^as\s+", text, flags=re.IGNORECASE) or not any(char.isalpha() for char in text):
        return "non_story_fragment"
    return None


def identity(text):
    return " ".join(text.split()).casefold()


def select(rows, digest):
    """Pure deterministic selection; input rows and their text remain unchanged."""
    eligible, seen, excluded = [], set(), Counter()
    for row in rows:
        text = row["original_story"]
        reason = exclusion_reason(text)
        if reason:
            excluded[reason] += 1
            continue
        key = identity(text)
        if key in seen:
            excluded["duplicate"] += 1
            continue
        seen.add(key)
        eligible.append(row)
    if len(eligible) < SIZE:
        raise ValueError("Fewer than 500 eligible unique user stories")
    chosen = random.Random(SEED).sample(eligible, SIZE)
    tasks = []
    for rank, row in enumerate(chosen, 1):
        filename, line = row["source_file"], int(row["line_number"])
        tasks.append({
            "task_id": f"US500-{Path(filename).stem}-L{line:04d}",
            "task_type": "user_story_refinement", "source": "Dalpiaz",
            "input": {"original_text": row["original_story"]},
            "reference": {"original_source_file": filename, "original_line_number": line},
            "metadata": {
                "difficulty": None, "word_count": len(row["original_story"].split()),
                "selection": {"seed": SEED, "sample_rank": rank,
                              "method": "random.Random(42).sample; source CSV order",
                              "source_file": SOURCE.relative_to(ROOT).as_posix(),
                              "source_sha256": digest, "criteria": CRITERIA.copy()},
            },
            "expected_output": {"type": "refined_user_story", "gold_reference": None},
        })
    return tasks, {"raw_records": len(rows), "eligible_unique": len(eligible),
                   "excluded": dict(sorted(excluded.items())), "selected": len(tasks),
                   "source_files_selected": len({row["source_file"] for row in chosen})}


def validate(tasks, rows, schema):
    validator = Draft202012Validator(schema)
    if len(tasks) != SIZE or len({task["task_id"] for task in tasks}) != SIZE:
        raise ValueError("Expected 500 distinct task IDs")
    if len({identity(task["input"]["original_text"]) for task in tasks}) != SIZE:
        raise ValueError("Duplicate story text")
    source = {(row["source_file"], int(row["line_number"])): row["original_story"] for row in rows}
    for rank, task in enumerate(tasks, 1):
        validator.validate(task)
        reference = task["reference"]
        key = reference["original_source_file"], reference["original_line_number"]
        text = task["input"]["original_text"]
        if source.get(key) != text or exclusion_reason(text):
            raise ValueError("Unusable story or changed source text")
        if (task["task_type"] != "user_story_refinement" or task["source"] != "Dalpiaz"
                or task["metadata"]["word_count"] != len(text.split())
                or task["metadata"]["selection"]["sample_rank"] != rank):
            raise ValueError("Invalid task metadata")


def load_source():
    raw = SOURCE.read_bytes()
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    # Match the original preparation script's cp1252 decoding and line stripping.
    originals = {path.name: path.read_text(encoding="cp1252").splitlines()
                 for path in sorted(RAW.glob("*.txt"))}
    for row in rows:
        line = int(row["line_number"])
        if originals[row["source_file"]][line - 1].strip() != row["original_story"]:
            raise ValueError("Candidate differs from original raw source")
    return rows, hashlib.sha256(raw).hexdigest()


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
