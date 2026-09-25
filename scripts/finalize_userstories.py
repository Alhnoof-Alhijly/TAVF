import pandas as pd

selected_ids = [
    "USC03", "USC05", "USC07", "USC10", "USC11",
    "USC12", "USC14", "USC19", "USC20", "USC21",
    "USC22", "USC25", "USC26", "USC27", "USC29",
    "USC32", "USC33", "USC38", "USC41", "USC42"
]

df = pd.read_csv("data/processed/userstories_shortlist.csv")

final_df = df[df["candidate_id"].isin(selected_ids)].copy()

final_df = final_df[
    ["candidate_id", "source_file", "line_number", "original_story", "word_count"]
]

final_df = final_df.rename(columns={
    "candidate_id": "task_id",
    "original_story": "input"
})

final_df["task_type"] = "user_story_refinement"
final_df["expected_output"] = ""

final_df = final_df[
    [
        "task_id",
        "task_type",
        "source_file",
        "line_number",
        "input",
        "expected_output",
        "word_count"
    ]
]

final_df.to_csv(
    "data/processed/userstories_final20.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Final samples:", len(final_df))
print("Unique sources:", final_df["source_file"].nunique())
print("Saved to: data/processed/userstories_final20.csv")