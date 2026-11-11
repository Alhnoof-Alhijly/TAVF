"""Single-task TAVF orchestration; no batch execution or final evaluation."""

import json
from collections.abc import Mapping
from copy import deepcopy

from tavf.final_output import build_final_output
from tavf.generation import GenerationError, generate_initial_output
from tavf.prompting import build_prompt
from tavf.refinement import refine_output
from tavf.task_identifier import identify_task
from utils.llm_client import LLMClient


def run_task(task: Mapping, client=None, *, execute: bool = False,
             trusted_oracle: dict | None = None) -> dict:
    """Run one JSON-ready task with a shared client for initial and revised output.

    Inject an LLMClient backed by a mock provider for offline use. Invalid task
    types/inputs raise before client construction. Generation failures return
    a failed record retaining task, prompt, and all available history. Provider
    exception details are never copied into the record. No files are written.
    Internal validation, feedback and revision routing are owned by refinement.
    Test-case execute/trusted_oracle options apply to every version. Docker is
    disabled by default; trusted examples must be explicitly supplied by callers.
    """
    task_type = identify_task(task)
    if task_type == "test_case_generation":
        prompt = build_prompt(task_type, task.get("input"), task_reference=task.get("reference"))
    else:
        prompt = build_prompt(task_type, task.get("input"))
    task_snapshot = deepcopy(dict(task))
    # Reject non-JSON task data before any potentially paid request.
    json.dumps(task_snapshot, allow_nan=False)
    record = {
        "task": task_snapshot,
        "task_id": task.get("task_id"),
        "task_type": task_type,
        "method": "tavf",
        "initial_prompt": prompt,
        "status": "failed",
        "artifact": None,
        "valid": False,
        "versions": [],
        "validation_history": [],
        "feedback_history": [],
        "generation_history": [],
        "attempts": [],
        "errors": [],
    }

    if client is None:
        try:
            client = LLMClient()
        except Exception:
            record["stop_reason"] = "client_initialization_failed"
            record["errors"].append({"stage": "generation", "message": "LLM client initialization failed."})
            return record

    try:
        initial = generate_initial_output(prompt, client=client)
    except GenerationError:
        record["stop_reason"] = "initial_generation_failed"
        record["errors"].append({"stage": "generation", "message": "Initial generation failed."})
        return record

    record["generation_history"].append({"attempt": 0, "generation": deepcopy(initial)})
    try:
        # Components 4 and 5 run inside refinement before any revision request;
        # refinement then repeats them after each successful attempt.
        refinement = refine_output(task_type, task["input"], initial, client,
                                   execute=execute, trusted_oracle=trusted_oracle)
    except (ValueError, TypeError):
        record["stop_reason"] = "refinement_setup_failed"
        record["errors"].append({"stage": "refinement", "message": "Refinement setup failed; check client configuration and generation metadata."})
        return record

    record.update(build_final_output(refinement))
    record["generation_history"].extend(
        {"attempt": attempt["attempt"], "generation": deepcopy(attempt["generation"])}
        for attempt in refinement["attempts"] if "generation" in attempt
    )
    failed = [attempt for attempt in refinement["attempts"] if attempt["status"] == "failed"]
    if failed:
        record["errors"] = [{"stage": "refinement", "attempt": attempt["attempt"],
                             "message": attempt["error"]} for attempt in failed]
        record["status"] = "failed"
    else:
        record["status"] = "completed" if record["valid"] else "unresolved"
    json.dumps(record, allow_nan=False)
    return record
