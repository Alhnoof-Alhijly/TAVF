
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from baseline.baseline_runner import BaselineRunner
from utils.llm_client import LLMClient
from utils.logger import ExperimentLogger
from cost_tracker import check_budget

DATA_FILE = ROOT / "data/pilot/pilot_tasks.json"

MOCK_LOG_DIR = ROOT / "experiments/baseline/pilot/mock_logs"
REAL_LOG_DIR = ROOT / "experiments/baseline/pilot/real_logs"

# Existing cost tracker reads this file.
RESULTS_FILE = ROOT / "results/pilot/pilot_outputs.json"

MODEL = "gpt-5.4-mini-2026-03-17"
MAX_OUTPUT_TOKENS = 8192


class FakeLLMClient:
    """Local simulation without API requests."""

    model = "fake-test-model"
    reasoning_effort = "none"
    max_output_tokens = MAX_OUTPUT_TOKENS

    def generate(self, prompt):
        return {
            "model": self.model,
            "output": "Simulated baseline response",
            "response_id": None,
            "parameters": {
                "reasoning_effort": self.reasoning_effort,
                "max_output_tokens": self.max_output_tokens,
            },
            "input_tokens": None,
            "output_tokens": None,
            "cached_input_tokens": None,
            "execution_time_seconds": 0.0,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }


def load_tasks():
    tasks = json.loads(
        DATA_FILE.read_text(encoding="utf-8")
    )

    assert len(tasks) == 3, "Expected three pilot tasks."
    assert len({t["task_id"] for t in tasks}) == 3
    assert len({t["task_type"] for t in tasks}) == 3

    return tasks


def save_results(records):
    RESULTS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = RESULTS_FILE.with_suffix(".tmp")

    temporary.write_text(
        json.dumps(
            records,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    temporary.replace(RESULTS_FILE)


def run_mock(tasks):
    # Separate logs for every local test.
    logger = ExperimentLogger(log_dir=MOCK_LOG_DIR)
    runner = BaselineRunner(
        client=FakeLLMClient(),
        logger=logger,
    )

    print("BASELINE PILOT — MOCK TEST")

    for task in tasks:
        result = runner.run_task(task)

        print(
            result["task_id"],
            result["task_type"],
            "SUCCESS",
        )

    print("Completed:", len(tasks))
    print("Real API calls: 0")


def run_real(tasks):
    client = LLMClient(
        model=MODEL,
        reasoning_effort="none",
        max_output_tokens=MAX_OUTPUT_TOKENS,
    )

    logger = ExperimentLogger(log_dir=REAL_LOG_DIR)

    runner = BaselineRunner(
        client=client,
        logger=logger,
    )

    if RESULTS_FILE.exists():
        records = json.loads(
            RESULTS_FILE.read_text(encoding="utf-8")
        )
    else:
        records = []

    completed = {}

    for record in records:
        task_id = record["task_id"]

        if task_id in completed:
            raise ValueError(
                f"Duplicate saved task: {task_id}"
            )

        if record["model"] != MODEL:
            raise ValueError(
                "Saved pilot results use another model."
            )

        completed[task_id] = record

    print("BASELINE PILOT — REAL EXECUTION")

    for task in tasks:
        task_id = task["task_id"]

        if task_id in completed:
            print("Skipping completed:", task_id)
            continue

        prompt = runner.build_prompt(task)

        # Conservative local estimate, not an API spending cap.
        if not check_budget(
            estimated_input_tokens=len(prompt),
            max_output_tokens=MAX_OUTPUT_TOKENS,
        ):
            print("Stopped: budget safety limit.")
            break

        try:
            result = runner.run_task(task)

            record = {
                **result,
                "llm_calls": 1,
            }

            records.append(record)
            save_results(records)

            completed[task_id] = record

            print("Completed:", task_id)

        except Exception as error:
            print("Stopped at:", task_id)
            print("Error:", error)
            print(
                "Review the logs before retrying. "
                "An interrupted request may still be billed."
            )
            break

    print("Saved real outputs:", len(records))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--execute",
        action="store_true",
        help="Enable real API requests.",
    )

    parser.add_argument(
        "--confirm-paid",
        action="store_true",
        help="Confirm paid execution.",
    )

    args = parser.parse_args()
    tasks = load_tasks()

    if not args.execute:
        run_mock(tasks)
        return

    if not args.confirm_paid:
        parser.error(
            "Paid execution requires both "
            "--execute and --confirm-paid."
        )

    run_real(tasks)


if __name__ == "__main__":
    main()
