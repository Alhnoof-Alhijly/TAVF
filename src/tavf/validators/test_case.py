"""Static test checks with explicit opt-in Docker execution and explicit trusted assertion examples."""

import ast
import inspect
from collections.abc import Mapping

from tavf.validators.execution import validate_execution
from tavf.validators.assertions import check_assertions


def _signature(function, bound=False):
    """Build a binding-only signature without evaluating annotations/defaults."""
    args = function.args
    positional = args.posonlyargs + args.args
    defaults_start = len(positional) - len(args.defaults)
    parameters = []
    for index, arg in enumerate(positional):
        kind = (inspect.Parameter.POSITIONAL_ONLY if index < len(args.posonlyargs)
                else inspect.Parameter.POSITIONAL_OR_KEYWORD)
        default = None if index >= defaults_start else inspect.Parameter.empty
        parameters.append(inspect.Parameter(arg.arg, kind, default=default))
    if bound:
        if not parameters:
            return None
        parameters = parameters[1:]
    if args.vararg:
        parameters.append(inspect.Parameter(args.vararg.arg, inspect.Parameter.VAR_POSITIONAL))
    for arg, default in zip(args.kwonlyargs, args.kw_defaults):
        parameters.append(inspect.Parameter(
            arg.arg, inspect.Parameter.KEYWORD_ONLY,
            default=inspect.Parameter.empty if default is None else None,
        ))
    if args.kwarg:
        parameters.append(inspect.Parameter(args.kwarg.arg, inspect.Parameter.VAR_KEYWORD))
    return inspect.Signature(parameters)


def _input_validity(tree, context):
    """Narrow, conservative call resolution; no domain or runtime inference."""
    details = {"scope": "signature_only", "domain_status": "not_verified", "calls": []}
    source = context.get("python_solution")
    if tree is None or not isinstance(source, str) or not source.strip():
        return "not_verified", "Generated syntax or reference signature is unavailable.", details
    try:
        reference = ast.parse(source)
        compile(reference, "<reference_signature>", "exec")
    except (SyntaxError, ValueError, RecursionError):
        return "not_verified", "Reference signatures cannot be parsed.", details

    if any(
        (isinstance(node, ast.Attribute) and isinstance(node.ctx, (ast.Store, ast.Del)))
        or (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in {"exec", "eval", "setattr", "delattr", "globals", "locals"})
        for node in ast.walk(tree)
    ):
        return "not_verified", "Dynamic bindings or attribute mutation prevent conservative target resolution.", details

    # Any generated binding/shadowing makes a direct reference name ambiguous.
    bindings = [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
                and isinstance(node.ctx, (ast.Store, ast.Del))]
    bindings += [node.arg for node in ast.walk(tree) if isinstance(node, ast.arg)]
    bindings += [node.name for node in ast.walk(tree)
                 if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    bindings += [alias.asname or alias.name.split(".")[0]
                 for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))
                 for alias in node.names]
    wildcard = "*" in bindings
    reference_bindings = {node.id for node in ast.walk(reference)
                          if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del))}
    reference_bindings.update(alias.asname or alias.name.split(".")[0]
                              for node in ast.walk(reference)
                              if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in node.names)
    definitions = {}
    for node in reference.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            definitions.setdefault(node.name, []).append(node)
    functions, classes = {}, {}
    for name, nodes in definitions.items():
        if (len(nodes) != 1 or name in reference_bindings or "*" in reference_bindings
                or name in bindings or wildcard):
            continue
        node = nodes[0]
        if isinstance(node, ast.FunctionDef) and not node.decorator_list:
            functions[name] = _signature(node)
        elif (isinstance(node, ast.ClassDef) and not node.decorator_list
              and not node.bases and not node.keywords):
            if any(isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                   and item.name in {"__getattribute__", "__getattr__", "__new__"}
                   for item in node.body):
                continue
            methods = {}
            for method in node.body:
                if isinstance(method, ast.FunctionDef):
                    methods.setdefault(method.name, []).append(method)
            classes[name] = {method: _signature(items[0], bound=True)
                             for method, items in methods.items()
                             if len(items) == 1 and not items[0].decorator_list
                             and method not in reference_bindings}

    # Resolve only straight-line, same-scope instance assignments. No aliases,
    # imports, inheritance, decorators, conditional assignments or rebinding.
    scopes = {}
    def visit(node, scope):
        scopes[id(node)] = scope
        next_scope = node if isinstance(node, (ast.Module, ast.FunctionDef,
                                               ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)) else scope
        for child in ast.iter_child_nodes(node):
            visit(child, next_scope)
    visit(tree, tree)
    instances = {}
    constructors = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name) and node.value.func.id in classes
                and not node.value.args and not node.value.keywords
                and bindings.count(node.targets[0].id) == 1
                and node in getattr(scopes[id(node)], "body", [])):
            instances[node.targets[0].id] = (node.value.func.id, node, scopes[id(node)])
            constructors.add(id(node.value))

    for call in sorted((n for n in ast.walk(tree) if isinstance(n, ast.Call)), key=lambda n: n.lineno):
        signature = None
        if id(call) in constructors:
            continue
        target = call.func
        if isinstance(target, ast.Name):
            signature = functions.get(target.id)
        elif isinstance(target, ast.Attribute):
            receiver = target.value
            if (isinstance(receiver, ast.Name) and receiver.id == "self"
                    and target.attr.startswith("assert")):
                continue  # unittest assertion helpers are assessed separately.
            class_name = None
            if (isinstance(receiver, ast.Call) and isinstance(receiver.func, ast.Name)
                    and receiver.func.id in classes and not receiver.args and not receiver.keywords):
                class_name = receiver.func.id
                constructors.add(id(receiver))
            elif isinstance(receiver, ast.Name) and receiver.id in instances:
                name, assignment, scope = instances[receiver.id]
                if scope is scopes[id(call)] and assignment.lineno < call.lineno:
                    class_name = name
            if class_name:
                signature = classes[class_name].get(target.attr)
        # Inline constructor nodes may be visited after their enclosing call.
        if id(call) in constructors:
            continue
        item = {"line": call.lineno, "target": ast.unparse(target)}
        if signature is None or any(isinstance(arg, ast.Starred) for arg in call.args) or any(
            keyword.arg is None for keyword in call.keywords
        ):
            item.update(status="not_verified", message="Call target or unpacked arguments cannot be resolved conservatively.")
        else:
            try:
                signature.bind(*([None] * len(call.args)), **{kw.arg: None for kw in call.keywords})
            except TypeError as error:
                item.update(status="failed", message=str(error))
            else:
                item.update(status="passed", message="Arguments bind to the reference signature; domain not checked.")
        details["calls"].append(item)

    statuses = [item["status"] for item in details["calls"]]
    if "failed" in statuses:
        return "failed", "Statically resolved target arguments do not match the reference signature.", details
    if not statuses or "not_verified" in statuses:
        return "not_verified", "No complete unambiguous set of target calls; input domain remains unverified.", details
    return "passed", "Resolved call signatures match; input-domain constraints remain unverified.", details


def validate_test_case(artifact: str, task_input: Mapping | None = None, *,
                       execute: bool = False, trusted_oracle: dict | None = None) -> dict:
    """Return valid, issues, evidence for the four approved checks.

    Optional task_input uses the existing description/python_solution fields.
    Reference AST signatures support argument binding only, not input-domain
    constraints or executable oracles. Evidence status is passed,
    failed, or not_verified. Unverified checks produce missing_information
    issues; detected structural defects are fixable. valid requires all four
    checks to pass. execute=True opts into isolated Docker execution; the default
    never launches Docker. trusted_oracle explicitly supplies caller-trusted examples:
    {'source': 'curated examples', 'cases': [{'call': 'target(1)', 'expected': 1}]}.
    Only direct equality assertions with literal inputs/expected values are checked.
    Task metadata, reference code and execution success do not establish trust.
    """
    if not isinstance(artifact, str):
        raise TypeError("Test case artifact must be a string.")
    if task_input is not None and not isinstance(task_input, Mapping):
        raise TypeError("task_input must be a mapping or None.")

    issues, evidence = [], []

    def record(check, status, message, classification=None, **details):
        evidence.append({"check": check, "status": status, "message": message, **details})
        if status != "passed":
            issues.append({
                "check": check,
                "classification": classification,
                "message": message,
                "evidence_index": len(evidence) - 1,
            })

    tree = None
    try:
        if not artifact.strip():
            raise SyntaxError("No test code supplied.")
        tree = ast.parse(artifact, filename="<generated_tests>", mode="exec")
        # Compile without executing, including checks such as return outside a function.
        compile(tree, "<generated_tests>", "exec")
    except (SyntaxError, ValueError, RecursionError) as error:
        tree = None
        record("Syntax Validity", "failed", "Test code cannot be compiled as Python.",
               "fixable", error_type=type(error).__name__,
               line=getattr(error, "lineno", None),
               offset=getattr(error, "offset", None))
    else:
        record("Syntax Validity", "passed", "Python syntax compiles; code was not executed.")

    context = task_input if task_input is not None else {}
    context_fields = [
        field for field in ("description", "python_solution")
        if isinstance(context.get(field), str) and context[field].strip()
    ]
    input_status, input_message, input_details = _input_validity(tree, context)
    record("Input Validity", input_status, input_message,
           "fixable" if input_status == "failed" else "missing_information",
           available_context_fields=context_fields, **input_details)
    if execute and tree is not None:
        reference = context.get("python_solution", "")
        execution = validate_execution(artifact, reference if isinstance(reference, str) else "")
        status = execution.pop("status")
        message = execution.pop("message")
        record("Execution Success", status, message,
               "fixable" if status == "failed" else "missing_information", **execution)
    else:
        record("Execution Success", "not_verified",
               "Execution is disabled or generated syntax is invalid; code was not executed.",
               "missing_information")

    assertion_status, assertion_message, assertion_details = check_assertions(
        tree, input_details, evidence[2], trusted_oracle,
    )
    record("Assertion Validity", assertion_status, assertion_message,
           "fixable" if assertion_status == "failed" else "missing_information",
           **assertion_details)

    return {"valid": not issues, "issues": issues, "evidence": evidence}
