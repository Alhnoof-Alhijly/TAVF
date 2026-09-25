import json
import random
import pandas as pd

random.seed(42)

with open(
    "data/raw/testeval/data/leetcode-py.jsonl",
    encoding="utf-8"
) as f:
    rows = [json.loads(line) for line in f]

df = pd.DataFrame(rows)

samples = []

targets = {
    1: 6,
    2: 12,
    3: 12
}

for difficulty, n in targets.items():
    group = df[df["difficulty"] == difficulty]
    sampled = group.sample(n=n, random_state=42)
    samples.append(sampled)

shortlist = pd.concat(samples, ignore_index=True)

shortlist.insert(
    0,
    "candidate_id",
    [f"TCC{i:02d}" for i in range(1, len(shortlist) + 1)]
)

shortlist.to_csv(
    "data/processed/testcases_shortlist.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Shortlist size:", len(shortlist))
print(shortlist["difficulty"].value_counts().sort_index())
print("Saved to: data/processed/testcases_shortlist.csv")