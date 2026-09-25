# TAVF Experimental Logging Schema

Each experimental run must record the following fields.

## Core Identification

- `task_id`
- `task_type`
- `method`
  - `baseline`
  - `tavf`
- `model`
- `run_id`

## Input and Prompt

- `input`
- `prompt`
- `system_prompt`
- `temperature`
- `max_output_tokens`

## LLM Output

- `raw_output`
- `final_output`

## Validation and Refinement

- `validation_result`
- `validation_score`
- `validation_feedback`
- `number_of_revisions`

## Timing and Usage

- `response_time_seconds`
- `input_tokens`
- `output_tokens`
- `total_tokens`
- `estimated_cost`

## Human Evaluation

- `human_evaluation_score`
- `human_evaluation_notes`

## Task-Specific Evaluation

### User Story Refinement
- `user_story_rubric_score`
- `atomicity_score`
- `minimality_score`
- `conceptual_soundness_score`
- `problem_orientation_score`
- `unambiguity_score`
- `estimability_score`
- `means_ends_score`
- `intent_preservation_score`

### Bug Report Refinement
- `bug_report_rubric_score`
- `summary_clarity_score`
- `steps_completeness_score`
- `expected_behavior_score`
- `actual_behavior_score`
- `technical_context_score`
- `organization_score`
- `conciseness_score`
- `factual_preservation_score`

### Test Case Generation
- `execution_success`
- `test_correctness`
- `line_coverage`
- `branch_coverage`
- `target_coverage`
- `valid_generated_tests`

## Error Tracking

- `error_type`
- `error_message`

## Reproducibility

- `timestamp`
- `prompt_version`
- `validator_version`
- `experiment_version`