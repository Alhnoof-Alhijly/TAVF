import pandas as pd

# User Stories
us = pd.read_csv("data/processed/userstories_final20.csv")

us_final = pd.DataFrame({
    "task_id": us["task_id"],
    "task_type": "user_story_refinement",
    "input": us["input"],
    "expected_output": us["expected_output"],
    "source": "Dalpiaz User Stories",
    "difficulty": "",
    "metadata": us["source_file"]
})

# Bug Reports
br = pd.read_csv("data/processed/bugreports_final20.csv")

br_final = pd.DataFrame({
    "task_id": br["task_id"],
    "task_type": "bug_report_refinement",
    "input": br["input"],
    "expected_output": br["expected_output"],
    "source": "BugsRepo",
    "difficulty": "",
    "metadata": br["Product"]
})

# Test Cases
tc = pd.read_csv("data/processed/testcases_final20.csv")

tc_input = (
    "Task Description:\n" +
    tc["description"].astype(str) +
    "\n\nReference Implementation:\n" +
    tc["python_solution"].astype(str)
)

tc_final = pd.DataFrame({
    "task_id": tc["task_id"],
    "task_type": "test_case_generation",
    "input": tc_input,
    "expected_output": tc["expected_output"],
    "source": "TestEval",
    "difficulty": tc["difficulty"],
    "metadata": tc["task_title"]
})

# Merge all tasks
final_df = pd.concat(
    [us_final, br_final, tc_final],
    ignore_index=True
)

final_df.to_csv(
    "data/processed/experimental_dataset.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Total tasks:", len(final_df))
print("\nTask distribution:")
print(final_df["task_type"].value_counts())
print("\nMissing inputs:", final_df["input"].isna().sum())
print("Duplicate task IDs:", final_df["task_id"].duplicated().sum())
print("\nSaved to: data/processed/experimental_dataset.csv")