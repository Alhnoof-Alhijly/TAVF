from pathlib import Path
import csv

source = Path("data/raw/dalpiaz_userstories")
output = Path("data/processed/userstories_candidates.csv")

rows = []

for file in sorted(source.glob("*.txt")):
    with open(file, encoding="cp1252") as f:
        for line_number, line in enumerate(f, start=1):
            story = line.strip()

            if story:
                rows.append({
                    "source_file": file.name,
                    "line_number": line_number,
                    "original_story": story
                })

output.parent.mkdir(parents=True, exist_ok=True)

with open(output, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["source_file", "line_number", "original_story"]
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"Total user stories: {len(rows)}")
print(f"Saved to: {output}")