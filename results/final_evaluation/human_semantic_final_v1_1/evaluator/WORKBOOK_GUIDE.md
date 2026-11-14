# Single-rater workbook

Use `single_rater.xlsx` with the approved `rubric.md` and `rater_guidance.md`.
The corrected two sheets contain 50 User Story outputs and 50 Bug Report outputs
(25 complete A/B pairs per task type, selected with seed 42). Each row
includes anonymous IDs, its local A/B label, original source, and unchanged output.
Headers and identity columns stay visible when scrolling. Text wraps; expand row
heights or use Excel's formula bar to read long reports in full.

Enter only applicable integer ratings 1–5 using the dropdowns, plus a short note.
Leave a rating blank when unassessable and explain which criterion and why in the
notes. For uncertain judgments, use a defensible rating and identify the uncertainty
in notes. Do not edit identity, source, or output cells. No method labels or
automatic scores are included. The detailed CSV and rubric remain unchanged.

Save a completed copy under a new workbook filename. To transfer it to a **new**
detailed CSV from the project root:

```powershell
& .venv/Scripts/python.exe evaluation/human_semantic_workbook.py transfer --workbook "PATH_TO_COMPLETED_WORKBOOK.xlsx" --output-csv "PATH_TO_NEW_DETAILED_CSV.csv" --selection-file "results/final_evaluation/human_semantic_final_v1_1/evaluator/single_rater.selection.json"
```

The default `--csv` is the existing detailed `scoring_sheet.csv`; specify another
existing detailed CSV if it contains additional data to preserve. Transfer matches
all 200 IDs, verifies source/output text and A/B labels, validates 1–5 ratings, and
refuses missing/duplicate rows, formulas, conflicting ratings, or overwriting files.
All original detailed columns and values are retained. Shared workbook notes go
into the detailed `notes` column, preserving existing notes. Per-criterion status
and evidence fields remain as they were: the simplified workbook cannot express
these separately. Review shared notes to complete criterion-specific `rated`,
`uncertain`, or `unassessable` statuses/evidence in the exported CSV; the transfer
does not infer those judgments. A blank rating remains blank, never zero-filled.
