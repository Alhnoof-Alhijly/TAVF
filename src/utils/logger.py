
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[2]

DEFAULT_LOG_DIR = ROOT / "experiments/baseline/logs"


class ExperimentLogger:
    """Record experiment outputs and errors as JSONL."""

    def __init__(self, log_dir=DEFAULT_LOG_DIR):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.results_file = self.log_dir / "results.jsonl"
        self.errors_file = self.log_dir / "errors.jsonl"

    @staticmethod
    def timestamp():
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def append_record(path, record):
        with path.open("a", encoding="utf-8") as file:
            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )
            file.flush()
            os.fsync(file.fileno())

    def log_success(self, task, prompt, response):
        """Store a successful LLM generation."""

        record = {
            "run_id": str(uuid4()),
            "task_id": task["task_id"],
            "task_type": task["task_type"],
            "method": "baseline",
            "prompt_version": "v1",
            "prompt": prompt,
            "model": response["model"],
            "parameters": response.get("parameters", {}),
            "response": response["output"],
            "response_id": response.get("response_id"),
            "input_tokens": response.get("input_tokens"),
            "output_tokens": response.get("output_tokens"),
            "cached_input_tokens": response.get(
                "cached_input_tokens"
            ),
            "execution_time_seconds": response.get(
                "execution_time_seconds"
            ),
            "timestamp": response.get(
                "timestamp",
                self.timestamp()
            ),
            "status": "success"
        }

        self.append_record(
            self.results_file,
            record
        )

        return record

    def log_error(
        self,
        task,
        prompt,
        error,
        model,
        parameters=None
    ):
        """Store a failed generation attempt."""

        record = {
            "run_id": str(uuid4()),
            "task_id": task["task_id"],
            "task_type": task["task_type"],
            "method": "baseline",
            "prompt_version": "v1",
            "prompt": prompt,
            "model": model,
            "parameters": parameters or {},
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": self.timestamp(),
            "status": "error"
        }

        self.append_record(
            self.errors_file,
            record
        )

        return record
