"""Conservative surface checks; passing does not establish semantic quality.

Well-formed checks Connextra role/request/benefit slots. Atomic flags repeated
explicit 'I want' clauses, not conjunctions. Minimal flags exact duplicate
stories and standalone Markdown fences, not verbosity or irrelevant content.
Stories start on separate lines (optional bullets/numbers); wrapped lines join
the preceding story. Arbitrary prose and same-line story boundaries are not
semantically parsed. No source-intent or factual-preservation claim is made.
"""

import re


_PREFIX = re.compile(r"^\s*(?:(?:[-*+] |\d+[.)] )\s*)?")
_START = re.compile(r"^As\s+(?:a|an)\b", re.IGNORECASE)
_FORM = re.compile(
    r"^As\s+(?:a|an)\s+(?P<role>.*?),?\s*\bI want\b\s*"
    r"(?P<goal>.*?),?\s*\bso that\b\s*(?P<benefit>.*?)\s*[.!]?\s*$",
    re.IGNORECASE,
)
_MISSING = {"", "not provided", "[role]", "[goal]", "[benefit]"}


def validate_user_story(artifact: str) -> dict:
    """Return valid, classified issues, and rule evidence for an artifact.

    valid means no issues detected by these rules. missing_information requires
    source clarification; fixable denotes a surface/structural issue only.
    Story numbers are one-based; artifact-level evidence uses story=None.
    """
    if not isinstance(artifact, str):
        raise TypeError("User story artifact must be a string.")

    issues, evidence, stories = [], [], []

    def add(criterion, classification, message, story, text):
        evidence.append({"story": story, "text": text})
        issues.append({
            "criterion": criterion,
            "classification": classification,
            "message": message,
            "story": story,
            "evidence_index": len(evidence) - 1,
        })

    for line in artifact.splitlines():
        text = _PREFIX.sub("", line).strip()
        if not text:
            continue
        if text.startswith("```"):
            add("Minimal", "fixable", "Standalone Markdown fence.", None, line)
            continue
        if _START.match(text) or not stories:
            stories.append(text)
        else:
            stories[-1] += " " + text

    if not stories:
        add("Well-formed", "missing_information", "No user story supplied.", None, artifact)

    seen = set()
    for number, story in enumerate(stories, 1):
        match = _FORM.fullmatch(story)
        if match is None:
            # Without unambiguous slots, do not infer missing facts from prose.
            has_markers = bool(
                _START.match(story)
                and re.search(r"\bI want\b", story, re.IGNORECASE)
                and re.search(r"\bso that\b", story, re.IGNORECASE)
            )
            add("Well-formed", "fixable" if has_markers else "missing_information",
                "Cannot establish Connextra role, goal, and benefit slots.", number, story)
        else:
            for slot, value in match.groupdict().items():
                if value.strip(" ,.!?\t").lower() in _MISSING:
                    add("Well-formed", "missing_information",
                        f"Missing or placeholder {slot}.", number, story)

        if len(re.findall(r"\bI want\b", story, re.IGNORECASE)) > 1:
            add("Atomic", "fixable", "Repeated explicit request clauses; review grouping.",
                number, story)

        if story in seen:
            add("Minimal", "fixable", "Exact duplicate story.", number, story)
        seen.add(story)

    return {"valid": not issues, "issues": issues, "evidence": evidence}
