
# TAVF — Final Dataset Selection

## 1. Selection Criteria

The experimental datasets were selected based on four primary requirements:

1. Scientific publication or documented use in published research.
2. Public availability and accessible data files.
3. Suitability for the intended Agile software-development task.
4. Manageable size for a six-week research project.

Additional considerations include data completeness, provenance, reproducibility, and evaluation feasibility.

## 2. Final Dataset Selection

| Task | Selected Dataset | Original Records | Experimental Samples |
|---|---|---:|---:|
| User Story Refinement | Dalpiaz User Stories | 1,680 | 20 |
| Bug Report Refinement | Mozilla structured bug reports (jag2023) | 3,158 | 20 |
| Test Case Generation | TestEval | 210 | 20 |
| Total | | | 60 |

### 2.1 User Story Refinement

The Dalpiaz dataset was selected because it contains original user stories collected from 22 projects.

After duplicate removal and length filtering, 1,623 candidates remained. A shortlist of 44 was created, from which 20 stories covering 15 source files were selected.

UStAI was retained as a supplementary source for designing the User Story Evaluation Rubric.

**Final file:** `data/processed/userstories_final20.csv`

### 2.2 Bug Report Refinement

A publicly available Mozilla bug-report dataset was selected from Hugging Face.

The downloaded version contains 3,158 records with original comment text and structured reproduction, expected-result, and actual-result fields.

Twenty reports from 20 different products were selected.

SWE-bench was not selected because it primarily evaluates automated code repair.

The exact relationship between the downloaded Hugging Face dataset and the published EASE 2025 BugsRepo release remains unverified. The downloaded source must be attributed separately, and its reuse permissions require confirmation before public redistribution.

**Final file:** `data/processed/bugreports_final20.csv`

### 2.3 Test Case Generation

TestEval was selected because it provides Python programming tasks, reference implementations, coverage targets, and evaluation scripts.

Twenty tasks were selected from the 210 available programs.

Difficulty distribution:
- Level 1: 4
- Level 2: 8
- Level 3: 8

**Final file:** `data/processed/testcases_final20.csv`

## 3. Experimental Dataset

The three selected datasets were combined into one master file:

`data/processed/experimental_dataset.csv`

The master dataset contains:
- 20 User Story Refinement tasks;
- 20 Bug Report Refinement tasks;
- 20 Test Case Generation tasks.

All 60 tasks have unique identifiers and non-missing inputs.

Each task will be evaluated using both Direct LLM Prompting and TAVF.

## 4. Reference Outputs and Evaluation

User Story Refinement and Bug Report Refinement do not have manually verified gold-standard rewritten outputs. They will be evaluated using task-specific quality rubrics and source-information preservation checks.

Test Case Generation will use execution-based correctness and coverage metrics.

The same tasks, model, and evaluation procedures will be used for both experimental methods.

## 5. Reproducibility

The experiment retains:
- Original downloaded datasets.
- Filtering and sampling scripts.
- Fixed sampling seed (42).
- Candidate shortlists.
- Final selected samples.
- Original source identifiers.

These records support reproducibility and traceability.

## 6. Dataset References

1. Dalpiaz User Stories:
   https://zenodo.org/records/13880060

2. UStAI:
   https://github.com/asmayamani/UStAI

3. Downloaded Mozilla Bug Report Dataset:
   https://huggingface.co/datasets/jag2023/Bug_report_Final_new_dataset_2024

4. Published BugsRepo:
   https://doi.org/10.1145/3756681.3756994

5. TestEval:
   https://aclanthology.org/2025.findings-naacl.197/
