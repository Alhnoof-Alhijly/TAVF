"""Static expected-result comparisons against explicitly trusted examples."""

import ast


def _literal(node):
    value = ast.literal_eval(node)
    # Restrict comparisons to plain literal data, with no custom equality code.
    def plain(item):
        if type(item) in (str, int, float, bool, type(None)):
            return True
        if type(item) in (list, tuple):
            return all(plain(value) for value in item)
        if type(item) is dict:
            return all(plain(key) and plain(value) for key, value in item.items())
        return False
    if not plain(value):
        raise ValueError("Unsupported literal")
    return value


def _call_key(node):
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
        raise ValueError("Only direct calls are supported")
    for argument in node.args:
        _literal(argument)
    for keyword in node.keywords:
        if keyword.arg is None:
            raise ValueError("Unpacked arguments are unsupported")
        _literal(keyword.value)
    return ast.dump(node, include_attributes=False)


def check_assertions(tree, input_details, execution, trusted_oracle=None):
    """Check assert call(literals) == literal (or reversed) without execution.

    trusted_oracle is supplied by the caller, never read from generated/task data:
    {'source': 'curated examples', 'cases': [{'call': 'target(1)', 'expected': 1}]}.
    Source labels document provenance; callers are responsible for establishing
    trust. Reference code and successful execution are never treated as oracles.
    This verifies expected values only, not runtime reachability or test coverage.
    """
    details = {"scope": "expected_results_only", "execution_status": execution["status"],
               "execution_evidence_index": 2, "assertion_lines": [], "assertions": []}
    if tree is None:
        return "not_verified", "Assertions cannot be inspected until syntax is corrected.", details
    nodes = sorted((node for node in ast.walk(tree) if isinstance(node, ast.Assert) or (
        isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name) and node.func.value.id == "self"
        and node.func.attr.startswith("assert")
    )), key=lambda node: (node.lineno, node.col_offset))
    details["assertion_lines"] = sorted({node.lineno for node in nodes})
    if not nodes:
        return "failed", "No statically visible assert statements or self.assert* calls; dynamic helpers are not inspected.", details
    oracle = {}
    try:
        if type(trusted_oracle) is not dict or type(trusted_oracle.get("source")) is not str or not trusted_oracle["source"].strip():
            raise ValueError("Missing trusted provenance")
        cases = trusted_oracle["cases"]
        if type(cases) is not list or not cases:
            raise ValueError("Missing examples")
        for case in cases:
            if type(case) is not dict or type(case.get("call")) is not str:
                raise ValueError("Invalid example")
            key = _call_key(ast.parse(case["call"], mode="eval").body)
            # Parse only builtin literal representations, never caller objects.
            expected = case["expected"]
            if type(expected) not in (str, int, float, bool, type(None), list, tuple, dict):
                raise ValueError("Invalid expected value")
            # Nested custom objects must not have repr/equality invoked either.
            def literal_node(value):
                if type(value) in (list, tuple):
                    return (ast.List if type(value) is list else ast.Tuple)(elts=[literal_node(v) for v in value])
                if type(value) is dict:
                    return ast.Dict(keys=[literal_node(k) for k in value], values=[literal_node(v) for v in value.values()])
                if type(value) not in (str, int, float, bool, type(None)):
                    raise ValueError("Invalid expected value")
                return ast.Constant(value=value)
            expected = _literal(literal_node(expected))
            if key in oracle:
                raise ValueError("Ambiguous duplicate examples")
            oracle[key] = expected
    except (KeyError, TypeError, ValueError, SyntaxError, RecursionError):
        return "not_verified", "No complete, unambiguous trusted oracle is available; execution success does not prove assertion correctness.", details
    details["oracle_source"] = trusted_oracle["source"]
    resolved = {(item["line"], item["target"]) for item in input_details["calls"] if item["status"] == "passed"}
    for node in nodes:
        item = {"line": node.lineno, "status": "not_verified"}
        try:
            if not (isinstance(node, ast.Assert) and isinstance(node.test, ast.Compare)
                    and len(node.test.ops) == 1 and isinstance(node.test.ops[0], ast.Eq)):
                raise ValueError("Unsupported assertion")
            actual, expected = node.test.left, node.test.comparators[0]
            if not isinstance(actual, ast.Call):
                actual, expected = expected, actual
            key = _call_key(actual)
            value = _literal(expected)
            if (actual.lineno, ast.unparse(actual.func)) not in resolved or key not in oracle:
                raise ValueError("Unresolved target or missing oracle example")
            item["status"] = "passed" if value == oracle[key] else "failed"
        except (TypeError, ValueError, SyntaxError, RecursionError):
            pass
        details["assertions"].append(item)
    statuses = {item["status"] for item in details["assertions"]}
    if "failed" in statuses:
        return "failed", "An asserted expected value disagrees with the trusted oracle.", details
    if "not_verified" in statuses:
        return "not_verified", "Some assertions are unsupported, unresolved, or lack a trusted example.", details
    return "passed", "All visible assertion expected values match trusted examples; runtime coverage is not established.", details
