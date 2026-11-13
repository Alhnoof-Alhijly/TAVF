"""Reconcile the pre-dispatch deferral and resume unchanged generation."""
import hashlib
import json
from pathlib import Path
import time

import resume_build as previous

main = previous.main
DIRECTORY = main.DIRECTORY
KEY = "3a1206f299e5c679fb3dbd8b290625ade0831744b99fdddcee849e4d7630c157"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconcile_deferred():
    audit_path = DIRECTORY / "deferred_reconciliation.json"
    if audit_path.exists():
        audit = json.loads(audit_path.read_text())
        if audit["decision"] != "confirmed_not_dispatched_safe_to_retry":
            raise ValueError("Unexpected deferred reconciliation")
        return audit
    with main.driver._lock(DIRECTORY):
        # Check the unchanged input, prompt, validator and model manifest first.
        main.driver.run_experiment(main.driver.load_tasks(), DIRECTORY)
        path = DIRECTORY / "requests" / (KEY + ".json")
        request = json.loads(path.read_text())
        records = [json.loads(p.read_text()) for p in (DIRECTORY / "requests").glob("*.json")]
        results = list((DIRECTORY / "results").glob("*.json"))
        headers = [json.loads(line) for line in (DIRECTORY / "rate_headers.jsonl").read_text().splitlines()]
        last = headers[-1]
        completed = [r for r in records if r["state"] == "completed"]
        latest = max(completed, key=lambda r: r["response"]["timestamp"])
        from datetime import datetime
        response_time = datetime.fromisoformat(latest["response"]["timestamp"]).timestamp()
        reset = previous.seconds(last["headers"]["x-ratelimit-reset-requests"])
        if (len(results) != 43 or len(completed) != 43 or len(records) != 44
                or request["state"] != "uncertain" or "response" in request
                or request["task_id"] != "US500-g21-badcamp-L0035" or request["method"] != "tavf"
                or last["http_status"] != 200 or last["headers"]["x-ratelimit-remaining-requests"] != "0"
                or reset <= 3600 or abs(path.stat().st_mtime - last["received_unix"]) > 2
                or abs(response_time - last["received_unix"]) > 1
                or latest["task_id"] != request["task_id"] or latest["method"] != "baseline"):
            raise ValueError("Deferred request evidence does not prove pre-dispatch stop")
        # These are the two relevant branches in the exact prior launcher.
        source = Path(previous.__file__).read_text()
        guard = source.index('raise RuntimeError("Required delay exceeds pacing window; defer the run")')
        dispatch = source.index('return self.client.generate(prompt)')
        if guard >= dispatch or len({r["response"]["response_id"] for r in completed}) != 43:
            raise ValueError("Dispatch ordering or unique response audit failed")
        audit = {"request": KEY, "decision": "confirmed_not_dispatched_safe_to_retry",
                 "evidence": {"last_http_response": last, "last_completed_task": latest["task_id"],
                              "last_completed_method": latest["method"], "required_reset_seconds": reset,
                              "journal_mtime_unix": path.stat().st_mtime,
                              "explanation": "Pacing raises above one hour before invoking LLMClient.generate; final HTTP response belongs to preceding baseline. No dispatch of deferred TAVF occurred.",
                              "prior_launcher_sha256": digest(Path(previous.__file__))},
                 "original_journal_sha256": digest(path),
                 "preserved_result_sha256": {p.name: digest(p) for p in results},
                 "preserved_request_sha256": {p.name: digest(p) for p in (DIRECTORY / "requests").glob("*.json") if p != path},
                 "additional_reserved_cost_usd": "0", "reconciled_unix": time.time()}
        archive = DIRECTORY / "reconciled_requests" / path.name
        if archive.exists():
            raise ValueError("Deferred archive already exists")
        main.SAVE(audit_path, audit)
        path.rename(archive)
        return audit


def run():
    if (DIRECTORY / "connection_failure_liability.json").exists():
        raise RuntimeError("Critical connection failure requires outcome and billing reconciliation before resume")
    audit = reconcile_deferred()
    original_refresh = main.refresh_summary

    def refresh():
        for folder, field in (("results", "preserved_result_sha256"), ("requests", "preserved_request_sha256")):
            if any(digest(DIRECTORY / folder / name) != value for name, value in audit[field].items()):
                raise RuntimeError("An original completed artifact changed")
        summary = original_refresh()
        summary.update(original_43_outputs_unchanged=True, deferred_request_confirmed_not_sent=True,
                       deferred_reconciliation="deferred_reconciliation.json")
        main.SAVE(DIRECTORY / "run_summary.json", summary)
        return summary

    main.refresh_summary = refresh
    # Keep the existing conservative reserve, both budget checks and pacing.
    previous.main_resume()


if __name__ == "__main__":
    run()
