# Independent Bug Report Structural Evaluation v1

This is a deterministic, text-only structural assessment of blinded artifacts.
It does not use TAVF validation, method labels, source fidelity, or semantic
judgments. It is separate from the eight-criterion qualitative rubric.

Four equally weighted components are assessed: Summary, Steps to Reproduce,
Expected Result, Actual Result. Each receives 1/pass if exactly one recognized
section contains populated text, 0/fail if absent, empty, or explicitly missing,
or null/unassessable if its heading occurs repeatedly (ambiguous ownership).

Headings are case-insensitive and may be plain, Markdown headings, bold,
numbered, or bulleted. A colon may introduce inline content. Aliases:

- Summary: Summary, Title, Bug Summary.
- Steps to Reproduce: Steps, Steps to Reproduce, Reproduction Steps.
- Expected Result: Expected, Expected Result(s), Expected Behavior/Behaviour.
- Actual Result: Actual, Actual Result(s), Actual Behavior/Behaviour.

Fences are ignored as presentation. Other Markdown headings, standalone bold
labels, short colon-terminated labels, and common context labels (Environment,
Technical Context, Additional Information, Notes, Attachments, Regression) end
the preceding section. Heading-like text inside code may be misinterpreted;
retain evidence for review. Unrecognized headings are not inferred semantically.

Nonempty prose and numbered/bulleted steps are both accepted; no number of steps,
word limit, or imperative-verb test is imposed. Formatting alone never establishes
actionability. After stripping presentation markers and terminal punctuation,
literal Not provided, Not specified, Not available, Unknown, N/A, TBD, and
[Not provided] are explicit missing values. They are not populated information.
Mixed missing markers plus other substantive text are recorded as populated.

Structural score = 25 × sum of four binary component scores (0–100), only when
all four are assessable; otherwise null. Never treat null as zero. Retain section
heading lines, body text, state and reason for every component. Populated text
does not establish factual accuracy, clarity, reproducibility or source support.

Score all 1,000 artifacts before opening the private mapping. Report component
Pass/Fail/Unassessable out of 500 per method and assessable denominators. For total
means use artifacts with four assessable components. Paired differences are
TAVF minus Baseline using jointly assessable pairs, with denominators, exclusions,
ties and direction counts. Preserve original artifacts, manifests and other scores.
