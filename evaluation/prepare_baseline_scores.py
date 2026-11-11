
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

TASKS_FILE = ROOT / "data/processed/experiment_tasks.json"
OUTPUT_FILE = ROOT / "results/baseline/baseline_outputs.json"
SCORES_FILE = ROOT / "results/baseline/baseline_scores.csv"

CRITERIA = {
    "user_story_refinement": [
        "atomicity",
        "minimality",
        "conceptual_soundness",
        "problem_orientation",
        "unambiguity",
        "estimability",
        "means_ends",
        "intent_preservation",
    ],
    "bug_report_refinement": [
        "summary_clarity",
        "steps_completeness",
        "expected_behavior",
        "actual_behavior",
        "technical_context_preservation",
        "organization",
        "conciseness",
        "factual_preservation",
    ],
    "test_case_generation": [
        "syntactic_validity",
        "test_relevance",
        "assertion_quality",
        "input_diversity",
        "edge_case_coverage",
        "requirement_coverage",
        "test_independence",
        "code_clarity",
    ],
}

# Create a consistent set of columns.
all_criteria = sorted({
    criterion
    for group in CRITERIA.values()
    for criterion in group
})

tasks = json.loads(
    TASKS_FILE.read_text(encoding="utf-8")
)

# Check which actual baseline outputs are available.
completed_ids = set()

if OUTPUT_FILE.exists():
    outputs = json.loads(
        OUTPUT_FILE.read_text(encoding="utf-8")
    )
    completed_ids = {
        item["task_id"] for item in outputs
    }

rows = []

for task in tasks:
    row = {
        "task_id": task["task_id"],
        "task_type": task["task_type"],
        "method": "baseline",
        "output_available": (
            task["task_id"] in completed_ids
        ),
        "evaluation_status": "pending",
    }

    # Only the eight relevant criteria will be scored.
    for criterion in all_criteria:
        row[criterion] = ""

    row["quality_score"] = ""
    row["normalized_quality"] = ""
    row["evaluator_id"] = ""
    row["evaluation_notes"] = ""

    rows.append(row)

assert len(rows) == 60, "Expected 60 evaluation rows."
assert len({
    row["task_id"] for row in rows
}) == 60, "Duplicate task IDs."

SCORES_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

# Protect any existing evaluation work.
if SCORES_FILE.exists():
    raise FileExistsError(
        f"Scores file already exists: {SCORES_FILE}"
    )

df = pd.DataFrame(rows)

df.to_csv(
    SCORES_FILE,
    index=False,
    encoding="utf-8-sig",
)

print("Evaluation template created")
print("Total tasks:", len(df))
print("Tasks with outputs:", len(completed_ids))
print("Criteria per task: 8")
print("Maximum quality score: 16")
print("Saved to:", SCORES_FILE)
