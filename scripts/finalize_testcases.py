import pandas as pd

selected_ids = [
    "TCC02", "TCC03", "TCC04", "TCC06",
    "TCC07", "TCC08", "TCC10", "TCC11",
    "TCC13", "TCC15", "TCC16", "TCC18",
    "TCC19", "TCC21", "TCC22", "TCC23",
    "TCC25", "TCC27", "TCC28", "TCC30"
]

df = pd.read_csv("data/processed/testcases_shortlist.csv")

final_df = df[df["candidate_id"].isin(selected_ids)].copy()

final_df = final_df.rename(columns={
    "candidate_id": "task_id"
})

final_df["task_type"] = "test_case_generation"
final_df["expected_output"] = ""

final_df = final_df[
    [
        "task_id",
        "task_type",
        "task_num",
        "task_title",
        "difficulty",
        "func_name",
        "description",
        "python_solution",
        "blocks",
        "target_lines",
        "expected_output"
    ]
]

final_df.to_csv(
    "data/processed/testcases_final20.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Final samples:", len(final_df))
print("Difficulty distribution:")
print(final_df["difficulty"].value_counts().sort_index())
print("Saved to: data/processed/testcases_final20.csv")