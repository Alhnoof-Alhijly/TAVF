
# TAVF Unified Task Schema

## 1. Purpose

The unified task schema defines a consistent JSON structure for all 60 experimental tasks. It preserves the original inputs, source information, and task-specific evaluation references.

The schema is defined in `data/task_schema.json` using JSON Schema Draft 2020-12.

## 2. Common Fields

| Field | Description |
|---|---|
| task_id | Unique identifier for each task |
| task_type | User Story Refinement, Bug Report Refinement, or Test Case Generation |
| source | Original dataset |
| input | Information provided to the LLM |
| reference | Source information retained for evaluation |
| metadata | Additional task information |
| expected_output | Required output type and optional gold reference |

## 3. Task-Specific Fields

### User Story Refinement

- Input: Original user story.
- Reference: Source file and original line number.
- Output: Refined user story.

### Bug Report Refinement

- Input: Original bug-report text.
- Reference: Bug ID, product, reproduction steps, expected behavior, and actual behavior.
- Output: Refined bug report.

### Test Case Generation

- Input: Programming task description and Python implementation.
- Reference: Task number, function name, code blocks, and target lines.
- Output: Executable Python test cases.

## 4. Information Separation

Only the designated input fields will be included in generation prompts.

Reference fields are retained separately for evaluation and traceability. Evaluation-only information, including TestEval coverage targets, must not be exposed to the LLM during generation.

## 5. Validation

Every exported task must conform to `data/task_schema.json`.

Task identifiers must be unique, required inputs must be present, and each task must contain the fields required by its task type.
