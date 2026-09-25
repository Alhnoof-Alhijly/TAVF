
import json
from pathlib import Path
import pandas as pd

# Project paths
ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data/processed/userstories_final20.csv"
OUTPUT = ROOT / "data/processed/user_story_tasks.json"

# Read the selected user stories
df = pd.read_csv(INPUT, keep_default_na=False)

tasks = []

for _, row in df.iterrows():
    task = {
        "task_id": str(row["task_id"]),
        "task_type": "user_story_refinement",
        "source": "Dalpiaz",
        "input": {
            "original_text": str(row["input"])
        },
        "reference": {
            "original_source_file": str(row["source_file"]),
            "original_line_number": int(row["line_number"])
        },
        "metadata": {
            "difficulty": None,
            "word_count": int(row["word_count"])
        },
        "expected_output": {
            "type": "refined_user_story",
            "gold_reference": None
        }
    }

    tasks.append(task)

# Basic checks
assert len(tasks) == 20, "Expected exactly 20 user stories."
assert len({t["task_id"] for t in tasks}) == 20, "Duplicate task IDs."
assert all(t["input"]["original_text"].strip() for t in tasks), "Empty input found."

# Export JSON
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(tasks, f, ensure_ascii=False, indent=2)

print(f"Exported {len(tasks)} user story tasks.")
print(f"Saved to: {OUTPUT}")
