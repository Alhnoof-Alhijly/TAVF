# TAVF Task Definitions

## 1. User Story Refinement

**Task Type:** `user_story_refinement`

**Input:**  
An original user story selected from the Dalpiaz user-story dataset.

**TAVF Prompt Instruction:**
Refine the supplied original user story, preserving its intent and source facts.

**Expected Output:**  
A refined version of the same user story that preserves the original intent while improving its quality.

The refined user story should:
- preserve the original meaning;
- improve clarity;
- reduce ambiguity;
- remove unnecessary redundancy;
- correct wording and grammatical issues;
- follow good user-story quality principles.

**Gold Reference Output:**  
Not available.

**Evaluation Method:**  
The refined user story will be evaluated using a task-specific user-story quality rubric.


## 2. Bug Report Refinement

**Task Type:** `bug_report_refinement`

**Input:**  
The original bug report text selected from the BugsRepo structured dataset.

**Expected Output:**  
A refined and well-structured bug report that preserves the original technical meaning and improves readability and completeness.

The refined bug report should clearly organize:
- a concise issue summary;
- steps to reproduce;
- expected behavior;
- actual behavior;
- relevant technical context when available.

The refinement should:
- preserve all important facts;
- avoid inventing new information;
- remove unnecessary repetition;
- improve clarity and organization;
- keep the report technically consistent with the original input.

**Gold Reference Output:**  
Not available as a single rewritten reference report.

**Reference Information:**  
The original dataset provides structured fields for:
- Steps to Reproduce;
- Expected Result;
- Actual Result.

These fields will be used to verify whether the refined output preserves the essential bug information.

**Evaluation Method:**  
The generated output will be evaluated using a task-specific bug-report quality rubric.

## 3. Test Case Generation

**Task Type:** `test_case_generation`

**Input:**  
A programming task description together with its reference Python implementation from the TestEval dataset.

**Expected Output:**  
A set of executable test cases that exercise the provided implementation and cover important behaviors, edge cases, and branches.

The generated test cases should:
- be valid and executable;
- test the intended function correctly;
- include normal and edge cases;
- avoid redundant tests;
- aim to maximize code coverage;
- remain consistent with the task description.

**Gold Reference Output:**  
Not required as a textual reference.

**Reference Information:**  
The TestEval dataset provides:
- task description;
- reference Python solution;
- code blocks;
- target lines.

The `blocks` and `target_lines` fields will not be included in the generation prompt. They will be retained for evaluation only.

**Evaluation Method:**  
The generated tests will be evaluated using execution-based metrics such as code coverage and task-specific TestEval measures.

User Story Refinement
Input → Original User Story
Output → Refined User Story
Evaluation → Quality Rubric

Bug Report Refinement
Input → Original Bug Report
Output → Structured Refined Bug Report
Evaluation → Bug Report Rubric

Test Case Generation
Input → Description + Python Solution
Output → Executable Test Cases
Evaluation → Coverage / TestEval Metrics
