
# TAVF — Baseline Configuration

## 1. Objective

This document defines the configuration for the Direct LLM Prompting baseline in TAVF.

The same LLM and generation settings will be used for both the Baseline and TAVF to ensure a controlled experimental comparison.

## 2. Model Configuration

| Parameter | Value |
|---|---|
| API Provider | OpenAI |
| Model Identifier | gpt-5.4-mini-2026-03-17 |
| Temperature | TBD — subject to API support |
| Maximum Output Tokens | TBD |
| Random Seed | TBD — if supported |
| Prompt Version | v1 |
| API Status | Insufficient credits |
| Pending pilot verification| Model selected; API verification pending |

The selected model will be used for all three experimental tasks.

Before execution, API access and model availability must be verified. The final generation parameters will be documented and frozen after the pilot test.

## 3. Baseline Prompts

Three task-specific baseline prompts have been prepared:

- `prompts/baseline/user_story.txt`
- `prompts/baseline/bug_report.txt`
- `prompts/baseline/test_case.txt`

Each prompt receives only the designated task input.

Evaluation-only reference fields will not be exposed to the model.

The same baseline prompts will be used throughout the main experiment without modification.

## 4. Experimental Dataset

The finalized experimental dataset is stored in:

`data/processed/experiment_tasks.json`

It contains 60 tasks:

| Task | Number of Samples |
|---|---:|
| User Story Refinement | 20 |
| Bug Report Refinement | 20 |
| Test Case Generation | 20 |
| Total | 60 |

Each task will be processed using Direct LLM Prompting and TAVF.

The original inputs and selected model will remain identical across the two methods.

## 5. Baseline Execution

The baseline will generate one initial response for each task.

No automated validation or refinement will be applied to baseline outputs.

The generation script is:

`scripts/run_baseline.py`

The script supports:

- Loading the finalized experimental dataset.
- Selecting the appropriate task-specific prompt.
- Preparing all 60 tasks.
- Dry-run execution without API requests.
- Saving results after each successful request.
- Recording API errors.
- Resuming execution without repeating completed tasks.
- Recording token usage and execution time.

## 6. Pilot Test

A small pilot test will be conducted before the main experiment.

The pilot will include one task from each category:

1. User Story Refinement.
2. Bug Report Refinement.
3. Test Case Generation.

The pilot aims to:

- Verify API access and model availability.
- Confirm the supported generation parameters.
- Check prompt formatting and output structure.
- Inspect generated outputs.
- Verify token usage and execution logs.
- Estimate the cost of the main experiment.

Pilot outputs will be stored separately from the main experimental results.

## 7. Experimental Controls

The following controls will be maintained:

- Identical original task inputs for both methods.
- The same LLM and generation settings.
- Fixed prompt versions.
- Separate generation and evaluation data.
- Consistent task-specific evaluation criteria.
- Persistent output and error logs.
- Recorded model identifiers and API usage.

Changes to the configuration after the main experiment begins must be documented.

## 8. Evaluation

Baseline outputs will be evaluated using the task-specific rubrics:

- User Story Evaluation Rubric: 16 points.
- Bug Report Evaluation Rubric: 16 points.
- Test Case Evaluation Rubric: 16 points.

Execution success, test correctness, and code coverage will be measured separately for Test Case Generation.

Additional metrics include:

- Execution time.
- Number of LLM calls.
- Input tokens.
- Output tokens.
- Total token consumption.
- Estimated API cost.

## 9. Output and Logging

Successful baseline outputs will be stored in:

`results/baseline/baseline_outputs.json`

Execution errors will be recorded in:

`results/baseline/baseline_errors.jsonl`

The evaluation results will use the fields defined in:

`evaluation/evaluation_template.csv`

Each output will be associated with its task ID, task type, model, prompt version, and execution metadata.

## 10. Current Progress

- [x] Select the experimental model.
- [x] Prepare the 60 experimental tasks.
- [x] Create the three baseline prompts.
- [x] Implement the baseline generation script.
- [x] Complete the dry-run test.
- [x] Complete the local resume test.
- [x] Complete the local recovery test.
- [x] Prepare the evaluation rubrics and logging schema.
- [ ] Verify model availability through the API.
- [ ] Add sufficient API credits.
- [ ] Confirm and freeze generation parameters.
- [ ] Complete the actual pilot test.
- [ ] Estimate the experimental cost using pilot results.
- [ ] Execute the baseline on all 60 tasks.
- [ ] Evaluate and analyze baseline outputs.

## 11. Execution Status

The baseline implementation is prepared and has passed local tests using simulated API responses.

The actual pilot and main experiment remain pending until API access is available and the selected model and its generation settings have been verified.
