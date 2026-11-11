"""Opt-in target coverage evaluation, separate from TAVF internal validation.

Source is executed only inside Docker, using the existing unittest harness.
Tracing observes Python line events, not assertion correctness. As with other
in-process Python instrumentation, reports are not tamper-proof against code
deliberately modifying the tracer or harness.
"""

from collections.abc import Mapping
import hashlib
import json
import subprocess
import threading
import uuid

from tavf.validators.execution import _HARNESS


MAX_OUTPUT_BYTES = 65536
TIMEOUT_SECONDS = 10

# The existing harness compiles the unchanged program as <reference>. Running
# it in a separate namespace keeps normal test bindings away from the collector.
_COVERAGE_HARNESS = """
import contextlib, json, os, sys
observed = set()
def trace(frame, event, arg):
    if event == 'line' and frame.f_code.co_filename == '<reference>':
        observed.add(frame.f_lineno)
    return trace
report_stream = sys.stdout
test_exit_code = 0
completed = False
with open(os.devnull, 'w') as sink:
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        sys.settrace(trace)
        try:
            exec(HARNESS, {})
            completed = True
        except SystemExit as error:
            test_exit_code = error.code if type(error.code) is int else (0 if error.code is None else 1)
            completed = test_exit_code == 0
        except BaseException:
            test_exit_code = 1
        finally:
            tracer_intact = sys.gettrace() is trace
            sys.settrace(None)
report = {'version': 1, 'completed': completed, 'tracer_intact': tracer_intact,
          'test_exit_code': test_exit_code, 'executed_lines': sorted(observed)}
report_stream.write(json.dumps(report))
report_stream.flush()
""".replace("exec(HARNESS, {})", "exec(" + repr(_HARNESS) + ", {})")


def _run_container(command, payload):
    """Drain stdout with a hard capture cap; kill the CLI on overflow/timeout.

    The caller always force-removes the container, including after CLI failure.
    Stdin writing is also asynchronous so a stalled Docker client cannot block
    the wall-clock timeout. No host environment is sent as container input.
    """
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, shell=False)
    captured = bytearray()
    overflow = threading.Event()
    io_error = threading.Event()

    def read_output():
        try:
            while True:
                chunk = process.stdout.read(4096)
                if not chunk:
                    break
                remaining = MAX_OUTPUT_BYTES - len(captured)
                captured.extend(chunk[:remaining])
                if len(chunk) > remaining:
                    overflow.set()
                    process.kill()
                    break
        except (OSError, ValueError):
            io_error.set()

    def write_input():
        try:
            process.stdin.write(payload)
            process.stdin.close()
        except (OSError, ValueError):
            io_error.set()

    reader = threading.Thread(target=read_output, daemon=True)
    writer = threading.Thread(target=write_input, daemon=True)
    reader.start()
    writer.start()
    timed_out = False
    try:
        process.wait(timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        process.wait(timeout=5)
    finally:
        reader.join(timeout=1)
        writer.join(timeout=1)
        if not reader.is_alive():
            process.stdout.close()
    return {"exit_code": process.returncode, "output": bytes(captured),
            "timed_out": timed_out, "output_overflow": overflow.is_set(),
            "transport_incomplete": io_error.is_set() or reader.is_alive() or writer.is_alive()}


def _execute_trace(source, artifact, harness):
    """Shared isolated transport for final line, branch and path evaluation."""
    evidence = {"image": "python:3.12-slim", "network": "none", "mounts": [],
                "read_only": True, "cpu_limit": 0.5, "memory_bytes": 134217728,
                "process_limit": 16, "timeout_seconds": TIMEOUT_SECONDS,
                "max_output_bytes": MAX_OUTPUT_BYTES}
    name = "tavf-line-coverage-" + uuid.uuid4().hex
    # Same isolation contract as validate_execution; no mounts, pulls or secrets.
    command = ["docker", "run", "--rm", "--pull=never", "--name", name, "-i",
               "--network", "none", "--read-only", "--cap-drop", "ALL",
               "--security-opt", "no-new-privileges", "--cpus", "0.5",
               "--memory", "128m", "--memory-swap", "128m", "--pids-limit", "16",
               "--user", "65534:65534", "--log-driver", "none"]
    for proxy in ("HTTP_PROXY", "HTTPS_PROXY", "FTP_PROXY", "NO_PROXY", "ALL_PROXY"):
        for key in (proxy, proxy.lower()):
            command.extend(["--env", key + "="])
    command.extend(["python:3.12-slim", "python", "-I", "-B", "-c", harness])
    transport = None
    try:
        transport = _run_container(command, json.dumps([source, artifact]).encode("utf-8"))
        evidence.update({key: value for key, value in transport.items() if key != "output"})
    except (OSError, subprocess.TimeoutExpired) as error:
        evidence["error_type"] = type(error).__name__
    finally:
        try:
            cleanup = subprocess.run(["docker", "rm", "--force", name],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                     timeout=5, shell=False)
            evidence["cleanup_exit_code"] = cleanup.returncode
        except (OSError, subprocess.TimeoutExpired) as error:
            evidence["cleanup_error"] = type(error).__name__
    return transport, evidence


def evaluate_line_target(artifact: str, task: Mapping) -> dict:
    """Evaluate one schema-style TestEval task; never invoke an LLM or validator.

    Returns covered/not_covered only for a completed successful trace. Docker
    errors, timeouts, malformed reports and unsupported targets are unverified.
    """
    evidence = {"image": "python:3.12-slim", "network": "none", "mounts": [],
                "read_only": True, "cpu_limit": 0.5, "memory_bytes": 134217728,
                "process_limit": 16, "timeout_seconds": TIMEOUT_SECONDS,
                "max_output_bytes": MAX_OUTPUT_BYTES, "executed_lines": [],
                "collection": "python_line_events_for_<reference>",
                "assertion_correctness": "not_verified"}

    def result(status, message):
        return {"status": status, "message": message, "evidence": evidence}

    if not isinstance(task, Mapping) or not isinstance(artifact, str) or not artifact.strip():
        return result("not_verified", "A task and nonempty test source are required.")
    context, reference = task.get("input"), task.get("reference")
    if not isinstance(context, Mapping) or not isinstance(reference, Mapping):
        return result("not_verified", "Program source and selected line target are unavailable.")
    source, target = context.get("python_solution"), reference.get("target")
    if (task.get("task_type") != "test_case_generation" or reference.get("target_type") != "line"
            or not isinstance(source, str) or not source.strip() or not isinstance(target, Mapping)
            or set(target) != {"line"} or type(target["line"]) is not int
            or not 1 <= target["line"] <= len(source.splitlines())):
        return result("not_verified", "A valid selected line target and program source are required.")
    evidence.update(task_id=task.get("task_id"), target_line=target["line"],
                    program_sha256=hashlib.sha256(source.encode("utf-8")).hexdigest(),
                    tests_sha256=hashlib.sha256(artifact.encode("utf-8")).hexdigest())
    transport, execution_evidence = _execute_trace(source, artifact, _COVERAGE_HARNESS)
    evidence.update(execution_evidence)
    if (transport is None or transport["exit_code"] != 0 or transport["timed_out"]
            or transport["output_overflow"] or transport["transport_incomplete"]
            or "cleanup_error" in evidence):
        return result("not_verified", "Docker execution or coverage collection did not complete reliably.")
    try:
        raw = transport["output"]
        if len(raw) > MAX_OUTPUT_BYTES:
            raise ValueError("Oversized report")
        report = json.loads(raw)
        lines = report["executed_lines"]
        if (type(report["version"]) is not int or report["version"] != 1
                or report["completed"] is not True or report["tracer_intact"] is not True
                or type(report["test_exit_code"]) is not int or report["test_exit_code"] != 0
                or type(lines) is not list or not lines
                or any(type(line) is not int or not 1 <= line <= len(source.splitlines()) for line in lines)):
            raise ValueError("Incomplete or invalid trace")
        evidence["executed_lines"] = sorted(set(lines))
        evidence["test_exit_code"] = report["test_exit_code"]
        evidence["trace_completed"] = True
    except (KeyError, TypeError, ValueError, UnicodeError, RecursionError):
        return result("not_verified", "No valid, complete coverage report was returned.")
    covered = target["line"] in evidence["executed_lines"]
    return result("covered" if covered else "not_covered",
                  "Selected line was observed." if covered else "Selected line was not observed in the completed run.")
