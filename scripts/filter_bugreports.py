import pandas as pd

df = pd.read_parquet(
    "data/raw/bugsrepo/train-00000-of-00001.parquet"
)

df["word_count"] = df["Comment Text"].astype(str).str.split().str.len()

filtered = df[
    (df["word_count"] >= 40) &
    (df["word_count"] <= 250)
].copy()

filtered.to_csv(
    "data/processed/bugreports_filtered.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Filtered reports:", len(filtered))
print("Products:", filtered["Product"].nunique())
print(filtered["word_count"].describe())