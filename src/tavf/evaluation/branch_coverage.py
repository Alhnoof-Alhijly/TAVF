"""TestEval branch-block entry evaluation using the isolated line tracer.

TestEval counts a block as entered when start + 1 is executed. This is its
block-entry metric, not full control-flow arc coverage or assertion correctness.
"""

from collections.abc import Mapping

from tavf.evaluation.line_coverage import evaluate_line_target


def evaluate_branch_target(artifact: str, task: Mapping) -> dict:
    """Evaluate one selected branch without executing code outside Docker."""
    invalid = {"status": "not_verified",
               "message": "A valid selected branch block and program source are required.",
               "evidence": {"target_type": "branch", "definition": "TestEval block entry: start + 1",
                            "executed_lines": [], "assertion_correctness": "not_verified"}}
    if not isinstance(task, Mapping):
        return invalid
    reference, context = task.get("reference"), task.get("input")
    if not isinstance(reference, Mapping) or not isinstance(context, Mapping):
        return invalid
    target, source = reference.get("target"), context.get("python_solution")
    if (reference.get("target_type") != "branch" or not isinstance(target, Mapping)
            or set(target) != {"start", "end"} or not isinstance(source, str)):
        return invalid
    start, end = target["start"], target["end"]
    if type(start) is not int or type(end) is not int or not 1 <= start < end <= len(source.splitlines()):
        return invalid
    entry_line = start + 1
    # Adapt only the target, preserving the original program, task and test
    # source. The line evaluator owns Docker isolation, tracing and cleanup.
    line_task = dict(task)
    line_task["reference"] = {**reference, "target_type": "line", "target": {"line": entry_line}}
    evaluated = evaluate_line_target(artifact, line_task)
    evidence = {**evaluated["evidence"], "target_type": "branch",
                "target": {"start": start, "end": end}, "entry_line": entry_line,
                "definition": "TestEval block entry: start + 1"}
    messages = {
        "covered": "Selected branch block entry line was observed.",
        "not_covered": "Selected branch block entry line was not observed in the completed run.",
    }
    return {"status": evaluated["status"],
            "message": messages.get(evaluated["status"], evaluated["message"]), "evidence": evidence}
