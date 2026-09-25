
# TAVF — Experiment Protocol

## 1. Objective

This experiment investigates whether task-specific validation and refinement improve the quality of LLM-generated software-development artifacts compared with Direct LLM Prompting.

The experiment covers three tasks:
- User Story Refinement
- Bug Report Refinement
- Test Case Generation

## 2. Experimental Design

The study uses a paired experimental design. Each task is processed using two methods:

**Baseline:** Direct LLM Prompting.

**Proposed Method:** Task-Aware Validation Framework (TAVF).

Both methods use the same LLM, original task input, and task-specific evaluation criteria.

The experiment contains 60 tasks: 20 user stories, 20 bug reports, and 20 test-generation tasks. Each method processes all 60 tasks, producing 120 primary experimental outputs.

## 3. Dataset

The selected datasets are:

| Task | Dataset | Samples |
|---|---|---:|
| User Story Refinement | Dalpiaz User Stories | 20 |
| Bug Report Refinement | jag2023 Mozilla Bug Reports | 20 |
| Test Case Generation | TestEval | 20 |
| **Total** | | **60** |

The finalized tasks are stored in:

`data/processed/experiment_tasks.json`

The same finalized dataset will be used throughout the experiment. Task selection must not be changed after experimental execution begins.

## 4. Model and Generation Settings

The same model and generation configuration will be used for both methods.

The following settings must be recorded before execution:

- Model name and exact API identifier: TBD
- API/provider: TBD
- Temperature: TBD, subject to model support
- Maximum output tokens: TBD
- Random seed: recorded where supported
- Prompt versions: frozen before the main experiment
- API pricing: recorded at the time of execution

The exact model must be verified through the provider's current documentation and a successful API test.

**Current status:** The OpenAI SDK is installed, but the API execution test is blocked by insufficient API credits.

## 5. Baseline Procedure

For each task:

1. Load the original task input.
2. Select the appropriate task-specific baseline prompt.
3. Generate one output using the selected LLM.
4. Save the output without an automated refinement step.
5. Record execution time, token consumption, and API usage.
6. Evaluate the output using the relevant task-specific rubric.

The baseline prompt may identify the task and specify its required output format. It must not receive information reserved for evaluation.

## 6. TAVF Procedure

For each task:

1. Identify the task type.
2. Apply task-specific prompting.
3. Generate an initial output using the same LLM.
4. Perform task-specific validation.
5. Produce structured feedback identifying detected issues.
6. Refine the output using the feedback, subject to a predefined iteration limit.
7. Save the initial and final outputs.
8. Submit the final output for evaluation and human review.

The framework's validation rules, feedback format, stopping conditions, and maximum refinement iterations must be frozen before the main experiment.

Human review is part of the framework workflow, but any human editing must be recorded separately from the automated output.

## 7. Experimental Controls

To ensure a controlled comparison:

- Both methods receive identical original task inputs.
- Both methods use the same model and generation settings.
- Prompt versions are recorded.
- Generation and evaluation data remain separate.
- Reference fields are not exposed to the model unless explicitly designated as task inputs.
- The same evaluation criteria are applied to both methods.
- Execution conditions and failures are logged.
- All refinement attempts are retained.

Model nondeterminism will be acknowledged when interpreting results. If additional repeated runs are conducted, they will be reported separately from the primary paired experiment.

## 8. Evaluation

### 8.1 User Story Refinement

The eight-criterion User Story Evaluation Rubric will be applied.

Maximum quality score: 16.

### 8.2 Bug Report Refinement

The eight-criterion Bug Report Evaluation Rubric will be applied.

Maximum quality score: 16.

### 8.3 Test Case Generation

The eight-criterion qualitative Test Case Evaluation Rubric will be applied.

Maximum quality score: 16.

Execution success, test correctness, and code coverage will be measured separately.

### 8.4 Common Metrics

The primary comparison uses paired quality scores for the same tasks.

Additional measurements include:
- Validation issues detected and confirmed.
- Refinement gain.
- Number of refinement iterations.
- Execution time.
- Number of LLM calls.
- Input and output tokens.
- Estimated API cost.

## 9. Result Logging

Every experimental execution must receive a unique run identifier.

Results will be recorded using:

`evaluation/evaluation_template.csv`

Generated outputs, validation feedback, and intermediate refinement outputs will be preserved separately.

The evaluation record will identify the task, method, model, prompt version, scores, resource usage, and evaluator.

Missing measurements must remain missing rather than being replaced with zero.

## 10. Analysis

The primary analysis will compare the final output of TAVF with the baseline output for each of the 60 tasks.

The study will report:
- Mean and median quality scores.
- Standard deviation.
- Paired quality differences.
- Separate results for each task type.
- Validation and refinement outcomes.
- Execution-based test results.
- Time, token, and cost overhead.

Confidence intervals and suitable paired statistical tests will be considered after inspecting the collected results.

The study will distinguish measured improvements from claims about generalizability.

## 11. Threats to Validity

Potential threats include:

- The small sample of 20 tasks per category.
- Subjectivity in qualitative evaluation.
- Variation in LLM-generated outputs.
- Differences between benchmark tasks and industrial projects.
- Potential errors in dataset reference fields.
- Possible evaluator bias.

The evaluator should assess outputs without seeing their method labels where feasible.

Any changes to the protocol after experimentation begins must be documented and justified.

## 12. Pre-Experiment Checklist

- [x] Define the three task types.
- [x] Select 60 experimental tasks.
- [x] Create the unified task schema.
- [x] Export and validate the experimental dataset.
- [x] Prepare task-specific evaluation rubrics.
- [x] Define common evaluation metrics.
- [x] Create the evaluation logging template.
- [ ] Verify the selected model and API access.
- [ ] Freeze prompts and model settings.
- [ ] Finalize validation rules and stopping conditions.
- [ ] Define the human-review procedure.
- [ ] Conduct a small pilot test.
- [ ] Begin the main experiment.
