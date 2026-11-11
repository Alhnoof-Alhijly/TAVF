
import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from run_baseline import build_prompt
from cost_tracker import check_budget

ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = ROOT / "data/pilot/pilot_tasks.json"
OUTPUT_DIR = ROOT / "results/pilot"
OUTPUT_FILE = OUTPUT_DIR / "pilot_outputs.json"
ERROR_FILE = OUTPUT_DIR / "pilot_errors.jsonl"

MODEL = "gpt-5.4-mini-2026-03-17"
PROMPT_VERSION = "v1"
MAX_OUTPUT_TOKENS = 8192


def get_prompt_hash(prompt):
    return hashlib.sha256(
        prompt.encode("utf-8")
    ).hexdigest()


def save_results(records):
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    temporary = OUTPUT_FILE.with_suffix(".tmp")

    temporary.write_text(
        json.dumps(
            records,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    temporary.replace(OUTPUT_FILE)


def log_error(task_id, error):
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    record = {
        "task_id": task_id,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat()
    }

    with ERROR_FILE.open(
        "a",
        encoding="utf-8"
    ) as f:
        f.write(
            json.dumps(
                record,
                ensure_ascii=False
            ) + "\n"
        )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--execute",
        action="store_true",
        help="Enable paid API requests."
    )

    parser.add_argument(
        "--confirm-paid",
        action="store_true",
        help="Confirm paid execution."
    )

    args = parser.parse_args()

    # Load the three pilot tasks
    tasks = json.loads(
        DATA_FILE.read_text(
            encoding="utf-8"
        )
    )

    assert len(tasks) == 3, (
        "Expected exactly three pilot tasks."
    )

    assert len({
        task["task_id"]
        for task in tasks
    }) == 3, "Duplicate task IDs."

    assert len({
        task["task_type"]
        for task in tasks
    }) == 3, "Expected one task per category."

    # Prepare prompts
    prepared = {}

    for task in tasks:
        prompt = build_prompt(task)

        assert prompt.strip(), (
            f"Empty prompt: {task['task_id']}"
        )

        prepared[task["task_id"]] = {
            "prompt": prompt,
            "hash": get_prompt_hash(prompt)
        }

    # Default mode: no API calls
    if not args.execute:
        print("PILOT — DRY RUN")
        print("Model:", MODEL)

        for task in tasks:
            print(
                task["task_id"],
                task["task_type"],
                "READY"
            )

        print("Prepared:", len(tasks))
        print("API calls: 0")
        return

    # Require explicit confirmation
    if not args.confirm_paid:
        parser.error(
            "Paid execution requires "
            "--execute and --confirm-paid."
        )

    # Load the API key
    load_dotenv(ROOT / ".env")

    if not os.getenv("OPENAI_API_KEY"):
        parser.error(
            "OPENAI_API_KEY is missing."
        )

    # Load previously saved results
    if OUTPUT_FILE.exists():
        records = json.loads(
            OUTPUT_FILE.read_text(
                encoding="utf-8"
            )
        )
    else:
        records = []

    completed = {}

    for record in records:
        task_id = record["task_id"]

        if task_id in completed:
            raise ValueError(
                f"Duplicate saved result: {task_id}"
            )

        if record["model"] != MODEL:
            raise ValueError(
                "Saved results use a different model."
            )

        completed[task_id] = record

    # Validate saved prompts before resuming
    for task in tasks:
        task_id = task["task_id"]

        if task_id not in completed:
            continue

        saved = completed[task_id]

        if (
            saved["prompt_hash"]
            != prepared[task_id]["hash"]
            or saved["prompt_version"]
            != PROMPT_VERSION
        ):
            raise ValueError(
                f"Prompt changed for {task_id}"
            )

    from openai import OpenAI

    client = OpenAI(
        max_retries=0,
        timeout=120
    )

    # Execute pending pilot tasks
    for task in tasks:
        task_id = task["task_id"]

        if task_id in completed:
            print(
                "Skipping completed:",
                task_id
            )
            continue

        prompt_data = prepared[task_id]

        # Check the budget before every request
        if not check_budget(
            estimated_input_tokens=len(
                prompt_data["prompt"]
            ),
            max_output_tokens=MAX_OUTPUT_TOKENS,
        ):
            print(
                "Pilot stopped: budget safety limit."
            )
            break

        start = time.perf_counter()

        try:
            response = client.responses.create(
                model=MODEL,
                input=prompt_data["prompt"],
                reasoning={
                    "effort": "none"
                },
                max_output_tokens=MAX_OUTPUT_TOKENS,
            )

            output = response.output_text

            if not output or not output.strip():
                raise ValueError(
                    "Model returned an empty output."
                )

            elapsed = (
                time.perf_counter() - start
            )

            usage = response.usage

            input_tokens = (
                usage.input_tokens
                if usage else None
            )

            output_tokens = (
                usage.output_tokens
                if usage else None
            )

            cached_tokens = 0

            if usage:
                details = getattr(
                    usage,
                    "input_tokens_details",
                    None
                )

                if details:
                    cached_tokens = (
                        getattr(
                            details,
                            "cached_tokens",
                            0
                        ) or 0
                    )

            record = {
                "task_id": task_id,
                "task_type": task["task_type"],
                "method": "baseline_pilot",
                "model": MODEL,
                "prompt_version": PROMPT_VERSION,
                "prompt_hash": prompt_data["hash"],
                "output": output,
                "response_id": response.id,
                "execution_time_seconds": round(
                    elapsed,
                    3
                ),
                "llm_calls": 1,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cached_input_tokens": cached_tokens,
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat()
            }

            records.append(record)
            save_results(records)

            completed[task_id] = record

            print(
                "Completed:",
                task_id
            )

        except Exception as error:
            log_error(
                task_id,
                error
            )

            print(
                "Stopped at:",
                task_id
            )

            print(
                "Error:",
                error
            )

            print(
                "Previously saved results are preserved."
            )

            break

    print(
        "Saved pilot results:",
        len(records)
    )


if __name__ == "__main__":
    main()
