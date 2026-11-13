# User Story Structural Evaluation v2

Post hoc revision: retain v1 unchanged and report v2 separately. This text-only,
deterministic assessment uses no TAVF validator, method labels, source-fidelity
judgments, or semantic scoring. Freeze this protocol before anonymous scoring;
join the private method mapping only after writing the scores.

Scores are 1/pass, 0/fail, or null/unassessable. There is no combined total.

## Segmentation and presentation

Ignore enclosing Markdown fences and leading bullets/numbers as presentation.
Split stories at line-initial `As a/an` and sentence-boundary `As a/an` following
`.`, `!`, or `?`. Join wrapped lines. Non-story text before a story, or a separate
line after a sentence-ending story, is commentary. An additional `As a/an` inside
a segment without a recognized boundary makes segmentation ambiguous; its role
may be quoted text, so do not infer another requirement. Preserve all text and
line evidence. Multiple stories are allowed and evaluated individually.

## Independent criteria

- **Structural Form:** identifiable `As a/an <role>, I want <goal>, so that
  <benefit>` structure, with optional commas. All three slots must be nonempty
  text or explicit missing markers. Empty slots or absent delimiters fail;
  ambiguous segmentation is unassessable. `Not provided` satisfies slot presence.
- **Information Completeness:** record each slot as `populated`,
  `explicitly_missing`, `empty`, or `unparseable`. Case-insensitive `Not provided`,
  `N/A`, `TBD`, and literal `[role]`, `[goal]`, `[benefit]` are explicit missing
  markers after trimming enclosing whitespace and terminal punctuation. Pass
  requires all slots populated. Any explicit missing/empty slot fails; remaining
  unparseable cases are unassessable. Populated does not mean source-supported.
- **Atomic:** multiple explicit `I want` clauses before `so that` fail within
  one story. One identifiable populated goal with one such clause passes, even
  if role or benefit is absent. Missing/unparseable goal is unassessable.
  Ignore `I want` in benefits; conjunctions alone do not fail.
- **Minimal:** exact duplicate stories (case and whitespace normalized) or
  separately identifiable commentary fail. Multiple distinct stories, missing
  information, bullets, numbering, fences, and wrapping do not fail. Otherwise
  pass when story boundaries are known; ambiguous boundaries or no story are
  unassessable unless explicit commentary already establishes failure. Inline
  prose not separable by these rules is not semantically judged. No length cutoff.

Keep per-story slots and criterion evidence. For artifact aggregation, any
assessable story failure causes failure; all stories must pass for a pass;
otherwise unassessable. Minimal additionally includes artifact-level commentary
and duplicates. Missing information never propagates into Atomic or Minimal.

## Denominators and analysis

Report artifact Pass/Fail/Unassessable counts out of 500 per method, with separate
assessable denominators (Pass + Fail). Paired differences are TAVF minus Baseline
only for task pairs assessable in both methods for that criterion. Report omitted
pairs by missingness pattern; never zero-fill unassessable scores. Report slot-state
counts with denominator three slots per segmented story. Multi-story artifacts
retain one artifact-level observation per original task/method, avoiding extra
weight from story splitting. No assertion of semantic quality or source fidelity
follows from a structural pass. Record parser limitations and retain evidence for
independent review; do not adjust rules after seeing v2 method comparisons.
