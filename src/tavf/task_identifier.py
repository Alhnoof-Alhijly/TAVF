"""Identify tasks from their supplied schema-defined task type only."""

import json
from collections.abc import Mapping
from pathlib import Path


SCHEMA_FILE = Path(__file__).resolve().parents[2] / "data/task_schema.json"
SUPPORTED_TASK_TYPES = tuple(
    json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    ["properties"]["task_type"]["enum"]
)


def identify_task(task: Mapping) -> str:
    """Return the supplied task type without inferring it from task content.

    This component validates only task_type, not the complete task schema.
    """
    if not isinstance(task, Mapping):
        raise TypeError("Task must be a mapping containing 'task_type'.")

    if "task_type" not in task:
        raise ValueError("Missing required field: task_type.")

    task_type = task["task_type"]
    if not isinstance(task_type, str) or task_type not in SUPPORTED_TASK_TYPES:
        raise ValueError(
            f"Unsupported task_type: {task_type!r}. "
            f"Expected one of: {', '.join(SUPPORTED_TASK_TYPES)}."
        )

    return task_type
