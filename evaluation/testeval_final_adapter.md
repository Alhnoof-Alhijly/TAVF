# Blinded TestEval Final Evaluation adapter

`evaluate_testeval_blinded.py` reads only the public blinded artifact manifest,
selects its 999 Test Case artifacts, and preserves anonymous/pair IDs and the
full original task, including selected TestEval targets. It never reads private
method labels or generation validation histories.

Default invocation is a read-only dry run:

```powershell
& .venv/Scripts/python.exe evaluation/evaluate_testeval_blinded.py
```

Generated-code execution requires a separate explicit `--execute` invocation.
`--limit N` bounds newly evaluated artifacts for a future authorized pilot. No
generated code is executed by importing the adapter or by a dry run.

The default image is the previously verified immutable Linux image ID:
`sha256:acd3865aef3c1877be238341570499fb39ff2c72a2877a4b75649a9b9a00c1df`
(`tavf-testeval:py312-sortedcontainers-2.4.0`, Python 3.12.16,
sortedcontainers 2.4.0). An execute invocation inspects the local image; no pulls
are allowed during evaluation. The adapter substitutes only this image in
existing evaluator Docker commands. All isolation flags, empty proxy variables,
timeouts, resource limits, bounded coverage transport, and forced cleanup remain
owned by the unchanged execution and coverage evaluators.

Fresh syntax evidence is extracted from the existing checker with execution
disabled; no saved internal validator result is reused. Execution uses the
existing isolated harness. Coverage dispatches to the unchanged selected line,
branch-block-entry or ordered-path evaluator. Coverage is unverified when syntax
or execution fails. Assertion Correctness is explicitly `not_verified`: no
trusted oracle is supplied, and successful execution does not prove correctness.

Default output: `results/final_evaluation/testeval_metrics_v1/`:
`config.json`, `scores/<anonymous-id>.json`, `checkpoints/<anonymous-id>.json`,
`errors/` when needed, and `summary.json`. No private method labels are written.
Results are metric records, not a combined quality score. In-process tracing
retains the existing limitations against deliberately adversarial test code.

Resume requires identical manifest, image, adapter/evaluator sources and path
instrumentation hashes. An OS lock prevents concurrent writers. Completed records
are checked and skipped; a started checkpoint without a durable score requires
manual reconciliation and is never automatically rerun. Infrastructure failures
are saved as unverified measurements and stop the invocation. Retrying such a
saved measurement requires a separately authorized audit-preserving procedure.
