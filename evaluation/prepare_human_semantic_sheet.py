"""Create blank semantic-rating rows using public human samples only."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import uuid

ROOT = Path(__file__).resolve().parents[1]
CRITERIA = {"user_story_refinement": ("conceptually_sound", "problem_oriented", "unambiguous", "source_fidelity"),
            "bug_report_refinement": ("clarity", "reproducibility", "factual_consistency")}
ALL = tuple(c for criteria in CRITERIA.values() for c in criteria)
META = ("blinded_output_id", "sample_id", "presentation_index", "task_type", "output_label", "applicable_criteria")
FIELDS = list(META) + [name + suffix for name in ALL for suffix in ("_rating", "_status", "_evidence")] + ["rater_id", "assessment_date", "notes"]


def blank_rows(samples):
    if len({r["sample_id"] for r in samples}) != len(samples):
        raise ValueError("Duplicate sample ID")
    rows = []
    for sample in samples:
        if sample["task_type"] not in CRITERIA or set(sample["outputs"]) != {"A", "B"}:
            raise ValueError("Unexpected task or output labels")
        for label in ("A", "B"):
            if not isinstance(sample["outputs"][label], str) or not sample["outputs"][label].strip():
                raise ValueError("Empty blinded output")
            row = {field: "" for field in FIELDS}
            row.update(blinded_output_id=uuid.uuid5(uuid.NAMESPACE_URL, "tavf-human-semantic-v1/" + sample["sample_id"] + "/" + label).hex,
                       sample_id=sample["sample_id"], presentation_index=sample["presentation_index"],
                       task_type=sample["task_type"], output_label=label,
                       applicable_criteria=";".join(CRITERIA[sample["task_type"]]))
            rows.append(row)
    return rows


def build(samples_path, output):
    if output.exists():
        raise ValueError("Destination exists; refusing to overwrite scoring sheets")
    original = samples_path.read_bytes()
    samples = [json.loads(line) for line in original.decode("utf-8").splitlines()]
    counts = {kind: sum(s["task_type"] == kind for s in samples) for kind in CRITERIA}
    if len(samples) != 100 or counts != {kind: 50 for kind in CRITERIA}:
        raise ValueError("Expected 50 paired samples per task type")
    rows = blank_rows(samples)
    output.mkdir(parents=True)
    path = output / "blank_scoring_sheet.csv"
    with path.open("x", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    rubric = Path(__file__).with_name("human_semantic_rubric_v1.md")
    (output / "rubric.md").write_bytes(rubric.read_bytes())
    info = {"procedure": "human_semantic_v1", "sample_pairs": 100, "outputs": len(rows), "task_pairs": counts,
            "samples_file": samples_path.relative_to(ROOT).as_posix(), "samples_sha256": hashlib.sha256(original).hexdigest(),
            "rubric_sha256": hashlib.sha256(rubric.read_bytes()).hexdigest(),
            "builder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "private_mapping_read": False, "ratings_assigned": False,
            "rating_values": [1, 2, 3, 4, 5], "statuses": ["rated", "uncertain", "unassessable"]}
    (output / "sheet_manifest.json").write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        loaded = list(csv.DictReader(handle))
    if len(loaded) != 200 or len({r["blinded_output_id"] for r in loaded}) != 200:
        raise ValueError("Invalid scoring sheet inventory")
    assert all(not r[k] for r in loaded for k in FIELDS if k not in META)
    assert samples_path.read_bytes() == original
    return info


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=Path, default=ROOT / "results/final_evaluation/human_samples_v1/evaluator/samples.jsonl")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/final_evaluation/human_semantic_v1/evaluator")
    args = parser.parse_args()
    print(json.dumps(build(args.samples, args.output_dir)))
