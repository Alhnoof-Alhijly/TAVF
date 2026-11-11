"""Bounded refinement history; no initial generation or final-output packaging."""

import json
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path

from tavf.feedback import generate_feedback
from tavf.generation import GenerationError, generate_initial_output
from tavf.prompting import PROMPT_TEMPLATE_REGISTRY
from tavf.validators.bug_report import validate_bug_report
from tavf.validators.test_case import validate_test_case
from tavf.validators.user_story import validate_user_story


MAX_REFINEMENT_ATTEMPTS = 2
PROMPT_FILE = Path(__file__).resolve().parents[2] / "prompts/tavf/refinement.txt"


def _validate(task_type, output, original_input, *, execute=False, trusted_oracle=None):
    if task_type == "user_story_refinement":
        return validate_user_story(output)
    if task_type == "bug_report_refinement":
        return validate_bug_report(output, original_input["original_text"])
    return validate_test_case(output, original_input, execute=execute,
                              trusted_oracle=trusted_oracle)


def refine_output(task_type: str, task_input: Mapping,
                  initial_generation: Mapping, client, *, execute: bool = False,
                  trusted_oracle: dict | None = None) -> dict:
    """Revalidate and refine at most twice using the initial generation's client.

    Callers must supply the same configured client used for initial generation;
    its model and recorded generation parameters are checked before any call.
    versions includes the initial artifact and every successful revision, each
    with metadata, validation and full feedback. attempts also retains failed
    requests with sanitized errors. No missing-information issue is instructed.
    Explicit test-case execution and oracle options apply equally to initial
    validation and every revision; other task validators do not receive them.
    """
    if not isinstance(task_type, str) or task_type not in PROMPT_TEMPLATE_REGISTRY:
        raise ValueError(f"Unsupported task_type: {task_type!r}.")
    if not isinstance(task_input, Mapping) or not isinstance(initial_generation, Mapping):
        raise TypeError("task_input and initial_generation must be mappings.")
    fields = PROMPT_TEMPLATE_REGISTRY[task_type][1]
    original_input = {}
    for field in fields:
        value = task_input.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Original input requires a non-empty '{field}'.")
        original_input[field] = value
    output = initial_generation.get("output")
    if not isinstance(output, str) or not output.strip():
        raise ValueError("Initial generation requires a non-empty output.")
    model = initial_generation.get("model")
    if not isinstance(model, str) or not model or getattr(client, "model", None) != model:
        raise ValueError("Refinement requires the same model as initial generation.")
    parameters = initial_generation.get("parameters")
    if not isinstance(parameters, Mapping) or any(
        getattr(client, name, None) != value for name, value in parameters.items()
    ):
        raise ValueError("Refinement client parameters must match initial generation.")

    versions, attempts = [], []

    def preserve(generation, attempt):
        validation = _validate(task_type, generation["output"], original_input,
                               execute=execute, trusted_oracle=trusted_oracle)
        versions.append({
            "attempt": attempt,
            "generation": deepcopy(dict(generation)),
            "validation": validation,
            "feedback": generate_feedback(task_type, validation),
        })

    preserve(initial_generation, 0)
    while True:
        previous = versions[-1]
        if previous["validation"]["valid"]:
            reason = "validation_passed"
            break
        fixable = [entry for entry in previous["feedback"]["feedback"]
                   if entry["issue"]["classification"] == "fixable"
                   and entry["instruction"] is not None]
        if not fixable:
            reason = ("unmapped_fixable_issues" if previous["feedback"]["unmapped_issue_codes"]
                      else "no_fixable_issues")
            break
        if len(attempts) >= MAX_REFINEMENT_ATTEMPTS:
            reason = "attempt_limit"
            break

        prompt = PROMPT_FILE.read_text(encoding="utf-8").format(
            task_type=task_type,
            original_input=json.dumps(original_input, ensure_ascii=False),
            previous_output=json.dumps(previous["generation"]["output"], ensure_ascii=False),
            fixable_feedback=json.dumps(fixable, ensure_ascii=False),
        )
        attempt = {"attempt": len(attempts) + 1, "prompt": prompt}
        attempts.append(attempt)
        try:
            generation = generate_initial_output(prompt, client=client)
        except GenerationError:
            attempt.update(status="failed", error="Refinement generation failed.")
            reason = "generation_failed"
            break
        attempt["generation"] = deepcopy(generation)
        if generation.get("model") != model or generation.get("parameters") != parameters:
            attempt.update(status="failed", error="Refinement model or parameters changed.")
            reason = "configuration_mismatch"
            break
        attempt["status"] = "success"
        preserve(generation, attempt["attempt"])

    return {"versions": versions, "attempts": attempts, "stop_reason": reason}
