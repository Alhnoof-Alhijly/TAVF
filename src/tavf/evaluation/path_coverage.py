"""Final TestEval path evaluation; no connection to Internal Validation.

Reproduces the vendored match_path algorithm, whose docstring calls it LCS but
whose implementation measures a longest contiguous common segment. A complete
target segment scores 1 even with extra surrounding events. Instrumentation is
in-process and not tamper-proof against deliberately adversarial Python code.
"""

import ast
from collections.abc import Mapping
import hashlib
import json
from pathlib import Path

from tavf.evaluation.line_coverage import MAX_OUTPUT_BYTES, _execute_trace
from tavf.validators.execution import _HARNESS


INSTRUMENTED_DATA = Path(__file__).resolve().parents[3] / "data/raw/testeval/data/leetcode-py-instrumented.jsonl"
MAX_EVENTS = 2048
_PATH_TEST_HARNESS = _HARNESS.replace(
    "exec(compile(reference, '<reference>', 'exec'), namespace)",
    "exec(compile(reference, '<reference>', 'exec'), namespace)\nnamespace['log_function'] = _record",
)
_PATH_HARNESS = """
import contextlib, json, os, sys
events = []
event_bytes = 0
truncated = False
def record(event):
    global event_bytes, truncated
    if type(event) is not str:
        raise TypeError('Invalid path event')
    size = len(json.dumps(event))
    if len(events) >= 2048 or event_bytes + size > 49152:
        truncated = True
        return
    events.append(event)
    event_bytes += size
environment = {'_record': record}
report_stream = sys.stdout
completed = False
test_exit_code = 0
with open(os.devnull, 'w') as sink:
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        try:
            exec(HARNESS, environment)
            completed = True
        except SystemExit as error:
            test_exit_code = error.code if type(error.code) is int else (0 if error.code is None else 1)
            completed = test_exit_code == 0
        except BaseException:
            test_exit_code = 1
logger_intact = environment.get('namespace', {}).get('log_function') is record
report_stream.write(json.dumps({'version': 1, 'completed': completed,
    'test_exit_code': test_exit_code, 'logger_intact': logger_intact,
    'truncated': truncated, 'observed_path': events}))
report_stream.flush()
""".replace("exec(HARNESS, environment)", "exec(" + repr(_PATH_TEST_HARNESS) + ", environment)")


def match_path(observed, target):
    """Same score as TestEval eval_pathcov.match_path, using bounded memory."""
    if not target:
        raise ValueError("Empty path targets are unsupported")
    previous, longest = [0] * (len(target) + 1), 0
    for event in observed:
        current = [0] * (len(target) + 1)
        for index, expected in enumerate(target, 1):
            if event == expected:
                current[index] = previous[index - 1] + 1
                longest = max(longest, current[index])
        previous = current
    return longest / len(target)


class _RemoveLogging(ast.NodeTransformer):
    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "log_function":
            return None
        return self.generic_visit(node)


def _verified_instrumentation(source, row):
    """Check source identity and allow only added logging statements/helper."""
    if not isinstance(row, Mapping) or row.get("python_solution") != source:
        raise ValueError("Instrumented program does not match selected source")
    instrumented = row.get("python_solution_instrumented")
    if not isinstance(instrumented, str) or not instrumented.strip():
        raise ValueError("Instrumentation is unavailable")
    tree = ast.parse(instrumented)
    helpers = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "log_function"]
    if len(helpers) != 1:
        raise ValueError("Expected one log helper")
    tree.body = [n for n in tree.body if n is not helpers[0]]
    stripped = _RemoveLogging().visit(tree)
    if ast.dump(stripped, include_attributes=False) != ast.dump(ast.parse(source), include_attributes=False):
        raise ValueError("Instrumentation changes program logic")
    return instrumented


def evaluate_path_target(artifact: str, task: Mapping, *, instrumented_program: Mapping | None = None) -> dict:
    """Evaluate one artifact's ordered log stream in isolated Docker only.

    By default, look up local instrumentation by task_num, never row position.
    Callers may explicitly supply the corresponding local instrumentation row.
    Reference conditions are preserved as evidence, not evaluated on the host.
    """
    evidence = {"target_type": "path", "observed_path": [], "match_score": None,
                "matching_method": "TestEval match_path: longest contiguous common segment / target length",
                "collection": "ordered artifact-level log_function events",
                "assertion_correctness": "not_verified"}

    def result(status, message):
        return {"status": status, "message": message, "evidence": evidence}

    if not isinstance(task, Mapping) or not isinstance(artifact, str) or not artifact.strip():
        return result("not_verified", "A task and nonempty test source are required.")
    reference, context = task.get("reference"), task.get("input")
    if not isinstance(reference, Mapping) or not isinstance(context, Mapping):
        return result("not_verified", "Path target or program source is unavailable.")
    target, source = reference.get("target"), context.get("python_solution")
    if (task.get("task_type") != "test_case_generation" or reference.get("target_type") != "path"
            or not isinstance(source, str) or not source.strip() or not isinstance(target, Mapping)
            or set(target) != {"execution_path", "condition_path"}
            or any(not isinstance(target[key], list) or not target[key]
                   or len(target[key]) > MAX_EVENTS
                   or any(type(event) is not str or not event.strip() for event in target[key])
                   for key in ("execution_path", "condition_path"))):
        return result("not_verified", "A valid nonempty path target is required.")
    evidence.update(task_id=task.get("task_id"), target=target,
                    program_sha256=hashlib.sha256(source.encode()).hexdigest(),
                    tests_sha256=hashlib.sha256(artifact.encode()).hexdigest())
    try:
        row = instrumented_program
        if row is None:
            rows = [json.loads(line) for line in INSTRUMENTED_DATA.read_text(encoding="utf-8").splitlines() if line.strip()]
            matches = [r for r in rows if r.get("task_num") == reference.get("task_num")]
            if len(matches) != 1:
                raise ValueError("No unambiguous instrumented program")
            row = matches[0]
        if row.get("task_num") != reference.get("task_num"):
            raise ValueError("Instrumented task ID differs")
        instrumented = _verified_instrumentation(source, row)
        labels = {node.args[0].value for node in ast.walk(ast.parse(instrumented))
                  if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                  and node.func.id == "log_function" and len(node.args) == 1
                  and isinstance(node.args[0], ast.Constant) and type(node.args[0].value) is str}
        if any(event not in labels for event in target["execution_path"]):
            raise ValueError("Target event is absent from program instrumentation")
        evidence["instrumented_sha256"] = hashlib.sha256(instrumented.encode()).hexdigest()
    except (OSError, ValueError, TypeError, AttributeError, SyntaxError, RecursionError) as error:
        evidence["error_type"] = type(error).__name__
        return result("not_verified", "Matching local program instrumentation is unavailable or inconsistent.")
    transport, execution = _execute_trace(instrumented, artifact, _PATH_HARNESS)
    evidence.update(execution)
    if (transport is None or transport["exit_code"] != 0 or transport["timed_out"]
            or transport["output_overflow"] or transport["transport_incomplete"] or "cleanup_error" in evidence):
        return result("not_verified", "Docker execution or path collection did not complete reliably.")
    try:
        if len(transport["output"]) > MAX_OUTPUT_BYTES:
            raise ValueError("Oversized report")
        report = json.loads(transport["output"])
        observed = report["observed_path"]
        if (type(report["version"]) is not int or report["version"] != 1
                or report["completed"] is not True or report["logger_intact"] is not True
                or report["truncated"] is not False or type(report["test_exit_code"]) is not int
                or report["test_exit_code"] != 0 or type(observed) is not list or len(observed) > MAX_EVENTS
                or any(type(event) is not str or not event.strip() for event in observed)):
            raise ValueError("Incomplete path report")
    except (KeyError, TypeError, ValueError, UnicodeError, RecursionError):
        return result("not_verified", "No valid complete path report was returned.")
    score = match_path(observed, target["execution_path"])
    evidence.update(observed_path=observed, match_score=score, test_exit_code=0, trace_completed=True)
    return result("covered" if score == 1 else "not_covered",
                  "Full target matched using TestEval's method." if score == 1 else "Full target was not matched.")
