import pandas as pd

df = pd.read_csv("data/processed/userstories_candidates.csv")

df = df.drop_duplicates(subset=["original_story"]).copy()

df["word_count"] = df["original_story"].str.split().str.len()

filtered = df[
    (df["word_count"] >= 10) &
    (df["word_count"] <= 40)
].copy()

filtered.to_csv(
    "data/processed/userstories_filtered.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Filtered candidates:", len(filtered))
print("Source files:", filtered["source_file"].nunique())
print(filtered["word_count"].describe())