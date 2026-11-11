
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TASKS_FILE = ROOT / "data/processed/experiment_tasks.json"
OUTPUTS_FILE = ROOT / "results/baseline/baseline_outputs.json"

RUBRIC_FILES = {
    "user_story_refinement": "user_story_rubric.md",
    "bug_report_refinement": "bug_report_rubric.md",
    "test_case_generation": "test_case_rubric.md",
}


def main():
    # Load the original experimental tasks
    tasks = json.loads(
        TASKS_FILE.read_text(encoding="utf-8")
    )

    task_lookup = {
        task["task_id"]: task
        for task in tasks
    }

    assert len(tasks) == 60
    assert len(task_lookup) == 60

    # Check the evaluation rubrics
    for filename in RUBRIC_FILES.values():
        path = ROOT / "evaluation" / filename
        assert path.exists(), f"Missing rubric: {filename}"

    print("Experimental tasks:", len(tasks))
    print("Evaluation rubrics: 3")

    # Actual API execution has not started yet
    if not OUTPUTS_FILE.exists():
        print("Baseline outputs: Not generated yet")
        print("Evaluation preparation successful")
        return

    outputs = json.loads(
        OUTPUTS_FILE.read_text(encoding="utf-8")
    )

    evaluated_ids = set()
    counts = Counter()

    for result in outputs:
        task_id = result["task_id"]

        assert task_id in task_lookup, (
            f"Unknown task ID: {task_id}"
        )

        assert task_id not in evaluated_ids, (
            f"Duplicate result: {task_id}"
        )

        task = task_lookup[task_id]

        assert result["task_type"] == task["task_type"]
        assert result["output"].strip()

        evaluated_ids.add(task_id)
        counts[task["task_type"]] += 1

    print("Available baseline outputs:", len(outputs))
    print("Distribution:", dict(counts))
    print("Remaining tasks:", 60 - len(outputs))
    print("Output verification successful")


if __name__ == "__main__":
    main()
