
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = ROOT / "results/baseline/baseline_scores.csv"
OUTPUT_FILE = ROOT / "results/baseline/baseline_scores_calculated.csv"

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


def main():
    # Read scores as strings for pandas 3.0 compatibility.
    df = pd.read_csv(
        INPUT_FILE,
        dtype=str,
        keep_default_na=False,
    )

    assert len(df) == 60, "Expected 60 tasks."
    assert df["task_id"].is_unique, "Duplicate task IDs."

    evaluated = 0
    pending = 0

    for index, row in df.iterrows():
        task_id = row["task_id"]
        task_type = row["task_type"]

        if task_type not in CRITERIA:
            raise ValueError(
                f"Unknown task type: {task_id}"
            )

        required = CRITERIA[task_type]

        scores = [
            str(row[criterion]).strip()
            for criterion in required
        ]

        # Validate entered scores.
        for score in scores:
            if score and score not in ("0", "1", "2"):
                raise ValueError(
                    f"Invalid score in task {task_id}: {score}"
                )

        # Reject scores for tasks without actual outputs.
        output_available = (
            str(row["output_available"]).lower() == "true"
        )

        if not output_available and any(scores):
            raise ValueError(
                f"Scores entered without output: {task_id}"
            )

        # Calculate scores only when all criteria are entered.
        if output_available and all(scores):
            total = sum(int(score) for score in scores)

            # Convert numbers to strings for pandas 3.0.
            df.at[index, "quality_score"] = str(total)

            df.at[index, "normalized_quality"] = str(
                round(total / 16 * 100, 2)
            )

            df.at[index, "evaluation_status"] = "completed"

            evaluated += 1

        else:
            df.at[index, "quality_score"] = ""
            df.at[index, "normalized_quality"] = ""

            df.at[index, "evaluation_status"] = (
                "in_progress"
                if output_available and any(scores)
                else "pending"
            )

            pending += 1

    # Preserve manually entered scores in the original file.
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print("Baseline score calculation completed")
    print("Total tasks:", len(df))
    print("Evaluated:", evaluated)
    print("Pending:", pending)
    print("Maximum score: 16")
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
