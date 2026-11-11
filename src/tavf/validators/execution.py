"""Opt-in execution in a disposable Docker container; never execute on the host."""

import json
import subprocess
import uuid


# Only source strings cross the boundary. No task metadata, environment or files.
_HARNESS = """
import inspect, json, sys, unittest
reference, tests = json.load(sys.stdin)
namespace = {'__name__': '__tavf_tests__'}
exec(compile(reference, '<reference>', 'exec'), namespace)
exec(compile(tests, '<tests>', 'exec'), namespace)
suite = unittest.TestSuite()
for name, value in list(namespace.items()):
    if isinstance(value, type) and issubclass(value, unittest.TestCase):
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(value))
    elif name.startswith('test_') and inspect.isfunction(value):
        if inspect.iscoroutinefunction(value):
            raise TypeError('Async test functions require an unsupported runner')
        suite.addTest(unittest.FunctionTestCase(value))
if suite.countTestCases():
    result = unittest.TextTestRunner().run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
"""


def validate_execution(artifact: str, reference: str = "") -> dict:
    """Run top-level code, unittest cases and zero-argument test_* functions.

    Execution success does not establish assertion correctness. Output is discarded
    to bound host memory and avoid retaining secrets emitted by untrusted code.
    Docker infrastructure errors are unverified; runtime failures/timeouts fail.
    """
    name = "tavf-validation-" + uuid.uuid4().hex
    evidence = {
        "image": "python:3.12-slim", "timeout_seconds": 10,
        "cpu_limit": 0.5, "memory_bytes": 134217728, "process_limit": 16,
        "network": "none", "read_only": True, "mounts": [],
        "output": "discarded",
    }
    command = [
        "docker", "run", "--rm", "--pull=never", "--name", name, "-i",
        "--network", "none", "--read-only", "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges", "--cpus", "0.5",
        "--memory", "128m", "--memory-swap", "128m", "--pids-limit", "16",
        "--user", "65534:65534", "--log-driver", "none",
    ]
    # Docker can inject proxy credentials from the host's client config even
    # without explicit environment forwarding. Override every supported proxy.
    for proxy in ("HTTP_PROXY", "HTTPS_PROXY", "FTP_PROXY", "NO_PROXY", "ALL_PROXY"):
        for key in (proxy, proxy.lower()):
            command.extend(["--env", key + "="])
    command.extend(["python:3.12-slim", "python", "-I", "-B", "-c", _HARNESS])
    try:
        result = subprocess.run(
            command, input=json.dumps([reference, artifact]), text=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10,
            shell=False,
        )
        evidence["exit_code"] = result.returncode
        if result.returncode == 0:
            status, message = "passed", "Container completed successfully; assertion correctness is not established."
        elif result.returncode in (125, 126, 127):
            status, message = "not_verified", "Docker could not start the isolated Python process."
        else:
            status, message = "failed", "Container reported a runtime or test failure."
    except subprocess.TimeoutExpired:
        status, message = "failed", "Execution exceeded the 10-second timeout."
        evidence["timed_out"] = True
    except OSError as error:
        status, message = "not_verified", "Docker is unavailable or could not be launched."
        evidence["error_type"] = type(error).__name__
    finally:
        # Killing the CLI on timeout does not stop the container. Always remove it.
        try:
            cleanup = subprocess.run(
                ["docker", "rm", "--force", name], stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, timeout=5, shell=False,
            )
            evidence["cleanup_exit_code"] = cleanup.returncode
        except (OSError, subprocess.TimeoutExpired) as error:
            evidence["cleanup_error"] = type(error).__name__
            status, message = "not_verified", "Container cleanup could not be confirmed."
        if evidence.get("timed_out") and evidence.get("cleanup_exit_code", 1) != 0:
            status, message = "not_verified", "Execution timed out and container removal could not be confirmed."
    return {"status": status, "message": message, **evidence}
