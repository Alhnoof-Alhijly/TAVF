import pandas as pd

selected_ids = [
    "BRC01", "BRC03", "BRC06", "BRC07", "BRC08",
    "BRC10", "BRC13", "BRC14", "BRC16", "BRC18",
    "BRC21", "BRC24", "BRC26", "BRC28", "BRC30",
    "BRC36", "BRC40", "BRC44", "BRC46", "BRC53"
]

df = pd.read_csv("data/processed/bugreports_shortlist.csv")

final_df = df[df["candidate_id"].isin(selected_ids)].copy()

final_df = final_df[
    [
        "candidate_id",
        "Bug ID",
        "Product",
        "Comment Text",
        "Steps to Reproduce",
        "Expected_Res",
        "Actual_Res",
        "word_count"
    ]
]

final_df = final_df.rename(columns={
    "candidate_id": "task_id",
    "Comment Text": "input"
})

final_df["task_type"] = "bug_report_refinement"
final_df["expected_output"] = ""

final_df = final_df[
    [
        "task_id",
        "task_type",
        "Bug ID",
        "Product",
        "input",
        "Steps to Reproduce",
        "Expected_Res",
        "Actual_Res",
        "expected_output",
        "word_count"
    ]
]

final_df.to_csv(
    "data/processed/bugreports_final20.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Final samples:", len(final_df))
print("Unique products:", final_df["Product"].nunique())
print("Saved to: data/processed/bugreports_final20.csv")