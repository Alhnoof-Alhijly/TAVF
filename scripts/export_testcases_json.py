
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data/processed/testcases_final20.csv"
OUTPUT = ROOT / "data/processed/test_case_tasks.json"

df = pd.read_csv(INPUT, keep_default_na=False)

tasks = []

for _, row in df.iterrows():
    task = {
        "task_id": str(row["task_id"]),
        "task_type": "test_case_generation",
        "source": "TestEval",
        "input": {
            "description": str(row["description"]),
            "python_solution": str(row["python_solution"])
        },
        "reference": {
            "task_num": int(row["task_num"]),
            "func_name": str(row["func_name"]),
            "blocks": str(row["blocks"]),
            "target_lines": str(row["target_lines"])
        },
        "metadata": {
            "difficulty": int(row["difficulty"])
        },
        "expected_output": {
            "type": "python_test_cases",
            "gold_reference": None
        }
    }

    tasks.append(task)

assert len(tasks) == 20, "Expected exactly 20 test cases."
assert len({t["task_id"] for t in tasks}) == 20, "Duplicate task IDs."
assert all(
    t["input"]["description"].strip()
    and t["input"]["python_solution"].strip()
    for t in tasks
), "Missing task input."

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(tasks, f, ensure_ascii=False, indent=2)

print(f"Exported {len(tasks)} test case tasks.")
print(f"Saved to: {OUTPUT}")
