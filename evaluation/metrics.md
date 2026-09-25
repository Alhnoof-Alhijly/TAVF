
# TAVF — Common Evaluation Metrics

## 1. Objective

This document defines the common metrics used to compare Direct LLM Prompting and TAVF across three software-development tasks:

- User Story Refinement
- Bug Report Refinement
- Test Case Generation

Both methods will use the same LLM, task inputs, and evaluation criteria.

## 2. Output Quality

Output quality will be measured using task-specific evaluation rubrics.

| Task | Quality Measurement |
|---|---|
| User Story Refinement | Eight criteria, each scored 0–2; maximum 16 |
| Bug Report Refinement | Eight criteria, each scored 0–2; maximum 16 |
| Test Case Generation | Eight qualitative criteria, each scored 0–2; maximum 16 |

A normalized quality score will support comparisons across tasks:

Normalized Quality = (Obtained Score / 16) × 100

Task-specific results will also be reported separately.

## 3. Quality Improvement

The quality difference between TAVF and Direct Prompting will be calculated for each task:

Quality Difference = TAVF Quality − Baseline Quality

The mean difference will be reported separately for each task type and across the complete experimental dataset.

For TAVF, the quality difference between the initial generated output and the final refined output will also be measured.

## 4. Validation Effectiveness

Validation effectiveness measures whether task-specific validation identifies problems in generated outputs.

The following information will be recorded:

- Number of issues identified.
- Issue categories.
- Number of valid issues confirmed through evaluation.
- Number of issues addressed during refinement.
- Number of unresolved issues.

Where reliable issue-level reference annotations are available, precision and recall may also be calculated.

## 5. Refinement Effectiveness

Refinement effectiveness measures changes between the initial and final TAVF outputs.

The experiment will record:

- Initial quality score.
- Final quality score.
- Number of refinement attempts.
- Number of issues resolved.
- Number of new issues introduced.

Refinement Gain = Final Quality − Initial Quality

A negative value indicates that refinement reduced the measured output quality.

## 6. Execution-Based Test Metrics

For Test Case Generation, the following metrics will be reported separately from rubric scores:

- Execution success.
- Test correctness.
- Line coverage.
- Branch coverage.
- Target coverage.
- Number of valid generated tests.

Both experimental methods will use the same execution environment and coverage tools.

## 7. Efficiency and Overhead

The following measurements will be collected for each experimental run:

| Metric | Definition |
|---|---|
| Execution Time | Total elapsed time required to produce the final output |
| LLM Calls | Number of model requests |
| Refinement Attempts | Number of refinement iterations |
| Input Tokens | Total input tokens consumed |
| Output Tokens | Total output tokens generated |
| Total Tokens | Input tokens + output tokens |
| Estimated API Cost | Cost calculated using recorded token usage and applicable model pricing |
| Human Review Time | Time spent reviewing the final output, when measured |

TAVF overhead will be calculated relative to the baseline.

Time Overhead = TAVF Time − Baseline Time

Token Overhead = TAVF Total Tokens − Baseline Total Tokens

All costs will be reported in USD. Actual pricing and the selected model must be documented before experimentation.

## 8. Analysis Procedure

The experiment contains 60 tasks, with 20 tasks per task type.

Each task will be processed using both methods, producing 60 paired comparisons.

Results will include:
- Mean and median quality scores.
- Standard deviation.
- Mean paired quality difference.
- Task-specific comparisons.
- Execution and coverage results for test generation.
- Time, token consumption, and refinement overhead.

Where appropriate, paired statistical tests and confidence intervals will be used. Test selection will depend on the distribution and measurement characteristics of the collected data.

## 9. Evaluation Consistency

Both methods must use identical task inputs and the same evaluation procedures.

The LLM model, generation settings, prompt versions, and evaluation configuration must be recorded.

Rubric scores, automated measurements, and resource-consumption metrics will be stored separately.

The final analysis must distinguish observed experimental results from interpretations about the framework's effectiveness.
