"""Launcher execution policy for durable provider rejections; no prompt changes."""
from copy import deepcopy
import json

import main_run as main


class ProviderRejected(BaseException):
    """Bypass framework error wrappers after an explicit rejection is saved."""


def is_invalid_prompt(error):
    body = getattr(error, "body", None)
    if isinstance(body, dict) and isinstance(body.get("error"), dict):
        body = body["error"]
    code = getattr(error, "code", None) or (body.get("code") if isinstance(body, dict) else None)
    return getattr(error, "status_code", None) == 400 and code == "invalid_prompt"


def save_rejection(directory, session, key, attempt_id, error, save):
    """Keep original journal plus explicit rejection, with a full cost reserve."""
    if not is_invalid_prompt(error):
        raise ValueError("Only explicit HTTP 400 invalid_prompt can continue")
    path = directory / "requests" / (key + ".json")
    request = json.loads(path.read_text(encoding="utf-8"))
    if request["state"] != "started" or request.get("attempt_id") != attempt_id:
        raise ValueError("Rejection does not match the in-flight journal")
    archive = session / "rejections" / attempt_id
    archive.mkdir(parents=True, exist_ok=False)
    (archive / "request.before.json").write_bytes(path.read_bytes())
    reserve = main.cost_tracker.calculate_cost(len(request["prompt"].encode("utf-8")) + 512,
                                               main.driver.MAX_OUTPUT_TOKENS)
    request.update(state="provider_rejected", outcome="provider_rejected", http_status=400,
                   provider_code="invalid_prompt", request_id=getattr(error, "request_id", None),
                   reserved_cost_usd=str(reserve), successful_output=False,
                   rejection_evidence=str((session / "errors" / (attempt_id + ".json")).relative_to(directory)))
    save(archive / "decision.json", request)
    save(path, request)
    return request


def run_scoped(tasks, directory, scope, client):
    """Reuse original prompting, journaling, guards and validators for one scope."""
    driver = main.driver
    with driver._lock(directory):
        records = {q.stem: json.loads(q.read_text(encoding="utf-8")) for q in directory.glob("requests/*.json")}
        if any(r["state"] not in {"completed", "provider_rejected"} for r in records.values()):
            raise ValueError("Unfinished request requires reconciliation")
        scope.rejected.update((r["task_id"], r["method"]) for r in records.values()
                              if r["state"] == "provider_rejected" and r["task_id"] in scope.tasks)
        manifest = driver._manifest(tasks, driver.MAX_OUTPUT_TOKENS)
        if manifest != json.loads((directory / "manifest.json").read_text(encoding="utf-8")):
            raise ValueError("Manifest changed")
        if any(getattr(client, k, None) != manifest[k] for k in ("model", "reasoning_effort", "max_output_tokens")):
            raise ValueError("Client settings differ")
        journal = driver._JournalClient(client, directory, manifest,
                                       {k: r for k, r in records.items() if r["state"] == "completed"})
        baseline = driver.TargetBaselineRunner(client=journal)
        saved = skipped = 0
        for task in tasks:
            if task["task_id"] not in scope.tasks:
                continue
            for method in ("baseline", "tavf"):
                identity = (task["task_id"], method)
                if identity in scope.saved or identity in scope.rejected:
                    skipped += 1
                    continue
                journal.task, journal.method, journal.sequence = task, method, 0
                try:
                    outcome = (baseline.run_task(deepcopy(task)) if method == "baseline"
                               else driver.run_tavf(deepcopy(task), client=journal))
                except ProviderRejected:
                    scope.rejected.add(identity)
                    continue
                except Exception:
                    if journal.halted:
                        return {"status": journal.halted, "saved": saved, "skipped": skipped}
                    raise
                if journal.halted:
                    return {"status": journal.halted, "saved": saved, "skipped": skipped}
                driver._save(directory / "results" / (driver._hash([task["task_id"], method]) + ".json"),
                             {"task": task, "method": method, "result": outcome,
                              "final_evaluation": {"status": "not_verified", "message": "Not run by generation driver."}})
                saved += 1
        return {"status": "completed", "saved": saved, "skipped": skipped,
                "scope": scope.task_type, "provider_rejected_method_tasks": len(scope.rejected)}
