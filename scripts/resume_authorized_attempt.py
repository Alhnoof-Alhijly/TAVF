"""Resume with explicit attempt identities and retained unknown liabilities."""
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from uuid import uuid4
import argparse
from contextlib import contextmanager
import os

import resume_build as paced
from connection_diagnostics import describe, redact

main = paced.main
D = main.DIRECTORY
KEY = "3a1206f299e5c679fb3dbd8b290625ade0831744b99fdddcee849e4d7630c157"
SESSION = D / "authorized_resume"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_preserved(plan):
    for folder, field in (("results", "preserved_result_sha256"), ("requests", "preserved_request_sha256")):
        if any(sha(D / folder / name) != digest for name, digest in plan[field].items()):
            raise RuntimeError("Original completed artifact integrity failure")


def prepare(*, user_stories_only=False, bug_reports_only=False, test_cases_only=False, supersede_prepared=False):
    """Offline only: preserve history and prepare a single-use session."""
    if sum((user_stories_only, bug_reports_only, test_cases_only)) > 1:
        raise ValueError("Select exactly one task scope")
    task_type = ("test_case_generation" if test_cases_only else
                 "bug_report_refinement" if bug_reports_only else
                 "user_story_refinement" if user_stories_only else None)
    with main.driver._lock(D):
        main.driver.run_experiment(main.driver.load_tasks(), D)  # Read-only manifest check.
        summary = read(D / "run_summary.json")
        source_session = (D / summary["authorized_resume_plan"]).parent
        original = read(source_session / "plan.json")
        verify_preserved(original)
        if read(source_session / "status.json")["status"] != "stopped":
            raise RuntimeError("Source session is not stopped")
        results = list((D / "results").glob("*.json"))
        if len(results) != summary["final_outputs_saved"]:
            raise RuntimeError("Unexpected completed output count")
        records = {q.stem: read(q) for q in (D / "requests").glob("*.json")}
        pending = [key for key, r in records.items() if r["state"] != "completed"]
        if len(pending) > 1:
            raise RuntimeError("Multiple unfinished requests require reconciliation")
        path, unknown = None, None
        if pending:
            key = pending[0]
            path = D / "requests" / (key + ".json")
            unknown = read(path)
            if (unknown["state"] != "uncertain" or "response" in unknown
                    or unknown != read(source_session / "attempts" / (unknown["attempt_id"] + ".json"))):
                raise RuntimeError("Unknown attempt differs from audited checkpoint")
        else:
            saved = {(read(q)["task"]["task_id"], read(q)["method"]) for q in results}
            remaining = [(task, method) for task in main.driver.load_tasks()
                         if task_type is None or task["task_type"] == task_type
                         for method in ("baseline", "tavf") if (task["task_id"], method) not in saved]
            if not remaining:
                raise RuntimeError("Requested scope is already complete")
            next_task, next_method = remaining[0]
            key = main.driver._hash([next_task["task_id"], next_method, 0])
        reserve = Decimal(summary["reserved_unknown_cost_usd"])
        expected = Decimal(original["historical_reserve_usd"])
        if unknown is not None:
            expected += main.cost_tracker.calculate_cost(len(unknown["prompt"].encode("utf-8")) + 512,
                                                         main.driver.MAX_OUTPUT_TOKENS)
        if reserve != expected or Decimal(summary["actual_usage_cost_usd"]) + reserve >= Decimal("5.00"):
            raise RuntimeError("Reserve reconciliation or budget check failed")
        sessions = D / "resume_sessions"
        prepared = []
        for q in sessions.glob("*/status.json"):
            state = read(q)["status"]
            if state == "running" or (state == "prepared" and not supersede_prepared):
                raise RuntimeError("Another prepared/running resume session requires inspection")
            if state == "prepared":
                validate_session(q.parent)
                prepared.append(q.parent)
        if task_type is not None:
            story_ids = {t["task_id"] for t in main.driver.load_tasks() if t["task_type"] == task_type}
            if len(story_ids) != 500 or (unknown is not None and unknown["task_id"] not in story_ids):
                raise RuntimeError("Selected scope does not match the uncertain task")
        old_hashes = {q.relative_to(source_session).as_posix(): sha(q)
                      for q in source_session.rglob("*") if q.is_file()}
        # Check unique logical outputs and response identities before preparing.
        identities = [(read(q)["task"]["task_id"], read(q)["method"]) for q in results]
        completed = {key: r for key, r in records.items() if r["state"] == "completed"}
        response_ids = [r["response"]["response_id"] for r in completed.values()]
        if len(set(identities)) != len(identities) or len(set(response_ids)) != len(response_ids):
            raise RuntimeError("Duplicate output or response identity")
        spent = sum((main.cost_tracker.calculate_cost(r["response"]["input_tokens"], r["response"]["output_tokens"],
                     r["response"].get("cached_input_tokens", 0)) for r in completed.values()), Decimal(0))
        if spent != Decimal(summary["actual_usage_cost_usd"]) or spent + reserve + main.cost_tracker.calculate_spent() >= Decimal("5"):
            raise RuntimeError("Recorded spending or aggregate budget differs")
        new_session = sessions / uuid4().hex
        new_session.mkdir(parents=True)
        prior_id, next_id = unknown["attempt_id"] if unknown is not None else None, uuid4().hex
        if path is not None:
            (new_session / "original_uncertain_request.json").write_bytes(path.read_bytes())
        plan = {"authorized_utc": datetime.now(timezone.utc).isoformat(),
                "authorization": "User explicitly permits a new attempt while retaining original unknown outcome and cost reserve",
                "prior_attempt_id": prior_id, "new_attempt_id": next_id, "logical_request": key,
                "historical_reserve_usd": str(reserve), "historical_connection_failures": summary["connection_failure_count"],
                "source_session": str(source_session.relative_to(D)), "source_session_file_sha256": old_hashes,
                "preserved_output_count": len(results),
                "session_id": new_session.name, "source_checkpoint_sha256": sha(path) if path is not None else None,
                "manifest_sha256": sha(D / "manifest.json"), "run_config_sha256": sha(D / "run_config.json"),
                "preserved_result_sha256": {q.name: sha(q) for q in results},
                "preserved_request_sha256": {key + ".json": sha(D / "requests" / (key + ".json")) for key in completed},
                "output_identity": "Existing task_id/method result slot; attempt IDs never add output slots",
                "final_evaluation": "not_run", "docker_execution": False}
        if task_type is not None:
            plan.update(task_types=[task_type], target_outputs_per_method=500,
                        scope_expected_outputs=1000, supersedes_prepared_sessions=[q.name for q in prepared])
        main.SAVE(new_session / "plan.json", plan)
        main.SAVE(new_session / "status.json", {"status": "prepared", "api_requests": 0})
        if any(sha(source_session / name) != digest for name, digest in old_hashes.items()):
            raise RuntimeError("Old session changed during finalization")
        for previous in prepared:
            snapshot = previous / "superseded_prepared_status.json"
            if snapshot.exists():
                raise RuntimeError("Prepared status archive already exists")
            snapshot.write_bytes((previous / "status.json").read_bytes())
            main.SAVE(previous / "status.json", {"status": "stopped", "reason": "superseded_before_execution",
                      "superseded_by": new_session.name, "api_requests": 0})
        return new_session


class ScopeComplete(Exception):
    pass


class UserStoryBoundary:
    """Launcher-only boundary; full manifest and framework stay unchanged."""
    def __init__(self, tasks, results, task_type="user_story_refinement"):
        if task_type not in {"user_story_refinement", "bug_report_refinement", "test_case_generation"}:
            raise ValueError("Unsupported execution scope")
        self.task_type = task_type
        self.tasks = {t["task_id"]: t for t in tasks if t["task_type"] == task_type}
        if len(self.tasks) != 500:
            raise RuntimeError("Expected exactly 500 manifest inputs for selected scope")
        self.saved = set()
        for record in results:
            if record["task"]["task_type"] == task_type:
                self.check_identity(record["task"]["task_id"], record["method"])
                if record["task"] != self.tasks[record["task"]["task_id"]]:
                    raise RuntimeError("Saved scoped input differs from manifest")
                key = (record["task"]["task_id"], record["method"])
                if key in self.saved:
                    raise RuntimeError("Duplicate scoped output")
                self.saved.add(key)

    def check_identity(self, task_id, method):
        if task_id not in self.tasks or method not in {"baseline", "tavf"}:
            raise RuntimeError("Session refuses out-of-scope generation or output")

    def before_save(self, path, value):
        if path.parent == D / "requests":
            task_id, method = value["task_id"], value["method"]
        elif path.parent == D / "results":
            task_id, method = value["task"]["task_id"], value["method"]
            if value["task"] != self.tasks.get(task_id):
                raise RuntimeError("Output input differs from manifest")
        else:
            return
        self.check_identity(task_id, method)
        if (task_id, method) in self.saved:
            raise RuntimeError("Completed scoped output must not be repeated")

    def after_save(self, path, value):
        if path.parent == D / "results":
            self.saved.add((value["task"]["task_id"], value["method"]))
            if self.complete:
                raise ScopeComplete()

    @property
    def complete(self):
        return all(sum(method == m for _, method in self.saved) == 500 for m in ("baseline", "tavf"))


def validate_session(session):
    plan = read(session / "plan.json")
    if read(session / "status.json")["status"] != "prepared":
        raise RuntimeError("Session is single-use and is no longer prepared; inspect its final status")
    verify_preserved(plan)
    if (sha(D / "manifest.json") != plan["manifest_sha256"]
            or sha(D / "run_config.json") != plan["run_config_sha256"]
            or (plan["source_checkpoint_sha256"] is not None
                and sha(D / "requests" / (plan["logical_request"] + ".json")) != plan["source_checkpoint_sha256"])
            or read(D / "run_summary.json")["reserved_unknown_cost_usd"] != plan["historical_reserve_usd"]):
        raise RuntimeError("Prepared checkpoint, settings or reserves changed")
    if plan["source_checkpoint_sha256"] is None and any(
            read(q)["state"] != "completed" for q in (D / "requests").glob("*.json")):
        raise RuntimeError("New unfinished request appeared after preparation")
    main.driver.run_experiment(main.driver.load_tasks(), D)
    return plan


def run(session_id):
    global SESSION, KEY
    # Fail before any checkpoint change if accidentally launched inside Codex.
    if os.environ.get("CODEX_SANDBOX_NETWORK_DISABLED") == "1":
        raise RuntimeError("Run from the local VS Code PowerShell terminal outside the Codex sandbox")
    if len(session_id) != 32 or any(c not in "0123456789abcdef" for c in session_id):
        raise ValueError("Invalid session ID")
    SESSION = D / "resume_sessions" / session_id
    plan = validate_session(SESSION)
    KEY = plan["logical_request"]
    next_id, prior_id = plan["new_attempt_id"], plan["prior_attempt_id"]
    reserve = Decimal(plan["historical_reserve_usd"])
    historical_unknowns = list(read(D / "run_summary.json").get("historical_unknown_attempts", []))
    if prior_id is not None and not any(r["attempt_id"] == prior_id for r in historical_unknowns):
        historical_unknowns.append({"attempt_id": prior_id, "outcome": "unknown",
                                   "audit": str(SESSION.relative_to(D) / "original_uncertain_request.json")})
    scope = None
    if plan.get("task_types") in (["user_story_refinement"], ["bug_report_refinement"], ["test_case_generation"]):
        scope = UserStoryBoundary(main.driver.load_tasks(), [read(q) for q in (D / "results").glob("*.json")],
                                  task_type=plan["task_types"][0])
        original_run = main.driver.run_experiment

        def scoped_run(tasks, directory, **kwargs):
            if not kwargs.get("execute"):
                return original_run(tasks, directory, **kwargs)
            before = len(scope.saved)
            if scope.complete:
                return {"status": "completed", "scope": scope.task_type, "saved": 0, "skipped": 1000}
            try:
                return original_run(tasks, directory, **kwargs)
            except ScopeComplete:
                return {"status": "completed", "scope": scope.task_type, "saved": len(scope.saved) - before, "skipped": before}

        main.driver.run_experiment = scoped_run

    # Retirement occurs inside the generation driver's existing OS lock.
    # Concurrent launchers cannot retire/checkpoint or dispatch twice.
    original_lock = main.driver._lock

    @contextmanager
    def start_session(directory):
        with original_lock(directory):
            validate_session(SESSION)
            main.SAVE(SESSION / "status.json", {"status": "running", "started_utc": datetime.now(timezone.utc).isoformat()})
            if plan["source_checkpoint_sha256"] is not None:
                path = D / "requests" / (KEY + ".json")
                path.rename(SESSION / "retired_active_checkpoint.json")
                main.REQUESTS.pop(KEY, None)
            yield

    main.driver._lock = start_session

    ids = {KEY: next_id}
    current = {"key": None, "id": None}
    original_summary = main.refresh_summary
    old_spent = main.cost_tracker.calculate_spent
    # Both existing budget guards retain every historical reservation.
    main.cost_tracker.calculate_spent = lambda: old_spent() + reserve
    main.driver.calculate_spent = main.cost_tracker.calculate_spent

    def refresh():
        if any(sha(D / "results" / name) != digest for name, digest in plan["preserved_result_sha256"].items()):
            raise RuntimeError("Original output changed")
        if any(sha(D / "requests" / name) != digest for name, digest in plan["preserved_request_sha256"].items()):
            raise RuntimeError("Original completed request changed")
        summary = original_summary()
        pending = sum((main.cost_tracker.calculate_cost(len(r["prompt"].encode("utf-8")) + 512,
                        main.driver.MAX_OUTPUT_TOKENS) for r in main.REQUESTS.values()
                       if r["state"] != "completed" and r.get("attempt_id") != prior_id), Decimal(0))
        total_reserve = reserve + pending
        summary.update(original_43_outputs_unchanged=True,
                       preserved_outputs_unchanged=True, preserved_output_count=plan.get("preserved_output_count", 43),
                       historical_unknown_attempts=historical_unknowns,
                       reserved_unknown_cost_usd=str(total_reserve), historical_reserved_cost_usd=str(reserve),
                       spent_plus_reserved_usd=str(Decimal(summary["actual_usage_cost_usd"]) + total_reserve),
                       billing_total_verified=False, cost_verified=False,
                       authorized_resume_plan=str(SESSION.relative_to(D) / "plan.json"),
                       connection_failure_count=plan["historical_connection_failures"] + len(list((SESSION / "errors").glob("*.json"))),
                       pacing="Single in-flight request; response rate limits, reset headers and Retry-After")
        if scope is not None:
            summary.update(active_task_types=[scope.task_type], scope_expected_outputs=1000,
                           target_outputs_per_method=500)
        if Decimal(summary["spent_plus_reserved_usd"]) + old_spent() > Decimal("5.00"):
            raise RuntimeError("Aggregate cost plus reserves exceeds $5")
        main.SAVE(D / "run_summary.json", summary)
        return summary

    main.refresh_summary = refresh
    observed = main.observed_save

    def save_attempt(path, value):
        if scope is not None:
            scope.before_save(path, value)
        if path.parent == D / "requests":
            ident = ids.setdefault(path.stem, uuid4().hex)
            value = {**value, "attempt_id": ident}
            current.update(key=path.stem, id=ident)
            main.SAVE(SESSION / "attempts" / (ident + ".json"), value)
        observed(path, value)
        if scope is not None:
            scope.after_save(path, value)

    main.observed_save = save_attempt

    class Client(paced.PacedClient):
        def observe(self, response):
            super().observe(response)
            safe_headers = {k: redact(v) for k, v in response.headers.items()
                            if k.lower() not in {"set-cookie", "authorization", "proxy-authorization"}}
            main.SAVE(SESSION / "headers" / (current["id"] + ".json"), {
                      "attempt_id": current["id"], "http_status": response.status_code,
                      "request_id": response.headers.get("x-request-id"), "headers": safe_headers})

        def generate(self, prompt):
            main.SAVE(SESSION / "dispatch" / (current["id"] + ".json"), {
                      "attempt_id": current["id"], "logical_request": current["key"],
                      "entered_provider_utc": datetime.now(timezone.utc).isoformat()})
            try:
                return super().generate(prompt)
            except Exception as error:
                diagnostic = describe(error)
                diagnostic.update(attempt_id=current["id"], logical_request=current["key"], headers=self.headers)
                main.SAVE(SESSION / "errors" / (current["id"] + ".json"), diagnostic)
                raise

    main.ObservedClient = Client
    try:
        main.main()
    finally:
        summary = read(D / "run_summary.json")
        main.SAVE(SESSION / "status.json", {"status": "stopped", "driver_status": main.STATUS,
                  "stopped_utc": datetime.now(timezone.utc).isoformat(),
                  "reserved_unknown_cost_usd": summary["reserved_unknown_cost_usd"],
                  "actual_usage_cost_usd": summary["actual_usage_cost_usd"]})
    if main.STATUS != "completed":
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare-only", action="store_true", help="Finalize and prepare offline; never send requests")
    mode.add_argument("--session", help="Execute exactly one previously prepared session")
    scope_args = parser.add_mutually_exclusive_group()
    scope_args.add_argument("--user-stories-only", action="store_true", help="Prepare a User Story-only session, 500 outputs per method")
    scope_args.add_argument("--bug-reports-only", action="store_true", help="Prepare a Bug Report-only session, 500 outputs per method")
    scope_args.add_argument("--test-cases-only", action="store_true", help="Prepare a Test Case-only session, 500 outputs per method; no Docker or Final Evaluation")
    parser.add_argument("--supersede-prepared", action="store_true", help="Preserve and stop older unused prepared sessions")
    args = parser.parse_args()
    if args.prepare_only:
        print(json.dumps({"prepared_session": prepare(user_stories_only=args.user_stories_only,
                                                    bug_reports_only=args.bug_reports_only,
                                                    test_cases_only=args.test_cases_only,
                                                    supersede_prepared=args.supersede_prepared).name, "api_requests": 0}))
    else:
        run(args.session)
