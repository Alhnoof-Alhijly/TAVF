"""Authorized main generation run, capped at $5; no Final Evaluation."""

from collections import Counter
from contextlib import redirect_stdout
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import cost_tracker
import run_experiment as driver
from utils.llm_client import LLMClient
from tavf.refinement import MAX_REFINEMENT_ATTEMPTS
from experiment_paths import launcher_sha256

DIRECTORY = ROOT / "results" / "main_experiment"
CAP = Decimal("5.00")
SAVE = driver._save
REQUESTS, RESULTS = {}, {}
STATUS = "preflight"


def refresh_summary():
    costs, inputs, outputs, cached, refinements = Decimal("0"), 0, 0, 0, 0
    counts, validations = Counter(), Counter()
    failures, unresolved = [], []
    for key, request in REQUESTS.items():
        if request.get("state") != "completed":
            unresolved.append({"request": key, "task_id": request.get("task_id"),
                               "method": request.get("method"), "state": request.get("state")})
            continue
        response = request["response"]
        inputs += response["input_tokens"]
        outputs += response["output_tokens"]
        cached += response.get("cached_input_tokens", 0) or 0
        costs += cost_tracker.calculate_cost(response["input_tokens"], response["output_tokens"],
                                             response.get("cached_input_tokens", 0) or 0)
        refinements += request.get("method") == "tavf" and request.get("sequence", 0) > 0
    for record in RESULTS.values():
        task, method, result = record["task"], record["method"], record["result"]
        artifact = result.get("output") if method == "baseline" else result.get("artifact")
        if isinstance(artifact, str) and artifact.strip():
            counts[(task["task_type"], method)] += 1
        else:
            failures.append({"task_id": task["task_id"], "method": method, "reason": "no_final_output"})
        if result.get("status") == "failed":
            failures.append({"task_id": task["task_id"], "method": method, "reason": result.get("stop_reason", "failed")})
        if method == "tavf":
            validations[result.get("status", "unknown")] += 1
    summary = {"status": STATUS, "updated_utc": datetime.now(timezone.utc).isoformat(),
               "api_cap_usd": str(CAP), "actual_usage_cost_usd": str(costs),
               "cost_basis": "Reported API token usage at recorded repository prices; not a billing invoice.",
               "cost_verified": not unresolved,
               "completed_by_task_and_method": {task_type: {method: counts[(task_type, method)] for method in ("baseline", "tavf")}
                                                for task_type in driver.DATASETS.values()},
               "final_outputs_saved": sum(counts.values()), "expected_outputs": 3000,
               "completed_api_requests": sum(r.get("state") == "completed" for r in REQUESTS.values()),
               "refinement_requests": refinements, "tavf_framework_status_counts": dict(validations),
               "input_tokens": inputs, "output_tokens": outputs, "cached_input_tokens": cached,
               "failures": failures, "unresolved_requests": unresolved,
               "final_evaluation": "not_run", "docker_execution": False}
    SAVE(DIRECTORY / "run_summary.json", summary)
    if costs > CAP:
        raise RuntimeError("Recorded spending exceeds cap; stop")
    return summary


def observed_save(path, value):
    SAVE(path, value)
    if path.parent == DIRECTORY / "requests":
        enriched = dict(value)
        if value.get("state") == "completed":
            response = value["response"]
            enriched["actual_usage_cost_usd"] = str(cost_tracker.calculate_cost(
                response["input_tokens"], response["output_tokens"], response.get("cached_input_tokens", 0) or 0))
            # Supplementary cost record; preserve the driver's request format.
            SAVE(DIRECTORY / "costs" / path.name, {key: enriched[key] for key in (
                "task_id", "method", "sequence", "actual_usage_cost_usd") } | {
                    "response_id": response.get("response_id"), "input_tokens": response["input_tokens"],
                    "output_tokens": response["output_tokens"], "cached_input_tokens": response.get("cached_input_tokens", 0) or 0})
        REQUESTS[path.stem] = enriched
        refresh_summary()
    elif path.parent == DIRECTORY / "results":
        RESULTS[path.stem] = value
        refresh_summary()
        if value["result"].get("status") == "failed":
            raise RuntimeError("Critical failed framework result; stopped after preserving it")


class ObservedClient:
    def __init__(self):
        self.client = LLMClient()
        for field in ("model", "reasoning_effort", "max_output_tokens"):
            setattr(self, field, getattr(self.client, field))

    def generate(self, prompt):
        try:
            return self.client.generate(prompt)
        except Exception as error:
            diagnostic = {"error_type": type(error).__name__, "http_status": getattr(error, "status_code", None)}
            code = getattr(error, "code", None)
            if isinstance(code, str) and len(code) < 100:
                diagnostic["provider_code"] = code
            SAVE(DIRECTORY / "api_error.json", diagnostic)
            raise


def main():
    global STATUS
    tasks = driver.load_tasks()
    if len(tasks) != 1500 or MAX_REFINEMENT_ATTEMPTS != 2:
        raise ValueError("Main run configuration differs")
    config = {"cap_usd": str(CAP), "task_count": len(tasks), "expected_outputs": 3000,
              "model": driver.DEFAULT_MODEL, "reasoning_effort": "none",
              "max_output_tokens": driver.MAX_OUTPUT_TOKENS, "max_refinements": 2,
              "original_guard": {"budget": str(cost_tracker.BUDGET), "safety_limit": str(cost_tracker.SAFETY_LIMIT)},
              "rates_per_million_tokens": {"input": str(cost_tracker.INPUT_PRICE),
                                            "cached_input": str(cost_tracker.CACHED_INPUT_PRICE),
                                            "output": str(cost_tracker.OUTPUT_PRICE)},
              "launcher_sha256": launcher_sha256(Path(__file__)),
              "final_evaluation": "not_run", "docker_execution": False}
    config_path = DIRECTORY / "run_config.json"
    if config_path.exists() and json.loads(config_path.read_text(encoding="utf-8")) != config:
        raise ValueError("Run settings changed; resume refused")
    SAVE(config_path, config)
    # The user explicitly authorized this $5 main-run limit. Keep the legacy
    # and cumulative driver checks enabled, including per-request reservations.
    cost_tracker.BUDGET = cost_tracker.SAFETY_LIMIT = CAP
    driver.BUDGET = driver.SAFETY_LIMIT = CAP
    for path in (DIRECTORY / "requests").glob("*.json"):
        REQUESTS[path.stem] = json.loads(path.read_text(encoding="utf-8"))
    for path in (DIRECTORY / "results").glob("*.json"):
        RESULTS[path.stem] = json.loads(path.read_text(encoding="utf-8"))
    STATUS = "running"
    refresh_summary()
    driver._save = observed_save
    print(json.dumps({"main_run": config}), flush=True)
    try:
        with (DIRECTORY / "run.log").open("a", encoding="utf-8", buffering=1) as log:
            with redirect_stdout(log):
                outcome = driver.run_experiment(tasks, DIRECTORY, execute=True, client=ObservedClient())
        STATUS = outcome["status"]
        SAVE(DIRECTORY / "driver_outcome.json", outcome)
    except Exception as error:
        STATUS = "critical_error"
        SAVE(DIRECTORY / "critical_error.json", {"error_type": type(error).__name__})
    summary = refresh_summary()
    print(json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
