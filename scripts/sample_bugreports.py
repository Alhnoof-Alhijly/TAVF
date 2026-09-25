import pandas as pd

df = pd.read_csv("data/processed/bugreports_filtered.csv")

groups = []

for product, group in df.groupby("Product"):
    n = min(2, len(group))
    groups.append(group.sample(n=n, random_state=42))

sampled = pd.concat(groups, ignore_index=True)

sampled.insert(
    0,
    "candidate_id",
    [f"BRC{i:02d}" for i in range(1, len(sampled) + 1)]
)

sampled.to_csv(
    "data/processed/bugreports_shortlist.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Shortlist size:", len(sampled))
print("Products:", sampled["Product"].nunique())
print("Saved to: data/processed/bugreports_shortlist.csv")