"""Convert selected TestEval targets to existing TAVF tasks; execute no code."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parent.parent
SELECTION = ROOT / "data/processed/testeval_targets_500.json"
PROGRAMS = ROOT / "data/raw/testeval/data/leetcode-py-all.jsonl"
OUTPUT = ROOT / "data/processed/test_cases_500.json"


def convert(selection, programs, selection_hash):
    indexed = {row["task_num"]: row for row in programs}
    if len(indexed) != len(programs):
        raise ValueError("Duplicate source programs")
    tasks = []
    for instance in selection["instances"]:
        row = indexed[instance["task_num"]]
        original = instance["input"]
        if any(original[key] != row[key] for key in ("description", "python_solution", "func_name")):
            raise ValueError("Selected program differs from source")
        kind, target, index = instance["target_type"], original["target"], instance["source_target_index"]
        if kind != original["target_type"] or instance["difficulty"] != row["difficulty"]:
            raise ValueError("Selected metadata differs from source")
        if type(index) is not int or index < 0:
            raise ValueError("Invalid target index")
        if kind == "line":
            expected = {"line": row["target_lines"][index]}
        elif kind == "branch":
            block = row["blocks"][index]
            expected = {"start": block["start"], "end": block["end"]}
        elif kind == "path":
            expected = {"execution_path": row["sampled_paths"][index],
                        "condition_path": row["sampled_condition_paths"][index]}
        else:
            raise ValueError("Unsupported target type")
        if target != expected:
            raise ValueError("Selected target differs from source")
        tasks.append({
            "task_id": instance["instance_id"], "task_type": "test_case_generation",
            "source": "TestEval",
            "input": {"description": original["description"], "python_solution": original["python_solution"]},
            "reference": {
                "task_num": row["task_num"], "func_name": original["func_name"],
                # Preserve the existing exported task convention for these fields.
                "blocks": str(row["blocks"]), "target_lines": str(row["target_lines"]),
                "target_type": kind, "target": deepcopy(target),
                "source_target_index": index,
            },
            "metadata": {
                "difficulty": instance["difficulty"], "task_title": instance["task_title"],
                "selection_file": SELECTION.relative_to(ROOT).as_posix(),
                "selection_sha256": selection_hash,
                "selection": deepcopy(selection["metadata"]),
            },
            "expected_output": {"type": "python_test_cases", "gold_reference": None},
        })
    if len(tasks) != 500 or len({task["task_id"] for task in tasks}) != 500:
        raise ValueError("Expected 500 unique tasks")
    if len({(task["reference"]["task_num"], task["reference"]["target_type"]) for task in tasks}) != 500:
        raise ValueError("Repeated program/target type")
    return tasks


def main():
    raw_selection, raw_programs = SELECTION.read_bytes(), PROGRAMS.read_bytes()
    selection = json.loads(raw_selection)
    if hashlib.sha256(raw_programs).hexdigest() != selection["metadata"]["source_sha256"]:
        raise ValueError("Original dataset hash differs from selection provenance")
    programs = [json.loads(line) for line in raw_programs.decode("utf-8").splitlines() if line.strip()]
    tasks = convert(selection, programs, hashlib.sha256(raw_selection).hexdigest())
    validator = Draft202012Validator(json.loads((ROOT / "data/task_schema.json").read_text(encoding="utf-8")))
    for task in tasks:
        validator.validate(task)
    with OUTPUT.open("x", encoding="utf-8") as handle:
        json.dump(tasks, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(f"Converted {len(tasks)} schema-valid tasks to {OUTPUT.name}")


if __name__ == "__main__":
    main()
