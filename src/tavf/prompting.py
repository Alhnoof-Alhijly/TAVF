"""Registry and rendering for TAVF generation prompts only."""

from collections.abc import Mapping
import json
from pathlib import Path
from types import MappingProxyType


PROMPT_DIR = Path(__file__).resolve().parents[2] / "prompts/tavf"
PROMPT_TEMPLATE_REGISTRY = MappingProxyType({
    "user_story_refinement": ("user_story.txt", ("original_text",)),
    "bug_report_refinement": ("bug_report.txt", ("original_text",)),
    "test_case_generation": (
        "test_case.txt", ("description", "python_solution"),
    ),
})


def build_prompt(task_type: str, task_input: Mapping, *, task_reference: Mapping | None = None) -> str:
    """Render inputs plus only the explicitly selected TestEval target, if supplied."""
    if not isinstance(task_type, str) or task_type not in PROMPT_TEMPLATE_REGISTRY:
        raise ValueError(f"Unsupported task_type: {task_type!r}.")
    if not isinstance(task_input, Mapping):
        raise TypeError("Task input must be a mapping.")

    filename, required_fields = PROMPT_TEMPLATE_REGISTRY[task_type]
    context = {}
    for field in required_fields:
        if field not in task_input:
            raise ValueError(f"Missing required input field: {field}.")
        value = task_input[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Input field '{field}' must be a non-empty string.")
        context[field] = value

    if task_type == "test_case_generation":
        context["target_context"] = _target_context(task_reference)
    template = (PROMPT_DIR / filename).read_text(encoding="utf-8")
    return template.format(**context)


def _target_context(reference):
    if reference is None:
        return ""
    if not isinstance(reference, Mapping):
        raise TypeError("task_reference must be a mapping or None.")
    if "target_type" not in reference and "target" not in reference:
        return ""
    kind, target = reference.get("target_type"), reference.get("target")
    if not isinstance(target, dict):
        raise ValueError("Selected target details must be an object.")
    positive = lambda value: type(value) is int and value > 0
    if kind == "line":
        valid = set(target) == {"line"} and positive(target["line"])
        instruction = "Generate tests that execute the selected line. Line numbers are 1-based in the unchanged reference implementation."
    elif kind == "branch":
        valid = (set(target) == {"start", "end"} and positive(target["start"])
                 and positive(target["end"]) and target["start"] <= target["end"])
        instruction = "Generate tests that execute the selected branch block, from start through end (inclusive, 1-based line numbers)."
    elif kind == "path":
        valid = set(target) == {"execution_path", "condition_path"} and all(
            isinstance(target[key], list) and bool(target[key])
            and all(isinstance(entry, str) and entry.strip() for entry in target[key])
            for key in ("execution_path", "condition_path")
        )
        instruction = "Generate tests that follow the exact selected execution path and satisfy its branch conditions in the given order, including repeated steps."
    else:
        raise ValueError("Selected target type must be line, branch, or path.")
    if not valid:
        raise ValueError("Invalid selected target details for " + kind)
    return ("Selected Target Type: " + kind + "\nSelected Target Details (JSON):\n"
            + json.dumps(target, ensure_ascii=False, indent=2) + "\n"
            + instruction + "\n\n")
