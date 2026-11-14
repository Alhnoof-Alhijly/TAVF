# Final paired statistical analysis v1

Analysis only: frozen automated and human scores are read without rescoring.
Differences are TAVF minus Baseline. Structural, information completeness, human
semantic, execution, coverage and success-availability results stay separate.
User Story structural v2 is primary; v1 is retained as a labelled sensitivity
analysis because v2 was a post hoc protocol revision, not an independent experiment.

Binary outcomes: exact two-sided McNemar/binomial test conditional on discordant
pairs; effect is paired risk difference. Bug Report total structural score uses
an exact paired sign-flip test of the mean difference (integer score increments).
Human 1–5 ratings use exact paired sign tests, excluding ties from the test but
retaining them in the effect denominator. Ordinal effects are the net win fraction
(TAVF wins minus Baseline wins)/all valid pairs and probability of superiority
(wins + half ties)/valid pairs. Method medians are descriptive; no interval-scale
assumption or pooled human total is used.

TestEval targets sharing a reference program are dependent. Its tests flip signs
jointly at the reference `task_num` level, and confidence intervals resample these
program clusters. Integer binary differences allow exact cluster sign-flip tests.
Continuous Path match scores use 100,000 seeded cluster sign-flip permutations,
with (extreme + 1)/(draws + 1), reporting Monte Carlo standard error. Target types
and overall results are reported separately; pooled targets are not assumed
independent. Path match fraction and full-target coverage are distinct endpoints.

All effects receive nominal two-sided 95% percentile bootstrap intervals using
20,000 resamples. Other tasks resample paired inputs; TestEval resamples program
clusters, retaining all available target-level differences in each chosen cluster
and using their weighted mean. A constant observed difference yields a degenerate
bootstrap interval; this is not evidence of zero population uncertainty.
Random streams derive deterministically from master seed 42 and endpoint labels.

Conditional comparisons require both metrics assessable. Missing/invalid human
ratings and skipped/not_verified automated outcomes are excluded criterion by
criterion, with original status transitions and denominators retained. Separately,
observed success yield compares the proportion of complete-pair artifacts with a
verified pass/covered outcome. It does not relabel unknown/skipped results as
verified failures. Rejected/missing artifacts never enter complete paired tests.
Assertion correctness has no verified measurements, so no test is calculated.

Holm–Bonferroni controls family-wise error at 0.05 over **all calculated endpoint
p-values**, including overlapping target-specific, availability, human and v1
sensitivity analyses. Report raw and adjusted p-values. Bootstrap confidence
intervals are nominal, not multiplicity-adjusted. No additional criterion is
created, and no model-based judging, evaluation execution or ratings are generated.

Limitations: one human rater, reduced 25-pair samples per semantic task, ordinal
ceiling/tie effects, no inter-rater reliability estimate, post hoc structural
revision, conditional selection/missingness, correlated TestEval programs, and
single generated artifacts per method/input. Sign-flip tests assume symmetry or
method exchangeability under their null; method assignment was not randomized.
Inference describes this frozen sample under these assumptions, not causal or
universal superiority. Project-level dependence in User Story/Bug Report samples
is not separately modelled. No independent trusted assertion oracle is available.
