"""Structural bug-report checks, without semantic or reproducibility claims.

Only explicitly labeled original sections establish available source content.
Unlabeled source prose is not interpreted: missing_information can therefore
mean that information could not be established structurally, not that it is
definitely absent. Non-placeholder text is only a surface content signal.
"""

import re


_ALIASES = {
    "summary": "Summary",
    "steps": "Steps to Reproduce",
    "steps to reproduce": "Steps to Reproduce",
    "expected": "Expected Result",
    "expected result": "Expected Result",
    "expected results": "Expected Result",
    "expected behavior": "Expected Result",
    "expected behaviour": "Expected Result",
    "actual": "Actual Result",
    "actual result": "Actual Result",
    "actual results": "Actual Result",
    "actual behavior": "Actual Result",
    "actual behaviour": "Actual Result",
}
_SECTIONS = ("Summary", "Steps to Reproduce", "Expected Result", "Actual Result")
_LABEL = "|".join(sorted(_ALIASES, key=len, reverse=True))
_HEADING = re.compile(
    rf"^\s*(?:\#{{1,6}}\s+)?(?:\*\*|__)?(?P<label>{_LABEL})"
    r"(?:(?:\*\*|__)?\s*:\s*(?:\*\*|__)?\s*(?P<body>.*)"
    r"|(?:\*\*|__)?\s*)$",
    re.IGNORECASE,
)
_PLACEHOLDERS = {
    "", "not provided", "not specified", "not available", "unknown", "none",
    "na", "n a", "tbd", "todo", "missing",
}


def _has_content(text):
    for line in text.splitlines():
        line = re.sub(r"^\s*(?:[-*+]\s+|\d+[.)]\s*)", "", line)
        normalized = " ".join(re.findall(r"[^\W_]+", line.lower()))
        if normalized not in _PLACEHOLDERS and any(c.isalpha() for c in normalized):
            return True
    return False


def _parse_sections(text):
    sections = {section: [] for section in _SECTIONS}
    current = None
    for line in text.splitlines():
        heading = _HEADING.fullmatch(line)
        if heading:
            current = _ALIASES[heading["label"].lower()]
            sections[current].append(heading["body"] or "")
        elif re.match(r"^\s*#{1,6}\s+", line) or re.fullmatch(
            r"\s*(?:\*\*|__)?Technical Context(?:\*\*|__)?\s*:?\s*", line,
            re.IGNORECASE,
        ):
            current = None
        elif current is not None:
            sections[current][-1] += "\n" + line
    return sections


def validate_bug_report(artifact: str, original_input: str) -> dict:
    """Return valid, classified issues, and evidence; never modify either input.

    Accept canonical headings and the shorter headings in TAVF's prompt.
    A missing/empty output section is fixable only when its labeled source
    section contains non-placeholder text. Otherwise source clarification is
    required. valid means only that these structural checks found no issues.
    """
    if not isinstance(artifact, str) or not isinstance(original_input, str):
        raise TypeError("Bug report artifact and original_input must be strings.")

    output_sections = _parse_sections(artifact)
    source_sections = _parse_sections(original_input)
    issues, evidence = [], []

    def add(section, classification, message):
        evidence.append({
            "section": section,
            "output_present": bool(output_sections[section]),
            "output_text": "\n".join(output_sections[section]),
            "source_text": "\n".join(source_sections[section]),
            "source_content_available": any(
                _has_content(text) for text in source_sections[section]
            ),
        })
        issues.append({
            "section": section,
            "classification": classification,
            "message": message,
            "evidence_index": len(evidence) - 1,
        })

    for section in _SECTIONS:
        blocks = output_sections[section]
        if not blocks or not any(_has_content(text) for text in blocks):
            available = any(_has_content(text) for text in source_sections[section])
            condition = "missing" if not blocks else "empty or placeholder-only"
            add(section, "fixable" if available else "missing_information",
                f"Section is {condition}. " + (
                    "Labeled source content is available."
                    if available else "Source content cannot be established from labeled sections."
                ))
        if len(blocks) > 1:
            add(section, "fixable", "Repeated section heading; review section organization.")

    return {"valid": not issues, "issues": issues, "evidence": evidence}
