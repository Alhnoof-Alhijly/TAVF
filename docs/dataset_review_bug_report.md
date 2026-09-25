
# Bug Report Dataset Review

## 1. Objective

This review evaluates datasets for the Bug Report Refinement task in TAVF.

The selection criteria are:
1. Published scientific research.
2. Public dataset availability.
3. Suitability for bug report refinement.
4. Manageable dataset size.

## 2. Candidate Datasets

### 2.1 SWE-bench

**Reference:** Jimenez et al., "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?", ICLR 2024.

**Dataset:** https://github.com/SWE-bench/SWE-bench

SWE-bench contains 2,294 software engineering problems collected from real GitHub issues and corresponding pull requests.

Its primary objective is to evaluate whether language models can generate code patches that resolve software issues.

**Assessment:**

SWE-bench satisfies the publication and availability requirements. However, it primarily supports automated program repair rather than bug report refinement.

It does not provide original bug reports paired with manually refined reports.

**Decision:** Not selected.

### 2.2 BugsRepo

**Reference:** Acharya and Ginde, "BugsRepo: A Comprehensive Curated Dataset of Bug Reports, Comments and Contributors Information from Bugzilla," EASE 2025.

**Paper DOI:** https://doi.org/10.1145/3756681.3756994

**Official dataset:** https://zenodo.org/records/15004067

BugsRepo contains 119,585 bug reports and a structured subset of 10,351 reports with reproduction steps, actual behavior, and expected behavior.

The complete dataset is substantially larger than required for the TAVF experiment.

### 2.3 Downloaded Structured Bug Report Dataset

**Source:**
https://huggingface.co/datasets/jag2023/Bug_report_Final_new_dataset_2024

The downloaded dataset contains 3,158 Mozilla bug-report records.

Its relevant fields include:
- Bug ID
- Comment Text
- Steps to Reproduce
- Expected_Res
- Actual_Res
- Summary
- Product

The downloaded Parquet file is approximately 4.44 MB.

Its structure is suitable for refining original bug-report text and evaluating whether essential information is preserved.

**Provenance limitation:**

The direct relationship between this Hugging Face dataset and the official EASE 2025 BugsRepo release has not been independently established.

The experimental data must therefore be attributed to the exact Hugging Face source rather than presented as a verified subset of the official release.

The repository's dataset card does not provide sufficient licensing information for a definitive redistribution assessment.

**Decision:** Selected as the working experimental dataset, subject to documenting its provenance and reuse permissions.

## 3. Experimental Preparation

The downloaded dataset was processed as follows:

1. Inspected all 3,158 records.
2. Confirmed unique Bug IDs and no duplicate Comment Text.
3. Filtered reports containing 40–250 words.
4. Retained 2,944 candidate reports.
5. Sampled up to two reports per product using a fixed random seed.
6. Created a shortlist of 54 reports from 32 products.
7. Selected 20 reports from 20 different products.

Final dataset:
`data/processed/bugreports_final20.csv`

## 4. Experimental Task

**Task:** Bug Report Refinement

**Input:** Original bug-report text.

**Expected output:** A structured, readable report containing a concise summary, reproduction steps, expected behavior, actual behavior, and relevant technical context.

**Reference information:** The original structured fields will be used to check factual preservation and completeness.

**Evaluation:** Eight-criterion Bug Report Evaluation Rubric.

No manually written gold-standard refinement is available.

## 5. References

[1] C. E. Jimenez et al., "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?", ICLR, 2024.

[2] J. Acharya and G. Ginde, "BugsRepo: A Comprehensive Curated Dataset of Bug Reports, Comments and Contributors Information from Bugzilla," EASE, pp. 986–993, 2025. doi: 10.1145/3756681.3756994.

[3] jag2023, "Bug_report_Final_new_dataset_2024," Hugging Face Datasets.
https://huggingface.co/datasets/jag2023/Bug_report_Final_new_dataset_2024
