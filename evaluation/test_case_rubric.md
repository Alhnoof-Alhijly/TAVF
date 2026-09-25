
# Test Case Evaluation Rubric

## 1. Objective

This rubric evaluates the quality of LLM-generated Python test cases in the TAVF experiment.

The same evaluation criteria will be applied to Direct LLM Prompting and TAVF.

Evaluation combines qualitative test quality, execution-based correctness, and code coverage.

## 2. Test Quality Criteria

Each criterion is scored from 0 to 2.

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Syntactic Validity | Invalid Python syntax | Minor issues requiring correction | Valid Python syntax |
| Test Relevance | Tests unrelated behavior | Partially relevant tests | Tests directly address the target function |
| Assertion Quality | Missing or incorrect assertions | Some meaningful assertions | Clear assertions with appropriate expected results |
| Input Diversity | Repetitive or insufficient inputs | Limited input variation | Diverse, meaningful inputs |
| Edge Case Coverage | No relevant edge cases | Some edge cases | Multiple relevant boundary or edge cases |
| Requirement Coverage | Major requirements omitted | Partial requirement coverage | Main documented requirements covered |
| Test Independence | Tests depend on shared state or execution order | Minor dependencies | Tests can execute independently |
| Code Clarity | Difficult to understand | Partially clear | Readable and well-organized |

**Maximum qualitative score: 16 points.**

## 3. Execution-Based Metrics

The following metrics are measured separately from the qualitative score.

| Metric | Measurement |
|---|---|
| Execution Success | Whether generated tests execute successfully |
| Test Correctness | Whether test outcomes agree with the reference implementation and documented behavior |
| Line Coverage | Percentage of executable lines covered |
| Branch Coverage | Percentage of branches covered |
| Target Coverage | Percentage of designated TestEval targets covered |
| Valid Test Count | Number of executable, valid generated tests |

Coverage will be calculated using the same tools and configuration for both experimental methods.

## 4. Scoring Procedure

Each generated test suite receives eight qualitative scores.

The total is calculated as:

Total Quality Score = Sum of the eight criterion scores.

Execution and coverage metrics are recorded separately. They are not added to the 16-point qualitative score.

A syntactically valid test suite is not automatically considered correct. Assertions and expected results must also be examined.

## 5. Evaluation Consistency

Both experimental methods will use the same rubric.

The evaluation will distinguish between:
- Automated measurements, such as execution and coverage.
- Qualitative judgments, such as test relevance and clarity.

Evaluation-only fields, including TestEval target lines and blocks, must not be included in the generation prompts.

## 6. Limitations

High code coverage does not guarantee that tests detect faults.

Qualitative scores may involve evaluator judgment. Scoring guidelines and evaluation records must therefore be preserved to support reproducibility.
