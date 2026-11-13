# Independent User Story Structural Evaluation v1

This deterministic evaluation reads only artifact text from the blinded manifest.
It does not import TAVF validators, consult generation histories or statuses, use
method labels, compare source intent, or perform semantic evaluation.

Each criterion has score **1** (surface rules satisfied), **0** (explicit surface
violation), or **null** (unassessable). Null never means zero. This is a separate
three-criterion structural assessment, not the eight-criterion 16-point rubric.

## Rules

For parsing, remove standalone Markdown fences and leading bullet/number markers
from lines, then collapse whitespace. Preserve the original text unchanged.
Use a case-insensitive, whole-text Connextra grammar:
`As a/an <role>, I want <goal>, so that <benefit>`; commas are optional.
Record slot values and character spans in the normalized text. A structural
story start is `As a/an` at the beginning of a line or after sentence punctuation,
optionally preceded by a list marker. These rules do not resolve quoted speech.

- **Well-formed:** 1 if exactly one story start parses with three populated slots;
  otherwise 0. Empty slots, `Not provided`, `N/A`, `TBD`, and literal role/goal/benefit
  bracket placeholders are unpopulated. This does not establish factual correctness.
- **Atomic:** 0 for multiple structural story starts or multiple explicit `I want`
  markers in the request region (before `so that`); 1 for a populated, parsed goal
  with one request marker; otherwise null. `I want` inside the benefit is ignored.
  Conjunctions and multiple implied needs are not interpreted semantically.
- **Minimal:** 0 for Markdown fences, leading list/heading markers, exact duplicate
  nonempty lines (case/whitespace normalized), multiple story starts, or an additional
  sentence boundary after `.`, `!`, or `?` followed by whitespace and an uppercase
  letter/digit; 1 for a populated parsed story with none of these signals;
  otherwise null. This is a surface-format/repetition measure, not a judgment of
  conciseness, relevance, or verbosity. Abbreviations can trigger the sentence rule.

No token/word length cutoff or semantic goal splitting is used. Record every
trigger, parsed slot, and unassessable reason. The total is the sum of three
binary scores only when all three are assessable; otherwise it remains null.
Always report assessable denominators separately. A pass means no violation was
detected by these specified rules, not that the artifact is semantically sound.

Score all 1,000 blinded User Story artifacts identically. Keep their anonymous
artifact and pair IDs. Do not open the private method mapping during scoring.
