"""Launch only the explicitly authorized three-task pilot with a tighter cap."""

from collections import Counter
from decimal import Decimal
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import cost_tracker
import run_experiment as driver
from tavf.refinement import MAX_REFINEMENT_ATTEMPTS
from utils.llm_client import LLMClient

DIRECTORY = Path(__file__).resolve().parent
IDS = ["US500-g05-openspending-L0061", "BR500-1784085", "testeval-1805-line"]
CAP = Decimal("1.00")


class ObservedClient:
    """Record sanitized failure diagnostics; leave API/retry behavior unchanged."""
    def __init__(self):
        self.client = LLMClient()
        for field in ("model", "reasoning_effort", "max_output_tokens"):
            setattr(self, field, getattr(self.client, field))

    def generate(self, prompt):
        try:
            return self.client.generate(prompt)
        except Exception as error:
            diagnostic = {"error_type": type(error).__name__,
                          "http_status": getattr(error, "status_code", None)}
            code = getattr(error, "code", None)
            if isinstance(code, str) and len(code) < 100:
                diagnostic["provider_code"] = code
            driver._save(DIRECTORY / "api_error.json", diagnostic)
            print(json.dumps({"api_failure": diagnostic}), flush=True)
            raise


def main():
    indexed = {task["task_id"]: task for task in driver.load_tasks()}
    tasks = [indexed[task_id] for task_id in IDS]
    if len({task["task_type"] for task in tasks}) != 3 or MAX_REFINEMENT_ATTEMPTS != 2:
        raise ValueError("Pilot selection or refinement configuration differs")
    prior = {"budget": str(cost_tracker.BUDGET), "safety_limit": str(cost_tracker.SAFETY_LIMIT)}
    # Only tighten configuration in this pilot process. Keep both existing
    # budget checks active, including the driver's durable-request accounting.
    cost_tracker.BUDGET = min(cost_tracker.BUDGET, CAP)
    cost_tracker.SAFETY_LIMIT = min(cost_tracker.SAFETY_LIMIT, CAP)
    driver.BUDGET = min(driver.BUDGET, CAP)
    driver.SAFETY_LIMIT = min(driver.SAFETY_LIMIT, CAP)
    config = {"task_ids": IDS, "pilot_cap_usd": str(CAP), "original_guard": prior,
              "model": driver.DEFAULT_MODEL, "max_refinements": 2, "docker_execution": False,
              "prices_per_million_tokens": {"input": str(cost_tracker.INPUT_PRICE),
                                            "cached_input": str(cost_tracker.CACHED_INPUT_PRICE),
                                            "output": str(cost_tracker.OUTPUT_PRICE)}}
    config_path = DIRECTORY / "pilot_config.json"
    if config_path.exists() and json.loads(config_path.read_text(encoding="utf-8")) != config:
        raise ValueError("Pilot settings changed; resume refused")
    driver._save(config_path, config)
    driver._save(DIRECTORY / "selected_tasks.json", tasks)
    print(json.dumps({"pilot_preflight": config}), flush=True)
    outcome = driver.run_experiment(tasks, DIRECTORY, execute=True, client=ObservedClient())
    requests = [json.loads(path.read_text(encoding="utf-8")) for path in sorted((DIRECTORY / "requests").glob("*.json"))]
    costs, total_input, total_output, total_cached = [], 0, 0, 0
    for request in requests:
        if request["state"] != "completed":
            continue
        response = request["response"]
        regular, output, cached = response["input_tokens"], response["output_tokens"], response.get("cached_input_tokens", 0) or 0
        cost = cost_tracker.calculate_cost(regular, output, cached)
        total_input += regular
        total_output += output
        total_cached += cached
        costs.append({"task_id": request["task_id"], "method": request["method"],
                      "sequence": request["sequence"], "response_id": response.get("response_id"),
                      "input_tokens": regular, "output_tokens": output, "cached_input_tokens": cached,
                      "actual_usage_cost_usd": str(cost)})
    total = sum((Decimal(item["actual_usage_cost_usd"]) for item in costs), Decimal("0"))
    saved = [json.loads(path.read_text(encoding="utf-8")) for path in (DIRECTORY / "results").glob("*.json")]
    lookup = {(record["task"]["task_id"], record["method"]): record for record in saved}
    if len(lookup) != len(saved):
        raise ValueError("Duplicate final outputs")
    rows = []
    for task in tasks:
        for method in ("baseline", "tavf"):
            record = lookup.get((task["task_id"], method))
            result = record["result"] if record else {}
            artifact = result.get("output") if method == "baseline" else result.get("artifact")
            intact = record is not None and record["task"] == task
            present = intact and isinstance(artifact, str) and bool(artifact.strip())
            relevant = [item for item in costs if item["task_id"] == task["task_id"] and item["method"] == method]
            rows.append({"task_id": task["task_id"], "task_type": task["task_type"], "method": method,
                         "success": present and result.get("status") != "failed",
                         "output_saved": present, "framework_status": result.get("status", "saved" if present else "not_saved"),
                         "valid": result.get("valid"), "refinements": len(result.get("attempts", [])),
                         "validation_history_entries": len(result.get("validation_history", [])),
                         "api_requests": len(relevant),
                         "actual_usage_cost_usd": str(sum((Decimal(item["actual_usage_cost_usd"]) for item in relevant), Decimal("0")))})
    summary = {"driver": outcome, "outputs": rows, "final_outputs_saved": sum(row["output_saved"] for row in rows),
               "all_six_saved": len(saved) == 6 and all(row["output_saved"] for row in rows),
               "completed_api_requests": len(costs), "unresolved_requests": sum(r["state"] != "completed" for r in requests),
               "input_tokens": total_input, "output_tokens": total_output, "cached_input_tokens": total_cached,
               "actual_usage_cost_usd": str(total), "pilot_cap_usd": str(CAP),
               "cost_basis": "Reported API token usage at recorded repository rates; not a billing invoice.",
               "calls": costs}
    driver._save(DIRECTORY / "pilot_summary.json", summary)
    print(json.dumps(summary, sort_keys=True), flush=True)
    if total > CAP:
        raise ValueError("Recorded pilot cost exceeded cap")


if __name__ == "__main__":
    main()
