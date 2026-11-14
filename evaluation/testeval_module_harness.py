"""Versioned final-evaluation target packaging; no changes to test/scoring code."""
VERSION = "testeval_target_module_v2"
ALIASES = ("solution", "main", "__main__")


def build_harnesses(execution_source, line_source, path_source, old_path_test_source):
    old = "namespace = {'__name__': '__tavf_tests__'}\nexec(compile(reference, '<reference>', 'exec'), namespace)"
    setup = """import types
target_module = types.ModuleType('solution')
target_module.__file__ = '<reference>'
for alias in ('solution', 'main', '__main__'):
    sys.modules[alias] = target_module
exec(compile(reference, '<reference>', 'exec'), target_module.__dict__)
# Path collection supplies instrumented reference text and its trusted recorder.
if '_record' in globals():
    target_module.__dict__['log_function'] = _record
namespace = dict(target_module.__dict__)
namespace['__name__'] = '__tavf_tests__'"""
    if execution_source.count(old) != 1:
        raise ValueError("Unknown execution harness layout")
    updated = execution_source.replace(old, setup)
    if line_source.count(repr(execution_source)) != 1 or path_source.count(repr(old_path_test_source)) != 1:
        raise ValueError("Unknown coverage harness embedding")
    return {"execution": updated,
            "line": line_source.replace(repr(execution_source), repr(updated)),
            "path": path_source.replace(repr(old_path_test_source), repr(updated))}
