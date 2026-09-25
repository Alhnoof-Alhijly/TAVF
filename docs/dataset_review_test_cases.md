
# Test Case Generation Dataset Review

## 1. Objective

This review evaluates the suitability of TestEval for the Test Case Generation task in TAVF.

The selection criteria are scientific publication, public availability, task relevance, and manageable size.

## 2. Selected Dataset: TestEval

**Paper:** Wang et al., "TestEval: Benchmarking Large Language Models for Test Case Generation."

**Publication:** Findings of NAACL 2025.

**Paper:** https://aclanthology.org/2025.findings-naacl.197/

**Repository:** https://github.com/LLM4SoftwareTesting/TestEval

**License:** MIT (repository).

TestEval contains 210 Python programs collected from LeetCode. It supports overall coverage, targeted line and branch coverage, and targeted path coverage.

The repository provides the dataset and evaluation scripts.

## 3. Dataset Assessment

| Criterion | Assessment |
|---|---|
| Scientific publication | NAACL 2025 |
| Public availability | Public GitHub repository |
| Task relevance | Specifically designed for LLM-based test generation |
| Dataset size | 210 Python programs |
| Ground truth | Reference implementations, not textual gold test suites |
| Evaluation feasibility | Executability, correctness, and coverage |
| Reproducibility | Public benchmark code and evaluation scripts |

**Decision:** Selected for the TAVF experiment.

## 4. Experimental Preparation

The `leetcode-py.jsonl` file was inspected.

It contains 210 unique programming tasks. The local dataset uses difficulty levels 1, 2, and 3.

A shortlist of 30 candidates was generated using a fixed random seed of 42.

Twenty tasks were selected with the following distribution:

- Difficulty 1: 4 tasks
- Difficulty 2: 8 tasks
- Difficulty 3: 8 tasks

The selection includes strings, arrays, graphs, matrices, search, geometry, and bitwise problems.

**Final dataset:** `data/processed/testcases_final20.csv`

## 5. Experimental Task

**Task:** Test Case Generation

**Input:**
- Programming task description.
- Reference Python implementation.

**Expected output:**
A set of executable Python test cases.

**Evaluation:**
- Execution success
- Test correctness
- Line coverage
- Branch coverage
- Target coverage
- Number of valid generated tests

The `blocks` and `target_lines` fields are retained for evaluation rather than included in the generation prompt.

Path coverage is optional and is excluded from the initial experiment.

## 6. Limitations

TestEval contains algorithmic Python problems rather than complete industrial software projects.

The selected sample contains only 20 tasks. Findings should therefore be interpreted within the scope of the selected programming tasks.

The experiment will compare Direct Prompting and TAVF using identical inputs and the same evaluation procedure.

## 7. Reference

[1] W. Wang et al., "TestEval: Benchmarking Large Language Models for Test Case Generation," in *Findings of the Association for Computational Linguistics: NAACL 2025*, pp. 3547–3562, 2025. doi: 10.18653/v1/2025.findings-naacl.197.
