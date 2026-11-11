"""Registry and rendering for TAVF generation prompts only."""

from collections.abc import Mapping
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


def build_prompt(task_type: str, task_input: Mapping) -> str:
    """Render a validated task type using designated input fields only."""
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

    template = (PROMPT_DIR / filename).read_text(encoding="utf-8")
    return template.format(**context)
