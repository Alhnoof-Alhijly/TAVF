"""One explicitly authorized request; never run the batch or retry automatically."""
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import time

import main_run as main
from connection_diagnostics import describe

D = main.DIRECTORY
KEY = "3a1206f299e5c679fb3dbd8b290625ade0831744b99fdddcee849e4d7630c157"
ATTEMPT = D / "controlled_retry"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def hashes(folder):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.glob("*.json")}


def run():
    with main.driver._lock(D):
        if ATTEMPT.exists():
            raise RuntimeError("One-shot retry already prepared; refusing another dispatch")
        tasks = main.driver.load_tasks()
        main.driver.run_experiment(tasks, D)  # Manifest-only dry run.
        preserved = hashes(D / "results")
        completed_requests = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in (D / "requests").glob("*.json") if read(p)["state"] == "completed"}
        if len(preserved) != 43 or len(completed_requests) != 43:
            raise ValueError("Expected exactly 43 completed outputs and requests")
        path = D / "requests" / (KEY + ".json")
        request = read(path)
        if request["state"] != "uncertain" or "response" in request:
            raise ValueError("Unexpected uncertain checkpoint")
        task = next(t for t in tasks if t["task_id"] == request["task_id"])
        prompt = main.driver.build_prompt(task["task_type"], task["input"], task_reference=task.get("reference"))
        if request["method"] != "tavf" or request["sequence"] != 0 or prompt != request["prompt"]:
            raise ValueError("Retry input differs")
        config = read(D / "run_config.json")
        if (config["model"] != main.driver.DEFAULT_MODEL or config["reasoning_effort"] != "none"
                or config["max_output_tokens"] != main.driver.MAX_OUTPUT_TOKENS):
            raise ValueError("Model settings differ")
        summary = read(D / "run_summary.json")
        reserve = Decimal(summary["reserved_unknown_cost_usd"])
        spent = sum((main.cost_tracker.calculate_cost(r["response"]["input_tokens"], r["response"]["output_tokens"],
                     r["response"].get("cached_input_tokens", 0)) for p in (D / "requests").glob("*.json")
                     if (r := read(p))["state"] == "completed"), Decimal(0))
        estimate = len(prompt.encode("utf-8")) + 512
        next_cost = main.cost_tracker.calculate_cost(estimate, config["max_output_tokens"])
        legacy = main.cost_tracker.calculate_spent()
        projected = legacy + spent + reserve + next_cost
        if projected > Decimal("5.00"):
            raise RuntimeError("Strict $5 aggregate budget check failed")
        # Retain the legacy guard as well as the cumulative request reservation.
        main.cost_tracker.BUDGET = main.cost_tracker.SAFETY_LIMIT = Decimal("5.00")
        original_spent = main.cost_tracker.calculate_spent
        main.cost_tracker.calculate_spent = lambda: original_spent() + spent + reserve
        if not main.cost_tracker.check_budget(estimate, config["max_output_tokens"]):
            raise RuntimeError("Budget guard refused request")
        ATTEMPT.mkdir()
        # Preserve the exact uncertain journal and failure evidence before overwriting any checkpoint.
        for name in ("api_error.json", "critical_error.json", "connection_failure_liability.json", "run_summary.json"):
            (ATTEMPT / ("prior_" + name)).write_bytes((D / name).read_bytes())
        (ATTEMPT / "prior_uncertain_request.json").write_bytes(path.read_bytes())
        audit = {"authorization": "User authorizes exactly one controlled retry despite uncertain prior outcome",
                 "prior_outcome": "still_unknown; conservative reserve retained", "request": KEY,
                 "preserved_result_sha256": preserved, "preserved_request_sha256": completed_requests,
                 "old_reserve_usd": str(reserve), "next_request_reservation_usd": str(next_cost),
                 "legacy_spending_usd": str(legacy), "projected_total_usd": str(projected),
                 "api_cap_usd": "5.00", "max_requests": 1, "created_utc": datetime.now(timezone.utc).isoformat()}
        main.SAVE(ATTEMPT / "authorization.json", audit)
        checkpoint = {**request, "state": "retry_prepared", "prior_uncertain_audit": "controlled_retry/prior_uncertain_request.json"}
        main.SAVE(ATTEMPT / "checkpoint.json", checkpoint)

        from dotenv import load_dotenv
        import httpx2
        from openai import OpenAI
        load_dotenv(main.ROOT / ".env")
        headers, sends = [], []

        def before_send(outgoing):
            if sends:
                raise RuntimeError("Second HTTP dispatch forbidden")
            sends.append({"method": outgoing.method, "host": outgoing.url.host,
                          "path": outgoing.url.path, "time_unix": time.time()})
            main.SAVE(ATTEMPT / "dispatch.json", sends[0])

        def observe(response):
            # Request credentials and bodies are never logged.
            safe = {k: v for k, v in response.headers.items() if k.lower() not in {"set-cookie", "authorization", "proxy-authorization"}}
            headers.append({"http_status": response.status_code, "headers": safe, "received_unix": time.time()})
            main.SAVE(ATTEMPT / "response_headers.json", headers)

        transport = httpx2.Client(follow_redirects=False, event_hooks={"request": [before_send], "response": [observe]})
        sdk = OpenAI(max_retries=0, timeout=120, http_client=transport)
        client = main.LLMClient(client=sdk)
        checkpoint["state"] = "started"
        main.SAVE(ATTEMPT / "checkpoint.json", checkpoint)
        try:
            response = client.generate(prompt)  # The only permitted real API call.
        except Exception as error:
            detail = describe(error)
            detail.update(response_headers=headers, http_dispatch_attempts=len(sends))
            main.SAVE(ATTEMPT / "error.json", detail)
            checkpoint.update(state="uncertain", diagnostic="controlled_retry/error.json")
            main.SAVE(ATTEMPT / "checkpoint.json", checkpoint)
            report = {"status": "failed_stopped", "error": detail, "usage": None,
                      "actual_cost_usd": None, "reserved_cost_usd": str(next_cost)}
            reserve += next_cost
        else:
            checkpoint.update(state="usage_unverified", response=response)
            main.SAVE(ATTEMPT / "checkpoint.json", checkpoint)
            if (response["model"] != config["model"] or response["parameters"] != {
                    "reasoning_effort": config["reasoning_effort"], "max_output_tokens": config["max_output_tokens"]}
                    or any(type(response[k]) is not int or response[k] < 0 for k in ("input_tokens", "output_tokens"))):
                raise RuntimeError("Response metadata requires manual reconciliation")
            cost = main.cost_tracker.calculate_cost(response["input_tokens"], response["output_tokens"], response.get("cached_input_tokens", 0))
            checkpoint["state"] = "completed"
            main.SAVE(ATTEMPT / "checkpoint.json", checkpoint)
            main.SAVE(path, {**request, "state": "completed", "response": response})
            main.SAVE(D / "costs" / path.name, {"task_id": task["task_id"], "method": "tavf", "sequence": 0,
                      "actual_usage_cost_usd": str(cost), "response_id": response["response_id"],
                      **{k: response[k] for k in ("input_tokens", "output_tokens", "cached_input_tokens")}})
            # Offline replay permits validation but can never send a refinement.
            class ReplayOnly:
                model, reasoning_effort, max_output_tokens = client.model, client.reasoning_effort, client.max_output_tokens
                calls = 0
                def generate(self, requested):
                    self.calls += 1
                    if self.calls != 1 or requested != prompt:
                        raise RuntimeError("Additional generation deferred by one-request authorization")
                    return response
            outcome = main.driver.run_tavf(task, client=ReplayOnly())
            main.SAVE(ATTEMPT / "validation_result.json", outcome)
            if outcome["status"] in {"completed", "unresolved"}:
                result_path = D / "results" / (main.driver._hash([task["task_id"], "tavf"]) + ".json")
                if result_path.exists():
                    raise RuntimeError("Refusing duplicate final output")
                main.SAVE(result_path, {"task": task, "method": "tavf", "result": outcome,
                          "final_evaluation": {"status": "not_verified", "message": "Not run by generation driver."}})
            report = {"status": "response_saved", "validation_status": outcome["status"],
                      "response_id": response["response_id"], "actual_cost_usd": str(cost),
                      "usage": {k: response[k] for k in ("input_tokens", "output_tokens", "cached_input_tokens")}}
            spent += cost
        finally:
            sdk.close()
        if any(hashlib.sha256((D / "results" / n).read_bytes()).hexdigest() != h for n, h in preserved.items()):
            raise RuntimeError("Original output integrity failure")
        if any(hashlib.sha256((D / "requests" / n).read_bytes()).hexdigest() != h for n, h in completed_requests.items()):
            raise RuntimeError("Original request integrity failure")
        report.update(http_dispatch_attempts=len(sends), original_43_outputs_unchanged=True,
                      total_recorded_usage_cost_usd=str(spent), reserved_unknown_cost_usd=str(reserve),
                      spent_plus_reserved_usd=str(spent + reserve), final_evaluation="not_run")
        main.SAVE(ATTEMPT / "report.json", report)
        for p in (D / "requests").glob("*.json"):
            main.REQUESTS[p.stem] = read(p)
        for p in (D / "results").glob("*.json"):
            main.RESULTS[p.stem] = read(p)
        main.STATUS = "controlled_retry_stopped"
        updated = main.refresh_summary()
        updated.update(reserved_unknown_cost_usd=str(reserve), spent_plus_reserved_usd=str(spent + reserve),
                       billing_total_verified=False, original_43_outputs_unchanged=True,
                       controlled_retry_report="controlled_retry/report.json", full_resume_authorized=False,
                       historical_uncertain_attempt="controlled_retry/prior_uncertain_request.json")
        main.SAVE(D / "run_summary.json", updated)
        print(json.dumps(report), flush=True)


if __name__ == "__main__":
    run()
