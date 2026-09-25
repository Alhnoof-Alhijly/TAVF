
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data/processed/bugreports_final20.csv"
OUTPUT = ROOT / "data/processed/bug_report_tasks.json"

df = pd.read_csv(INPUT, keep_default_na=False)

tasks = []

for _, row in df.iterrows():
    task = {
        "task_id": str(row["task_id"]),
        "task_type": "bug_report_refinement",
        "source": "jag2023/Bug_report_Final_new_dataset_2024",
        "input": {
            "original_text": str(row["input"])
        },
        "reference": {
            "bug_id": str(row["Bug ID"]),
            "product": str(row["Product"]),
            "steps_to_reproduce": str(row["Steps to Reproduce"]),
            "expected_result": str(row["Expected_Res"]),
            "actual_result": str(row["Actual_Res"])
        },
        "metadata": {
            "difficulty": None,
            "word_count": int(row["word_count"])
        },
        "expected_output": {
            "type": "refined_bug_report",
            "gold_reference": None
        }
    }

    tasks.append(task)

assert len(tasks) == 20, "Expected exactly 20 bug reports."
assert len({t["task_id"] for t in tasks}) == 20, "Duplicate task IDs."
assert all(
    t["input"]["original_text"].strip() for t in tasks
), "Empty bug report found."

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(tasks, f, ensure_ascii=False, indent=2)

print(f"Exported {len(tasks)} bug report tasks.")
print(f"Saved to: {OUTPUT}")
