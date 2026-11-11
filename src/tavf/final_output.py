"""Select one artifact from recorded refinement versions without generating code."""

import json
from collections.abc import Mapping
from copy import deepcopy


def build_final_output(refinement_result: Mapping) -> dict:
    """Package the earliest passing version, otherwise the fewest fixable issues.

    Uses the actual refinement result: versions contain attempt, generation,
    validation, and feedback. Version order must be chronological. Missing
    information never contributes to ranking. Unverified evidence prevents a
    passing selection even if a recorded valid flag incorrectly says True.
    No validation, generation, execution, or filesystem operations are invoked.
    """
    if not isinstance(refinement_result, Mapping):
        raise TypeError("refinement_result must be a mapping.")
    versions = refinement_result.get("versions")
    if not isinstance(versions, list) or not versions:
        raise ValueError("Refinement history must contain at least one version.")
    if not isinstance(refinement_result.get("attempts"), list):
        raise ValueError("Refinement history must contain an attempts list.")
    if not isinstance(refinement_result.get("stop_reason"), str):
        raise ValueError("Refinement history must contain a stop_reason string.")

    counts, passing = [], []
    previous_attempt = -1
    for version in versions:
        if not isinstance(version, Mapping):
            raise ValueError("Each version must be a mapping.")
        attempt = version.get("attempt")
        if type(attempt) is not int or attempt <= previous_attempt:
            raise ValueError("Versions must have increasing non-negative attempt numbers.")
        previous_attempt = attempt
        generation = version.get("generation")
        if not isinstance(generation, Mapping) or not isinstance(generation.get("output"), str):
            raise ValueError("Each version must contain a generated output string.")
        validation = version.get("validation")
        if not isinstance(validation, Mapping) or type(validation.get("valid")) is not bool:
            raise ValueError("Each version must contain a boolean validation valid flag.")
        issues, evidence = validation.get("issues"), validation.get("evidence")
        if not isinstance(issues, list) or not isinstance(evidence, list):
            raise ValueError("Validation must contain issues and evidence lists.")
        if any(not isinstance(issue, Mapping) or issue.get("classification") not in
               ("fixable", "missing_information") for issue in issues):
            raise ValueError("Each validation issue needs a supported classification.")
        if any(not isinstance(item, Mapping) for item in evidence):
            raise ValueError("Validation evidence entries must be mappings.")
        if not isinstance(version.get("feedback"), Mapping):
            raise ValueError("Each version must preserve its feedback mapping.")
        counts.append(sum(issue["classification"] == "fixable" for issue in issues))
        passing.append(validation["valid"] and not issues and all(
            item.get("status", "passed") == "passed" for item in evidence
        ))

    selected_index = next((index for index, passed in enumerate(passing) if passed), None)
    if selected_index is None:
        selected_index = min(range(len(versions)), key=lambda index: counts[index])
        reason = "fewest_fixable_issues"
    else:
        reason = "first_passing_version"
    selected = versions[selected_index]
    validation = selected["validation"]
    record = deepcopy({
        "selected_version_index": selected_index,
        "selected_attempt": selected["attempt"],
        "artifact": selected["generation"]["output"],
        "selection_reason": reason,
        "valid": passing[selected_index],
        "fixable_issue_count": counts[selected_index],
        "unresolved_issues": validation["issues"],
        "missing_information": [issue for issue in validation["issues"]
                                if issue["classification"] == "missing_information"],
        "unresolved_checks": [item for item in validation["evidence"]
                              if "status" in item and item["status"] != "passed"],
        "versions": versions,
        "validation_history": [version["validation"] for version in versions],
        "feedback_history": [version["feedback"] for version in versions],
        "attempts": refinement_result["attempts"],
        "stop_reason": refinement_result["stop_reason"],
    })
    # Enforce JSON-ready data without replacing missing values or serializing objects to strings.
    json.dumps(record, allow_nan=False)
    return record
