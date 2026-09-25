
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data/processed"

FILES = [
    DATA / "user_story_tasks.json",
    DATA / "bug_report_tasks.json",
    DATA / "test_case_tasks.json",
]

OUTPUT = DATA / "experiment_tasks.json"
SCHEMA = ROOT / "data/task_schema.json"

# Load the schema and task files
with SCHEMA.open(encoding="utf-8") as f:
    schema = json.load(f)

Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema)

tasks = []

for path in FILES:
    with path.open(encoding="utf-8") as f:
        batch = json.load(f)

    assert len(batch) == 20, f"{path.name}: expected 20 tasks"
    tasks.extend(batch)

# Check the complete experimental dataset
assert len(tasks) == 60, "Expected exactly 60 tasks."

ids = [task["task_id"] for task in tasks]
assert len(set(ids)) == 60, "Duplicate task IDs found."

counts = Counter(task["task_type"] for task in tasks)

expected_counts = {
    "user_story_refinement": 20,
    "bug_report_refinement": 20,
    "test_case_generation": 20,
}

assert counts == expected_counts, "Incorrect task distribution."

errors = [
    (task["task_id"], error.message)
    for task in tasks
    for error in validator.iter_errors(task)
]

assert not errors, f"Schema validation failed: {errors}"

# Export the unified dataset
with OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(tasks, f, ensure_ascii=False, indent=2)

print("Total tasks:", len(tasks))
print("Distribution:", dict(counts))
print("Duplicate IDs: 0")
print("Validation errors: 0")
print("Saved to:", OUTPUT)
