import pandas as pd

df = pd.read_csv("data/processed/userstories_filtered.csv")

sampled = (
    df.groupby("source_file", group_keys=False)
      .sample(n=2, random_state=42)
      .reset_index(drop=True)
)

sampled.insert(
    0,
    "candidate_id",
    [f"USC{i:02d}" for i in range(1, len(sampled) + 1)]
)

sampled.to_csv(
    "data/processed/userstories_shortlist.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Shortlist size:", len(sampled))
print("Source files:", sampled["source_file"].nunique())
print("Saved to: data/processed/userstories_shortlist.csv")