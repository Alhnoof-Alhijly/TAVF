# Human Semantic Evaluation pilot

Use rubric v1.1. Judge each output independently against its source.
No ratings have been assigned. A/B identities remain blinded.

## Pilot pair 1: ca9c2af1e74dc2131b12d40d00a51da6

Task: user_story_refinement

### Original source input

original_text:

As a Cornell faculty member, I want to see clearly what reuse rights I have to files discovered in the repository, so that I know how I can reuse them.

### Output A

As a Cornell faculty member, I want to see clearly what reuse rights I have for files discovered in the repository, so that I know how I can reuse them.

### Output B

As a Cornell faculty member, I want to clearly see the reuse rights for files discovered in the repository, so that I know how I can reuse them.

## Pilot pair 2: fd3b17a7045d845dbc0e23362043c517

Task: bug_report_refinement

### Original source input

original_text:

created attachment 9162412
expected_candidate_list.png

user agent: mozilla/5.0 (windows nt 10.0; win64; x64; rv:79.0) gecko/20100101 firefox/79.0

steps to reproduce:

1. enable chinese (traditional) cangjie ime
2. place focus on any text input element on webpage (e.g. the search box on bugzilla)
3. enable cangjie ime
4. type "竹戈" ("h" + "i"), then press spacebar


actual results:

"么" appears with a dashed underline, but the candidate list is not visible.


expected results:

"么" should appear with a dashed underline, and a candidate list with at least "么" and "鬼" as options. (see attachment for an example.)

### Output A

Summary  
When using Chinese (Traditional) Cangjie IME in Firefox 79 on Windows 10, typing “竹戈” (`h` + `i`) and pressing spacebar shows “么” with a dashed underline, but no candidate list is displayed.

Steps  
1. Enable Chinese (Traditional) Cangjie IME.  
2. Place focus on any text input element on a webpage (e.g. the search box on Bugzilla).  
3. Enable Cangjie IME.  
4. Type “竹戈” (`h` + `i`), then press the spacebar.  

Expected  
“么” should appear with a dashed underline, and a candidate list should be visible with at least “么” and “鬼” as options. (See attachment for an example.)

Actual  
“么” appears with a dashed underline, but the candidate list is not visible.

### Output B

## Summary
When using the Chinese (Traditional) Cangjie IME in Firefox 79 on Windows 10, typing `竹戈` (`h` + `i`) and pressing Spacebar causes `么` to appear with a dashed underline, but the candidate list does not appear.

## Steps to Reproduce
1. Enable Chinese (Traditional) Cangjie IME.
2. Place focus on any text input element on a webpage (e.g. the search box on Bugzilla).
3. Enable Cangjie IME.
4. Type `竹戈` (`h` + `i`), then press Spacebar.

## Expected Behavior
`么` should appear with a dashed underline, and a candidate list with at least `么` and `鬼` as options should be visible. (See attachment for an example.)

## Actual Behavior
`么` appears with a dashed underline, but the candidate list is not visible.

## Technical Context
- Attachment: `9162412`
- File: `expected_candidate_list.png`
- User agent: `mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0`
