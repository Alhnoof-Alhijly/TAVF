"""Deterministic instructions from existing validator issue identifiers.

Validators have no separate code field: their identifiers are criterion,
section, and check. Preserve these fields rather than introducing new codes.
Missing information and unmapped issues remain report-only (instruction=None).
"""

from collections.abc import Mapping
from copy import deepcopy


_FIELDS = {
    "user_story_refinement": "criterion",
    "bug_report_refinement": "section",
    "test_case_generation": "check",
}
_INSTRUCTIONS = {
    "user_story_refinement": {
        "Well-formed": (
            "Format the existing role, goal, and benefit as 'As a [role], I want "
            "[goal], so that [benefit].' Preserve source facts and requirements; "
            "do not supply missing elements."
        ),
        "Atomic": (
            "Review the repeated 'I want' clauses and separate explicitly stated "
            "requests only where the source supplies their context. Preserve all "
            "requirements; do not invent roles or benefits or assume the clauses "
            "are semantically independent."
        ),
        "Minimal": (
            "Remove only the reported standalone Markdown fences or exact duplicate "
            "story copies. Keep one copy of each story and preserve every distinct "
            "source fact and requirement."
        ),
    },
    "bug_report_refinement": {
        section: (
            f"Organize '{section}' under one heading. For a missing or placeholder "
            "section, use only its supplied labeled source content in the evidence; "
            "for repeated headings, consolidate their existing content. Preserve "
            "all original facts and step order; do not invent bug details."
        ) for section in ("Summary", "Steps to Reproduce", "Expected Result", "Actual Result")
    },
    "test_case_generation": {
        "Syntax Validity": (
            "Correct the reported Python syntax or remove Markdown fences as "
            "applicable. Preserve the supplied test intent, inputs, and expected "
            "values; do not invent reference behavior or execute untrusted code."
        ),
        "Assertion Validity": (
            "Review the absence of statically visible assertions. Add an assertion "
            "only where its expected behavior is explicitly supported by supplied "
            "source information or a trusted oracle. Do not invent expected outputs; "
            "leave unsupported expectations unresolved. Assertion presence or passing "
            "execution does not establish correctness."
        ),
    },
}


def generate_feedback(task_type: str, validation_result: Mapping) -> dict:
    """Return feedback entries (issue/evidence/instruction) and unmapped labels.

    Preserve issue order, story numbers, classifications, and linked evidence.
    Reject malformed evidence links instead of attaching unrelated evidence.
    No validator, generation, execution, or refinement is invoked here.
    """
    if not isinstance(task_type, str) or task_type not in _FIELDS:
        raise ValueError(f"Unsupported task_type: {task_type!r}.")
    if not isinstance(validation_result, Mapping):
        raise TypeError("validation_result must be a mapping.")
    issues = validation_result.get("issues")
    evidence = validation_result.get("evidence")
    if not isinstance(issues, list) or not isinstance(evidence, list):
        raise ValueError("validation_result must contain issues and evidence lists.")

    feedback, unmapped = [], []
    field = _FIELDS[task_type]
    for issue in issues:
        if not isinstance(issue, Mapping) or not isinstance(issue.get(field), str):
            raise ValueError(f"Each issue must contain its existing '{field}' identifier.")
        classification = issue.get("classification")
        if classification not in ("fixable", "missing_information"):
            raise ValueError("Unsupported issue classification.")
        index = issue.get("evidence_index")
        if type(index) is not int or not 0 <= index < len(evidence):
            raise ValueError("Issue evidence_index must reference existing evidence.")
        if not isinstance(evidence[index], Mapping):
            raise ValueError("Linked evidence must be a mapping.")

        instruction = None
        if classification == "fixable":
            instruction = _INSTRUCTIONS[task_type].get(issue[field])
            if instruction is None and issue[field] not in unmapped:
                unmapped.append(issue[field])
        feedback.append({
            "issue": deepcopy(dict(issue)),
            "evidence": deepcopy(dict(evidence[index])),
            "instruction": instruction,
        })

    return {"feedback": feedback, "unmapped_issue_codes": unmapped}
