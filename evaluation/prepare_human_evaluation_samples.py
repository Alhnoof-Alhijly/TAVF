"""Reproducible paired human-evaluation packets; no ratings or auto scores."""
import argparse
from collections import defaultdict, Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import platform
import random

ROOT = Path(__file__).resolve().parents[1]
KINDS = ("user_story_refinement", "bug_report_refinement")
SEED = 42


def assemble(artifacts, mapping, *, seed=SEED, per_type=50):
    by_id = {r["artifact_id"]: r for r in artifacts}
    labels = {r["artifact_id"]: r for r in mapping}
    if len(by_id) != len(artifacts) or len(labels) != len(mapping):
        raise ValueError("Duplicate anonymous IDs")
    groups = defaultdict(list)
    for row in artifacts:
        if row["task"]["task_type"] in KINDS:
            groups[row["task"]["task_type"], row["task"]["task_id"]].append(row)
    eligible = {kind: [] for kind in KINDS}
    for (kind, task_id), rows in groups.items():
        if len(rows) != 2:
            continue
        a, b = rows
        if a["task"] != b["task"] or a["pair_id"] != b["pair_id"]:
            raise ValueError("Paired task metadata mismatch")
        if any(not isinstance(r["artifact"], str) or not r["artifact"].strip() for r in rows):
            raise ValueError("Empty paired output")
        methods = []
        for r in rows:
            label = labels[r["artifact_id"]]
            if label["task_id"] != task_id or label["pair_id"] != r["pair_id"] or label["task_type"] != kind:
                raise ValueError("Private mapping mismatch")
            methods.append(label["method"])
        if set(methods) != {"baseline", "tavf"}:
            raise ValueError("Pair must contain one output per method")
        eligible[kind].append(task_id)
    selection = random.Random(seed)
    presentation = random.Random(seed + 1)
    selected = []
    for kind in KINDS:
        population = sorted(eligible[kind])
        if len(population) < per_type:
            raise ValueError("Insufficient complete pairs")
        selected.extend((kind, task_id) for task_id in selection.sample(population, per_type))
    presentation.shuffle(selected)
    packet, private = [], []
    for position, (kind, task_id) in enumerate(selected, 1):
        ids = sorted(r["artifact_id"] for r in groups[kind, task_id])
        presentation.shuffle(ids)  # Order depends on anonymous IDs, never methods.
        sample_id = format(presentation.getrandbits(128), "032x")
        task = by_id[ids[0]]["task"]
        packet.append({"sample_id": sample_id, "presentation_index": position, "task_type": kind,
                       "source_input": deepcopy(task["input"]),
                       "outputs": {label: by_id[ident]["artifact"] for label, ident in zip(("A", "B"), ids)}})
        private.append({"sample_id": sample_id, "task_id": task_id, "task_type": kind, "pair_id": by_id[ids[0]]["pair_id"],
                        "outputs": {label: {"artifact_id": ident, "method": labels[ident]["method"],
                                           "artifact_sha256": hashlib.sha256(by_id[ident]["artifact"].encode()).hexdigest()}
                                    for label, ident in zip(("A", "B"), ids)}})
    if len({r["sample_id"] for r in packet}) != len(packet):
        raise ValueError("Sample ID collision")
    return packet, private, {"seed": seed, "presentation_seed": seed + 1,
                             "eligible_complete_pairs": {kind: len(eligible[kind]) for kind in KINDS},
                             "selected_pairs": dict(Counter(kind for kind, _ in selected))}


def write_jsonl(path, rows):
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")


def build(output, *, seed=SEED):
    if output.exists():
        raise ValueError("Destination exists; refusing to overwrite human-evaluation samples")
    source = ROOT / "results/final_evaluation/blinded_manifest"
    artifact_path = source / "evaluator/artifacts.jsonl"
    mapping_path = source / "private/method_mapping.jsonl"
    raw, key = artifact_path.read_bytes(), mapping_path.read_bytes()
    artifacts = [json.loads(line) for line in raw.decode("utf-8").splitlines()]
    mapping = [json.loads(line) for line in key.decode("utf-8").splitlines()]
    packet, private, info = assemble(artifacts, mapping, seed=seed)
    if info["eligible_complete_pairs"] != {kind: 500 for kind in KINDS}:
        raise ValueError("Expected 500 complete pairs for each selected task type")
    evaluator, private_dir = output / "evaluator", output / "private"
    evaluator.mkdir(parents=True)
    private_dir.mkdir()
    write_jsonl(evaluator / "samples.jsonl", packet)
    write_jsonl(private_dir / "method_mapping.jsonl", private)
    manifest = {"procedure": "human_paired_samples_v1", **info, "paired_inputs": 100, "generated_outputs": 200,
                "selection_rule": "Sorted task IDs; Python Random(seed) samples User Stories then Bug Reports; complete pairs only",
                "presentation_rule": "Separate Random(seed+1) shuffles pairs and sorted anonymous artifact IDs; random opaque sample IDs",
                "python_version": platform.python_version(), "ratings_assigned": False,
                "automatic_scores_included": False, "internal_statuses_included": False,
                "source_artifacts_sha256": hashlib.sha256(raw).hexdigest(),
                "source_mapping_sha256": hashlib.sha256(key).hexdigest(),
                "builder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (private_dir / "selection_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    text = ["# Blinded human-evaluation samples\n\nNo ratings have been assigned. A/B order varies independently by sample.\n"]
    for row in packet:
        text.append(f"\n## Sample {row['presentation_index']}: {row['sample_id']}\n\nTask: {row['task_type']}\n\n### Original input\n")
        for name, value in row["source_input"].items():
            text.append(f"\n{name}:\n\n{value}\n")
        for label, artifact in row["outputs"].items():
            text.append(f"\n### Output {label}\n\n{artifact}\n")
    (evaluator / "samples.md").write_text("".join(text), encoding="utf-8")
    (output / "README.md").write_text(
        f"Selection seed: {seed}; presentation seed: {seed + 1}.\n"
        "100 paired inputs (50 User Stories, 50 Bug Reports), 200 output texts.\n"
        "Share evaluator/ only. Keep private/ and the source method mapping hidden from raters.\n"
        "JSONL is authoritative; Markdown is a readable rendering of the same text.\n"
        "No automatic scores, internal statuses, or human ratings are included.\n"
        "Existing evaluation criteria remain unchanged.\n", encoding="utf-8")
    assert artifact_path.read_bytes() == raw and mapping_path.read_bytes() == key
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/final_evaluation/human_samples_v1")
    args = parser.parse_args()
    print(json.dumps(build(args.output_dir, seed=args.seed)))
