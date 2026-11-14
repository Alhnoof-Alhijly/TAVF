"""Bounded Docker diagnostics; no generated code is run by this module itself."""
import re
import subprocess
import threading

MAX_STREAM_BYTES = 65536


def classify(exit_code, stdout, stderr, *, timed_out=False, infrastructure=False):
    """Diagnostic labels only; never change evaluator pass/fail decisions."""
    if infrastructure or exit_code in (125, 126, 127):
        return "infrastructure_failure"
    if timed_out:
        return "timeout"
    if exit_code == 0:
        return "none"
    text = stdout + "\n" + stderr
    imports = bool(re.search(r"\b(?:ModuleNotFoundError|ImportError)\b", text))
    assertions = bool(re.search(r"\bAssertionError\b|FAILED\s*\([^)]*failures=[1-9]", text))
    runtime = bool(re.search(r"FAILED\s*\([^)]*errors=[1-9]", text) or
                   re.search(r"(?m)^(?!AssertionError\b|ImportError\b|ModuleNotFoundError\b)[\w.]+(?:Error|Exception):", text))
    categories = (["import_error"] if imports else []) + (["test_assertion_failure"] if assertions else [])
    if runtime and not imports:
        categories.append("runtime_error")
    return "+".join(categories) if categories else "unclassified_failure"


def capture(command, payload, timeout, *, combined_limit=None, popen=None):
    """Drain both pipes, retaining at most 64 KiB per stream.

    Execution discards excess bytes without killing the process, like DEVNULL.
    Coverage supplies its original combined-output cap and still kills on overflow.
    """
    popen = popen or subprocess.Popen
    streams = {"stdout": bytearray(), "stderr": bytearray()}
    observed = {"stdout": 0, "stderr": 0}
    combined = bytearray()
    lock = threading.Lock()
    io_error, overflow = threading.Event(), threading.Event()
    process = popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)

    def drain(name):
        try:
            while True:
                chunk = getattr(process, name).read(4096)
                if not chunk:
                    break
                with lock:
                    observed[name] += len(chunk)
                    room = max(0, MAX_STREAM_BYTES - len(streams[name]))
                    streams[name].extend(chunk[:room])
                    if combined_limit is not None:
                        room = max(0, combined_limit - len(combined))
                        combined.extend(chunk[:room])
                        if sum(observed.values()) > combined_limit:
                            overflow.set()
                if overflow.is_set():
                    process.kill()
        except (OSError, ValueError):
            io_error.set()

    def write():
        try:
            process.stdin.write(payload)
            process.stdin.close()
        except (OSError, ValueError):
            io_error.set()

    readers = [threading.Thread(target=drain, args=(name,), daemon=True) for name in streams]
    writer = threading.Thread(target=write, daemon=True)
    for thread in readers + [writer]:
        thread.start()
    timed_out = False
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        process.wait(timeout=5)
    finally:
        for thread in readers + [writer]:
            thread.join(timeout=1)
        for name, thread in zip(streams, readers):
            if not thread.is_alive():
                getattr(process, name).close()
    # Copy while holding the lock; daemon threads cannot mutate these snapshots.
    with lock:
        diagnostics = {name: bytes(value).decode("utf-8", errors="replace") for name, value in streams.items()}
        diagnostics.update(exit_code=process.returncode, timed_out=timed_out,
                           max_bytes_per_stream=MAX_STREAM_BYTES,
                           bytes_observed=dict(observed),
                           truncated={name: observed[name] > len(streams[name]) for name in streams},
                           transport_incomplete=io_error.is_set() or any(t.is_alive() for t in readers + [writer]))
        transport = {"exit_code": process.returncode, "output": bytes(combined), "timed_out": timed_out,
                     "output_overflow": overflow.is_set(), "transport_incomplete": diagnostics["transport_incomplete"]}
    diagnostics["failure_category"] = classify(process.returncode, diagnostics["stdout"], diagnostics["stderr"], timed_out=timed_out)
    return transport, diagnostics
