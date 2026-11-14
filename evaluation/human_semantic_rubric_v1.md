# Human Semantic Evaluation rubric v1

## Instructions

Use the original source input and one blinded output at a time. Judge A and B
independently; do not rank them or infer their generation method. Apply the same
anchors to both. Do not consult automatic scores, internal validation, or private
method mappings. Evaluate meaning, not Connextra formatting or heading presence.
No execution or external fact-finding is required.

Each applicable criterion uses integer ratings **1–5**, with higher meaning better.
Use the criterion-specific anchors below, not a comparison with the other output.
Record a short source/output quotation or line reference explaining each rating.
Judge explicit statements and justified paraphrases; plausibility alone does not
make added information source-supported. An honest indication that a source fact
is missing is not an invention. Do not infer an unstated role, benefit, step, or
technical fact. Missing source information must not automatically reduce a rating.

For each criterion, set status `rated`, `uncertain`, or `unassessable`. If a rating
is defensible but uncertain, enter it with status `uncertain` and explain the
ambiguity. If source information or interpretation is insufficient to judge,
leave the rating blank, use `unassessable`, and state why. Never substitute 1 or
the midpoint 3 for missing evidence. Leave nonapplicable criteria entirely blank.
The prepared sheet contains no prefilled ratings or assessment statuses.

## User Stories

### Conceptually Sound

The output expresses a coherent user need: role, goal, and benefit are logically
compatible to the extent those elements are supplied by the source. Assess their
meaning and relationship, not merely whether template slots exist.

| Rating | Anchor |
|---|---|
| 1 | The central need is incoherent or role, goal, and benefit materially conflict. |
| 2 | A major conceptual disconnect obscures what the user needs or why. |
| 3 | The core need is understandable, but a meaningful relationship remains weak or unclear. |
| 4 | The supplied elements form a coherent need, with only a minor conceptual weakness. |
| 5 | All assessable elements express a clear, logically coherent user need and rationale. |

### Problem-oriented

The output communicates the user's problem, desired capability or outcome rather
than substituting an implementation recipe. Retaining a technical constraint
explicitly required by the source is not itself a defect.

| Rating | Anchor |
|---|---|
| 1 | Implementation instructions replace the user problem or desired outcome. |
| 2 | Implementation dominates; the user need is difficult to recover. |
| 3 | The need is visible but mixed with substantial unnecessary implementation prescription. |
| 4 | The need or outcome is primary, with minor unnecessary implementation emphasis. |
| 5 | Clearly focuses on the user need or outcome while retaining necessary source constraints. |

### Unambiguous

An informed reader can interpret the assessable role, intended capability, scope,
and rationale consistently, without unresolved wording or conflicting meanings.
Do not expect the output to resolve uncertainty that the source cannot resolve.

| Rating | Anchor |
|---|---|
| 1 | Central wording permits incompatible interpretations or is unintelligible. |
| 2 | Major ambiguity leaves the intended capability or scope substantially unclear. |
| 3 | The main intent is understandable, but a consequential ambiguity remains. |
| 4 | Meaning is clear overall; only a minor ambiguity remains. |
| 5 | Assessable meaning and scope are precise and internally consistent. |

### Source Fidelity

The output preserves the original intent, requirements, facts, qualifications and
scope without unsupported additions, omissions, or strengthened certainty.

| Rating | Anchor |
|---|---|
| 1 | Replaces or contradicts the central intent, or invents a materially different requirement. |
| 2 | Major unsupported additions or omissions materially change the source meaning. |
| 3 | Preserves the central intent but introduces or loses a meaningful secondary detail. |
| 4 | Preserves intent and material details, with only a minor unsupported inference or omission. |
| 5 | Faithfully preserves all material source meaning; missing information remains honestly missing. |

## Bug Reports

### Clarity

The output communicates the issue, observed behavior and intended behavior in a
readable, logically organized way. Assess comprehensibility, not heading format.

| Rating | Anchor |
|---|---|
| 1 | The central issue cannot be understood or descriptions materially conflict. |
| 2 | Major confusion or disorganization makes the issue difficult to understand. |
| 3 | The central issue is understandable, but important descriptions remain unclear. |
| 4 | Issue and assessable behaviors are clear, with minor wording or organization problems. |
| 5 | The issue and available behavioral distinctions are precise, coherent, and easy to follow. |

### Reproducibility

The output organizes source-supported setup, actions, triggering conditions and
observations into a usable reproduction procedure. This is a human judgment of
the procedure, not proof that the bug reproduces. Unsupported invented steps do
not improve the rating. If the source lacks enough detail to assess usability,
mark unassessable and explain the missing prerequisites.

| Rating | Anchor |
|---|---|
| 1 | Omits or contradicts essential available actions, making the procedure unusable. |
| 2 | Major ordering, setup or action gaps prevent a reader from following the available procedure. |
| 3 | A partly usable procedure remains, but consequential gaps or sequencing problems persist. |
| 4 | Available setup and actions form a usable procedure with minor gaps or ambiguity. |
| 5 | All available reproduction details form a clear, ordered, source-supported procedure. |

### Factual Consistency

The output preserves source-supported observations, expected/actual distinctions,
environment, versions, conditions and uncertainty without invention or distortion.
Assess consistency with the supplied report, not independent truth about software.

| Rating | Anchor |
|---|---|
| 1 | Reverses or contradicts the central reported behavior or invents the central facts. |
| 2 | Major invented, omitted or distorted facts materially change the report. |
| 3 | Central facts remain, but meaningful secondary inaccuracies or unsupported claims occur. |
| 4 | Material facts are preserved, with a minor inconsistency, omission or unsupported inference. |
| 5 | All material available facts and uncertainty are preserved without unsupported additions. |

## Scoring sheet

Each row identifies one blinded output using `sample_id` and `output_label` (A/B).
Find that output and its source in the existing samples packet. `blinded_output_id`
is a stable opaque row identifier; it does not encode the method. Record rater ID
and assessment date, then complete only the listed applicable criteria. Do not
enter ratings for nonapplicable task types. No total or pairwise preference is
requested. Keep completed sheets separate from the private method mapping.
