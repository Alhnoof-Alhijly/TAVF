
import argparse
import hashlib
import json
import os
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from cost_tracker import check_budget
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data/processed/experiment_tasks.json"
PROMPT_DIR = ROOT / "prompts/baseline"
OUTPUT_DIR = ROOT / "results/baseline"

OUTPUT_FILE = OUTPUT_DIR / "baseline_outputs.json"
ERROR_FILE = OUTPUT_DIR / "baseline_errors.jsonl"

PROMPT_FILES = {
    "user_story_refinement": "user_story.txt",
    "bug_report_refinement": "bug_report.txt",
    "test_case_generation": "test_case.txt",
}

PROMPT_VERSION = "v1"


def build_prompt(task):
    path = PROMPT_DIR / PROMPT_FILES[task["task_type"]]
    template = path.read_text(encoding="utf-8")
    return template.format(**task["input"])


def prompt_hash(prompt):
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def save_results(records):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Atomic replacement protects previously saved results.
    temporary = OUTPUT_FILE.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary.replace(OUTPUT_FILE)


def log_error(task_id, error):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    record = {
        "task_id": task_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error_type": type(error).__name__,
        "error_message": str(error),
    }

    with ERROR_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--execute",
        action="store_true",
        help="Enable paid API requests.",
    )
    parser.add_argument("--model", default=None)
    parser.add_argument("--limit", type=int, default=60)

    args = parser.parse_args()

    if not 1 <= args.limit <= 60:
        parser.error("--limit must be between 1 and 60")

    tasks = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    assert len(tasks) == 60, "Expected exactly 60 tasks."
    assert len({t["task_id"] for t in tasks}) == 60

    selected = tasks[:args.limit]

    # Prepare prompts without making API calls.
    prepared = {
        task["task_id"]: build_prompt(task)
        for task in selected
    }

    if not args.execute:
        print("DRY RUN — No API requests")
        print("Total tasks:", len(tasks))
        print("Prepared:", len(prepared))
        print(
            "Distribution:",
            dict(Counter(t["task_type"] for t in tasks)),
        )
        print("API calls: 0")
        return

    load_dotenv(ROOT / ".env")

    if not args.model:
        parser.error("--model is required with --execute")

    if not os.getenv("OPENAI_API_KEY"):
        parser.error("OPENAI_API_KEY is missing")

    # Load previous results for safe resumption.
    if OUTPUT_FILE.exists():
        records = json.loads(
            OUTPUT_FILE.read_text(encoding="utf-8")
        )
    else:
        records = []

    completed = {}

    for record in records:
        task_id = record["task_id"]

        if task_id in completed:
            raise ValueError(f"Duplicate saved result: {task_id}")

        if record["model"] != args.model:
            raise ValueError(
                "Saved results use a different model. "
                "Do not mix experiments."
            )

        completed[task_id] = record

    # Detect changes to previously executed prompts.
    for task in selected:
        task_id = task["task_id"]

        if task_id in completed:
            saved = completed[task_id]
            current_hash = prompt_hash(prepared[task_id])

            if (
                saved.get("prompt_version") != PROMPT_VERSION
                or saved.get("prompt_hash") != current_hash
            ):
                raise ValueError(
                    f"Prompt changed for completed task: {task_id}"
                )

    from openai import OpenAI

    client = OpenAI(max_retries=0, timeout=120)

    for task in selected:
        task_id = task["task_id"]

        if task_id in completed:
            print("Skipping completed:", task_id)
            continue

        prompt = prepared[task_id]

        # Check the budget before each API request.
        if not check_budget(
            estimated_input_tokens=len(prompt),
            max_output_tokens=8192,
        ):
            print("Baseline stopped: budget safety limit.")
            break

        start = time.perf_counter()

        try:
            response = client.responses.create(
            model=args.model,
            input=prompt,
            reasoning={"effort": "none"},
            max_output_tokens=8192,
            )

            elapsed = time.perf_counter() - start
            usage = response.usage

            record = {
                "task_id": task_id,
                "task_type": task["task_type"],
                "method": "baseline",
                "model": args.model,
                "prompt_version": PROMPT_VERSION,
                "prompt_hash": prompt_hash(prompt),
                "output": response.output_text,
                "response_id": response.id,
                "execution_time_seconds": round(elapsed, 3),
                "llm_calls": 1,
                "input_tokens": (
                    usage.input_tokens if usage else None
                ),
                "output_tokens": (
                    usage.output_tokens if usage else None
                ),
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            }

            records.append(record)
            save_results(records)

            completed[task_id] = record
            print("Completed:", task_id)

        except Exception as error:
            log_error(task_id, error)
            print(f"Stopped at {task_id}: {error}")
            print("Previous results remain saved.")
            print(
                "Check the error before restarting. "
                "An interrupted request may still be billed."
            )
            break

    print("Total saved results:", len(records))


if __name__ == "__main__":
    main()
