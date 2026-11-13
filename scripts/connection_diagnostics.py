"""Persist exception chains without request bodies or credentials."""
import os
import re
import traceback


def redact(value):
    text = str(value)
    for name, secret in os.environ.items():
        if secret and any(word in name.upper() for word in ("KEY", "TOKEN", "PASSWORD", "SECRET")):
            text = text.replace(secret, "[REDACTED]")
    text = re.sub(r"(?i)(https?://)[^/\s@]+@", r"\1[REDACTED]@", text)
    return re.sub(r"\bsk-[A-Za-z0-9_-]+", "[REDACTED]", text)


def describe(error):
    chain, seen = [], set()
    current = error
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        chain.append({"type": type(current).__module__ + "." + type(current).__name__,
                      "message": redact(current), "errno": getattr(current, "errno", None),
                      "winerror": getattr(current, "winerror", None)})
        current = current.__cause__ or (None if current.__suppress_context__ else current.__context__)
    return {"error_type": type(error).__name__, "exception_chain": chain,
            "traceback": redact("".join(traceback.format_exception(type(error), error, error.__traceback__))),
            "http_status": getattr(error, "status_code", None),
            "request_id": getattr(error, "request_id", None)}
