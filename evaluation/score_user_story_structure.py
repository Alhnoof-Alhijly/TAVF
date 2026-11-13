"""Independent text-only structural scoring; no TAVF imports or model calls."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
VERSION = "user_story_structural_v1"
PREFIX = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+|\#{1,6}\s+)")
START = re.compile(r"(?:^|[.!?]\s+|\n\s*)(?:(?:[-*+]|\d+[.)])\s+)?As\s+(?:a|an)\b", re.I)
FORM = re.compile(r"\AAs\s+(?:a|an)\s+(?P<role>.*?)\s*,?\s*\bI\s+want\b\s*"
                  r"(?P<goal>.*?)\s*,?\s*\bso\s+that\b\s*(?P<benefit>.*?)\s*\Z", re.I)
PLACEHOLDERS = {"", "not provided", "n/a", "tbd", "[role]", "[goal]", "[benefit]"}


def populated(value):
    return value.strip(" \t\r\n,.!?").casefold() not in PLACEHOLDERS


def criterion(score, evidence):
    return {"score": score, "status": "unassessable" if score is None else "pass" if score else "fail",
            "evidence": evidence}


def score_text(text):
    if not isinstance(text, str):
        raise TypeError("Artifact must be text")
    lines, fences, prefixes, seen, duplicates = [], [], [], {}, []
    for number, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith(("```", "~~~")):
            fences.append({"line": number, "text": line})
            continue
        if PREFIX.match(line):
            prefixes.append({"line": number, "text": line})
        cleaned = PREFIX.sub("", line).strip()
        if cleaned:
            fingerprint = " ".join(cleaned.split()).casefold()
            if fingerprint in seen:
                duplicates.append({"line": number, "duplicate_of_line": seen[fingerprint], "text": line})
            seen.setdefault(fingerprint, number)
            lines.append(cleaned)
    starts = [{"span": list(m.span()), "text": m.group()} for m in START.finditer("\n".join(lines))]
    normalized = " ".join(" ".join(lines).split())
    match = FORM.fullmatch(normalized)
    slots = ({name: {"value": match[name].strip(" ,"), "span": list(match.span(name)),
                     "populated": populated(match[name])} for name in ("role", "goal", "benefit")}
             if match else {})
    well_formed = len(starts) == 1 and bool(slots) and all(v["populated"] for v in slots.values())
    wf_evidence = {"rule": "WF1", "story_start_count": len(starts), "slots": slots,
                   "whole_text_parsed": match is not None}
    request_region = re.split(r"\bso\s+that\b", normalized, maxsplit=1, flags=re.I)[0]
    requests = [{"span": list(m.span()), "text": m.group()}
                for m in re.finditer(r"\bI\s+want\b", request_region, re.I)]
    atomic = (0 if len(starts) > 1 or len(requests) > 1 else
              1 if match and slots["goal"]["populated"] and len(requests) == 1 else None)
    extra_sentences = [{"span": list(m.span()), "text": m.group()}
                       for m in re.finditer(r"[.!?]\s+(?=[A-Z0-9])", normalized)]
    minimal_signals = {"fences": fences, "line_prefixes": prefixes, "duplicate_lines": duplicates,
                       "multiple_story_starts": starts if len(starts) > 1 else [],
                       "additional_sentence_boundaries": extra_sentences}
    minimal = 0 if any(minimal_signals.values()) else 1 if well_formed else None
    scores = {"Well-formed": criterion(int(well_formed), wf_evidence),
              "Atomic": criterion(atomic, {"rule": "A1", "story_start_count": len(starts),
                                           "request_region": request_region, "request_markers": requests,
                                           "unassessable_reason": "No populated parsed goal" if atomic is None else None}),
              "Minimal": criterion(minimal, {"rule": "M1", **minimal_signals,
                                             "unassessable_reason": "No populated whole-story parse" if minimal is None else None})}
    return {"criteria": scores, "normalized_text": normalized,
            "structural_total": sum(v["score"] for v in scores.values())
            if all(v["score"] is not None for v in scores.values()) else None,
            "structural_maximum": 3, "assessable_criteria": sum(v["score"] is not None for v in scores.values())}


def score_record(row):
    return {"artifact_id": row["artifact_id"], "pair_id": row["pair_id"], "task_id": row["task"]["task_id"],
            "procedure": VERSION, "artifact_sha256": hashlib.sha256(row["artifact"].encode()).hexdigest(),
            **score_text(row["artifact"])}


def run(manifest, output):
    if output.exists():
        raise ValueError("Destination exists; refusing to overwrite scores")
    manifest_bytes = manifest.read_bytes()
    rows = [json.loads(line) for line in manifest_bytes.decode("utf-8").splitlines()]
    stories = [r for r in rows if r["task"]["task_type"] == "user_story_refinement"]
    if len(stories) != 1000 or len({r["artifact_id"] for r in stories}) != 1000:
        raise ValueError("Expected 1,000 unique blinded User Story artifacts")
    scored = [score_record(row) for row in stories]
    counts = {name: dict(Counter(row["criteria"][name]["status"] for row in scored))
              for name in ("Well-formed", "Atomic", "Minimal")}
    protocol = Path(__file__).with_name("user_story_structural_protocol.md")
    summary = {"procedure": VERSION, "scored_artifacts": len(scored), "criterion_counts": counts,
               "complete_structural_totals": sum(row["structural_total"] is not None for row in scored),
               "score_definition": "1=surface pass; 0=surface violation; null=unassessable; total 0..3 only if all assessed",
               "semantic_evaluation": "not_performed", "internal_validation_used": False,
               "input_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
               "scorer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "protocol_sha256": hashlib.sha256(protocol.read_bytes()).hexdigest()}
    output.mkdir(parents=True)
    with (output / "scores.jsonl").open("x", encoding="utf-8", newline="\n") as handle:
        for row in scored:
            handle.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    if manifest.read_bytes() != manifest_bytes:
        raise RuntimeError("Blinded manifest changed")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "results/final_evaluation/blinded_manifest/evaluator/artifacts.jsonl")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/final_evaluation/user_story_structural_v1")
    args = parser.parse_args()
    print(json.dumps(run(args.manifest, args.output_dir)))
