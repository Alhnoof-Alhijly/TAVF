
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from utils.logger import ExperimentLogger

DATA_FILE = ROOT / "data/processed/experiment_tasks.json"
PROMPT_DIR = ROOT / "prompts/baseline"

PROMPT_FILES = {
    "user_story_refinement": "user_story.txt",
    "bug_report_refinement": "bug_report.txt",
    "test_case_generation": "test_case.txt",
}

PROMPT_VERSION = "v1"


class BaselineRunner:
    """Direct prompting without validation or refinement."""

    def __init__(self, client=None, logger=None):
        self.client = client
        self.logger = logger

    def build_prompt(self, task):
        task_type = task["task_type"]

        if task_type not in PROMPT_FILES:
            raise ValueError(
                f"Unsupported task type: {task_type}"
            )

        template = (
            PROMPT_DIR / PROMPT_FILES[task_type]
        ).read_text(encoding="utf-8")

        prompt = template.format(**task["input"])

        if not prompt.strip():
            raise ValueError("Empty prompt.")

        return prompt

    def run_task(self, task):
        if self.client is None:
            raise RuntimeError(
                "An LLM client is required for generation."
            )

        prompt = self.build_prompt(task)

        try:
            response = self.client.generate(prompt)

        except Exception as error:
            if self.logger:
                self.logger.log_error(
                    task=task,
                    prompt=prompt,
                    error=error,
                    model=self.client.model,
                    parameters={
                        "reasoning_effort":
                            self.client.reasoning_effort,
                        "max_output_tokens":
                            self.client.max_output_tokens,
                    },
                )
            raise

        result = {
            "task_id": task["task_id"],
            "task_type": task["task_type"],
            "method": "baseline",
            "prompt_version": PROMPT_VERSION,
            "prompt": prompt,
            **response,
        }

        if self.logger:
            self.logger.log_success(
                task=task,
                prompt=prompt,
                response=response,
            )

        return result


def main():
    # Dry run only: no API requests.
    tasks = json.loads(
        DATA_FILE.read_text(encoding="utf-8")
    )

    assert len(tasks) == 60
    assert len({
        task["task_id"] for task in tasks
    }) == 60

    runner = BaselineRunner()
    counts = Counter()

    for task in tasks:
        runner.build_prompt(task)
        counts[task["task_type"]] += 1

    print("BASELINE PIPELINE — DRY RUN")
    print("Total tasks:", len(tasks))
    print("Distribution:", dict(counts))
    print("API calls: 0")


if __name__ == "__main__":
    main()
