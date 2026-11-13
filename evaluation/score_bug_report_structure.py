"""Independent blinded Bug Report structural scoring; standard library only."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
VERSION = "bug_report_structural_v1"
ALIASES = {
    "Summary": ("summary", "title", "bug summary"),
    "Steps to Reproduce": ("steps", "steps to reproduce", "reproduction steps"),
    "Expected Result": ("expected", "expected result", "expected results", "expected behavior", "expected behaviour"),
    "Actual Result": ("actual", "actual result", "actual results", "actual behavior", "actual behaviour"),
}
LOOKUP = {alias: name for name, aliases in ALIASES.items() for alias in aliases}
MISSING = {"not provided", "not specified", "not available", "unknown", "n/a", "tbd", "[not provided]"}
CONTEXT = {"environment", "technical context", "additional information", "notes", "attachments", "regression"}


def heading(raw):
    clean = re.sub(r"^\s*(?:\#{1,6}\s*|[-*+]\s+|\d+[.)]\s+)", "", raw.strip())
    clean = re.sub(r"[*_`]", "", clean).strip()
    label, colon, body = clean.partition(":")
    label = " ".join(label.split()).casefold()
    if label in LOOKUP:
        return LOOKUP[label], body.strip() if colon else ""
    if (raw.lstrip().startswith("#") or re.fullmatch(r"\s*\*\*[^*]+\*\*\s*", raw)
            or (clean.endswith(":") and len(clean) <= 80) or label in CONTEXT):
        return "other", body.strip()
    return None


def score_text(text):
    if not isinstance(text, str):
        raise TypeError("Artifact must be text")
    sections = {name: [] for name in ALIASES}
    current = None
    for number, raw in enumerate(text.splitlines(), 1):
        if raw.strip().startswith(("```", "~~~")):
            continue
        parsed = heading(raw)
        if parsed is not None:
            name, inline = parsed
            current = None if name == "other" else {"heading_line": number, "heading_text": raw, "body_lines": []}
            if current is not None:
                sections[name].append(current)
                if inline:
                    current["body_lines"].append({"line": number, "text": inline})
        elif current is not None:
            current["body_lines"].append({"line": number, "text": raw})
    criteria = {}
    for name, occurrences in sections.items():
        if len(occurrences) > 1:
            state, score = "duplicate_sections", None
        elif not occurrences:
            state, score = "absent", 0
        else:
            lines = [re.sub(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)", "", line["text"]).strip()
                     for line in occurrences[0]["body_lines"]]
            body = " ".join(" ".join(lines).split()).strip(" \t\r\n.!?:;*_`")
            state, score = (("empty", 0) if not body else
                            ("explicitly_missing", 0) if body.casefold() in MISSING else ("populated", 1))
        criteria[name] = {"score": score, "status": "unassessable" if score is None else "pass" if score else "fail",
                          "state": state, "evidence": {"section_count": len(occurrences), "sections": occurrences}}
    values = [v["score"] for v in criteria.values()]
    return {"criteria": criteria, "structural_score_100": None if None in values else 25 * sum(values),
            "assessable_components": sum(v is not None for v in values)}


def score_record(row):
    return {"artifact_id": row["artifact_id"], "pair_id": row["pair_id"], "task_id": row["task"]["task_id"],
            "procedure": VERSION, "artifact_sha256": hashlib.sha256(row["artifact"].encode()).hexdigest(), **score_text(row["artifact"])}


def run(manifest, output):
    if output.exists():
        raise ValueError("Refusing to overwrite scores")
    original = manifest.read_bytes()
    artifacts = [json.loads(line) for line in original.decode().splitlines()]
    rows = [r for r in artifacts if r["task"]["task_type"] == "bug_report_refinement"]
    if len(rows) != 1000 or len({r["artifact_id"] for r in rows}) != 1000:
        raise ValueError("Expected 1,000 unique Bug Report artifacts")
    scores = [score_record(row) for row in rows]
    summary = {"procedure": VERSION, "artifacts": 1000, "scoring_blinded": True, "internal_validation_used": False,
               "semantic_evaluation": "not_performed", "criterion_counts": {
                   name: dict(Counter(r["criteria"][name]["status"] for r in scores)) for name in ALIASES},
               "total_score_distribution": dict(Counter(str(r["structural_score_100"]) for r in scores)),
               "input_manifest_sha256": hashlib.sha256(original).hexdigest(),
               "scorer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "protocol_sha256": hashlib.sha256(Path(__file__).with_name("bug_report_structural_protocol.md").read_bytes()).hexdigest()}
    output.mkdir(parents=True)
    with (output / "scores.jsonl").open("x", encoding="utf-8", newline="\n") as handle:
        for row in scores:
            handle.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    assert manifest.read_bytes() == original
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "results/final_evaluation/blinded_manifest/evaluator/artifacts.jsonl")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/final_evaluation/bug_report_structural_v1")
    args = parser.parse_args()
    print(json.dumps(run(args.manifest, args.output_dir)))
