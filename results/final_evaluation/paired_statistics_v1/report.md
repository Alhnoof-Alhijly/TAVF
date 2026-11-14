# Final paired statistical analysis

Effects are TAVF minus Baseline. Raw and global Holm-adjusted p-values are reported for 40 tests.
Confidence intervals are nominal 95% bootstrap intervals, not simultaneous intervals.

Reproduce with `.venv/Scripts/python.exe evaluation/final_paired_statistics.py --output-dir PATH_TO_NEW_DIRECTORY`.
Seed 42; 20,000 bootstrap resamples; 100,000 permutations for continuous Path match.
See protocol.md and statistical_summary.json for algorithms, versions, source hashes, transitions and missingness.

## structural_v2

| Task / criterion | Valid pairs | Units | Effect [95% CI] | Raw p | Holm p |
|---|---:|---|---:|---:|---:|
| user_story_refinement / Structural Form | 495 | percentage points | +0.202 [+0.000, +0.606] | 1 | 1 |
| user_story_refinement / Atomic | 495 | percentage points | +0.000 [+0.000, +0.000] | 1 | 1 |
| user_story_refinement / Minimal | 495 | percentage points | +0.000 [+0.000, +0.000] | 1 | 1 |

## information_completeness

| Task / criterion | Valid pairs | Units | Effect [95% CI] | Raw p | Holm p |
|---|---:|---|---:|---:|---:|
| user_story_refinement / Information Completeness | 494 | percentage points | -26.518 [-30.364, -22.672] | 7.34684e-40 | 2.86527e-38 |

## structural

| Task / criterion | Valid pairs | Units | Effect [95% CI] | Raw p | Holm p |
|---|---:|---|---:|---:|---:|
| bug_report_refinement / Summary | 499 | percentage points | -0.601 [-1.603, +0.200] | 0.375 | 1 |
| bug_report_refinement / Steps to Reproduce | 493 | percentage points | +6.085 [+4.057, +8.316] | 1.86265e-09 | 7.07805e-08 |
| bug_report_refinement / Expected Result | 499 | percentage points | +1.202 [+0.000, +2.405] | 0.109375 | 1 |
| bug_report_refinement / Actual Result | 499 | percentage points | +3.206 [+1.603, +4.810] | 0.000144958 | 0.00478363 |
| bug_report_refinement / Structural score /100 | 491 | score points | +2.495 [+1.680, +3.360] | 2.11589e-09 | 7.82878e-08 |

## structural_v1_sensitivity

| Task / criterion | Valid pairs | Units | Effect [95% CI] | Raw p | Holm p |
|---|---:|---|---:|---:|---:|
| user_story_refinement / Well-formed | 500 | percentage points | -26.400 [-30.200, -22.600] | 3.67342e-40 | 1.46937e-38 |
| user_story_refinement / Atomic | 499 | percentage points | +0.000 [+0.000, +0.000] | 1 | 1 |
| user_story_refinement / Minimal | 367 | percentage points | +0.000 [+0.000, +0.000] | 1 | 1 |

## human_semantic

| Task / criterion | Valid pairs | Units | Effect [95% CI] | Raw p | Holm p |
|---|---:|---|---:|---:|---:|
| user_story_refinement / conceptually_sound | 25 | net win fraction | -0.240 [-0.400, -0.080] | 0.03125 | 0.75 |
| user_story_refinement / problem_oriented | 25 | net win fraction | +0.000 [+0.000, +0.000] | 1 | 1 |
| user_story_refinement / unambiguous | 25 | net win fraction | -0.240 [-0.400, -0.080] | 0.03125 | 0.75 |
| user_story_refinement / source_fidelity | 25 | net win fraction | +0.040 [-0.080, +0.160] | 1 | 1 |
| bug_report_refinement / clarity | 25 | net win fraction | -0.520 [-0.760, -0.240] | 0.00234985 | 0.0704956 |
| bug_report_refinement / reproducibility | 25 | net win fraction | -0.160 [-0.320, -0.040] | 0.125 | 1 |
| bug_report_refinement / factual_consistency | 25 | net win fraction | -0.520 [-0.760, -0.280] | 0.00234985 | 0.0704956 |

## syntax

| Task / criterion | Valid pairs | Units | Effect [95% CI] | Raw p | Holm p |
|---|---:|---|---:|---:|---:|
| test_case_generation / overall: Syntax | 499 | percentage points | +0.601 [+0.000, +1.392] | 0.25 | 1 |
| test_case_generation / line: Syntax | 166 | percentage points | +1.205 [+0.000, +3.012] | 0.5 | 1 |
| test_case_generation / branch: Syntax | 167 | percentage points | +0.599 [+0.000, +1.796] | 1 | 1 |
| test_case_generation / path: Syntax | 166 | percentage points | +0.000 [+0.000, +0.000] | 1 | 1 |

## execution

| Task / criterion | Valid pairs | Units | Effect [95% CI] | Raw p | Holm p |
|---|---:|---|---:|---:|---:|
| test_case_generation / overall: Execution | 496 | percentage points | +11.895 [+7.129, +16.735] | 3.98085e-06 | 0.000143311 |
| test_case_generation / line: Execution | 164 | percentage points | +7.317 [-0.610, +15.244] | 0.103805 | 1 |
| test_case_generation / branch: Execution | 166 | percentage points | +12.048 [+3.614, +20.482] | 0.00907334 | 0.24498 |
| test_case_generation / path: Execution | 166 | percentage points | +16.265 [+7.831, +24.699] | 0.000460005 | 0.0147202 |

## execution_availability

| Task / criterion | Valid pairs | Units | Effect [95% CI] | Raw p | Holm p |
|---|---:|---|---:|---:|---:|
| test_case_generation / overall: Execution | 499 | percentage points | +11.824 [+7.099, +16.601] | 3.98085e-06 | 0.000143311 |
| test_case_generation / line: Execution | 166 | percentage points | +7.229 [-0.602, +15.060] | 0.103805 | 1 |
| test_case_generation / branch: Execution | 167 | percentage points | +11.976 [+3.593, +20.359] | 0.00907334 | 0.24498 |
| test_case_generation / path: Execution | 166 | percentage points | +16.265 [+7.831, +24.699] | 0.000460005 | 0.0147202 |

## coverage

| Task / criterion | Valid pairs | Units | Effect [95% CI] | Raw p | Holm p |
|---|---:|---|---:|---:|---:|
| test_case_generation / overall: Target Coverage | 118 | percentage points | +0.000 [-5.833, +5.738] | 1 | 1 |
| test_case_generation / line: Target Coverage | 27 | percentage points | +3.704 [+0.000, +11.111] | 1 | 1 |
| test_case_generation / branch: Target Coverage | 41 | percentage points | +0.000 [-7.317, +7.317] | 1 | 1 |
| test_case_generation / path: Target Coverage | 50 | percentage points | -2.000 [-14.000, +10.000] | 1 | 1 |
| test_case_generation / Path match fraction | 50 | percentage points | -0.400 [-4.000, +3.200] | 1 | 1 |

## coverage_availability

| Task / criterion | Valid pairs | Units | Effect [95% CI] | Raw p | Holm p |
|---|---:|---|---:|---:|---:|
| test_case_generation / overall: Target Coverage | 499 | percentage points | +10.822 [+5.943, +15.675] | 3.15759e-05 | 0.00107358 |
| test_case_generation / line: Target Coverage | 166 | percentage points | +8.434 [+0.602, +16.265] | 0.054076 | 1 |
| test_case_generation / branch: Target Coverage | 167 | percentage points | +11.377 [+2.994, +19.760] | 0.0144538 | 0.361346 |
| test_case_generation / path: Target Coverage | 166 | percentage points | +12.651 [+4.819, +21.084] | 0.00380165 | 0.106446 |

## Interpretation and limitations

Human effects use ordinal win/loss directions, not rating distances; all seven have 25 valid pairs. No human criterion survives the global Holm correction.

Coverage success yield over 499 complete TestEval pairs is distinct from conditional coverage among 118 jointly assessable pairs. Unknown or skipped results remain unknown; they are not verified failures. The rejected Baseline case is excluded from paired tests, not imputed. Assertion correctness remains unverified.

Information Completeness measures populated slots, not source fidelity: an unsupported invented benefit can appear populated. Structural and semantic findings must remain separate.

- Single human rater; 25 paired inputs per semantic task; no inter-rater reliability estimate
- Human ratings are ordinal; sign tests and direction effects do not assume interval spacing
- Structural v2 is a post hoc revision; v1 is retained as sensitivity analysis
- Conditional assessability can induce selection bias; availability yields are distinct endpoints
- TestEval program clustering accounted for; project dependence in other tasks not separately modelled
- No randomized method assignment; sign-flip assumptions do not establish causal effects
- Single generated artifact per method/input; bootstrap intervals are nominal and may degenerate under ceiling/ties
- No trusted assertion oracle; assertion correctness remains unverified
