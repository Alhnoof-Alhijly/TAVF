"""Anonymous v2 structural scoring, independently of framework validation."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
VERSION = "user_story_structural_v2"
CRITERIA = ("Structural Form", "Information Completeness", "Atomic", "Minimal")
PREFIX = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")
OPEN = re.compile(r"^As\s+(?:a|an)\b\s*", re.I)
EMBEDDED = re.compile(r"\bAs\s+(?:a|an)\b", re.I)
REQUEST = re.compile(r"\bI\s+want\b", re.I)
BENEFIT = re.compile(r"\bso\s+that\b", re.I)
MISSING = {"not provided", "n/a", "tbd", "[role]", "[goal]", "[benefit]"}


def result(score, evidence):
    return {"score": score, "status": "unassessable" if score is None else "pass" if score else "fail", "evidence": evidence}


def aggregate(values):
    return 0 if 0 in values else 1 if values and all(v == 1 for v in values) else None


def slot(value):
    if value is None:
        return {"value": None, "state": "unparseable"}
    clean = value.strip(" \t\r\n,.!?")
    return {"value": value.strip(" ,"), "state": "empty" if not clean else
            "explicitly_missing" if clean.casefold() in MISSING else "populated"}


def score_text(text):
    if not isinstance(text, str):
        raise TypeError("Artifact must be text")
    segments, commentary, presentation = [], [], []
    for line_number, raw in enumerate(text.splitlines(), 1):
        if raw.strip().startswith(("```", "~~~")):
            presentation.append({"line": line_number, "text": raw})
            continue
        clean = PREFIX.sub("", raw).strip()
        if clean != raw.strip():
            presentation.append({"line": line_number, "text": raw})
        if not clean:
            continue
        for part in re.split(r"(?<=[.!?])\s+(?=As\s+(?:a|an)\b)", clean, flags=re.I):
            if OPEN.match(part):
                segments.append({"text": part, "lines": [line_number]})
            elif segments and not re.search(r"[.!?]$", segments[-1]["text"]):
                segments[-1]["text"] += " " + part
                segments[-1]["lines"].append(line_number)
            else:
                commentary.append({"line": line_number, "text": part})
    stories, seen = [], {}
    for number, segment in enumerate(segments, 1):
        normalized = " ".join(segment["text"].split())
        opening = OPEN.match(normalized)
        request = REQUEST.search(normalized)
        benefit = BENEFIT.search(normalized, request.end() if request else 0)
        ambiguous = len(EMBEDDED.findall(normalized)) > 1
        valid_order = bool(request and benefit and opening.end() <= request.start() < benefit.start())
        slots = {"role": slot(normalized[opening.end():request.start()] if request else None),
                 "goal": slot(normalized[request.end():benefit.start()] if valid_order else
                              normalized[request.end():] if request else None),
                 "benefit": slot(normalized[benefit.end():] if benefit else None)}
        states = [s["state"] for s in slots.values()]
        form = None if ambiguous else int(valid_order and all(s in {"populated", "explicitly_missing"} for s in states))
        information = (None if ambiguous else 0 if any(s in {"empty", "explicitly_missing"} for s in states)
                       else None if "unparseable" in states else 1)
        region = normalized[:benefit.start()] if benefit else normalized
        markers = [{"span": list(m.span()), "text": m.group()} for m in REQUEST.finditer(region)]
        atomic = None if ambiguous else 0 if len(markers) > 1 else 1 if len(markers) == 1 and slots["goal"]["state"] == "populated" else None
        fingerprint = normalized.casefold()
        duplicate = seen.get(fingerprint)
        seen.setdefault(fingerprint, number)
        minimal = 0 if duplicate is not None else None if ambiguous else 1
        stories.append({"story_index": number, "text": segment["text"], "lines": segment["lines"], "normalized_text": normalized,
                        "slots": slots, "ambiguous_boundaries": ambiguous,
                        "criteria": {"Structural Form": result(form, {"delimiters_in_order": valid_order, "slots": slots}),
                                     "Information Completeness": result(information, {"slot_states": {k: v["state"] for k, v in slots.items()}}),
                                     "Atomic": result(atomic, {"request_region": region, "request_markers": markers, "goal_state": slots["goal"]["state"]}),
                                     "Minimal": result(minimal, {"duplicate_of_story": duplicate, "ambiguous_boundaries": ambiguous})}})
    criteria = {}
    for name in CRITERIA:
        scores = [s["criteria"][name]["score"] for s in stories]
        score = aggregate(scores)
        if not stories and name == "Structural Form":
            score = 0
        if name == "Minimal" and commentary:
            score = 0
        criteria[name] = result(score, {"story_scores": scores, "commentary": commentary if name == "Minimal" else []})
    return {"criteria": criteria, "stories": stories, "story_count": len(stories), "presentation": presentation,
            "commentary": commentary, "slot_counts": dict(Counter(v["state"] for s in stories for v in s["slots"].values()))}


def score_record(row):
    return {"artifact_id": row["artifact_id"], "pair_id": row["pair_id"], "task_id": row["task"]["task_id"],
            "procedure": VERSION, "artifact_sha256": hashlib.sha256(row["artifact"].encode()).hexdigest(), **score_text(row["artifact"])}


def run(manifest, output):
    if output.exists():
        raise ValueError("Destination exists; refusing to overwrite scores")
    original = manifest.read_bytes()
    rows = [json.loads(line) for line in original.decode().splitlines()]
    stories = [r for r in rows if r["task"]["task_type"] == "user_story_refinement"]
    if len(stories) != 1000 or len({r["artifact_id"] for r in stories}) != 1000:
        raise ValueError("Expected 1,000 unique User Story artifacts")
    scores = [score_record(row) for row in stories]
    slots = Counter()
    for row in scores:
        slots.update(row["slot_counts"])
    protocol = Path(__file__).with_name("user_story_structural_protocol_v2.md")
    summary = {"procedure": VERSION, "artifacts": 1000, "stories": sum(s["story_count"] for s in scores),
               "criterion_counts": {c: {status: sum(s["criteria"][c]["status"] == status for s in scores)
                                        for status in ("pass", "fail", "unassessable")} for c in CRITERIA},
               "slot_counts": dict(slots), "slot_denominator": sum(slots.values()),
               "scoring_blinded": True, "internal_validation_used": False, "semantic_evaluation": "not_performed",
               "input_manifest_sha256": hashlib.sha256(original).hexdigest(),
               "scorer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "protocol_sha256": hashlib.sha256(protocol.read_bytes()).hexdigest()}
    output.mkdir(parents=True)
    with (output / "scores.jsonl").open("x", encoding="utf-8", newline="\n") as handle:
        for score in scores:
            handle.write(json.dumps(score, ensure_ascii=False, allow_nan=False) + "\n")
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    assert manifest.read_bytes() == original
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "results/final_evaluation/blinded_manifest/evaluator/artifacts.jsonl")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/final_evaluation/user_story_structural_v2")
    args = parser.parse_args()
    print(json.dumps(run(args.manifest, args.output_dir)))
