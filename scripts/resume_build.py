"""Resume the authorized run with rejection audit, reserved liability and pacing."""

import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time

import main_run as main
DIRECTORY = main.DIRECTORY

REQUEST = "f25753351fb53800d74b5d2930e47fb6cb5e023127caead2d5813931e186866e"
TASK_ID = "US500-g11-nsf-L0047"
RATE_FIELDS = ("retry-after", "x-request-id", "x-ratelimit-limit-requests", "x-ratelimit-limit-tokens",
               "x-ratelimit-remaining-requests", "x-ratelimit-remaining-tokens",
               "x-ratelimit-reset-requests", "x-ratelimit-reset-tokens",
               "x-ratelimit-limit-project-tokens", "x-ratelimit-remaining-project-tokens",
               "x-ratelimit-reset-project-tokens")


def reconcile():
    decision_path = DIRECTORY / "reconciliation.json"
    if decision_path.exists():
        decision = json.loads(decision_path.read_text(encoding="utf-8"))
        if decision["request"] != REQUEST or decision["decision"] != "rejected_rate_limit_no_saved_response":
            raise ValueError("Unexpected reconciliation decision")
        return decision
    error = json.loads((DIRECTORY / "api_error.json").read_text(encoding="utf-8"))
    request_path = DIRECTORY / "requests" / (REQUEST + ".json")
    request = json.loads(request_path.read_text(encoding="utf-8"))
    pending = [p for p in (DIRECTORY / "requests").glob("*.json")
               if json.loads(p.read_text(encoding="utf-8")).get("state") != "completed"]
    results = list((DIRECTORY / "results").glob("*.json"))
    if (error != {"error_type": "RateLimitError", "http_status": 429, "provider_code": "rate_limit_exceeded"}
            or pending != [request_path] or len(results) != 13
            or request.get("task_id") != TASK_ID or request.get("method") != "tavf"
            or request.get("state") != "uncertain" or request.get("response") is not None):
        raise ValueError("Cannot safely reconcile the uncertain request")
    if abs((DIRECTORY / "api_error.json").stat().st_mtime - request_path.stat().st_mtime) > 10:
        raise ValueError("Failure diagnostics cannot be temporally attributed")
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in results}
    reserve = main.cost_tracker.calculate_cost(len(request["prompt"].encode("utf-8")) + 512,
                                               main.driver.MAX_OUTPUT_TOKENS)
    decision = {"request": REQUEST, "task_id": TASK_ID, "method": "tavf",
                "decision": "rejected_rate_limit_no_saved_response", "assumed_success": False,
                "evidence": error, "attribution": "Only uncertain request; same-time recorded HTTP 429 rejection.",
                "billing_status": "unverified; full conservative request reservation retained",
                "reserved_cost_usd": str(reserve), "preserved_result_sha256": hashes,
                "original_journal_sha256": hashlib.sha256(request_path.read_bytes()).hexdigest()}
    archive = DIRECTORY / "reconciled_requests" / request_path.name
    archive.parent.mkdir(exist_ok=True)
    if archive.exists():
        raise ValueError("Existing archive requires manual inspection")
    # Preserve the exact rejected journal, outside the driver's active request
    # index. It is never marked completed or given fabricated token usage.
    request_path.rename(archive)
    main.SAVE(decision_path, decision)
    return decision


def seconds(value):
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        matches = re.findall(r"([0-9.]+)(ms|s|m|h)", value or "")
        if not matches:
            raise ValueError("Unrecognized rate reset duration")
        return sum(float(number) * {"ms": .001, "s": 1, "m": 60, "h": 3600}[unit] for number, unit in matches)


class PacedClient:
    def __init__(self):
        from dotenv import load_dotenv
        import httpx2
        from openai import OpenAI
        load_dotenv(main.ROOT / ".env")
        self.headers, self.received_at, self.last_start = {}, 0.0, 0.0
        self.last_status, self.next_allowed = None, 0.0
        transport = httpx2.Client(event_hooks={"response": [self.observe]})
        self.client = main.LLMClient(client=OpenAI(max_retries=0, timeout=120, http_client=transport))
        for key in ("model", "reasoning_effort", "max_output_tokens"):
            setattr(self, key, getattr(self.client, key))

    def observe(self, response):
        self.headers = {key: response.headers[key] for key in RATE_FIELDS if key in response.headers}
        self.received_at = time.monotonic()
        self.last_status = response.status_code
        record = {"http_status": response.status_code, "headers": self.headers,
                  "received_unix": time.time()}
        main.SAVE(DIRECTORY / "latest_rate_headers.json", record)
        with (DIRECTORY / "rate_headers.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        if "retry-after" in self.headers:
            self.next_allowed = max(self.next_allowed, self.received_at + seconds(self.headers["retry-after"]))

    def generate(self, prompt):
        reservation = len(prompt.encode("utf-8")) + 512 + self.max_output_tokens
        ready = max(self.next_allowed, self.last_start + 1.0)
        if self.last_status is not None:
            # Do not guess account limits from the tier name. Use actual model
            # and project response headers; absent limits stop further calls.
            if not all(key in self.headers for key in ("x-ratelimit-limit-requests", "x-ratelimit-limit-tokens")):
                raise RuntimeError("Rate-limit headers missing; refusing unpaced continuation")
            rpm = float(self.headers["x-ratelimit-limit-requests"])
            tpm = float(self.headers["x-ratelimit-limit-tokens"])
            if "x-ratelimit-limit-project-tokens" in self.headers:
                tpm = min(tpm, float(self.headers["x-ratelimit-limit-project-tokens"]))
            if rpm <= 0 or tpm < reservation:
                raise RuntimeError("Current rate limits cannot accommodate unchanged request settings")
            ready = max(ready, self.last_start + max(60 / rpm, 60 * reservation / tpm) * 1.1)
            for remaining, reset, needed in (
                ("x-ratelimit-remaining-requests", "x-ratelimit-reset-requests", 1),
                ("x-ratelimit-remaining-tokens", "x-ratelimit-reset-tokens", reservation),
                ("x-ratelimit-remaining-project-tokens", "x-ratelimit-reset-project-tokens", reservation),
            ):
                if remaining in self.headers and float(self.headers[remaining]) < needed:
                    if reset not in self.headers:
                        raise RuntimeError("Rate reset header missing; refusing early dispatch")
                    ready = max(ready, self.received_at + seconds(self.headers[reset]) + 1)
        if ready - time.monotonic() > 3600:
            raise RuntimeError("Required delay exceeds pacing window; defer the run")
        while time.monotonic() < ready:
            time.sleep(min(30, ready - time.monotonic()))
        self.last_start = time.monotonic()
        try:
            return self.client.generate(prompt)
        except Exception as error:
            from connection_diagnostics import describe
            diagnostic = describe(error)
            diagnostic["headers"] = self.headers
            code = getattr(error, "code", None)
            if isinstance(code, str) and len(code) < 100:
                diagnostic["provider_code"] = code
            main.SAVE(DIRECTORY / "api_error.json", diagnostic)
            raise


def main_resume():
    decision = reconcile()
    from decimal import Decimal
    reserve = Decimal(decision["reserved_cost_usd"])
    old_spent = main.cost_tracker.calculate_spent
    # Retain unknown billing conservatively, in BOTH existing budget checks.
    main.cost_tracker.calculate_spent = lambda: old_spent() + reserve
    main.driver.calculate_spent = main.cost_tracker.calculate_spent
    original_summary = main.refresh_summary

    def summary_with_reconciliation():
        summary = original_summary()
        summary.update(reconciled_rejections=1, reserved_unknown_cost_usd=str(reserve),
                       spent_plus_reserved_usd=str(Decimal(summary["actual_usage_cost_usd"]) + reserve),
                       billing_total_verified=False,
                       pacing="Single in-flight request; actual response limits, reset headers and Retry-After.")
        summary["original_13_outputs_unchanged"] = all(
            hashlib.sha256((DIRECTORY / "results" / name).read_bytes()).hexdigest() == digest
            for name, digest in decision["preserved_result_sha256"].items())
        if not summary["original_13_outputs_unchanged"]:
            raise RuntimeError("Original completed output changed")
        main.SAVE(DIRECTORY / "run_summary.json", summary)
        return summary

    main.refresh_summary = summary_with_reconciliation
    main.ObservedClient = PacedClient
    main.main()


if __name__ == "__main__":
    main_resume()
