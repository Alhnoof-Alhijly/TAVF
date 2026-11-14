# Blinded human-evaluation samples

No ratings have been assigned. A/B order varies independently by sample.

## Sample 1: ca9c2af1e74dc2131b12d40d00a51da6

Task: user_story_refinement

### Original input

original_text:

As a Cornell faculty member, I want to see clearly what reuse rights I have to files discovered in the repository, so that I know how I can reuse them.

### Output A

As a Cornell faculty member, I want to see clearly what reuse rights I have for files discovered in the repository, so that I know how I can reuse them.

### Output B

As a Cornell faculty member, I want to clearly see the reuse rights for files discovered in the repository, so that I know how I can reuse them.

## Sample 2: fd3b17a7045d845dbc0e23362043c517

Task: bug_report_refinement

### Original input

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

## Sample 3: 7f8439ca8847a774b79f98f51e58b604

Task: user_story_refinement

### Original input

original_text:

As a site visitor, I want to see a list of all upcoming Events, so that I can decide if I want to attend any.

### Output A

As a site visitor, I want to see a list of all upcoming events, so that I can decide whether I want to attend any.

### Output B

As a site visitor, I want to see a list of all upcoming Events, so that I can decide if I want to attend any.

## Sample 4: 74cbc8b2b3f91505c115bff5eff5ca26

Task: user_story_refinement

### Original input

original_text:

As a developer, I want to have an easy way to read data from health sensors the user is wearing.

### Output A

As a developer, I want an easy way to read data from health sensors that the user is wearing, so that I can access the sensor data.

### Output B

As a developer, I want to have an easy way to read data from health sensors the user is wearing, so that Not provided.

## Sample 5: 164f3dca62b65955f3422348db72357d

Task: user_story_refinement

### Original input

original_text:

As a researcher, I want to record research publications in the institutional repository or CRIS with DMP records, so that I can generate reports of research output resulting from a project.

### Output A

As a researcher, I want to record research publications in the institutional repository or CRIS with DMP records, so that I can generate reports of research output resulting from a project.

### Output B

As a researcher, I want to record research publications in the institutional repository or CRIS with DMP records, so that I can generate reports of research output resulting from a project.

## Sample 6: d8f30b8734c2901ab7bd86bf17cbc410

Task: user_story_refinement

### Original input

original_text:

As a trainingcoordinator, I want to have an admin view that helps track registration status for each attendee so that, so that we can see if attendend, refunded, no show.

### Output A

As a training coordinator, I want an admin view that helps track registration status for each attendee, so that we can see if they attended, were refunded, or were a no-show.

### Output B

As a training coordinator, I want an admin view to track each attendee’s registration status so that we can see whether they attended, were refunded, or were a no-show.

## Sample 7: 935c8b9fef69ad42af5f3eed31a9387f

Task: bug_report_refinement

### Original input

original_text:

steps to reproduce:
 1. enable webrender.
 2. open a background tab that's slow to paint, for example https://static.mozilla.com/moco/en-us/images/mozilla_eoy_2013_en.svg .
 3. switch to that tab.

expected results:
after 400ms, the ui should update to visually select the clicked tab and show a white tab with a spinner in the center. once the tab has finished painting, the spinner should go away and the actual tab contents should be shown.
the browser ui should be responsive while the tab is painting, and it should be possible to switch back and forth tabs, or to other tabs entirely.

actual results:
the whole ui "hangs", and the tab bar is inoperable, until rasterization has completed. the only thing you can do while the tab is painting is to scroll the original tab.

### Output A

## Summary
When WebRender is enabled, switching to a background tab that is slow to paint causes the entire browser UI to hang until rasterization completes.

## Steps to Reproduce
1. Enable WebRender.
2. Open a background tab that is slow to paint, for example: `https://static.mozilla.com/moco/en-us/images/mozilla_eoy_2013_en.svg`.
3. Switch to that tab.

## Expected Behavior
After 400ms, the UI should update to visually select the clicked tab and show a white tab with a spinner in the center. Once the tab has finished painting, the spinner should go away and the actual tab contents should be shown.

The browser UI should remain responsive while the tab is painting, and it should be possible to switch back and forth between tabs, or to other tabs entirely.

## Actual Behavior
The whole UI "hangs," and the tab bar is inoperable until rasterization has completed. The only thing you can do while the tab is painting is scroll the original tab.

## Technical Context
- WebRender is enabled.
- The issue occurs when opening and switching to a background tab that is slow to paint.
- Example URL: `https://static.mozilla.com/moco/en-us/images/mozilla_eoy_2013_en.svg`.
- The behavior is observed while rasterization is in progress.

### Output B

Summary  
UI hangs when switching to a background tab that is slow to paint with WebRender enabled; tab bar becomes inoperable until rasterization completes.

Steps  
1. Enable WebRender.  
2. Open a background tab that is slow to paint, for example https://static.mozilla.com/moco/en-us/images/mozilla_eoy_2013_en.svg.  
3. Switch to that tab.

Expected  
After 400 ms, the UI should update to visually select the clicked tab and show a white tab with a spinner in the center. Once the tab has finished painting, the spinner should go away and the actual tab contents should be shown. The browser UI should be responsive while the tab is painting, and it should be possible to switch back and forth between tabs, or to other tabs entirely.

Actual  
The whole UI "hangs", and the tab bar is inoperable until rasterization has completed. The only thing you can do while the tab is painting is scroll the original tab.

## Sample 8: 68a0bd8a961951489820e20442a46179

Task: bug_report_refinement

### Original input

original_text:

created attachment 9003960
screenshots.png

user agent: mozilla/5.0 (macintosh; intel mac os x 10.13; rv:63.0) gecko/20100101 firefox/63.0
build id: 20180824222409

steps to reproduce:

1. selecting "all cookies (may causes website to break)" or "all third-party cookies" option in the privacy preferences.
2. go to http://www.asahi.com/ajw/.
3. show identity popup panel.


actual results:

"third-party cookies" section in the identity popup panel shows "add blocking…".


expected results:

"third-party cookies" section in the identity popup panel shows "blocked".

### Output A

## Summary
When either **“all cookies (may causes website to break)”** or **“all third-party cookies”** is selected in privacy preferences, the **third-party cookies** section in the identity popup panel displays **“add blocking…”** instead of **“blocked”**.

## Steps to Reproduce
1. Select **“all cookies (may causes website to break)”** or **“all third-party cookies”** in the privacy preferences.
2. Go to **http://www.asahi.com/ajw/**.
3. Show the identity popup panel.

## Expected Behavior
The **third-party cookies** section in the identity popup panel should show **“blocked”**.

## Actual Behavior
The **third-party cookies** section in the identity popup panel shows **“add blocking…”**.

## Technical Context
- Attachment: **9003960** (`screenshots.png`)
- User agent: **mozilla/5.0 (macintosh; intel mac os x 10.13; rv:63.0) gecko/20100101 firefox/63.0**
- Build ID: **20180824222409**

### Output B

Summary  
When privacy preferences are set to block cookies, the identity popup panel shows incorrect text in the “third-party cookies” section.

Steps  
1. Select “all cookies (may causes website to break)” or “all third-party cookies” in the privacy preferences.  
2. Go to http://www.asahi.com/ajw/.  
3. Show the identity popup panel.  

Expected  
The “third-party cookies” section in the identity popup panel shows “blocked”.

Actual  
The “third-party cookies” section in the identity popup panel shows “add blocking…”.

## Sample 9: 2f90e1bf0d457c2258d4cab265dd854e

Task: bug_report_refinement

### Original input

original_text:

**steps to reproduce**
1. open the console
2. in the settings panel, ensure the "enable timestamps" option is checked
3. evaluate the following: `await new promise(res => settimeout(() => res("evaluation result"), 5000))`

**expected results**

after 5s, the "evaluation result" message should be displayed, with a timestamp of command timestamp +~ 5s (i.e. if command timestamp is 15:00:00.000, the result should have a timestamp of something around 15:00:05.000)

**actual results**

the timestamp of the evaluation result has a timestamp which is roughly the same as the command.

---

### Output A

## Summary
When running an asynchronous console evaluation with timestamps enabled, the evaluation result is displayed with a timestamp that is roughly the same as the command timestamp instead of being approximately 5 seconds later.

## Steps to Reproduce
1. Open the console.
2. In the settings panel, ensure the **"enable timestamps"** option is checked.
3. Evaluate the following:
   ```javascript
   await new promise(res => settimeout(() => res("evaluation result"), 5000))
   ```

## Expected Behavior
After 5 seconds, the **"evaluation result"** message should be displayed with a timestamp approximately 5 seconds after the command timestamp.

Example: if the command timestamp is `15:00:00.000`, the result should have a timestamp around `15:00:05.000`.

## Actual Behavior
The timestamp of the evaluation result is roughly the same as the command timestamp.

## Technical Context
- Console timestamps are enabled.
- The evaluated expression uses an asynchronous promise resolution after 5000 ms.
- Not provided.

### Output B

Summary

Timestamp for an awaited evaluation result is shown as roughly the same time as the command instead of about 5 seconds later when timestamps are enabled.

Steps

1. Open the console.
2. In the settings panel, ensure the "enable timestamps" option is checked.
3. Evaluate the following: `await new promise(res => settimeout(() => res("evaluation result"), 5000))`

Expected

After 5 seconds, the "evaluation result" message should be displayed with a timestamp of command timestamp + approximately 5 seconds (for example, if the command timestamp is 15:00:00.000, the result should have a timestamp around 15:00:05.000).

Actual

The timestamp of the evaluation result is roughly the same as the command timestamp.

## Sample 10: b4ca39ca30109707d3ce573cc8826d95

Task: bug_report_refinement

### Original input

original_text:

created attachment 9057568
image.png

**[affected versions]:**
- firefox nightly 68.0a1, build id 20190409221047
- firefox beta 67.b9, build id 20190408123043
- firefox release 66.0.3, build id 20190409155332

**[affected platforms]:**
- all windows
- all mac
- all linux

**[steps to reproduce]:**
1. start the browser with a clean new profile and open a new tab.
2. resize the browser window to 1/4 size horizontally.
3. observe the icon to the left of the "try firefox with the bookmarks, history and passwords from another browser." message.

**[expected results]:**
- the icon is fully visible.

**[actual results]:**
- the left and right parts of the icon are cut.

**[regression range]:**
 6:20.88 info: last good revision: 10fab7177ee397815f7b1e0b2c51437466e62268
 6:20.88 info: first bad revision: a6a21ea56a9c8f50a7f3dea145050985e7c4c0a5
 6:20.88 info: pushlog:
https://hg.mozilla.org/integration/autoland/pushloghtml?fromchange=10fab7177ee397815f7b1e0b2c51437466e62268&tochange=a6a21ea56a9c8f50a7f3dea145050985e7c4c0a5

looks like this was introduced by bug 1374540.

**[notes]:**
- attached a screenshot of the issue.

### Output A

Summary  
Icon to the left of the “try firefox with the bookmarks, history and passwords from another browser.” message is clipped when the browser window is resized narrow. A screenshot was attached (attachment 9057568, image.png). Regression range indicates this may have been introduced by bug 1374540.

Steps  
1. Start the browser with a clean new profile and open a new tab.
2. Resize the browser window to 1/4 size horizontally.
3. Observe the icon to the left of the “try firefox with the bookmarks, history and passwords from another browser.” message.

Expected  
The icon is fully visible.

Actual  
The left and right parts of the icon are cut.

Affected versions  
- Firefox Nightly 68.0a1, build id 20190409221047
- Firefox Beta 67.b9, build id 20190408123043
- Firefox Release 66.0.3, build id 20190409155332

Affected platforms  
- All Windows
- All Mac
- All Linux

Regression range  
- Last good revision: 10fab7177ee397815f7b1e0b2c51437466e62268
- First bad revision: a6a21ea56a9c8f50a7f3dea145050985e7c4c0a5
- Pushlog: https://hg.mozilla.org/integration/autoland/pushloghtml?fromchange=10fab7177ee397815f7b1e0b2c51437466e62268&tochange=a6a21ea56a9c8f50a7f3dea145050985e7c4c0a5

### Output B

**Summary**  
When Firefox is opened with a clean new profile and the browser window is resized to about one-quarter width, the icon to the left of the message “try firefox with the bookmarks, history and passwords from another browser.” is partially cut off.

**Steps to Reproduce**  
1. Start the browser with a clean new profile and open a new tab.
2. Resize the browser window to 1/4 size horizontally.
3. Observe the icon to the left of the “try firefox with the bookmarks, history and passwords from another browser.” message.

**Expected Behavior**  
The icon is fully visible.

**Actual Behavior**  
The left and right parts of the icon are cut off.

**Technical Context**  
- Affected versions:
  - Firefox Nightly 68.0a1, build id 20190409221047
  - Firefox Beta 67.b9, build id 20190408123043
  - Firefox Release 66.0.3, build id 20190409155332
- Affected platforms:
  - all Windows
  - all Mac
  - all Linux
- Regression range:
  - Last good revision: 10fab7177ee397815f7b1e0b2c51437466e62268
  - First bad revision: a6a21ea56a9c8f50a7f3dea145050985e7c4c0a5
  - Pushlog: https://hg.mozilla.org/integration/autoland/pushloghtml?fromchange=10fab7177ee397815f7b1e0b2c51437466e62268&tochange=a6a21ea56a9c8f50a7f3dea145050985e7c4c0a5
- Note: Looks like this was introduced by bug 1374540.
- Screenshot attached: image.png (attachment 9057568)

## Sample 11: 4cc73cbdf57538753bc1c56cab6e5537

Task: user_story_refinement

### Original input

original_text:

As a site member, I want to fill out an application to become a Certified Scrum Practitioner, so that I can earn that designation.

### Output A

As a site member, I want to complete an application to become a Certified Scrum Practitioner, so that I can earn that designation.

### Output B

As a site member, I want to fill out an application to become a Certified Scrum Practitioner, so that I can earn that designation.

## Sample 12: 376e0b2ac6cefb923012a6aa586c21e1

Task: user_story_refinement

### Original input

original_text:

As an Archivist, I don't want to inadvertently overwrite someone else's changes to a record that I'm editing.

### Output A

As an Archivist, I want to avoid inadvertently overwriting someone else's changes to a record I am editing, so that I do not lose their updates.

### Output B

As an Archivist, I want to avoid inadvertently overwriting someone else's changes to a record that I am editing, so that I do not lose their updates.

## Sample 13: 3990af27639f6342fd55ce5fd29eba72

Task: user_story_refinement

### Original input

original_text:

As a depositor, I want to deposit arbitrarily large files, so that I am not limited in what files I can and cannot deposit.

### Output A

As a depositor, I want to deposit arbitrarily large files, so that I am not limited in the files I can deposit.

### Output B

As a depositor, I want to deposit arbitrarily large files, so that I am not limited in what files I can and cannot deposit.

## Sample 14: 1892a86c0fac2b38805c400075544ec6

Task: user_story_refinement

### Original input

original_text:

As an API User, I want to be able to get a set of monetary measures transferred to different currencies, So that I can use this in scenarios that might enable comparison by normalisation.

### Output A

As an API User, I want to get a set of monetary measures transferred to different currencies, so that I can use this in scenarios that might enable comparison by normalisation.

### Output B

As an API user, I want to retrieve a set of monetary measures converted into different currencies, so that I can use them in scenarios that enable comparison by normalization.

## Sample 15: 9cfde533dc65a3308bba5d33061410f3

Task: bug_report_refinement

### Original input

original_text:

build id 	20180907225622
user agent 	mozilla/5.0 (windows nt 10.0; win64; x64; rv:64.0) gecko/20100101 firefox/64.0

reproducible: always

steps to reproduce:
1 open about:addons > extensions or themes or plugin

actual results:
gear icon instead of dropdown marker

expected results:
it should be dropdown marker 



regressed by: bug 1487765

### Output A

Summary
Build ID: 20180907225622  
User Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0  
Reproducibility: Always  
Regressed by: bug 1487765

Steps
1. Open about:addons > Extensions or Themes or Plugin.

Expected
Dropdown marker should be shown.

Actual
Gear icon is shown instead of the dropdown marker.

### Output B

## Summary
In build ID 20180907225622, the gear icon is shown instead of the dropdown marker in about:addons > Extensions/Themes/Plugins. This is reproducible always and was regressed by bug 1487765.

## Steps to Reproduce
1. Open about:addons.
2. Go to Extensions, Themes, or Plugins.

## Expected Behavior
It should display a dropdown marker.

## Actual Behavior
A gear icon is displayed instead of the dropdown marker.

## Technical Context
- Build ID: 20180907225622
- User agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0
- Reproducibility: Always
- Regressed by: bug 1487765

## Sample 16: 3838fa1d43743d8758764bf394355527

Task: user_story_refinement

### Original input

original_text:

As an admin, I want to be able to read users' feedback and complaints, so that we can add more features and keep improving the service we provide to them.

### Output A

As an admin, I want to read users' feedback and complaints, so that we can improve the service we provide and add more features.

### Output B

As an admin, I want to read users' feedback and complaints, so that we can add more features and keep improving the service we provide to them.

## Sample 17: 27948206641f1be5c3a3c88372e945e0

Task: bug_report_refinement

### Original input

original_text:

created attachment 8746506
example page

user agent: mozilla/5.0 (windows nt 6.3; wow64) applewebkit/537.36 (khtml, like gecko) chrome/49.0.2623.112 safari/537.36

steps to reproduce:

1. open any page with an iframe.
2. navigate into any element into iframe.
3. try to add rule to it with 'add new rule' button with plus sign symbol.


actual results:

rule was not added (though style was appended to the end of the page).


expected results:

rule with appropriate selector based on element tag/id/class was added.

### Output A

## Summary
When using the **Add New Rule** button (plus sign) on an element inside an iframe, the rule is not added correctly. A style is appended to the end of the page instead, but no rule is created with the appropriate selector.

## Steps to Reproduce
1. Open any page with an iframe.
2. Navigate into any element inside the iframe.
3. Try to add a rule to it using the **Add New Rule** button with the plus sign symbol.

## Expected Behavior
A rule with the appropriate selector based on the element’s tag, id, or class should be added.

## Actual Behavior
The rule was not added. A style was appended to the end of the page instead.

## Technical Context
- Attachment: 8746506 (example page)
- User agent: Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36

### Output B

### Summary
When using the **Add New Rule** button on an element inside an iframe, the rule is not added correctly. An attachment and example page were provided.

**User agent:** mozilla/5.0 (windows nt 6.3; wow64) applewebkit/537.36 (khtml, like gecko) chrome/49.0.2623.112 safari/537.36

### Steps
1. Open any page with an iframe.
2. Navigate into any element inside the iframe.
3. Try to add a rule to it using the **Add New Rule** button with the plus sign symbol.

### Expected
A rule with the appropriate selector based on the element’s tag, id, or class should be added.

### Actual
The rule was not added, though the style was appended to the end of the page.

## Sample 18: 38336541b30207e31bc04c840190cbe8

Task: user_story_refinement

### Original input

original_text:

As a PI, I want to know how secure data is, so that I can ensure legal compliance.

### Output A

As a PI, I want to know how secure data is, so that I can ensure legal compliance.

### Output B

As a PI, I want to know how secure data is, so that I can ensure legal compliance.

## Sample 19: 3375b2e96a5de37d9f58978990f52731

Task: bug_report_refinement

### Original input

original_text:

from github: https://github.com/mozilla-mobile/fenix/issues/16748.

> [comment]: # (please do your best to search for duplicate issues before filing a new issue so we can keep our issue board clean)
> [comment]: # (every issue should have the exact bug and steps to reproduce described in it. please do not file feedback list tickets as it is difficult to parse them and address their individual points)
> [comment]: # (read https://github.com/mozilla-mobile/fenix#i-want-to-file-an-issue for more information)
> 
> ## steps to reproduce
> 
> 1. open https://bbs.kafan.cn/forum.php?mobile=no
> 
> 2. type something in the search box, then press the enter key on the keyboard, not a button on the web page, it will pop up a blank page
> ![img_20201126_140327](https://user-images.githubusercontent.com/3154109/100314106-e1b00d80-2ff0-11eb-9021-cef23366daf6.jpg)
> 
> 3. the first page died
> 
> 
> ### expected behavior
> 
> 
> ### actual behavior
> 
> 
> ### device information
> 
> * android device: ?
> * fenix version: ?
>  nightly 201123 17:01 (build #2015777355)
> ac: 68.0.20201122190139, 52be4ca37
> gv: 85.0a1-20201122093438
> as: 67.0.0
> 

change performed by the [move to bugzilla add-on](https://addons.mozilla.org/en-us/firefox/addon/move-to-bugzilla/).

### Output A

## Summary
When using Firefox Fenix on the site `https://bbs.kafan.cn/forum.php?mobile=no`, entering text in the search box and pressing the keyboard Enter key causes a blank page to appear. The first page then dies.

## Steps to Reproduce
1. Open `https://bbs.kafan.cn/forum.php?mobile=no`.
2. Type something in the search box.
3. Press the Enter key on the keyboard, not a button on the web page.
4. A blank page appears.
5. The first page dies.

## Expected Behavior
Not provided.

## Actual Behavior
A blank page pops up after pressing Enter in the search box, and the first page dies.

## Technical Context
- Report source: GitHub issue `mozilla-mobile/fenix#16748`
- Device information:
  - Android device: Not provided
  - Fenix version: Not provided
- Build information:
  - Nightly 201123 17:01 (build #2015777355)
  - ac: `68.0.20201122190139, 52be4ca37`
  - gv: `85.0a1-20201122093438`
  - as: `67.0.0`
- Note: Change performed by the [move to bugzilla add-on](https://addons.mozilla.org/en-US/firefox/addon/move-to-bugzilla/).

### Output B

### Summary
Opening the following page and using the keyboard Enter key to submit a search causes a blank page to appear, and the first page dies:

https://bbs.kafan.cn/forum.php?mobile=no

Device information:
- android device: Not provided
- fenix version: nightly 201123 17:01 (build #2015777355)
- ac: 68.0.20201122190139, 52be4ca37
- gv: 85.0a1-20201122093438
- as: 67.0.0

### Steps
1. Open https://bbs.kafan.cn/forum.php?mobile=no
2. Type something in the search box.
3. Press the Enter key on the keyboard, not a button on the web page.
4. A blank page appears.
5. The first page died.

### Expected
Not provided

### Actual
A blank page appears after pressing Enter in the search box, and the first page dies.

## Sample 20: 2fd4ce0503c5d1dd1b0224af6cd32f2c

Task: user_story_refinement

### Original input

original_text:

As a Staff member, I want to Send or Post Citations and Fines, so that I can successfully send the Notice Of Violation document to the property owner and log information about the action.

### Output A

As a Staff member, I want to send or post citations and fines, so that I can successfully send the Notice Of Violation document to the property owner and log information about the action.

### Output B

As a staff member, I want to send or post citations and fines, so that I can send the Notice of Violation document to the property owner and log information about the action.

## Sample 21: 42d9f95250073c2a5410cf591dcc06ad

Task: user_story_refinement

### Original input

original_text:

As a data scientist, I want to be able to create a dataset instance of an existing dataset type without writing code.

### Output A

As a data scientist, I want to create a dataset instance of an existing dataset type without writing code, so that Not provided.

### Output B

As a data scientist, I want to create a dataset instance from an existing dataset type without writing code, so that I can do it without programming.

## Sample 22: b14c1dbe26c26109935d8dc08a7a2dce

Task: bug_report_refinement

### Original input

original_text:

created attachment 9139383
megabar popup bug.png

user agent: mozilla/5.0 (windows nt 10.0; win64; x64; rv:75.0) gecko/20100101 firefox/75.0

steps to reproduce:

1) apply a custom theme that specifies a dark `popup` background color and light `popup_text` color -- e.g.:
https://addons.mozilla.org/en-us/firefox/addon/charcoal-dark-lite/

2) focus megabar and start typing to expand the autocomplete popup menu.


actual results:

a) autocomplete popup apparently takes the theme's `toolbar_field` background and `toolbar_field_text` values, rather than `popup` and `popup_text` (curiously, this does not affect the native dark theme);

b) worse, legibility is degraded for the autocomplete suggestion items' url and action text colors, which are still apparently auto-calculated from the theme's declared popup colors, rather than the actual applied colors -- cf.:
https://hacks.mozilla.org/2018/07/dark-theme-darkening-better-theming-for-firefox-quantum/

c) theme key documentation does not specify any other way to deliberately theme those `ac-url` and `ac-action` text colors:
https://developer.mozilla.org/en-us/docs/mozilla/add-ons/webextensions/manifest.json/theme


expected results:

megabar autocomplete popup menu should apply theme's declared `popup` and `popup_text` colors; however, in case that may be deemed a wontfix, then themes need some way to specify `ac-url` and `ac-action` text colors.

### Output A

Summary  
Megabar autocomplete popup in Firefox 75.0 on Windows 10 does not appear to use a custom theme’s `popup` and `popup_text` colors correctly, and the suggestion URL/action text colors become hard to read when a dark popup theme is applied. Attachment: 9139383 (`megabar popup bug.png`).

Steps  
1. Apply a custom theme that specifies a dark `popup` background color and light `popup_text` color, for example: https://addons.mozilla.org/en-us/firefox/addon/charcoal-dark-lite/  
2. Focus megabar and start typing to expand the autocomplete popup menu.

Expected  
Megabar autocomplete popup menu should apply the theme’s declared `popup` and `popup_text` colors; however, if that is deemed a wontfix, themes need some way to specify `ac-url` and `ac-action` text colors.

Actual  
a. Autocomplete popup apparently takes the theme’s `toolbar_field` background and `toolbar_field_text` values, rather than `popup` and `popup_text` (this does not affect the native dark theme).  
b. Legibility is degraded for the autocomplete suggestion items’ URL and action text colors, which are still apparently auto-calculated from the theme’s declared popup colors rather than the actual applied colors; cf. https://hacks.mozilla.org/2018/07/dark-theme-darkening-better-theming-for-firefox-quantum/  
c. Theme key documentation does not specify any other way to deliberately theme those `ac-url` and `ac-action` text colors: https://developer.mozilla.org/en-us/docs/mozilla/add-ons/webextensions/manifest.json/theme

### Output B

## Summary
Megabar autocomplete popup does not appear to use a theme’s declared `popup` and `popup_text` colors when a custom dark theme is applied. Instead, it appears to use `toolbar_field` and `toolbar_field_text`, which affects readability of autocomplete suggestion URL and action text colors.

## Steps to Reproduce
1. Apply a custom theme that specifies a dark `popup` background color and light `popup_text` color, for example:
   - https://addons.mozilla.org/en-us/firefox/addon/charcoal-dark-lite/
2. Focus megabar and start typing to expand the autocomplete popup menu.

## Expected Behavior
Megabar autocomplete popup menu should apply the theme’s declared `popup` and `popup_text` colors.

If that is deemed a wontfix, then themes need some way to specify `ac-url` and `ac-action` text colors.

## Actual Behavior
a) Autocomplete popup apparently takes the theme’s `toolbar_field` background and `toolbar_field_text` values, rather than `popup` and `popup_text` (this does not affect the native dark theme).

b) Legibility is degraded for the autocomplete suggestion items’ URL and action text colors, which are still apparently auto-calculated from the theme’s declared popup colors rather than the actual applied colors, cf.:
   - https://hacks.mozilla.org/2018/07/dark-theme-darkening-better-theming-for-firefox-quantum/

c) Theme key documentation does not specify any other way to deliberately theme those `ac-url` and `ac-action` text colors:
   - https://developer.mozilla.org/en-us/docs/mozilla/add-ons/webextensions/manifest.json/theme

## Technical Context
- Attachment: 9139383 (`megabar popup bug.png`)
- User agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0

## Sample 23: 173a92e50b39b99c3c8b2ca9331f09e7

Task: bug_report_refinement

### Original input

original_text:

steps to reproduce:
1. browse <https://www.gpki.go.jp/>. ssl error page will be shown.
2. click "advanced".
3. click "sec_error_unknown_issuer".

actual result:
nothing will be shown after "certificate chain".

expected result:
certificate chain should be shown.

this makes troubleshooting nearly impossible in some bugs.

### Output A

## Summary
When browsing <https://www.gpki.go.jp/>, an SSL error page is shown, and selecting the certificate details does not display the full certificate chain. This makes troubleshooting nearly impossible in some bugs.

## Steps to Reproduce
1. Browse to <https://www.gpki.go.jp/>.
2. An SSL error page will be shown.
3. Click **"advanced"**.
4. Click **"sec_error_unknown_issuer"**.

## Expected Behavior
The certificate chain should be shown.

## Actual Behavior
Nothing is shown after **"certificate chain"**.

## Technical Context
- Site: <https://www.gpki.go.jp/>
- Error page: SSL error page
- Error item selected: **"sec_error_unknown_issuer"**
- Additional context: This makes troubleshooting nearly impossible in some bugs.

### Output B

Summary  
Certificate chain is not shown after selecting `sec_error_unknown_issuer` from the SSL error page on <https://www.gpki.go.jp/>, making troubleshooting nearly impossible in some bugs.

Steps  
1. Browse <https://www.gpki.go.jp/>. An SSL error page will be shown.  
2. Click "advanced".  
3. Click "sec_error_unknown_issuer".  

Expected  
Certificate chain should be shown.  

Actual  
Nothing will be shown after "certificate chain".

## Sample 24: 45f5c801ef9b37c3b3085d9b7a978a5e

Task: bug_report_refinement

### Original input

original_text:

user agent: mozilla/5.0 (windows nt 10.0; win64; x64; rv:74.0) gecko/20100101 firefox/74.0

steps to reproduce:

open a webpage with a 3d canvas (webgl context) on nightly, and resize the page dynamically.

test page :  https://threejs.org/examples/#webgl_materials_standard

(setup: nightly on windows 10, nvidia rtx 2060 card, and preview nightly on android 10, oneplus 6)


actual results:

the content of the canvas, which previously resized correctly, now renders on a streched zone instead of adapting the ratio as it used to. 


the size of the canvas is ok, but the rendered portion is stretched. it looks like a size setting problem, or more likely a problem when someone sets the webgl context viewport.

this bug happens on desktop nightly and on preview nighlty but not on regular stable-branch firefox.


expected results:

the aspect ratio of the drawn area should have adapted to the new canvas size.

(see stable firefox or chrome to compare)

### Output A

### Summary
WebGL canvas content becomes stretched after dynamically resizing a 3D canvas on Nightly builds. The canvas element itself resizes correctly, but the rendered content does not preserve the aspect ratio. This occurs on desktop Nightly and Preview Nightly, but not on stable Firefox.

### Steps
1. Open a webpage with a 3D canvas using a WebGL context on Nightly.
2. Dynamically resize the page.
3. Test page: https://threejs.org/examples/#webgl_materials_standard
4. Environment/setup: Nightly on Windows 10 with an NVIDIA RTX 2060, and Preview Nightly on Android 10 with a OnePlus 6.

### Expected
The aspect ratio of the drawn area should adapt to the new canvas size.

### Actual
The canvas size is correct, but the rendered content is drawn in a stretched area instead of adapting its ratio as before. It appears to be a size-setting issue or, more likely, an issue when setting the WebGL context viewport. The bug occurs on desktop Nightly and Preview Nightly, but not on the regular stable Firefox branch.

### Output B

## Summary
On Firefox Nightly, resizing a webpage with a 3D canvas (WebGL context) causes the rendered content to stretch instead of preserving the correct aspect ratio. This occurs on desktop Nightly and Preview Nightly, but not on regular stable-branch Firefox.

## Steps to Reproduce
1. Open a webpage with a 3D canvas (WebGL context) on Firefox Nightly.
2. Dynamically resize the page.
3. Test page: https://threejs.org/examples/#webgl_materials_standard

**Setup:**
- Nightly on Windows 10
- NVIDIA RTX 2060 card
- Preview Nightly on Android 10
- OnePlus 6

## Expected Behavior
The aspect ratio of the drawn area should adapt to the new canvas size.

## Actual Behavior
The canvas size is correct, but the rendered portion is stretched instead of adapting its ratio as it used to. The content appears on a stretched zone. It looks like a size setting problem, or more likely a problem when someone sets the WebGL context viewport.

## Technical Context
- User agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0
- Affects Firefox Nightly on desktop and Preview Nightly on Android
- Does not occur on regular stable-branch Firefox
- Comparison mentioned: stable Firefox or Chrome

## Sample 25: 24685a5d56f36506b40df9e27b537dc7

Task: user_story_refinement

### Original input

original_text:

As a DAMS manager, I want to know if application of a library policy to an object or object component has been modified, either manually or automatically.

### Output A

As a DAMS manager, I want to know if the application of a library policy to an object or object component has been modified, either manually or automatically, so that Not provided.

### Output B

As a DAMS manager, I want to know if the application of a library policy to an object or object component has been modified, either manually or automatically, so that I can identify changes to policy application.

## Sample 26: 351eaf15bac7ad44028ec91e392971ca

Task: bug_report_refinement

### Original input

original_text:

user agent: mozilla/5.0 (x11; linux x86_64; rv:56.0) gecko/20100101 firefox/56.0
build id: 20170926190823

steps to reproduce:

tried to load backup created by firefox 55.* from built-in bookmarks manager.


actual results:

"unable to process the backup file" displayed, nothing else happens.


expected results:

bookmark file should be normally imported.

when i create backup from firefox 56, it's imported without issues.

### Output A

## Summary
Firefox 56.0 on Linux x86_64 is unable to process a bookmark backup file created by Firefox 55.x when loading it through the built-in Bookmarks Manager.

## Steps to Reproduce
1. Use Firefox 55.x to create a bookmark backup.
2. In Firefox 56.0, try to load that backup from the built-in Bookmarks Manager.

## Expected Behavior
The bookmark backup file should be imported normally.

## Actual Behavior
A message appears: `"unable to process the backup file"`, and nothing else happens.

Backups created from Firefox 56 import without issues.

## Technical Context
- User agent: `mozilla/5.0 (x11; linux x86_64; rv:56.0) gecko/20100101 firefox/56.0`
- Build ID: `20170926190823`

### Output B

Summary  
Unable to import a Firefox 55.* bookmark backup created from the built-in bookmarks manager into Firefox 56.0.

Steps  
1. Tried to load a backup created by Firefox 55.* from the built-in bookmarks manager.  
2. Created a backup from Firefox 56.0 and imported it successfully.

Expected  
Bookmark file should be normally imported.

Actual  
"unable to process the backup file" is displayed, and nothing else happens.

## Sample 27: 493bc738267bdc9ca3ef8cd7f86b62a4

Task: bug_report_refinement

### Original input

original_text:

user agent: mozilla/5.0 (macintosh; intel mac os x 10_15_4) applewebkit/537.36 (khtml, like gecko) chrome/81.0.4044.138 safari/537.36

steps to reproduce:

try to getimagedata of the red rectangle.

const ctx = canvas.getcontext('2d');
ctx.fillstyle = 'rgb(255, 0, 0)';
ctx.fillrect(0, 0, 100, 100);
const data = ctx.getimagedata(50, 50, 1, 1).data;
console.log(data[0], data[1], data[2]);


https://jsbin.com/jaqaqeboro/edit?js,console,output


actual results:

getimagedata returns incorrect pixel information. for me, it was (252, 13, 27).


expected results:

the expected result is (255, 0, 0).

the same happening with any color i tried.
online demo: https://jsbin.com/jaqaqeboro/edit?js,console,output

### Output A

Summary

On macOS 10.15.4 using Chrome 81.0.4044.138, `CanvasRenderingContext2D.getImageData()` returns incorrect pixel information when reading a solid filled rectangle. The issue occurs for the provided red rectangle example and reportedly with any color tried.

Steps

1. Open the online demo: https://jsbin.com/jaqaqeboro/edit?js,console,output
2. Run the following code:
   ```javascript
   const ctx = canvas.getContext('2d');
   ctx.fillStyle = 'rgb(255, 0, 0)';
   ctx.fillRect(0, 0, 100, 100);
   const data = ctx.getImageData(50, 50, 1, 1).data;
   console.log(data[0], data[1], data[2]);
   ```
3. Check the console output for the returned pixel data.

Expected

`getImageData()` should return the correct pixel information for the filled red rectangle, which is `(255, 0, 0)`.

Actual

`getImageData()` returns incorrect pixel information. In the reported case, the result was `(252, 13, 27)`. The same behavior occurs with any color tried.

### Output B

## Summary
`CanvasRenderingContext2D.getImageData()` returns incorrect pixel information when reading from a filled red rectangle in Chrome 81 on macOS.

## Steps to Reproduce
1. Use the following user agent/environment:
   - Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36
2. Create a 2D canvas context.
3. Fill a rectangle with red:
   ```javascript
   const ctx = canvas.getContext('2d');
   ctx.fillStyle = 'rgb(255, 0, 0)';
   ctx.fillRect(0, 0, 100, 100);
   ```
4. Read pixel data from the rectangle:
   ```javascript
   const data = ctx.getImageData(50, 50, 1, 1).data;
   console.log(data[0], data[1], data[2]);
   ```
5. Reproduce in the online demo:
   - https://jsbin.com/jaqaqeboro/edit?js,console,output

## Expected Behavior
`getImageData(50, 50, 1, 1).data` should return `(255, 0, 0)` for the red rectangle.

## Actual Behavior
`getImageData()` returns incorrect pixel information. In the reported case, it returned `(252, 13, 27)`.

The same behavior occurs with any color tried.

## Technical Context
- User agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36
- Online demo: https://jsbin.com/jaqaqeboro/edit?js,console,output

## Sample 28: fa25939c7b1efa9fb90156514c8d0a11

Task: bug_report_refinement

### Original input

original_text:

user agent: mozilla/5.0 (windows nt 6.1; win64; x64; rv:60.0) gecko/20100101 firefox/60.0 seamonkey/2.57

steps to reproduce:

i updated from 66.0.3 x64 to 67.0 b14, b15 & b16.


actual results:

i've been running 66.0.3 x64 with manual proxy config set up. i have to enter username and password to authenticate through the proxy provider (torguardvpnaccess.com) @ port 6060. "use this proxy server for all protocols" is selected. "proxy dns when using socks v5" is checked.

after first authentication, the authentication dialogue box pops up repeatedly as if not having accepted the initial authentication. it will do this endlessly no matter how many time username and password are entered.

rolling back to 66.0.3 fixes it.


expected results:

after entering username and password to authenticate once, it should not ask ever again.

### Output A

Summary
After updating from Firefox 66.0.3 x64 to Firefox 67.0 beta 14, beta 15, and beta 16, proxy authentication prompts repeat endlessly on a manual proxy configuration that previously worked in 66.0.3 x64.

Steps
1. Update from Firefox 66.0.3 x64 to 67.0 b14, b15, or b16.
2. Use a manual proxy configuration.
3. Configure the proxy provider as torguardvpnaccess.com on port 6060.
4. Enter the proxy username and password when prompted.
5. Ensure "use this proxy server for all protocols" is selected.
6. Ensure "proxy dns when using socks v5" is checked.

Expected
After entering the username and password once to authenticate, the browser should not prompt for authentication again.

Actual
After the first authentication, the authentication dialog box pops up repeatedly as if the initial authentication was not accepted. This continues endlessly no matter how many times the username and password are entered. Rolling back to Firefox 66.0.3 x64 fixes the issue.

### Output B

## Summary
After updating from 66.0.3 x64 to 67.0 b14, b15, and b16, proxy authentication repeatedly prompts for username and password instead of accepting the initial authentication.

## Steps to Reproduce
1. Use Firefox/SeaMonkey 66.0.3 x64 with a manual proxy configuration.
2. Configure the proxy provider as `torguardvpnaccess.com` on port `6060`.
3. Select **Use this proxy server for all protocols**.
4. Check **Proxy DNS when using SOCKS v5**.
5. Update from 66.0.3 x64 to 67.0 b14, b15, or b16.
6. Enter the proxy username and password when the authentication dialog appears.

## Expected Behavior
After entering the username and password once to authenticate through the proxy, the browser should not ask for authentication again.

## Actual Behavior
After the first authentication, the authentication dialog repeatedly appears as if the initial authentication was not accepted. This continues endlessly no matter how many times the username and password are entered. Rolling back to 66.0.3 fixes the issue.

## Technical Context
- User agent: `mozilla/5.0 (windows nt 6.1; win64; x64; rv:60.0) gecko/20100101 firefox/60.0 seamonkey/2.57`
- Affected versions: `67.0 b14`, `67.0 b15`, `67.0 b16`
- Working version: `66.0.3 x64`
- Proxy configuration:
  - Manual proxy config
  - Proxy server: `torguardvpnaccess.com`
  - Port: `6060`
  - **Use this proxy server for all protocols**: selected
  - **Proxy DNS when using SOCKS v5**: checked

## Sample 29: c0919b50f6bc7215e987dc774eda7547

Task: bug_report_refinement

### Original input

original_text:

### steps to reproduce
1. open the firefox application.
2. open the "https://www.rockfm.ro/"
3. tap on play button.
4. observe the behaviour.

### expected behavior
the website is properly loaded. the media playback starts.

### actual behavior
 the tab crashes: "sorry. firefox nightly can't load that page."

device information
firefox version: nightly 115.0a1 from 19.05.2023
android device model: motorola moto g9 plus 
android os version: android 11
any additional information?
this issue is not reproducible on chrome browser.
this issue is also reproducible on: 
https://www.kissfm.ro/, 
https://www.radiozum.md/?utm_source=google&utm_medium=cpc&utm_campaign=g&utm_content=636266551814&utm_term=radio%20online
https://myradioonline.ro/virgin-radio, 
https://www.magicfm.ro/,
 https://www.romania-actualitati.ro/live/

in about:crashes appears: c42d0db9-b2c3-42fa-b8d8-5137586b68b3
                                          <native crash>

### Output A

### Summary
Firefox Nightly crashes when opening certain radio streaming websites and tapping the play button. The issue is not reproducible in Chrome. A crash ID is available in `about:crashes`.

### Steps
1. Open the Firefox application.
2. Open `https://www.rockfm.ro/`.
3. Tap the play button.
4. Observe the behavior.

### Expected
The website is properly loaded, and media playback starts.

### Actual
The tab crashes with: `"sorry. firefox nightly can't load that page."`

Additional technical context:
- Firefox version: Nightly 115.0a1 from 19.05.2023
- Android device model: Motorola Moto G9 Plus
- Android OS version: Android 11
- Not reproducible on Chrome browser
- Also reproducible on:
  - `https://www.kissfm.ro/`
  - `https://www.radiozum.md/?utm_source=google&utm_medium=cpc&utm_campaign=g&utm_content=636266551814&utm_term=radio%20online`
  - `https://myradioonline.ro/virgin-radio`
  - `https://www.magicfm.ro/`
  - `https://www.romania-actualitati.ro/live/`
- `about:crashes` shows: `c42d0db9-b2c3-42fa-b8d8-5137586b68b3` `<native crash>`

### Output B

## Summary
Firefox Nightly crashes when opening and attempting to play media on certain radio websites.

## Steps to Reproduce
1. Open the Firefox application.
2. Open `https://www.rockfm.ro/`.
3. Tap the play button.
4. Observe the behavior.

## Expected Behavior
The website is properly loaded and media playback starts.

## Actual Behavior
The tab crashes with the message: `sorry. firefox nightly can't load that page.`

## Technical Context
- Firefox version: Nightly 115.0a1 from 19.05.2023
- Android device model: Motorola Moto G9 Plus
- Android OS version: Android 11
- Not reproducible on Chrome browser
- Also reproducible on:
  - `https://www.kissfm.ro/`
  - `https://www.radiozum.md/?utm_source=google&utm_medium=cpc&utm_campaign=g&utm_content=636266551814&utm_term=radio%20online`
  - `https://myradioonline.ro/virgin-radio`
  - `https://www.magicfm.ro/`
  - `https://www.romania-actualitati.ro/live/`
- about:crashes entry: `c42d0db9-b2c3-42fa-b8d8-5137586b68b3`
- Crash type: `<native crash>`

## Sample 30: 6d82975c9c2cbd2e8c9ac1e6d86a4bc6

Task: bug_report_refinement

### Original input

original_text:

created attachment 9310658
screencast from 2023-01-04 15-14-23.webm

user agent: mozilla/5.0 (x11; linux x86_64; rv:108.0) gecko/20100101 firefox/108.0

steps to reproduce:

logged in to firefox relay yesterday, then tried to generate a mask today.

(note that the attached screencast shows that a nightly update is available as this was yesterday's version, but i get the same after an update.)


actual results:

i got a 403 error. i was still logged in to my firefox account, but my session on the relay website had apparently expired - i was no longer logged in there.

the "learn more" link just took me to the relay website.


expected results:

i guess firefox could have asked me to log in to relay again? or have a token that is valid for longer?

the error message could also be more helpful, as well as the "learn more" link.

### Output A

## Summary
After being logged in to Firefox Relay yesterday, attempting to generate a mask today resulted in a 403 error. The user was still logged in to their Firefox account, but their Firefox Relay website session had expired.

## Steps to Reproduce
1. Log in to Firefox Relay.
2. Wait until the next day.
3. Try to generate a mask.

## Expected Behavior
Firefox could ask the user to log in to Relay again, or use a token that remains valid longer.  
The error message and the “learn more” link could also be more helpful.

## Actual Behavior
A 403 error was shown. The user was still logged in to their Firefox account, but was no longer logged in to the Relay website because the session had expired. The “learn more” link only took the user to the Relay website.

## Technical Context
- Attachment: 9310658
- Screencast: `2023-01-04 15-14-23.webm`
- User agent: `Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0`
- Note: The screencast shows that a nightly update is available because it was from the previous day’s version, but the same issue occurs after an update.

### Output B

### Summary
Creating a Firefox Relay mask resulted in a 403 error. The user was still logged in to their Firefox account, but the session on the Relay website had expired, so they were no longer logged in there. The attached screencast is from `2023-01-04 15-14-23.webm`. User agent: `mozilla/5.0 (x11; linux x86_64; rv:108.0) gecko/20100101 firefox/108.0`. The screencast shows that a Nightly update was available, but the same issue occurred after updating.

### Steps
1. Logged in to Firefox Relay yesterday.
2. Tried to generate a mask today.

### Expected
Not provided. The reporter suggests Firefox could have prompted for Relay login again or used a longer-lived token, and that the error message and "learn more" link could be more helpful.

### Actual
A 403 error occurred. The user was still logged in to their Firefox account, but their Relay website session had expired and they were no longer logged in there. The "learn more" link only took the user to the Relay website.

## Sample 31: 120b7e3c9339b8e6d0b3243c849e28fd

Task: bug_report_refinement

### Original input

original_text:

created attachment 9364876
untitled.png

user agent: mozilla/5.0 (windows nt 10.0; win64; x64; rv:122.0) gecko/20100101 firefox/122.0

steps to reproduce:

1. use firefox with build id 20231121045833 
2. goto https://bitbucket.org/fargo3d/public/src/ae0fcdc67bb7c83aed85fc9a4d4a2d5061324597/makefile 



actual results:

 in makefile code font not render correctly


expected results:

font should render correctly.

after update it work properly i think it already backout in new version. 
but i want to let you known

### Output A

Summary  
Font rendering in the Makefile code view on Bitbucket does not render correctly in Firefox. Attachment: 9364876 (untitled.png). User agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0.

Steps  
1. Use Firefox with build id 20231121045833.  
2. Go to https://bitbucket.org/fargo3d/public/src/ae0fcdc67bb7c83aed85fc9a4d4a2d5061324597/makefile.  

Expected  
Font should render correctly.

Actual  
In the Makefile code, the font does not render correctly. The reporter noted that after an update it works properly, and suspects it may already have been backed out in a newer version.

### Output B

## Summary
In Firefox build ID `20231121045833`, the code font in the Makefile on a Bitbucket page does not render correctly.

## Steps to Reproduce
1. Use Firefox with build ID `20231121045833`.
2. Go to: `https://bitbucket.org/fargo3d/public/src/ae0fcdc67bb7c83aed85fc9a4d4a2d5061324597/makefile`

## Expected Behavior
The font should render correctly.

## Actual Behavior
In the Makefile, the code font does not render correctly.

## Technical Context
- Attachment: `9364876` (`untitled.png`)
- User agent: `mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0`
- Additional note: After an update, it works properly. The reporter thinks it may already have been backed out in a newer version, but wants to report it.

## Sample 32: a3a48779b313ede6ee437ccd9d29d841

Task: user_story_refinement

### Original input

original_text:

As a Zooniverse admin, I want to perform automatic segmentation or localization of plankton in Plankton Portal.

### Output A

As a Zooniverse admin, I want to perform automatic segmentation or localization of plankton in Plankton Portal, so that Not provided.

### Output B

As a Zooniverse admin, I want to perform automatic segmentation or localization of plankton in Plankton Portal, so that plankton can be identified automatically.

## Sample 33: a576fe30065a916bbede42149b3b0493

Task: bug_report_refinement

### Original input

original_text:

user agent: mozilla/5.0 (macintosh; intel mac os x 10_11_6) applewebkit/537.36 (khtml, like gecko) chrome/64.0.3282.186 safari/537.36

steps to reproduce:

test page:
https://fetch-progress.anthum.com/test/sw-response-with-url-fragments/

urls containing hash/fragment values (e.g. "image.png#value") prevent service workers from responding correctly when new response() constructor is used.  this bug does not occur in ff 58 and was introduced in ff 59.

history of bug discovery:
https://github.com/anthumchris/fetch-progress-indicators/issues/9


actual results:

images with url fragment values do not display when intercepted by service worker


expected results:

images with url fragment values should display.

### Output A

Summary  
URLs containing hash/fragment values (for example, `image.png#value`) prevent service workers from responding correctly when the `Response()` constructor is used. This issue does not occur in Firefox 58 and was introduced in Firefox 59.  
User agent: `mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36`  
Related bug discovery: `https://github.com/anthumchris/fetch-progress-indicators/issues/9`

Steps  
1. Visit the test page: `https://fetch-progress.anthum.com/test/sw-response-with-url-fragments/`
2. Use a URL containing a hash/fragment value, such as `image.png#value`.
3. Observe the service worker response behavior.

Expected  
Images with URL fragment values should display.

Actual  
Images with URL fragment values do not display when intercepted by the service worker.

### Output B

## Summary
URLs containing hash/fragment values (for example, `image.png#value`) prevent service workers from responding correctly when the new `Response()` constructor is used. Images with URL fragment values do not display when intercepted by a service worker. This bug does not occur in Firefox 58 and was introduced in Firefox 59.

## Steps to Reproduce
1. Open the test page:
   https://fetch-progress.anthum.com/test/sw-response-with-url-fragments/
2. Use URLs containing hash/fragment values, such as `image.png#value`.
3. Observe the behavior when the request is intercepted by a service worker.

## Expected Behavior
Images with URL fragment values should display.

## Actual Behavior
Images with URL fragment values do not display when intercepted by a service worker.

## Technical Context
- User agent: `mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36`
- Test page: `https://fetch-progress.anthum.com/test/sw-response-with-url-fragments/`
- History of bug discovery: `https://github.com/anthumchris/fetch-progress-indicators/issues/9`
- The issue occurs when service workers respond using the new `Response()` constructor.
- Not provided: additional reproduction details beyond the test page and example URL.

## Sample 34: b31bf637a3481a49e1bd1dc7cc878dc1

Task: user_story_refinement

### Original input

original_text:

As a CSM, I want to have my name listed in the registry without becoming a member of the site, so that employers or others can verify my certification.

### Output A

As a CSM, I want my name listed in the registry without becoming a member of the site, so that employers or others can verify my certification.

### Output B

As a CSM, I want my name listed in the registry without becoming a member of the site, so that employers or others can verify my certification.

## Sample 35: a70ec0fde4bc701ac51fd1b1e7868b90

Task: user_story_refinement

### Original input

original_text:

As a Research Information manager, I want to segment the view and download statistics by country and sector so that impact of datasets outside academia can be demonstrated.

### Output A

As a Research Information manager, I want to segment the view and download statistics by country and sector, so that the impact of datasets outside academia can be demonstrated.

### Output B

As a Research Information manager, I want to segment view and download statistics by country and sector, so that the impact of datasets outside academia can be demonstrated.

## Sample 36: 9c563ce8328b99d1fc33da0b301fc72e

Task: bug_report_refinement

### Original input

original_text:

**steps to reproduce**
on a webpage, press a function key (f1, f2 etc.), a media key (play, stop etc.), a browser key (previous, next) or a volume key (vol. up, mute etc.)

**actual result**
the cursor is hidden. it reappears when moved or if the key triggers the windows media overlay.

**expected result**
cursor should remain visible.
all keys not involved in typing text should not hides the cursor.

this is especially noticeable with the f5 key used to refresh the page.

this is similar to bug 1768903.

### Output A

Summary  
Pressing non-text keys on a webpage can hide the cursor. This includes function keys (for example F1, F2), media keys (play, stop), browser keys (previous, next), and volume keys (volume up, mute). This is especially noticeable with F5 used to refresh the page. This appears similar to bug 1768903.

Steps  
1. On a webpage, press a function key (F1, F2, etc.).  
2. Press a media key (play, stop, etc.).  
3. Press a browser key (previous, next).  
4. Press a volume key (volume up, mute, etc.).  

Expected  
Cursor should remain visible.  
All keys not involved in typing text should not hide the cursor.

Actual  
The cursor is hidden. It reappears when moved or if the key triggers the Windows media overlay.

### Output B

## Summary
On a webpage, pressing certain non-text keys causes the cursor to hide unexpectedly. This is especially noticeable with the F5 key used to refresh the page. The issue is similar to bug 1768903.

## Steps to Reproduce
1. Open a webpage.
2. Press a function key (for example, F1, F2, etc.), a media key (play, stop, etc.), a browser key (previous, next), or a volume key (volume up, mute, etc.).

## Expected Behavior
The cursor should remain visible.  
All keys not involved in typing text should not hide the cursor.

## Actual Behavior
The cursor is hidden. It reappears when moved or if the key triggers the Windows media overlay.

## Technical Context
- Affected inputs include function keys, media keys, browser keys, and volume keys.
- The issue is especially noticeable with the F5 key used to refresh the page.
- Similar to bug 1768903.

## Sample 37: ff7f17997c6c3d332b7cb5f241988b6c

Task: user_story_refinement

### Original input

original_text:

As an Archivist, I want to specify the Source for a Name Form of an Agent and add new Sources and edit existing Sources.

### Output A

As an Archivist, I want to specify the Source for a Name Form of an Agent and add new Sources and edit existing Sources, so that Not provided.

### Output B

As an Archivist, I want to specify the source for a Name Form of an Agent and add or edit sources, so that I can manage source information accurately.

## Sample 38: 57812880106e4bad4c16edcd6b4dcc87

Task: bug_report_refinement

### Original input

original_text:

user agent: mozilla/5.0 (windows nt 10.0; win64; x64; rv:57.0) gecko/20100101 firefox/57.0
build id: 20170915220136

steps to reproduce:

browse to http://www.experian.com/


actual results:

links and menu do not work.  then close tab.  nightly process stays stuck at ~25% cpu until process is killed in task manager.


expected results:

page should work.

### Output A

## Summary
Visiting `http://www.experian.com/` in Firefox causes the page’s links and menu to stop working, and after closing the tab, the Nightly process remains stuck at approximately 25% CPU until it is killed in Task Manager.

## Steps to Reproduce
1. Use the following environment:
   - User agent: `mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0`
   - Build ID: `20170915220136`
2. Browse to `http://www.experian.com/`.
3. Close the tab.

## Expected Behavior
The page should work.

## Actual Behavior
- Links and menu do not work.
- After closing the tab, the Nightly process stays stuck at about 25% CPU until the process is killed in Task Manager.

## Technical Context
- URL: `http://www.experian.com/`
- User agent: `mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0`
- Build ID: `20170915220136`

### Output B

Summary
Web page at http://www.experian.com/ does not function correctly in Firefox 57.0 on Windows 10; links and menu do not work, and after closing the tab the Nightly process remains stuck at about 25% CPU until it is killed in Task Manager.

Steps
1. Browse to http://www.experian.com/
2. Close the tab

Expected
Page should work.

Actual
Links and menu do not work. After closing the tab, the Nightly process stays stuck at approximately 25% CPU until the process is killed in Task Manager.

## Sample 39: 7faaab9344486948b1aaa0ec715d6cfc

Task: user_story_refinement

### Original input

original_text:

As a repository manager, I want to list all the components, in their appropriate order, for an object.

### Output A

As a repository manager, I want to list all the components for an object in their appropriate order, so that I can view them correctly.

### Output B

As a repository manager, I want to list all the components of an object in their appropriate order, so that I can view them correctly.

## Sample 40: 5bb10d6f5244c251cde9e0431d4d5e51

Task: user_story_refinement

### Original input

original_text:

As a user, I want a mechanism for electronically sharing papers and notes with other researchers, so that we can collaborate effectively.

### Output A

As a user, I want a way to electronically share papers and notes with other researchers, so that we can collaborate effectively.

### Output B

As a user, I want a mechanism for electronically sharing papers and notes with other researchers, so that we can collaborate effectively.

## Sample 41: 633d1532c88e5d7819d108cf5d654285

Task: user_story_refinement

### Original input

original_text:

As a collection curator, I want to have a tool to perform author authority control.

### Output A

As a collection curator, I want a tool to perform author authority control, so that Not provided.

### Output B

As a collection curator, I want a tool to perform author authority control, so that I can manage author names consistently.

## Sample 42: cbc65455d60ce96a4f4443dc53970b96

Task: bug_report_refinement

### Original input

original_text:

steps to reproduce:

using nightly 105.0a1, 20220814095107, having a pdf open in a viewer on a 1366x768 laptop system, suspend the system, attach a hidpi monitor, and resume.


actual results:

the font of the pdf was fuzzy.


expected results:

the font of the pdf should be sharp. reloading the page, the screen is sharp.

### Output A

## Summary
When resuming from suspend after attaching a HiDPI monitor, a PDF open in the viewer appears fuzzy on a 1366x768 laptop system.

## Steps to Reproduce
1. Use nightly 105.0a1, build 20220814095107.
2. Open a PDF in a viewer on a 1366x768 laptop system.
3. Suspend the system.
4. Attach a HiDPI monitor.
5. Resume the system.

## Expected Behavior
The font of the PDF should be sharp. Reloading the page makes the screen sharp.

## Actual Behavior
The font of the PDF was fuzzy.

## Technical Context
- Version: nightly 105.0a1
- Build: 20220814095107
- System: 1366x768 laptop system
- Display change involved: attaching a HiDPI monitor during suspend/resume


### Output B

Summary

PDF text becomes fuzzy after resuming from suspend when a HiDPI monitor is attached on Firefox Nightly 105.0a1.

Steps

1. Use Firefox Nightly 105.0a1 build 20220814095107.
2. Open a PDF in a viewer on a 1366x768 laptop system.
3. Suspend the system.
4. Attach a HiDPI monitor.
5. Resume the system.

Expected

The font of the PDF should be sharp. Reloading the page makes the screen sharp.

Actual

The font of the PDF was fuzzy.

## Sample 43: 2ea1e424768826d5ca9231393c93bd58

Task: bug_report_refinement

### Original input

original_text:

user agent: mozilla/5.0 (windows nt 10.0; win64; x64; rv:109.0) gecko/20100101 firefox/110.0

steps to reproduce:

i opened the new thunderbird


actual results:

i can't see any of the emails that are in my imap account online nor am i able to subscribe to them again. they have disappeared since i opened tb last time!

i discovered more - the problem was that i had folders set on unified. when i switched unified off i found all the folders under the account. but there seems no point to have unified as an option if it doesn't include all the folders unified.. and if i have all and unified together then a lot of stuff is in twice.


expected results:

i should have not lost all the folders that were subscribed to when i last opened tb, there seems to be a need for more thought in how unified folders works to unify all folders and not just a small subset... there used to be local folders that was where these folders went as i recall.

### Output A

## Summary
After opening the new Thunderbird, the user could not see IMAP account emails/folders that were available online and could not resubscribe to them. The issue was later found to be related to the account being set to Unified folders.

## Steps to Reproduce
1. Open the new Thunderbird.
2. Observe the IMAP account folders/emails.

## Expected Behavior
The subscribed folders from the IMAP account should still be available after opening Thunderbird. Unified folders should unify all folders, not just a subset.

## Actual Behavior
- The user could not see any of the emails that were in the IMAP account online.
- The user was not able to subscribe to the folders again.
- The folders appeared to have disappeared since the last time Thunderbird was opened.
- When Unified folders was turned off, the folders under the account became visible again.
- With both All and Unified together, some items appeared twice.

## Technical Context
- User agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0
- Thunderbird was opened in the new version.
- The problem was associated with folders being set to Unified.
- The report mentions that there used to be local folders where these folders went, as recalled by the user.

### Output B

Summary  
Thunderbird folders/subscriptions are not visible when Unified folders is enabled. After switching Unified off, the missing account folders reappear. The reporter notes that Unified does not appear to include all folders and may duplicate content when combined with “All.”

Steps  
1. Open the new Thunderbird.  
2. Observe the IMAP account folders while Unified folders is enabled.  
3. Switch Unified off.

Expected  
The subscribed folders should remain visible and accessible after opening Thunderbird. Unified folders should unify all folders, not only a subset. Not provided whether local folders are involved in the expected behavior.

Actual  
The IMAP account folders that were visible online could not be seen in Thunderbird, and the user was unable to subscribe to them again. The folders appeared to have disappeared since the last time Thunderbird was opened. After switching Unified off, the folders under the account were found again. The reporter also observed that using Unified alongside All causes many items to appear twice.

## Sample 44: 3d6ac1206f3d59b2feade8684d269116

Task: bug_report_refinement

### Original input

original_text:

created attachment 9215462
screen shot 2021-04-13 at 10.12.33 am.png

## steps to reproduce/what did you do?

* first, tab through the chrome to observe the dark/neon blue focus ring color (depending on the theme you have chosen)
* now tab into one of the dropdown menus like application menu or library

## expected behavior/ what did you think will happen?

* focus ring color is blue like the rest of the chrome

## actual behavior/ what actually happened

* focus ring color uses my system accent color (in my case, orange)

## additional notes

for me, the issue is not so much that it's one color or the other, it's that it's inconsistent. especially in dark theme where the orange sticks out.

### Output A

## Summary
Focus ring color is inconsistent between regular chrome elements and dropdown menus. In the chrome, the focus ring appears dark/neon blue depending on the selected theme, but when tabbing into dropdown menus such as the application menu or library, the focus ring uses the system accent color instead.

## Steps
1. Tab through the chrome to observe the dark/neon blue focus ring color, depending on the theme selected.
2. Tab into one of the dropdown menus such as the application menu or library.

## Expected
Focus ring color is blue like the rest of the chrome.

## Actual
Focus ring color uses the system accent color instead, in this case orange. The issue is that the color is inconsistent, especially in dark theme where the orange stands out.

### Output B

## Summary
When tabbing into a dropdown menu (such as the application menu or library), the focus ring color differs from the rest of the chrome. The chrome uses a dark/neon blue focus ring depending on the selected theme, but the dropdown menu focus ring uses the system accent color instead.

## Steps to Reproduce
1. Tab through the chrome to observe the dark/neon blue focus ring color, depending on the theme selected.
2. Tab into one of the dropdown menus, such as the application menu or library.

## Expected Behavior
The focus ring color should be blue like the rest of the chrome.

## Actual Behavior
The focus ring color uses the system accent color; in the reported case, it is orange.

Additional note: The issue is described as inconsistent, especially in dark theme where the orange color stands out.

## Technical Context
- Attachment provided: `9215462`
- Screenshot: `screen shot 2021-04-13 at 10.12.33 am.png`

## Sample 45: f2cc75810c735ea6a32fa35886f363af

Task: user_story_refinement

### Original input

original_text:

As a site member, I want to subscribe to an RSS feed of news, so that I remain sufficiently and easily informed.

### Output A

As a site member, I want to subscribe to an RSS feed of news, so that I can stay informed easily.

### Output B

As a site member, I want to subscribe to an RSS feed of news, so that I remain sufficiently and easily informed.

## Sample 46: c9e8cd93217f70b4e2cba0024d8cf839

Task: user_story_refinement

### Original input

original_text:

As a camp worker, I'm able to report a list of supplies to the manager that the camp is short of.

### Output A

As a camp worker, I want to report a list of supplies that the camp is short of to the manager, so that Not provided.

### Output B

As a camp worker, I want to report a list of supplies that the camp is short of to the manager, so that the manager is aware of the shortages.

## Sample 47: b0070fe12db6a24123de886336aa0fe2

Task: user_story_refinement

### Original input

original_text:

As a moderator, I want to invite estimators by giving them a URL where they can access the game, so that we can start the game.

### Output A

As a moderator, I want to invite estimators by sharing a URL that gives them access to the game, so that we can start the game.

### Output B

As a moderator, I want to invite estimators by giving them a URL where they can access the game, so that we can start the game.

## Sample 48: 6370c4707ff385c8e7df15c642cd38f4

Task: bug_report_refinement

### Original input

original_text:

user agent: mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/85.0.4183.102 safari/537.36

steps to reproduce:

upgraded to tb 78
migrated my enigmail data to the new e2ee
enabled openpgp for account gz0001@gmail.com
try to send an encrypted test message to gunter.zielke@gmail.com


actual results:

i am getting a "sending of the message failed" message box with no indication what might have gone wrong. this setup had worked with the previous version of tb and enigmail.


expected results:

the message is encrypted and sent to the recipient, or at least more information is given what might have gone wrong.

### Output A

## Summary
After upgrading to Thunderbird 78 and migrating Enigmail data to the new E2EE/OpenPGP setup, sending an encrypted test message fails for account `gz0001@gmail.com` when addressed to `gunter.zielke@gmail.com`.

## Steps to Reproduce
1. Upgrade to Thunderbird 78.
2. Migrate Enigmail data to the new E2EE setup.
3. Enable OpenPGP for account `gz0001@gmail.com`.
4. Try to send an encrypted test message to `gunter.zielke@gmail.com`.

## Expected Behavior
The message is encrypted and sent to the recipient, or at least more information is provided about what went wrong.

## Actual Behavior
A message box appears stating: `"sending of the message failed"` with no indication of what may have gone wrong. This setup had worked with the previous version of Thunderbird and Enigmail.

## Technical Context
- User agent: `mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/85.0.4183.102 safari/537.36`
- Thunderbird version: 78
- Enigmail data migrated to new E2EE
- OpenPGP enabled for account: `gz0001@gmail.com`
- Recipient: `gunter.zielke@gmail.com`

### Output B

Summary
Sending an encrypted message fails in Thunderbird 78 after migrating Enigmail data to the new E2EE and enabling OpenPGP for the account. The user reports that this setup worked in the previous Thunderbird and Enigmail version.

Steps
1. Upgraded to Thunderbird 78.
2. Migrated Enigmail data to the new E2EE.
3. Enabled OpenPGP for account gz0001@gmail.com.
4. Tried to send an encrypted test message to gunter.zielke@gmail.com.

Expected
The message is encrypted and sent to the recipient, or at least more information is given about what might have gone wrong.

Actual
A "sending of the message failed" message box appears with no indication of what might have gone wrong.

## Sample 49: e1b4d1c4d5420863413373f9fe2fbabc

Task: user_story_refinement

### Original input

original_text:

As a site administrator, I want to create an Other Course or Event that is not charged a listing fee, so that the Scrum Alliance doesn't charge itself for Scrum Gatherings that it puts on.

### Output A

As a site administrator, I want to create an Other Course or Event without being charged a listing fee, so that Scrum Alliance does not charge itself for Scrum Gatherings that it organizes.

### Output B

As a site administrator, I want to create an Other Course or Event that is not charged a listing fee, so that the Scrum Alliance doesn't charge itself for Scrum Gatherings that it puts on.

## Sample 50: 5cd599eb83f10875bf171c77d7732d72

Task: user_story_refinement

### Original input

original_text:

As an API User, I want to be able to normalise measures by GINI and related socioeconomic indexes, So that I work with datasets in reference to their contextual constraints.

### Output A

As an API User, I want to normalise measures by GINI and related socioeconomic indexes, so that I work with datasets in reference to their contextual constraints.

### Output B

As an API user, I want to normalize measures by GINI and related socioeconomic indexes, so that I can work with datasets in reference to their contextual constraints.

## Sample 51: 4eef74376f85e97dd55074181a7956a1

Task: user_story_refinement

### Original input

original_text:

As a team member, I want to know what the first hypothesis is, so that I can start developing a prototype to test.

### Output A

As a team member, I want to know what the first hypothesis is, so that I can start developing a prototype to test.

### Output B

As a team member, I want to know the first hypothesis, so that I can start developing a prototype to test it.

## Sample 52: b172f56a921f9ccf27722711187e2adf

Task: bug_report_refinement

### Original input

original_text:

created attachment 9357823
screen recording 2023-10-11 at 3.26.56 pm.mov

**found in**
* nightly 120.0a1 

**affected versions**
* nightly 120.0a1 

**tested platforms**
* affected platforms: windows 11, macos 12, ubuntu 22.04 x64

**preconditions**
* in about:config - set "browser.privatebrowsing.felt-privacy-v1" to true

**steps to reproduce**
1. open a new private window.
2. visit any website and pay attention to the tab's background during the page loading process.

**expected result**
* the tab's background color should align with the new theme while the site is loading.

**actual result**
* the tab's background color displays the old background during site loading. please see the screencast for more details.

**regression range**
* not a regression.

### Output A

Summary  
Tab background in a new private window shows the old background color during page loading when `browser.privatebrowsing.felt-privacy-v1` is set to `true`.

Steps  
1. In `about:config`, set `browser.privatebrowsing.felt-privacy-v1` to `true`.
2. Open a new private window.
3. Visit any website and observe the tab background during the page loading process.

Expected  
The tab's background color should align with the new theme while the site is loading.

Actual  
The tab's background color displays the old background during site loading. Please see the screencast for more details.



### Output B

## Summary
In Firefox Nightly 120.0a1, when `browser.privatebrowsing.felt-privacy-v1` is set to `true`, the tab background in a new private window shows the old background color during page loading instead of matching the new theme.

**Found in:** nightly 120.0a1  
**Affected versions:** nightly 120.0a1  
**Tested platforms:** Windows 11, macOS 12, Ubuntu 22.04 x64  
**Attachment:** 9357823 — `screen recording 2023-10-11 at 3.26.56 pm.mov`

## Steps to Reproduce
1. Set `browser.privatebrowsing.felt-privacy-v1` to `true` in `about:config`.
2. Open a new private window.
3. Visit any website.
4. Observe the tab background during the page loading process.

## Expected Behavior
The tab's background color should align with the new theme while the site is loading.

## Actual Behavior
The tab's background color displays the old background during site loading. See the screencast for more details.

## Technical Context
- Preference: `browser.privatebrowsing.felt-privacy-v1 = true`
- Reported as: not a regression
- Additional details: Not provided

## Sample 53: 70745912935f488d6044a52e0d20e651

Task: user_story_refinement

### Original input

original_text:

As a broker team member, I want to derive FundingAgencyCode, so that the data quality and completeness improves.

### Output A

As a broker team member, I want to derive FundingAgencyCode, so that the data quality and completeness improves.

### Output B

As a broker team member, I want to derive the FundingAgencyCode, so that data quality and completeness improve.

## Sample 54: a5f60dcd8aef0db2788586038fd695b6

Task: bug_report_refinement

### Original input

original_text:

user agent: mozilla/5.0 (windows nt 6.1; win64; x64; rv:59.0) gecko/20100101 firefox/59.0
build id: 20171227220103

steps to reproduce:

have passwords etc stored in password manager with a master password set.
set security.enterprise_roots.enabled to true
restart firefox
press "saved logins..." button
all users and remembered passwords are empty
set security.enterprise_roots.enabled back to false
restart firefox
press "saved logins..." button
all saved logins and passwords are back




actual results:

security.enterprise_roots.enabled manages to hide all saved usernames and passwords with a master pwd set. 
these settings should not be related.


expected results:

i should be able to view all my stored usernames and passwords even with enterprise_roots set.
if i disable i can't get out on internet, if i enable i can't see my passwords for sites.

### Output A

Summary  
Saved logins and passwords disappear from the Saved Logins dialog when `security.enterprise_roots.enabled` is set to `true` and a master password is configured.

Steps  
1. Have passwords etc stored in the password manager with a master password set.  
2. Set `security.enterprise_roots.enabled` to `true`.  
3. Restart Firefox.  
4. Press the “saved logins...” button.  
5. Set `security.enterprise_roots.enabled` back to `false`.  
6. Restart Firefox.  
7. Press the “saved logins...” button.  

Expected  
All saved usernames and passwords should remain visible, including when `security.enterprise_roots.enabled` is set to `true`.

Actual  
When `security.enterprise_roots.enabled` is `true`, all saved usernames and passwords are empty / hidden in the Saved Logins dialog. When it is set back to `false` and Firefox is restarted, all saved logins and passwords reappear.



### Output B

## Summary
Enabling `security.enterprise_roots.enabled` appears to hide all saved usernames and passwords in the Firefox Password Manager when a master password is set. This setting should not be related to saved logins visibility.

## Steps to Reproduce
1. Have passwords stored in the password manager with a master password set.
2. Set `security.enterprise_roots.enabled` to `true`.
3. Restart Firefox.
4. Press the **"Saved Logins..."** button.
5. Observe that all users and remembered passwords are empty.
6. Set `security.enterprise_roots.enabled` back to `false`.
7. Restart Firefox.
8. Press the **"Saved Logins..."** button.
9. Observe that all saved logins and passwords are back.

## Expected Behavior
I should be able to view all stored usernames and passwords even with `enterprise_roots` set.

## Actual Behavior
`security.enterprise_roots.enabled` hides all saved usernames and passwords when a master password is set. These settings should not be related.

## Technical Context
- User agent: `mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0`
- Build ID: `20171227220103`
- Preference involved: `security.enterprise_roots.enabled`
- Password manager master password: set

## Sample 55: 7c9547b2b7b4c686ace42221024a3260

Task: user_story_refinement

### Original input

original_text:

As a data manager, I want to plan the anonymization of data, so that we protect the privacy of the people participating in the research as good as possible and still ensure reusability of data.

### Output A

As a data manager, I want to plan the anonymization of data, so that we can protect the privacy of research participants as much as possible while still ensuring the data remains reusable.

### Output B

As a data manager, I want to plan the anonymization of data, so that we protect the privacy of the people participating in the research as good as possible and still ensure reusability of data.

## Sample 56: 1b8f158a4988d28c138600e8d17cbf3d

Task: bug_report_refinement

### Original input

original_text:

steps to reproduce:
1. go to data:text/html,test long xhr<script>const headers = new headers(); headers.append("accept", "application/json");fetch("https://httpstat.us/200?sleep=20000&test=true", {method: "post", headers})</script>
2. open the console
3. make sure you have the xhr filter turned on
4. reload the page
5. you should see an xhr request being logged, click on it to expand it
6. go to the response tab

expected results:
the request is resolved after 20s, and at that time, the response tab panel content should be updated with the response (200 ok). this is what is done in the netmonitor

actual results:
the panel content stays empty

### Output A

## Summary
When viewing a long-running XHR/fetch request in the console with the XHR filter enabled, the response tab does not update after the request completes. The panel content remains empty instead of showing the response.

## Steps to Reproduce
1. Go to: `data:text/html,test long xhr<script>const headers = new headers(); headers.append("accept", "application/json");fetch("https://httpstat.us/200?sleep=20000&test=true", {method: "post", headers})</script>`
2. Open the console.
3. Make sure the XHR filter is turned on.
4. Reload the page.
5. You should see an XHR request being logged; click on it to expand it.
6. Go to the response tab.

## Expected Behavior
The request is resolved after 20 seconds, and at that time the response tab panel content should be updated with the response (`200 ok`). This is what is done in the netmonitor.

## Actual Behavior
The panel content stays empty.

## Technical Context
- Console with XHR filter enabled
- Request type: XHR/fetch
- URL: `https://httpstat.us/200?sleep=20000&test=true`
- Method: `post`
- Header: `accept: application/json`

### Output B

**Summary**  
The response tab panel content stays empty for a logged XHR request in the console after the request resolves.

**Steps**  
1. Go to `data:text/html,test long xhr<script>const headers = new headers(); headers.append("accept", "application/json");fetch("https://httpstat.us/200?sleep=20000&test=true", {method: "post", headers})</script>`  
2. Open the console.  
3. Make sure the XHR filter is turned on.  
4. Reload the page.  
5. You should see an XHR request being logged; click on it to expand it.  
6. Go to the response tab.  

**Expected**  
The request is resolved after 20 seconds, and at that time the response tab panel content should be updated with the response (`200 ok`). This is what is done in the netmonitor.

**Actual**  
The panel content stays empty.

## Sample 57: ae49d0a61670a634b2f2d77a72b1ca5a

Task: bug_report_refinement

### Original input

original_text:

user agent: mozilla/5.0 (x11; linux x86_64; rv:63.0) gecko/20100101 firefox/63.0
build id: 20180826100553

steps to reproduce:

1- play a video
2- tap anywhere on the screen to hide controls or wait for them to disappear


actual results:

the controls begin to fade, then reappear a few milliseconds later and finally disappear completely.

video of the bug : https://youtu.be/grfnl1zxwn4


expected results:

the controls shouldn't reappear.

it seems to also affect firefox for desktop.

mozregression --app=fennec --good=2018-04-3 --bad=2018-04-4

or

mozregression --app=fennec --repo=mozilla-inbound --good=a3ac84a960c7a64150c5302ebb6d72abc39bb46c --bad=c9db3f332a190addcc47ab54b0ccd5366948fd35

### Output A

Summary  
Firefox for Android video controls briefly reappear while hiding. User agent: mozilla/5.0 (x11; linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0. Build ID: 20180826100553. Video of the bug: https://youtu.be/grfnl1zxwn4. It seems to also affect Firefox for desktop. mozregression results: `mozregression --app=fennec --good=2018-04-3 --bad=2018-04-4` or `mozregression --app=fennec --repo=mozilla-inbound --good=a3ac84a960c7a64150c5302ebb6d72abc39bb46c --bad=c9db3f332a190addcc47ab54b0ccd5366948fd35`.

Steps  
1. Play a video.  
2. Tap anywhere on the screen to hide controls or wait for them to disappear.

Expected  
The controls shouldn't reappear.

Actual  
The controls begin to fade, then reappear a few milliseconds later and finally disappear completely.

### Output B

## Summary
Video controls briefly reappear after being hidden during playback. This appears to affect Firefox for desktop as well.

## Steps to Reproduce
1. Play a video.
2. Tap anywhere on the screen to hide the controls, or wait for them to disappear.

## Expected Behavior
The controls should not reappear.

## Actual Behavior
The controls begin to fade, then reappear a few milliseconds later, and finally disappear completely.

## Technical Context
- User agent: mozilla/5.0 (x11; linux x86_64; rv:63.0) gecko/20100101 firefox/63.0
- Build ID: 20180826100553
- Video of the bug: https://youtu.be/grfnl1zxwn4
- Mozregression:
  - `mozregression --app=fennec --good=2018-04-3 --bad=2018-04-4`
  - `mozregression --app=fennec --repo=mozilla-inbound --good=a3ac84a960c7a64150c5302ebb6d72abc39bb46c --bad=c9db3f332a190addcc47ab54b0ccd5366948fd35`

## Sample 58: 2faba8b7f34fe78925b879b67abea1c8

Task: user_story_refinement

### Original input

original_text:

As a repository support team member, I want to alias (or map) an item from one collection to another (so the item will appear to belong to both collections), because the collection owner has asked them to.

### Output A

As a repository support team member, I want to alias (or map) an item from one collection to another, so that the item will appear to belong to both collections.

### Output B

As a repository support team member, I want to alias an item from one collection to another so that the item appears to belong to both collections, because the collection owner has asked me to.

## Sample 59: 54bf0e6643dc6c661511d2b301cf1dcf

Task: bug_report_refinement

### Original input

original_text:

user agent: mozilla/5.0 (macintosh; intel mac os x 10.15; rv:128.0) gecko/20100101 firefox/128.0

steps to reproduce:

this got lost when fdlibm was re-vendored, because the fix wasn't created as a patch in `modules/fdlibm/patches`

if compiling to wasi using a mozconfig like so:
```
ac_add_options --enable-project=js
ac_add_options --enable-application=js
ac_add_options --target=wasm32-unknown-wasi
ac_add_options --without-system-zlib
ac_add_options --disable-jit
ac_add_options --disable-shared-js
ac_add_options --disable-shared-memory
ac_add_options --disable-tests
ac_add_options --disable-clang-plugin
ac_add_options --enable-jitspew
ac_add_options --enable-optimize=-o3
ac_add_options --enable-portable-baseline-interp
mk_add_options autoclobber=1
ac_add_options --host=aarch64-apple-darwin
ac_add_options --enable-debug

```


actual results:

```
47 in file included from /users/jakechampion/mozilla-unified/obj-wasm32-unknown-wasi/dist/system_wrappers/signal.h:3:
 0:03.48 /users/jakechampion/.mozbuild/sysroot-wasm32-wasi/include/signal.h:2:2: error: "wasm lacks signal support; to enable minimal signal emulation, compile with -d_wasi_emulated_signal and link with -lwasi-emulated-signal"
 0:03.48     2 | #error "wasm lacks signal support; to enable minimal signal emulation, \
```


expected results:

a successful build should have occurred

### Output A

Summary  
Build failure when compiling Firefox/SpiderMonkey to WASI after fdlibm was re-vendored; the fix was lost because it was not created as a patch in `modules/fdlibm/patches`.

Steps  
1. Compile to WASI using the following mozconfig:
```িনি
ac_add_options --enable-project=js
ac_add_options --enable-application=js
ac_add_options --target=wasm32-unknown-wasi
ac_add_options --without-system-zlib
ac_add_options --disable-jit
ac_add_options --disable-shared-js
ac_add_options --disable-shared-memory
ac_add_options --disable-tests
ac_add_options --disable-clang-plugin
ac_add_options --enable-jitspew
ac_add_options --enable-optimize=-o3
ac_add_options --enable-portable-baseline-interp
mk_add_options autoclobber=1
ac_add_options --host=aarch64-apple-darwin
ac_add_options --enable-debug
```

Expected  
A successful build should have occurred.

Actual  
Build fails with:
```text
47 in file included from /users/jakechampion/mozilla-unified/obj-wasm32-unknown-wasi/dist/system_wrappers/signal.h:3:
0:03.48 /users/jakechampion/.mozbuild/sysroot-wasm32-wasi/include/signal.h:2:2: error: "wasm lacks signal support; to enable minimal signal emulation, compile with -d_wasi_emulated_signal and link with -lwasi-emulated-signal"
0:03.48     2 | #error "wasm lacks signal support; to enable minimal signal emulation, \
```

### Output B

## Summary
Building Firefox/SpiderMonkey for WASI fails because a previously applied fdlibm fix was lost when fdlibm was re-vendored, and the fix was not created as a patch in `modules/fdlibm/patches`.

## Steps to Reproduce
1. Configure a build for WASI using a mozconfig like the following:
   ```ి
   ac_add_options --enable-project=js
   ac_add_options --enable-application=js
   ac_add_options --target=wasm32-unknown-wasi
   ac_add_options --without-system-zlib
   ac_add_options --disable-jit
   ac_add_options --disable-shared-js
   ac_add_options --disable-shared-memory
   ac_add_options --disable-tests
   ac_add_options --disable-clang-plugin
   ac_add_options --enable-jitspew
   ac_add_options --enable-optimize=-o3
   ac_add_options --enable-portable-baseline-interp
   mk_add_options autoclobber=1
   ac_add_options --host=aarch64-apple-darwin
   ac_add_options --enable-debug
   ```
2. Compile to WASI.

## Expected Behavior
A successful build should have occurred.

## Actual Behavior
The build fails with the following error:
```text
47 in file included from /users/jakechampion/mozilla-unified/obj-wasm32-unknown-wasi/dist/system_wrappers/signal.h:3:
0:03.48 /users/jakechampion/.mozbuild/sysroot-wasm32-wasi/include/signal.h:2:2: error: "wasm lacks signal support; to enable minimal signal emulation, compile with -d_wasi_emulated_signal and link with -lwasi-emulated-signal"
0:03.48     2 | #error "wasm lacks signal support; to enable minimal signal emulation, \
```

## Technical Context
- User agent: `mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0`
- The issue got lost when fdlibm was re-vendored because the fix was not created as a patch in `modules/fdlibm/patches`.
- Build target: `wasm32-unknown-wasi`
- Relevant build options:
  - `--enable-project=js`
  - `--enable-application=js`
  - `--without-system-zlib`
  - `--disable-jit`
  - `--disable-shared-js`
  - `--disable-shared-memory`
  - `--disable-tests`
  - `--disable-clang-plugin`
  - `--enable-jitspew`
  - `--enable-optimize=-o3`
  - `--enable-portable-baseline-interp`
  - `--host=aarch64-apple-darwin`
  - `--enable-debug`

## Sample 60: d5c589558e61fc95e424439516acedcc

Task: user_story_refinement

### Original input

original_text:

As a user, I want to see all the component parts of an object.

### Output A

As a user, I want to see all the component parts of an object, so that I can understand its full composition.

### Output B

As a user, I want to see all the component parts of an object, so that I can understand what it is made of.

## Sample 61: 5b3d7d65a0eec5f205c108272f67fe8d

Task: user_story_refinement

### Original input

original_text:

As an UnivITservice, I want to be able to export all data to a different system, so that I am not tied into one system which may not be the most appropriate at some point in the future.

### Output A

As a UnivITservice, I want to export all data to a different system, so that I am not tied into one system which may not be the most appropriate at some point in the future.

### Output B

As an UnivITservice, I want to export all data to another system, so that I am not tied to one system that may not be the most appropriate in the future.

## Sample 62: 6a19d9191f721134dae45b56533d1177

Task: bug_report_refinement

### Original input

original_text:

from github: https://github.com/mozilla-mobile/fenix/issues/16037.

> ## steps to reproduce
> 1. open any web site with thai characters, for example https://th.wikipedia.org/ 
> 2. long tap on any thai text, as if you wanted to select some text. 
> 
> ### expected behavior
> 
> some text is being selected.
> 
> ### actual behavior
> 
> 1. no text is being selected by the long tap.
> 2. no text, not even with latin script, can be selected any more.
> 3. loading a page in new tabs will do nothing at all.
>  
> ### device information
> 
> * android device: xiaomi mi a2 lite, android 10, last system update 2020-09-01
> * fenix version: 81.1.4 (build #2015768387), reproducible with today's nightly build (from google play store)
>  

change performed by the [move to bugzilla add-on](https://addons.mozilla.org/en-us/firefox/addon/move-to-bugzilla/).

### Output A

## Summary
Long-pressing Thai text on a web page does not select text in Fenix. After this occurs, text selection appears to stop working entirely, and loading a page in new tabs does nothing.

## Steps to Reproduce
1. Open any website with Thai characters, for example: https://th.wikipedia.org/
2. Long tap on any Thai text, as if you wanted to select some text.

## Expected Behavior
Some text is selected.

## Actual Behavior
1. No text is selected by the long tap.
2. No text, not even with Latin script, can be selected any more.
3. Loading a page in new tabs does nothing at all.

## Technical Context
- Android device: Xiaomi Mi A2 Lite
- Android version: 10
- Last system update: 2020-09-01
- Fenix version: 81.1.4 (build #2015768387)
- Reproducible with today's nightly build (from Google Play Store)

### Output B

Summary
Text selection and page loading stop working after long-tapping Thai text in Firefox Fenix on Android.

Steps
1. Open any website with Thai characters, for example https://th.wikipedia.org/
2. Long tap on any Thai text, as if you wanted to select some text.

Expected
Some text is selected.

Actual
1. No text is selected by the long tap.
2. No text, not even with Latin script, can be selected any more.
3. Loading a page in new tabs does nothing at all.
4. Android device: Xiaomi Mi A2 Lite, Android 10, last system update 2020-09-01.
5. Fenix version: 81.1.4 (build #2015768387), reproducible with today's nightly build (from Google Play Store).

## Sample 63: b28fb61aa27c195102efbaea0f1cbe96

Task: user_story_refinement

### Original input

original_text:

As an OlderPerson, I want to use ALFRED to contact people from my own circle.

### Output A

As an OlderPerson, I want to use ALFRED to contact people from my own circle, so that I can stay in touch with them.

### Output B

As an OlderPerson, I want to use ALFRED to contact people from my own circle, so that Not provided.

## Sample 64: eda7d82b1aba84aae4ef9528381278a1

Task: user_story_refinement

### Original input

original_text:

As a user, I don't want to see NASA grants displayed as contracts.

### Output A

As a user, I want NASA grants to not be displayed as contracts, so that I can distinguish grants from contracts.

### Output B

As a user, I want NASA grants to not be displayed as contracts, so that I can distinguish between grants and contracts.

## Sample 65: 0ae7783d3e9d6de336246e9b9d2fce0a

Task: user_story_refinement

### Original input

original_text:

As a DAMS manager, I want to know the outcome of the event, e.g., object NN was deleted.

### Output A

As a DAMS manager, I want to know the outcome of the event, such as an object being deleted, so that I can be informed of what happened.

### Output B

As a DAMS manager, I want to know the outcome of the event, such as when an object is deleted, so that I can understand what action was completed.

## Sample 66: 197513971c660f53e4d48d110a11ee51

Task: bug_report_refinement

### Original input

original_text:

**affected versions**
* firefox 72.0a1 (buildid:20191126212708)

**affected platforms**
* windows 10 64bit.

**preconditions**
* connect to a vpn server:
steps to configure vpn server: https://my.ibvpn.com/knowledgebase/267/set-up-the-pptp-on-windows-10.html
free vpn servers: https://www.vpnbook.com/

**steps to reproduce**
1. launch firefox.
2. access the about:config page.
3. set the network.trr.mode pref to 2.
4. restart firefox.
5. access a random domain.

**expected result**
* a vpn connection is detected and the request is not being handled via trr.

**actual result**
* the request is being handled via trr.

**regression range**
*  i don’t think that this is a regression.

### Output A

## Summary
Firefox 72.0a1 on Windows 10 64-bit appears to handle requests via TRR even when connected to a VPN. The report indicates this is not believed to be a regression.

## Steps to Reproduce
1. Connect to a VPN server.
   - VPN setup instructions: https://my.ibvpn.com/knowledgebase/267/set-up-the-pptp-on-windows-10.html
   - Free VPN servers: https://www.vpnbook.com/
2. Launch Firefox.
3. Access the `about:config` page.
4. Set the `network.trr.mode` preference to `2`.
5. Restart Firefox.
6. Access a random domain.

## Expected Behavior
A VPN connection is detected and the request is not handled via TRR.

## Actual Behavior
The request is being handled via TRR.

## Technical Context
- Affected version: Firefox 72.0a1 (buildid: 20191126212708)
- Affected platform: Windows 10 64-bit
- Preconditions: Connected to a VPN server
- Regression range: Not provided / not believed to be a regression

### Output B

### Summary
Firefox 72.0a1 (buildid: 20191126212708) on Windows 10 64-bit appears to handle requests via TRR even when a VPN connection is active. The reporter states this does not seem to be a regression.

### Steps
1. Connect to a VPN server.  
   - Steps to configure VPN server: https://my.ibvpn.com/knowledgebase/267/set-up-the-pptp-on-windows-10.html  
   - Free VPN servers: https://www.vpnbook.com/
2. Launch Firefox.
3. Access the `about:config` page.
4. Set the `network.trr.mode` preference to `2`.
5. Restart Firefox.
6. Access a random domain.

### Expected
A VPN connection is detected, and the request is not handled via TRR.

### Actual
The request is handled via TRR.

## Sample 67: dfa64bfb9da402d3127d500e06c30a27

Task: user_story_refinement

### Original input

original_text:

As a moderator, I want to create an account for the application by entering my name, email address, a password and a username, so that I can start using the application.

### Output A

As a moderator, I want to create an account for the application by entering my name, email address, password, and username, so that I can start using the application.

### Output B

As a moderator, I want to create an account for the application by entering my name, email address, password, and username, so that I can start using the application.

## Sample 68: 9ba5757365d8f03d4738f69242540bc2

Task: user_story_refinement

### Original input

original_text:

As a agency user, I want to map the FederalActionObligation properly to the Atom Feed.

### Output A

As an agency user, I want to map the FederalActionObligation properly to the Atom Feed, so that the data is represented accurately.

### Output B

As a agency user, I want to map the FederalActionObligation properly to the Atom Feed, so that Not provided.

## Sample 69: b630edeea00b65c82b121e73ca90b012

Task: bug_report_refinement

### Original input

original_text:

created attachment 9165025
removesearchengine.gif

**affected versions**
* 80.0a1 (buildid:20200720214226)

**unaffected versions**
* 79.0b9 (buildid:20200717001501)
* 79.0 (buildid:20200720193547)
* 78.0.2 (builid:20200708170202)
* 68.10.0esr (buildid:20200622191537)
* 78.0.2esr (buildid:20200708170510)

**affected platforms**
* windows 10 64bit
* ubuntu 18.04 64bit
* macos 10.14

**steps to reproduce**
1. launch firefox.
2. access the about:preferences#search page.
3. remove a default search engine.
4. restart firefox or upgrade firefox.
5. access the about:preferences#search page.
6. try restoring the default search engines by clicking the “restore defaults search engine” button.

**expected result**
*  the “restore default search engine” button is enabled and the search engine can be successfully restored.

**actual result**
* the “restore default search engine” button is disabled and the previously removed search engine cannot be successfully restored.

**regression range**
* this seems to be a regression:
* pushlog: https://hg.mozilla.org/integration/autoland/pushloghtml?fromchange=50aa1945d817b7e6a7c9488fcf92e07352623cac&tochange=e1d659582192657c70a9420d98bd53fb3838c255
* possible regressor: bug 1647359 

**notes**
* for further information regarding this issue please observe the attached screencast.
* a workaround for this issue is to remove another search engine (during the same browser session) and restore them all by clicking the “restore default search engine”
* same issue is encountered if trying to reorder the search engines, after a browser restart their default position cannot be restored via the "restore default search engine" button.
* [proposed severity] i think that this is a s3 severity issue.

### Output A

## Summary
After removing a default search engine, the **“restore default search engine”** button on `about:preferences#search` becomes disabled after restarting or upgrading Firefox, preventing the removed default search engine from being restored.

## Steps to Reproduce
1. Launch Firefox.
2. Open `about:preferences#search`.
3. Remove a default search engine.
4. Restart Firefox or upgrade Firefox.
5. Open `about:preferences#search` again.
6. Try restoring the default search engines by clicking the **“restore defaults search engine”** button.

## Expected Behavior
The **“restore default search engine”** button is enabled, and the search engine can be successfully restored.

## Actual Behavior
The **“restore default search engine”** button is disabled, and the previously removed search engine cannot be successfully restored.

## Technical Context
- **Affected version:** 80.0a1 (buildid:20200720214226)
- **Unaffected versions:**
  - 79.0b9 (buildid:20200717001501)
  - 79.0 (buildid:20200720193547)
  - 78.0.2 (builid:20200708170202)
  - 68.10.0esr (buildid:20200622191537)
  - 78.0.2esr (buildid:20200708170510)
- **Affected platforms:**
  - Windows 10 64bit
  - Ubuntu 18.04 64bit
  - macOS 10.14
- **Regression range:** This seems to be a regression.
- **Pushlog:** https://hg.mozilla.org/integration/autoland/pushloghtml?fromchange=50aa1945d817b7e6a7c9488fcf92e07352623cac&tochange=e1d659582192657c70a9420d98bd53fb3838c255
- **Possible regressor:** bug 1647359
- **Notes:**
  - For further information regarding this issue, please observe the attached screencast.
  - Workaround: remove another search engine during the same browser session and restore them all by clicking the **“restore default search engine”** button.
  - The same issue is encountered if trying to reorder the search engines; after a browser restart, their default position cannot be restored via the **“restore default search engine”** button.
  - [proposed severity] S3 severity issue.

### Output B

Summary  
After removing a default search engine and restarting or upgrading Firefox, the “Restore Default Search Engine” button on about:preferences#search becomes disabled, preventing the removed search engine from being restored. This issue appears to be a regression. A similar problem also occurs when trying to reorder search engines and then restore their default position after a browser restart.

Steps  
1. Launch Firefox.  
2. Access the about:preferences#search page.  
3. Remove a default search engine.  
4. Restart Firefox or upgrade Firefox.  
5. Access the about:preferences#search page.  
6. Try restoring the default search engines by clicking the “restore defaults search engine” button.  

Expected  
The “Restore Default Search Engine” button is enabled, and the search engine can be successfully restored.

Actual  
The “Restore Default Search Engine” button is disabled, and the previously removed search engine cannot be successfully restored.  

Notes:
- A workaround is to remove another search engine during the same browser session and restore them all by clicking the “restore default search engine” button.
- The same issue is encountered if trying to reorder the search engines; after a browser restart, their default position cannot be restored via the “restore default search engine” button.
- A screencast is attached: attachment 9165025 (`removesearchengine.gif`).
- Affected versions: 80.0a1 (buildid:20200720214226).
- Unaffected versions: 79.0b9 (buildid:20200717001501), 79.0 (buildid:20200720193547), 78.0.2 (buildid:20200708170202), 68.10.0esr (buildid:20200622191537), 78.0.2esr (buildid:20200708170510).
- Affected platforms: Windows 10 64bit, Ubuntu 18.04 64bit, macOS 10.14.
- Regression range: https://hg.mozilla.org/integration/autoland/pushloghtml?fromchange=50aa1945d817b7e6a7c9488fcf92e07352623cac&tochange=e1d659582192657c70a9420d98bd53fb3838c255
- Possible regressor: bug 1647359
- Proposed severity: S3

## Sample 70: 690ed76492c536eaccbb50847dc3e20c

Task: bug_report_refinement

### Original input

original_text:

this seems to be timing problem.
i think that it can be easily reproduced with a slow pc.
this seems resent regression since nightly63? 
it does not seem to reproduce on 62.0b14.

reproducible: easy to reproduce with a slow pc.

steps to reproduce:
(preparation)
 copy link http://moji.gr.jp/firefox/sample.pdf to clipboard
(steps)
1. start firefox
2. immediately after ui ready, right click on urlbar and choose "paste and go"
or
2. immediately after ui ready,  hit ctrl+v and enter

or
(preparation)
 bookmarked http://moji.gr.jp/firefox/sample.pdf
1. start firefox
2. immediately after ui ready, click on the bookmark

actual results:
pdf will be downloaded without prompt

expected results:
the pdf opens in built-in pdf viewer

### Output A

## Summary
This appears to be a timing problem and may be a recent regression since nightly63. It does not seem to reproduce on 62.0b14. The issue is easy to reproduce on a slow PC.

## Steps to Reproduce
**Preparation:**
- Copy this link to the clipboard: `http://moji.gr.jp/firefox/sample.pdf`

**Method 1:**
1. Start Firefox.
2. Immediately after the UI is ready, right-click the URL bar and choose **"paste and go"**.

**Method 2:**
1. Start Firefox.
2. Immediately after the UI is ready, press `Ctrl+V` and `Enter`.

**Alternative preparation and steps:**
- Bookmark `http://moji.gr.jp/firefox/sample.pdf`
1. Start Firefox.
2. Immediately after the UI is ready, click the bookmark.

## Expected Behavior
The PDF opens in the built-in PDF viewer.

## Actual Behavior
The PDF is downloaded without a prompt.

## Technical Context
- Suspected timing problem.
- Easy to reproduce on a slow PC.
- Seems to be a recent regression since nightly63.
- Does not seem to reproduce on 62.0b14.

### Output B

## Summary
This appears to be a timing problem. It seems easy to reproduce on a slow PC. This seems like a recent regression since nightly63. It does not seem to reproduce on 62.0b14.

## Steps
1. Preparation: copy the link `http://moji.gr.jp/firefox/sample.pdf` to the clipboard.
2. Start Firefox.
3. Immediately after the UI is ready, right-click on the URL bar and choose "paste and go".
4. Alternatively, immediately after the UI is ready, press `Ctrl+V` and `Enter`.

Or:

1. Preparation: bookmark `http://moji.gr.jp/firefox/sample.pdf`.
2. Start Firefox.
3. Immediately after the UI is ready, click on the bookmark.

## Expected
The PDF opens in the built-in PDF viewer.

## Actual
The PDF is downloaded without prompt.

## Sample 71: 5f69462475a2d9af5432e6aea9e5a3e5

Task: user_story_refinement

### Original input

original_text:

As a site visitor, I want to do a full-text search of article body, title, and author name, so that I can find what I want.

### Output A

As a site visitor, I want to search article titles, body text, and author names, so that I can find the articles I want.

### Output B

As a site visitor, I want to perform a full-text search of article body, title, and author name, so that I can find what I want.

## Sample 72: d532cf0ca2e37f2d6fd4f8bb71441e0c

Task: bug_report_refinement

### Original input

original_text:

created attachment 8875550
page with a date field and another one in a frame

steps to reproduce:
1. click a date input outside the frame
2. click a date input inside the frame
3. click a date input outside the frame
4. click a date input inside the frame

expected behaviour:
date chooser will open.

actual behaviour:
date chooser is not opened.

frames are commonly used by jsfiddle where i first noticed this. there are actually many variations on the bug, looks like state management gone wrong.

### Output A

Summary  
Created attachment 8875550. Page with a date field and another one in a frame. Frames are commonly used by jsfiddle, where this issue was first noticed. There are many variations of the bug, suggesting state management gone wrong.

Steps  
1. Click a date input outside the frame.
2. Click a date input inside the frame.
3. Click a date input outside the frame.
4. Click a date input inside the frame.

Expected  
Date chooser will open.

Actual  
Date chooser is not opened.

### Output B

## Summary
A page with a date field outside a frame and another date field inside a frame exhibits a bug where the date chooser does not open after alternating clicks between the two fields. This was first noticed on jsfiddle, which commonly uses frames. There are many variations of the bug, and it appears to be related to state management gone wrong.

## Steps to Reproduce
1. Click a date input outside the frame.
2. Click a date input inside the frame.
3. Click a date input outside the frame.
4. Click a date input inside the frame.

## Expected Behavior
The date chooser will open.

## Actual Behavior
The date chooser is not opened.

## Technical Context
- Created attachment 8875550
- Page with a date field and another one in a frame
- Frames are commonly used by jsfiddle, where this issue was first noticed
- There are many variations of the bug, and it appears to be related to state management gone wrong

## Sample 73: d080cf9385c077b5044dd073d326b572

Task: user_story_refinement

### Original input

original_text:

As a site editor, I want to assign priority numbers to news items, so that I can indicate which articles I want featured most prominently on the site.

### Output A

As a site editor, I want to assign priority numbers to news items, so that I can indicate which articles should be featured most prominently on the site.

### Output B

As a site editor, I want to assign priority numbers to news items, so that I can indicate which articles I want featured most prominently on the site.

## Sample 74: 941dd8bbe74e0149085583c870bc5686

Task: user_story_refinement

### Original input

original_text:

As a l Staff member, I want to search for Property information, so that I can obtain all associated current and historic owners, permits, and applications.

### Output A

As a staff member, I want to search for property information, so that I can obtain all associated current and historic owners, permits, and applications.

### Output B

As a staff member, I want to search for property information, so that I can obtain all associated current and historic owners, permits, and applications.

## Sample 75: 13546b971cc1626fde090d15c49fd42a

Task: user_story_refinement

### Original input

original_text:

As a collection curator, I want to see a dashboard widget showing a summary of recent submissions to my collection.

### Output A

As a collection curator, I want to see a dashboard widget showing a summary of recent submissions to my collection, so that I can review recent activity at a glance.

### Output B

As a collection curator, I want to see a dashboard widget showing a summary of recent submissions to my collection, so that I can review recent activity.

## Sample 76: 1f784c951adc8dc7762539e813d38b41

Task: user_story_refinement

### Original input

original_text:

As an Inspection Staff member, I want to Create an Inspection, so that I can schedule and assign the inspection.

### Output A

As an Inspection Staff member, I want to create an inspection, so that I can schedule and assign the inspection.

### Output B

As an Inspection Staff member, I want to create an inspection, so that I can schedule and assign the inspection.

## Sample 77: f7de5533405d5356d29034f5a10ea9ca

Task: user_story_refinement

### Original input

original_text:

As a Data Publishing User, I want to be able to import data from a Google Spreadsheet, So that I do not have to convert data formats in order to use the data packager.

### Output A

As a Data Publishing User, I want to import data from a Google Spreadsheet so that I do not have to convert data formats in order to use the data packager.

### Output B

As a Data Publishing User, I want to import data from a Google Spreadsheet, so that I do not have to convert data formats in order to use the data packager.

## Sample 78: f9c61081c3646cae7f0d56c03b2e999b

Task: user_story_refinement

### Original input

original_text:

As a sponsor, I want to sponsor a summit that matches my brand, so that I can get exposure to potential customers and otherwise tout my Drupal credentials.

### Output A

As a sponsor, I want to sponsor a summit that matches my brand, so that I can gain exposure to potential customers and highlight my Drupal credentials.

### Output B

As a sponsor, I want to sponsor a summit that matches my brand, so that I can get exposure to potential customers and otherwise tout my Drupal credentials.

## Sample 79: 1a33a5a25db307aa502948c63de6f7cc

Task: bug_report_refinement

### Original input

original_text:

created attachment 9297362
an admittedly sloppy test case

firefox refuses to construct a websocket from webassembly. specifically, `reflect.construct.bind(null, websocket, ["ws://localhost:8080"])` is passed as an import when instantiating a webassembly module.
the module immediately calls the import from the start function.

this problem can be reproduced in the latest version of firefox nightly (build id 20221005094233).

### steps to reproduce
1. download and extract the attached .zip file to some directory.
2. open a terminal (like powershell).
3. run `cd <path to files>` to enter that directory.
4. run `npx serve .` (this assumes npm is installed on your system).
5. open firefox.
6. navigate to http://localhost:3000.

### expected result
the browser attempts to establish a websocket connection, and no error is displayed on the test page.

### actual result
the browser refuses to attempt establishing a websocket connection and throws a securityerror domexception, which is displayed on the test page.

### Output A

### Summary
Firefox refuses to construct a WebSocket from WebAssembly. Specifically, `reflect.construct.bind(null, websocket, ["ws://localhost:8080"])` is passed as an import when instantiating a WebAssembly module, and the module immediately calls the import from the start function.

This problem can be reproduced in the latest version of Firefox Nightly (build id 20221005094233).

### Steps
1. Download and extract the attached `.zip` file to some directory.
2. Open a terminal (like PowerShell).
3. Run `cd <path to files>` to enter that directory.
4. Run `npx serve .` (this assumes npm is installed on your system).
5. Open Firefox.
6. Navigate to `http://localhost:3000`.

### Expected
The browser attempts to establish a websocket connection, and no error is displayed on the test page.

### Actual
The browser refuses to attempt establishing a websocket connection and throws a `SecurityError` DOMException, which is displayed on the test page.

### Output B

## Summary
Firefox refuses to construct a WebSocket from WebAssembly when `reflect.construct.bind(null, websocket, ["ws://localhost:8080"])` is passed as an import during WebAssembly module instantiation.

This problem can be reproduced in the latest version of Firefox Nightly (build id 20221005094233).

## Steps to Reproduce
1. Download and extract the attached `.zip` file to some directory.
2. Open a terminal (like PowerShell).
3. Run `cd <path to files>` to enter that directory.
4. Run `npx serve .` (this assumes npm is installed on your system).
5. Open Firefox.
6. Navigate to `http://localhost:3000`.

## Expected Behavior
The browser attempts to establish a WebSocket connection, and no error is displayed on the test page.

## Actual Behavior
The browser refuses to attempt establishing a WebSocket connection and throws a `SecurityError` DOMException, which is displayed on the test page.

## Technical Context
- Attachment: 9297362
- Test case description: "an admittedly sloppy test case"
- Firefox behavior occurs when `reflect.construct.bind(null, websocket, ["ws://localhost:8080"])` is passed as an import when instantiating a WebAssembly module.
- The WebAssembly module immediately calls the import from the start function.
- Reproduced in Firefox Nightly build id `20221005094233`.

## Sample 80: e9f9cc6b02c8c738211c8c37160703ea

Task: bug_report_refinement

### Original input

original_text:

[affected versions]:
- firefox 51.0a1 (2016-08-31)
 
[affected platforms]:
- windows 10x64, mac os x 10.10.5, ubuntu 16.04x64

[steps to reproduce]:
1. launch firefox.
2. from about:config, enable the devtools.responsive.html.enabled pref.
3. enable rdm.
4. open non-remote(eg. about:config) page the opened tab.
5. select another tab.
6. click on the previous tab.

[expected result]:
- firefox works correctly.

[actual result]:
- firefox becomes unresponsive and in the browser console, the error: assertion failuretabbrowser.xml:3545:23 is thrown.

[regression range]:
- i will search for regression asap.

[additional notes]:
- also, after performing step 4 from str, the rdm tool is displayed as being enabled in the developer menu.

### Output A

## Summary
Firefox becomes unresponsive when switching back to a non-remote page tab after enabling Responsive Design Mode (RDM) with `devtools.responsive.html.enabled` enabled.

## Steps to Reproduce
1. Launch Firefox.
2. From `about:config`, enable the `devtools.responsive.html.enabled` preference.
3. Enable RDM.
4. Open a non-remote page (e.g. `about:config`) in the opened tab.
5. Select another tab.
6. Click on the previous tab.

## Expected Behavior
Firefox works correctly.

## Actual Behavior
Firefox becomes unresponsive, and the following error is thrown in the browser console:
`assertion failuretabbrowser.xml:3545:23`

## Technical Context
- Affected version: Firefox 51.0a1 (2016-08-31)
- Affected platforms:
  - Windows 10 x64
  - Mac OS X 10.10.5
  - Ubuntu 16.04 x64
- Regression range: Not provided
- Additional note: After performing step 4, the RDM tool is displayed as being enabled in the developer menu.

### Output B

### Summary
Firefox 51.0a1 (2016-08-31) becomes unresponsive after switching back to a previously opened non-remote tab with Responsive Design Mode enabled. The browser console shows `assertion failure tabbrowser.xml:3545:23`. Affected platforms: Windows 10 x64, macOS 10.10.5, Ubuntu 16.04 x64.

### Steps
1. Launch Firefox.
2. From `about:config`, enable the `devtools.responsive.html.enabled` preference.
3. Enable RDM.
4. Open a non-remote page (e.g. `about:config`) in the opened tab.
5. Select another tab.
6. Click on the previous tab.

### Expected
Firefox works correctly.

### Actual
Firefox becomes unresponsive, and the browser console shows `assertion failure tabbrowser.xml:3545:23`.

Additional note: After performing step 4, the RDM tool is displayed as enabled in the developer menu.

## Sample 81: 6eb6fc11de8e69181d35af2ea7d922cd

Task: bug_report_refinement

### Original input

original_text:

created attachment 9319753
screenshot 2023-02-23 202306.png

user agent: mozilla/5.0 (windows nt 10.0; win64; x64; rv:109.0) gecko/20100101 firefox/112.0

steps to reproduce:

opened browser, went to a usual bookmark folder and right clicked to "open all bookmarks"  and it again is doing nothing. non functional.   open all in tabs option is now working after this morning's update 112.0a1 (2023-02-24) (64-bit)


actual results:

open all tabs and the right click open all bookmarks from a bookmarks folder had stopped functioning as of yesterday's updates for mozilla nightly.  this morning's update, restored open all in tabs but not the right click select open all bookmarks option which remains non functional.


expected results:

open all bookmarks pretty much does what it implies and opens up all the bookmarks of a given folder you are in after right clicking on it. now it does not. semi functionality workaround restored this morning (2.24.2023) with the open all in tabs functioning again but not the right click on folder option to "open all bookmarks" feature. that remains non functional as of this report writing.   

https://connect.mozilla.org/t5/discussions/bookmark-error-after-update-to-version-110-0/m-p/25743#m10374

### Output A

## Summary
The right-click context menu option **“Open All Bookmarks”** in a bookmark folder is non functional. The separate **“Open All in Tabs”** option was restored after a later update, but the right-click **“Open All Bookmarks”** option remained non functional as of the report writing.

## Steps to Reproduce
1. Open the browser.
2. Go to a usual bookmark folder.
3. Right click the folder.
4. Select **“Open All Bookmarks.”**

## Expected Behavior
Selecting **“Open All Bookmarks”** should open all bookmarks in the selected folder.

## Actual Behavior
Selecting **“Open All Bookmarks”** does nothing and remains non functional.

The report also states that:
- As of yesterday’s updates for Mozilla Nightly, both **“Open All Tabs”** and the right-click **“Open All Bookmarks”** had stopped functioning.
- After this morning’s update, **“Open All in Tabs”** was working again.
- The right-click **“Open All Bookmarks”** option still was not working.

## Technical Context
- Attachment: **9319753** (`screenshot 2023-02-23 202306.png`)
- User agent: **mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0**
- Browser/version mentioned in report:
  - **112.0a1 (2023-02-24) (64-bit)**
- Related link provided in the report:
  - https://connect.mozilla.org/t5/discussions/bookmark-error-after-update-to-version-110-0/m-p/25743#m10374

### Output B

### Summary
After a Mozilla Nightly update, the bookmarks folder context-menu action **“Open All Bookmarks”** stopped functioning. The separate **“Open All in Tabs”** behavior was restored by the update 112.0a1 (2023-02-24) (64-bit), but the right-click folder option remains non-functional.

### Steps
1. Open the browser.
2. Go to a usual bookmark folder.
3. Right-click the folder.
4. Select **“Open All Bookmarks.”**

### Expected
Selecting **“Open All Bookmarks”** from a bookmark folder should open all bookmarks in that folder.

### Actual
The **“Open All Bookmarks”** right-click option on the bookmark folder does nothing and remains non-functional. The **“Open All in Tabs”** option was restored after the morning update, but this folder context-menu action was still broken at the time of the report.



## Sample 82: bc524cc033d15ed2106a8187ae0ff6bb

Task: bug_report_refinement

### Original input

original_text:

created attachment 9245260
alpenglow.gif

**[affected versions]:**
- firefox beta 94.0b4 (build id: 20211010185747) 
- firefox nightly 95.0a1 (build id: 20211011084036)

**[affected platforms]:**
- windows 10 x64;
- macos 11.5.1;
- linux ubuntu 20.04 x64;

**[steps to reproduce]:**
1. open the latest beta build.
2. open a new tab page and navigate to the "about:addons" page.
3. enable the firefox alpenglow theme from the themes section.
4. click and refresh the welcome to firefox tab.
5. navigate through onboarding until the "life in color" slide is displayed.
6. observe the panel.

**[expected result]:**
- the preview area displays the firefox alpenglow theme and its variations.
or
- a fallback of the theme is displayed.

**[actual result]:**
- the preview area is blank and doesn’t show any variations.

**[notes]:**
- the theme variations are displayed when hovering them.
- on the latest nightly, only the preview area is blank, while the variations of the theme are displayed.
- attached is a screen recording of the issue.

### Output A

## Summary
When using the Firefox Alpenglow theme, the preview area in onboarding’s “life in color” slide is blank and does not display theme variations.

## Steps to Reproduce
1. Open the latest beta build.
2. Open a new tab page and navigate to the `about:addons` page.
3. Enable the Firefox Alpenglow theme from the Themes section.
4. Click and refresh the “Welcome to Firefox” tab.
5. Navigate through onboarding until the “life in color” slide is displayed.
6. Observe the panel.

## Expected Behavior
- The preview area displays the Firefox Alpenglow theme and its variations, or
- a fallback of the theme is displayed.

## Actual Behavior
- The preview area is blank and doesn’t show any variations.

## Technical Context
- Attached file: `alpenglow.gif`
- Affected versions:
  - Firefox Beta 94.0b4 (build id: 20211010185747)
  - Firefox Nightly 95.0a1 (build id: 20211011084036)
- Affected platforms:
  - Windows 10 x64
  - macOS 11.5.1
  - Linux Ubuntu 20.04 x64
- Notes:
  - The theme variations are displayed when hovering them.
  - On the latest nightly, only the preview area is blank, while the variations of the theme are displayed.

### Output B

Summary  
Theme preview area is blank when the Firefox Alpenglow theme is enabled and the “life in color” onboarding slide is displayed. Affected versions: Firefox Beta 94.0b4 (build id: 20211010185747) and Firefox Nightly 95.0a1 (build id: 20211011084036). Affected platforms: Windows 10 x64, macOS 11.5.1, and Linux Ubuntu 20.04 x64. Attachment: 9245260 (alpenglow.gif).

Steps  
1. Open the latest beta build.  
2. Open a new tab page and navigate to the “about:addons” page.  
3. Enable the Firefox Alpenglow theme from the themes section.  
4. Click and refresh the “Welcome to Firefox” tab.  
5. Navigate through onboarding until the “life in color” slide is displayed.  
6. Observe the panel.  

Expected  
- The preview area displays the Firefox Alpenglow theme and its variations, or  
- A fallback of the theme is displayed.  

Actual  
- The preview area is blank and doesn’t show any variations.  
- Notes: The theme variations are displayed when hovering them. On the latest Nightly, only the preview area is blank, while the variations of the theme are displayed.

## Sample 83: 6e2c4137eca5ee228e2a5de08edc54dd

Task: bug_report_refinement

### Original input

original_text:

steps to reproduce:
  1. 57.0a1 (2017-08-18) (64-bit) with clean profile
  2. open new tab
  3. click "new to nightly?" icon
  4. check "mark all as complete, and hide the tour"
  5. click outside of the tour box
  6. reload the tab

actual result:
  the "new to nightly?" icon reappears

expected result:
  it doesn't reappear

this issue happens only in the same tab.
if i open another new tab in step 6, it doesn't reappear

### Output A

Summary  
In Firefox 57.0a1 (2017-08-18) 64-bit with a clean profile, the “new to nightly?” icon reappears after the tour is marked complete and hidden, but only when reloading the same tab.

Steps  
1. Use Firefox 57.0a1 (2017-08-18) (64-bit) with a clean profile.  
2. Open a new tab.  
3. Click the “new to nightly?” icon.  
4. Check “mark all as complete, and hide the tour”.  
5. Click outside of the tour box.  
6. Reload the tab.  

Expected  
The “new to nightly?” icon does not reappear.  

Actual  
The “new to nightly?” icon reappears. This issue happens only in the same tab. If another new tab is opened in step 6, it does not reappear.

### Output B

## Summary
In Firefox 57.0a1 (2017-08-18) 64-bit with a clean profile, the "new to nightly?" icon reappears after reloading the same tab, even after marking all items as complete and hiding the tour.

## Steps to Reproduce
1. Use Firefox 57.0a1 (2017-08-18) (64-bit) with a clean profile.
2. Open a new tab.
3. Click the "new to nightly?" icon.
4. Check "mark all as complete, and hide the tour".
5. Click outside of the tour box.
6. Reload the tab.

## Expected Behavior
The "new to nightly?" icon does not reappear.

## Actual Behavior
The "new to nightly?" icon reappears.

## Technical Context
- Issue occurs only in the same tab.
- If another new tab is opened in step 6, the icon does not reappear.

## Sample 84: 94040cbce2a2dad6b3519c1f5b756a5f

Task: bug_report_refinement

### Original input

original_text:

created attachment 8890342
high contrast issue win 7.png

[affected versions]: 
nightly 56.0a1, build id 20170723100358

[affected platforms]:
platforms: windows 7 x 64 

[steps to reproduce]:
1. in windows 7 go to control panel\all control panel items\personalization and select high contrast theme
2. launch nightly
3. go to "about:preferences" and check the main tabs content
4. go to firefox account tab

[expected result]:
preferences main tabs(icon and name) should be properly displayed on windows 7, when using a high contrast theme (screenshot section 2)
android and ios logos are properly displayed when using a high contrast theme(screenshot section 3)

[actual result]:
main tabs names from preferences are not visible on windows 7, when using a high contrast theme
android and ios logos are not visible when using a high contrast theme

also, please note that the "privacy & security" tab icon and name is not visible at all when high contrast theme is enabled(screenshot section 1)

for more details please check the attached screenshot. thank you

### Output A

Summary  
High Contrast issue on Windows 7 x64 in Firefox Nightly 56.0a1 (build id 20170723100358). In `about:preferences`, the main tabs content and Firefox Account tab graphics/text are not properly visible when a Windows high contrast theme is enabled. Attachment provided: `high contrast issue win 7.png`.

Steps  
1. In Windows 7, go to `Control Panel\All Control Panel Items\Personalization` and select a high contrast theme.  
2. Launch Nightly.  
3. Go to `about:preferences` and check the main tabs content.  
4. Go to the Firefox Account tab.  

Expected  
- Preferences main tabs (icon and name) should be properly displayed on Windows 7 when using a high contrast theme.  
- Android and iOS logos are properly displayed when using a high contrast theme.  
- The “Privacy & Security” tab icon and name should be visible when high contrast theme is enabled.  

Actual  
- Main tab names from Preferences are not visible on Windows 7 when using a high contrast theme.  
- Android and iOS logos are not visible when using a high contrast theme.  
- The “Privacy & Security” tab icon and name are not visible at all when high contrast theme is enabled.

### Output B

## Summary
High contrast display issue on Windows 7 x64 in Firefox Nightly 56.0a1 (build 20170723100358). In `about:preferences`, main tabs text/icons are not properly displayed when using a Windows high contrast theme. This also affects Android and iOS logos, and the “Privacy & Security” tab icon and name are not visible at all.

## Steps to Reproduce
1. On Windows 7, go to `Control Panel > All Control Panel Items > Personalization` and select a high contrast theme.
2. Launch Nightly.
3. Go to `about:preferences` and check the main tabs content.
4. Go to the Firefox Account tab.

## Expected Behavior
- Preferences main tabs (icon and name) should be properly displayed on Windows 7 when using a high contrast theme (screenshot section 2).
- Android and iOS logos should be properly displayed when using a high contrast theme (screenshot section 3).

## Actual Behavior
- Main tab names in preferences are not visible on Windows 7 when using a high contrast theme.
- Android and iOS logos are not visible when using a high contrast theme.
- The “Privacy & Security” tab icon and name are not visible at all when the high contrast theme is enabled (screenshot section 1).

## Technical Context
- Attachment: 8890342 (`high contrast issue win 7.png`)
- Affected version: nightly 56.0a1
- Build ID: 20170723100358
- Affected platform: Windows 7 x64

## Sample 85: 6cf0273daa988a8e486f769b5fcd7635

Task: bug_report_refinement

### Original input

original_text:

created attachment 8716525
unified.html

user agent: mozilla/5.0 (x11; linux x86_64) applewebkit/537.36 (khtml, like gecko) ubuntu chromium/48.0.2564.82 chrome/48.0.2564.82 safari/537.36

steps to reproduce:

run the attached sample for renegotiation. currently requires ff46+ until the distributed adapter.js shims ontrack.

note that i am munging the sdp to present a single stream to the receiver. this is probably different from what the existing tests do.


actual results:

video freezes after the audio track is added. rtp still seems to be flowing from looking at about:webrtc


expected results:

audio starts playing.

note that adding audio to a video track works. at least in ff47. ff44 with a custom adapter.js that shims ontrack never starts playing the video but continues playing audio.

### Output A

Summary
Video freezes after an audio track is added during renegotiation. RTP still appears to be flowing when checked in about:webrtc.

Steps
1. Run the attached sample for renegotiation (attachment 8716525, unified.html).
2. Note that this currently requires ff46+ until the distributed adapter.js shims ontrack.
3. Note that the SDP is munged to present a single stream to the receiver, which is probably different from what the existing tests do.

Expected
Audio starts playing.

Actual
Video freezes after the audio track is added. RTP still seems to be flowing from looking at about:webrtc. Note that adding audio to a video track works, at least in ff47. ff44 with a custom adapter.js that shims ontrack never starts playing the video but continues playing audio.

### Output B

## Summary
Video freezes after an audio track is added during renegotiation in the attached sample (`unified.html`).

## Steps to Reproduce
1. Run the attached sample for renegotiation.
2. Use Firefox 46 or later, since this currently requires ff46+ until the distributed `adapter.js` shims `ontrack`.
3. Note that the SDP is munged to present a single stream to the receiver.
4. This may differ from what the existing tests do.

## Expected Behavior
Audio starts playing.

## Actual Behavior
Video freezes after the audio track is added. RTP still seems to be flowing based on `about:webrtc`.

## Technical Context
- Attachment: `8716525` (`unified.html`)
- User agent: `mozilla/5.0 (x11; linux x86_64) applewebkit/537.36 (khtml, like gecko) ubuntu chromium/48.0.2564.82 chrome/48.0.2564.82 safari/537.36`
- Note: adding audio to a video track works, at least in Firefox 47.
- Note: Firefox 44 with a custom `adapter.js` that shims `ontrack` never starts playing the video but continues playing audio.

## Sample 86: 16a7d492bb3a4870b925ab1f7038e6d4

Task: bug_report_refinement

### Original input

original_text:

created attachment 8959789
background_repaint.zip

user agent: mozilla/5.0 (x11; linux x86_64; rv:61.0) gecko/20100101 firefox/61.0
build id: 20180316220124

steps to reproduce:

opened the page contained in the archive with webrender active.

system: amd kaveri 7650k, linux 4.15.9, mesa-17.3.6, radeonsi, amdgpu


actual results:

only when scrolling with the mouse, drawing the page in question sometimes takes a long time. however as soon as i click at a not-yet-painted area it is drawn immediatly: https://youtu.be/re5rkk0looy


looks like some flush operation is missing somewhere.

when scrolled with the keyboard, it works as expected.


expected results:

webrender should behave like the opengl compositor, and simply redraw previously obscured areas when scrolling.

### Output A

### Summary
With WebRender enabled, scrolling a page from the attached archive can sometimes take a long time to repaint certain areas. The issue appears only when scrolling with the mouse; clicking an unpainted area causes it to draw immediately. Keyboard scrolling works as expected.

### Steps to Reproduce
1. Open the page contained in the attached archive (`background_repaint.zip`).
2. Use Firefox with WebRender active.
3. Scroll the page with the mouse.

### Expected Behavior
WebRender should behave like the OpenGL compositor and simply redraw previously obscured areas when scrolling.

### Actual Behavior
- When scrolling with the mouse, drawing the page sometimes takes a long time.
- Clicking a not-yet-painted area causes it to be drawn immediately.
- When scrolling with the keyboard, it works as expected.
- This looks like some flush operation is missing somewhere.
- Video evidence: https://youtu.be/re5rkk0looy

### Technical Context
- Attachment: `background_repaint.zip` (created attachment 8959789)
- User agent: `mozilla/5.0 (x11; linux x86_64; rv:61.0) gecko/20100101 firefox/61.0`
- Build ID: `20180316220124`
- System:
  - AMD Kaveri 7650k
  - Linux 4.15.9
  - Mesa 17.3.6
  - RadeonSI
  - amdgpu

### Output B

Summary
Slow painting occurs in WebRender when scrolling the page from the provided archive with the mouse. Previously unpainted areas are drawn immediately when clicked, suggesting a possible missing flush operation. Keyboard scrolling works as expected. Attachment: 8959789 (background_repaint.zip). Video reference: https://youtu.be/re5rkk0looy

Steps
1. Open the page contained in the attached archive with WebRender active.
2. Scroll the page with the mouse.

Expected
WebRender should behave like the OpenGL compositor and simply redraw previously obscured areas when scrolling.

Actual
Only when scrolling with the mouse, drawing the page in question sometimes takes a long time. However, as soon as a click is made in a not-yet-painted area, it is drawn immediately. When scrolled with the keyboard, it works as expected.

## Sample 87: 051941860f13f70a02a8cf899cd2dced

Task: user_story_refinement

### Original input

original_text:

As a broker team member, I want to add the 00***** and 00FORGN PPoPCode cases to the derivation logic.

### Output A

As a broker team member, I want to add the 00***** and 00FORGN PPoPCode cases to the derivation logic, so that Not provided.

### Output B

As a broker team member, I want to add the 00***** and 00FORGN PPoPCode cases to the derivation logic, so that they are included in the processing rules.

## Sample 88: f1f8698dd836654640b0f5dc455a5433

Task: bug_report_refinement

### Original input

original_text:

created attachment 9173112
pagerangeall.gif

**affected versions**
* 82.0a1 (buildid:20200831091558)
* 81.0b4 (buildid:20200829200810)

**affected platforms**
* windows 10 64bit
* ubuntu 20.04 64bit
* macos 10.14 

**steps to reproduce**
1. launch firefox.
2. access the following [link](https://fr.wikipedia.org/wiki/gr%c3%a8ce).
3. select an invalid custom page range.
4. switch to “all” page range.

**expected result**
* the “all” page range is validated and the user can continue to set different printing options & to print the page.

**actual result**
* the “all” page range is invalidated and the printing options from the ui are locked.

**regression window**
* i will search for a regression asap.

**additional information**
*  for further information regarding this issue please observe the attached screencast.
* [suggested severity] s2

### Output A

## Summary
When printing in Firefox, switching from an invalid custom page range to the “all” page range causes the “all” option to be treated as invalid, which locks the printing UI options.

## Steps to Reproduce
1. Launch Firefox.
2. Access the following link: https://fr.wikipedia.org/wiki/gr%c3%a8ce
3. Select an invalid custom page range.
4. Switch to “all” page range.

## Expected Behavior
The “all” page range is validated, and the user can continue setting different printing options and print the page.

## Actual Behavior
The “all” page range is invalidated, and the printing options in the UI are locked.

## Technical Context
- Affected versions:
  - 82.0a1 (buildid:20200831091558)
  - 81.0b4 (buildid:20200829200810)
- Affected platforms:
  - Windows 10 64bit
  - Ubuntu 20.04 64bit
  - macOS 10.14
- Attachment: 9173112 (`pagerangeall.gif`)
- Regression window: Not provided.
- Additional information: A screencast is attached for further information.
- Suggested severity: s2

### Output B

Summary
Printing UI issue in Firefox where switching from an invalid custom page range to “all” causes the “all” page range to be invalidated and locks printing options in the UI.

Steps
1. Launch Firefox.
2. Access the following link: https://fr.wikipedia.org/wiki/gr%c3%a8ce
3. Select an invalid custom page range.
4. Switch to “all” page range.

Expected
The “all” page range is validated and the user can continue to set different printing options and print the page.

Actual
The “all” page range is invalidated and the printing options from the UI are locked.

Additional context
- Created attachment: 9173112 (`pagerangeall.gif`)
- Affected versions:
  - 82.0a1 (buildid: 20200831091558)
  - 81.0b4 (buildid: 20200829200810)
- Affected platforms:
  - Windows 10 64bit
  - Ubuntu 20.04 64bit
  - macOS 10.14
- Regression window: Not provided
- Suggested severity: S2

## Sample 89: 4e966d7e735859745b3ff49c0690c9b0

Task: bug_report_refinement

### Original input

original_text:

user agent: mozilla/5.0 (windows nt 10.0; wow64; rv:47.0) gecko/20100101 firefox/47.0
build id: 20160531183335

steps to reproduce:

go here in nightly - https://www.webrtc-experiment.com/recordrtc/

pick "audio"

do a recording.

press stop.

it will play it back. in nightly it will be slowed down.

do the same in stable or beta firefox and you will hear it play back at actual speed.

i actually discovered this because i used webrtc mic in a song identification addon i made here, and i hit this problem - https://addons.mozilla.org/en-us/firefox/addon/songifier/


actual results:

in firefox nightly, webrtc recording is slowed by 100%. so duration is 2x the actual duration.


expected results:

recording should not be slowed.

### Output A

Summary
WebRTC audio recordings played back in Firefox Nightly are slowed down by 100%, resulting in playback duration being 2x the actual duration. This does not occur in stable or beta Firefox.

Steps
1. Go to https://www.webrtc-experiment.com/recordrtc/ in Firefox Nightly.
2. Select "audio".
3. Start a recording.
4. Press stop.
5. Play back the recording.
6. Compare the behavior with stable or beta Firefox.

Expected
Recording playback should not be slowed down.

Actual
In Firefox Nightly, WebRTC recording playback is slowed down by 100%, so the duration is 2x the actual duration. In stable or beta Firefox, playback occurs at the actual speed.

### Output B

## Summary
WebRTC audio recording playback is slowed down in Firefox Nightly. The recording duration appears to be 2x the actual duration.

## Steps to Reproduce
1. Open the following page in Firefox Nightly: https://www.webrtc-experiment.com/recordrtc/
2. Select **"audio"**.
3. Perform a recording.
4. Press **Stop**.
5. Playback starts automatically.

The issue was also encountered while using WebRTC mic in a song identification addon: https://addons.mozilla.org/en-us/firefox/addon/songifier/

## Expected Behavior
The recording should play back at the actual speed and should not be slowed down.

## Actual Behavior
In Firefox Nightly, WebRTC recording is slowed by 100%, so the duration is 2x the actual duration. In stable or beta Firefox, the same recording plays back at the actual speed.

## Technical Context
- User agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0
- Build ID: 20160531183335
- Browser versions mentioned: Firefox Nightly, stable Firefox, beta Firefox

## Sample 90: 65cf611ba4e64dfff0797d131ffcad74

Task: bug_report_refinement

### Original input

original_text:

affected versions: 45 beta 4 (build id: 20160208194709), latest aurora 46.0a2 and nightly 47.0a1 (from 2016-02-09) with e10s enabled
affected platforms: mac os x 10.9.5, 10.10.5

steps to reproduce:
1. launch firefox.
2. navigate to:
* http://webglsamples.googlecode.com/hg/aquarium/aquarium.html
or
* http://goo.gl/zz1rox
3. drag the tab in a new window.
4. drag it back into the main window.

expected result: the content is properly displayed.

actual result: black artifacts and, intermittently, flickering are visible.

additional notes:
1. screen recording: https://goo.gl/dg5wal
2. not reproducible under ubuntu 12.04 x64, windows 10 x86 nor windows 7 x64. unable to reproduce with 44.0.2rc - 'browser.tabs.remote.autostart' pref has no effect.
3. with e10s disbabled i hit crash bug 1241875: bp-e6f5ab35-4f0c-4c0e-8419-f7b522160211
4. regression range:
(m-c)
last good revision: 0496b5b3e9ef (2015-06-05)
first bad revision: 4a07e1ac3cdf (2015-06-06)
pushlog:
https://hg.mozilla.org/mozilla-central/pushloghtml?fromchange=0496b5b3e9ef&tochange=4a07e1ac3cdf 

(m-i)
last good revision: c7720cbbe62ed6e3b56e0dafa794b94b720a0044
first bad revision: c4d1692d88ee675a949c325227324570c9c946aa
pushlog: https://hg.mozilla.org/integration/mozilla-inbound/pushloghtml?fromchange=c7720cbbe62ed6e3b56e0dafa794b94b720a0044&tochange=c4d1692d88ee675a949c325227324570c9c946aa 

looks like the following bug has the changes which introduced the regression:
https://bugzil.la/1144906

### Output A

## Summary
Black artifacts and intermittent flickering appear when dragging a WebGL tab into a new window and then dragging it back into the main window.

Affected versions:
- 45 beta 4 (build id: 20160208194709)
- Latest Aurora 46.0a2
- Nightly 47.0a1 (from 2016-02-09)

Affected platforms:
- Mac OS X 10.9.5
- Mac OS X 10.10.5

E10s enabled.

## Steps to Reproduce
1. Launch Firefox.
2. Navigate to one of the following:
   - http://webglsamples.googlecode.com/hg/aquarium/aquarium.html
   - http://goo.gl/zz1rox
3. Drag the tab into a new window.
4. Drag it back into the main window.

## Expected Behavior
The content is properly displayed.

## Actual Behavior
Black artifacts and, intermittently, flickering are visible.

## Technical Context
Additional notes:
1. Screen recording: https://goo.gl/dg5wal
2. Not reproducible under Ubuntu 12.04 x64, Windows 10 x86, or Windows 7 x64.
3. Unable to reproduce with 44.0.2rc - `browser.tabs.remote.autostart` pref has no effect.
4. With e10s disabled, crash bug 1241875 occurs: `bp-e6f5ab35-4f0c-4c0e-8419-f7b522160211`

Regression range:
- (m-c)
  - Last good revision: `0496b5b3e9ef` (2015-06-05)
  - First bad revision: `4a07e1ac3cdf` (2015-06-06)
  - Pushlog: https://hg.mozilla.org/mozilla-central/pushloghtml?fromchange=0496b5b3e9ef&tochange=4a07e1ac3cdf
- (m-i)
  - Last good revision: `c7720cbbe62ed6e3b56e0dafa794b94b720a0044`
  - First bad revision: `c4d1692d88ee675a949c325227324570c9c946aa`
  - Pushlog: https://hg.mozilla.org/integration/mozilla-inbound/pushloghtml?fromchange=c7720cbbe62ed6e3b56e0dafa794b94b720a0044&tochange=c4d1692d88ee675a949c325227324570c9c946aa

Likely related regression:
- https://bugzil.la/1144906

### Output B

Summary  
Black artifacts and intermittent flickering are visible when detaching and reattaching a tab containing WebGL content in Firefox with e10s enabled.

Steps  
1. Launch Firefox.  
2. Navigate to:
   - http://webglsamples.googlecode.com/hg/aquarium/aquarium.html
   - or http://goo.gl/zz1rox
3. Drag the tab into a new window.  
4. Drag it back into the main window.  

Expected  
The content is properly displayed.

Actual  
Black artifacts and, intermittently, flickering are visible.

Additional context:
- Affected versions: 45 beta 4 (build id: 20160208194709), latest Aurora 46.0a2, and Nightly 47.0a1 (from 2016-02-09) with e10s enabled.
- Affected platforms: Mac OS X 10.9.5, 10.10.5.
- Screen recording: https://goo.gl/dg5wal
- Not reproducible under Ubuntu 12.04 x64, Windows 10 x86, or Windows 7 x64.
- Unable to reproduce with 44.0.2rc; `browser.tabs.remote.autostart` pref has no effect.
- With e10s disabled, crash bug 1241875 occurs: bp-e6f5ab35-4f0c-4c0e-8419-f7b522160211.
- Regression range:
  - mozilla-central: last good revision 0496b5b3e9ef (2015-06-05), first bad revision 4a07e1ac3cdf (2015-06-06)
  - mozilla-inbound: last good revision c7720cbbe62ed6e3b56e0dafa794b94b720a0044, first bad revision c4d1692d88ee675a949c325227324570c9c946aa
- Suspected introducing bug: https://bugzil.la/1144906

## Sample 91: 5006e1a9c12890a64566d584c85b261a

Task: bug_report_refinement

### Original input

original_text:

created attachment 9105557
screen shot 2019-10-31 at 14.21.58.png

## steps to reproduce
- go to https://codepen.io/fvsch/pen/ylbmewe
- open the inspector
- use the frame switcher dropdown to select the iframe as the currently inspected document

## expected
the markup view updates to show the iframe contents.

## actual result
the markup view stops rendering at the root node.

[mozregression range](https://hg.mozilla.org/mozilla-central/pushloghtml?fromchange=9277be3613ca5109ae4007a512ee75856f8f1120&tochange=0ec9e4f71228e0cdc4bcb325fe9095ede13df7d5). likely regressed by changes in bug 1590050.

## error in console

```
typeerror: "container.editor is undefined"
    shownode resource://devtools/client/inspector/markup/markup.js:1577
    process resource://gre/modules/promise-backend.js:961
    walkerloop resource://gre/modules/promise-backend.js:845
    schedulewalkerloop resource://gre/modules/promise-backend.js:775
    schedulepromise resource://gre/modules/promise-backend.js:809
    completepromise resource://gre/modules/promise-backend.js:741
    checkforcompletion resource://gre/modules/promise-backend.js:596
    resolver resource://gre/modules/promise-backend.js:603
markup.js:425:15
```

### Output A

## Summary
When using Firefox DevTools Inspector on a page with an iframe, switching the inspected document to the iframe causes the markup view to stop rendering past the root node.

## Steps to Reproduce
1. Go to https://codepen.io/fvsch/pen/ylbmewe
2. Open the Inspector.
3. Use the frame switcher dropdown to select the iframe as the currently inspected document.

## Expected Behavior
The markup view updates to show the iframe contents.

## Actual Behavior
The markup view stops rendering at the root node.

A console error is shown:
```text
typeerror: "container.editor is undefined"
    shownode resource://devtools/client/inspector/markup/markup.js:1577
    process resource://gre/modules/promise-backend.js:961
    walkerloop resource://gre/modules/promise-backend.js:845
    schedulewalkerloop resource://gre/modules/promise-backend.js:775
    schedulepromise resource://gre/modules/promise-backend.js:809
    completepromise resource://gre/modules/promise-backend.js:741
    checkforcompletion resource://gre/modules/promise-backend.js:596
    resolver resource://gre/modules/promise-backend.js:603
markup.js:425:15
```

## Technical Context
- Attachment: 9105557
- Screenshot: `screen shot 2019-10-31 at 14.21.58.png`
- mozregression range: https://hg.mozilla.org/mozilla-central/pushloghtml?fromchange=9277be3613ca5109ae4007a512ee75856f8f1120&tochange=0ec9e4f71228e0cdc4bcb325fe9095ede13df7d5
- Likely regressed by changes in bug 1590050.

### Output B

## Summary
When switching the Inspector to inspect an iframe on the CodePen page, the Markup view stops rendering after the root node. A console error is shown: `TypeError: "container.editor is undefined"` in `resource://devtools/client/inspector/markup/markup.js:1577`. A mozregression range is provided: https://hg.mozilla.org/mozilla-central/pushloghtml?fromchange=9277be3613ca5109ae4007a512ee75856f8f1120&tochange=0ec9e4f71228e0cdc4bcb325fe9095ede13df7d5. It is likely regressed by changes in bug 1590050.

## Steps
1. Go to https://codepen.io/fvsch/pen/ylbmewe
2. Open the Inspector
3. Use the frame switcher dropdown to select the iframe as the currently inspected document

## Expected
The markup view updates to show the iframe contents.

## Actual
The markup view stops rendering at the root node.

Console error:
```text
typeerror: "container.editor is undefined"
    shownode resource://devtools/client/inspector/markup/markup.js:1577
    process resource://gre/modules/promise-backend.js:961
    walkerloop resource://gre/modules/promise-backend.js:845
    schedulewalkerloop resource://gre/modules/promise-backend.js:775
    schedulepromise resource://gre/modules/promise-backend.js:809
    completepromise resource://gre/modules/promise-backend.js:741
    checkforcompletion resource://gre/modules/promise-backend.js:596
    resolver resource://gre/modules/promise-backend.js:603
markup.js:425:15
```

## Sample 92: bd6cbadacb21a1720b41ae965a60a0a2

Task: user_story_refinement

### Original input

original_text:

As a MedicalCaregiver, I want to use video calls in case of emergency.

### Output A

As a MedicalCaregiver, I want to use video calls in case of emergency, so that Not provided.

### Output B

As a MedicalCaregiver, I want to use video calls in case of an emergency, so that I can communicate with others remotely during urgent situations.

## Sample 93: 54a2b3e36a981bcc1fb5a7578ad5a862

Task: bug_report_refinement

### Original input

original_text:

created attachment 9194874
fingerprinting_cfr.gif

*[affected versions]:*
- firefox nightly 86.0a1, build id 20201228205313

*[affected platforms]:*
- windows 10 x64
- macos 10.15
- ubuntu 20 x64

*[prerequisites]:*
- have a clean new profile.

*[steps to reproduce]:*
1. open the browser with the profile from prerequisites and navigate to the "https://edition.cnn.com/" page.
2. open 2 new tabs and navigate to cnn in both of them.
3. navigate to cnn in a new tab and observe the behavior.

*[expected result]:*
- the "fingerprinters protection" cfr doorhanger is displayed.

*[actual result]:*
- the doorhanger is not displayed.

*[regression]:*
- i have managed to find a regression window, using the mozregression tool. here are the results: 
12:55.39 info: last good revision: aa95b6225a7416d52310f0a90152a91788527d33
12:55.39 info: first bad revision: 60e886fcc3db9f0ed4e173732653ef00ccead3c3
12:55.39 info: pushlog:
https://hg.mozilla.org/integration/autoland/pushloghtml?fromchange=aa95b6225a7416d52310f0a90152a91788527d33&tochange=60e886fcc3db9f0ed4e173732653ef00ccead3c3
- from the pushlog, it seems that bug 1682821  might have caused this issue.

*[notes]:*
- attached a screen recording of the issue:

@andreio could you please take a look at this?

### Output A

## Summary
In Firefox Nightly 86.0a1, the “fingerprinters protection” CFR doorhanger is not displayed when navigating to CNN after opening multiple CNN tabs in a clean new profile.

## Steps to Reproduce
1. Open the browser with a clean new profile.
2. Navigate to `https://edition.cnn.com/`.
3. Open 2 new tabs and navigate to CNN in both of them.
4. Navigate to CNN in a new tab and observe the behavior.

## Expected Behavior
The “fingerprinters protection” CFR doorhanger is displayed.

## Actual Behavior
The doorhanger is not displayed.

## Technical Context
- **Affected version:** Firefox Nightly 86.0a1
- **Build ID:** 20201228205313
- **Affected platforms:**
  - Windows 10 x64
  - macOS 10.15
  - Ubuntu 20 x64
- **Prerequisite:** Clean new profile
- **Attachment:** `fingerprinting_cfr.gif`
- **Regression info:**
  - Last good revision: `aa95b6225a7416d52310f0a90152a91788527d33`
  - First bad revision: `60e886fcc3db9f0ed4e173732653ef00ccead3c3`
  - Pushlog: `https://hg.mozilla.org/integration/autoland/pushloghtml?fromchange=aa95b6225a7416d52310f0a90152a91788527d33&tochange=60e886fcc3db9f0ed4e173732653ef00ccead3c3`
- Suspected related bug: Bug 1682821


### Output B

Summary
Fingerprinting protection CFR doorhanger is not displayed on Firefox Nightly 86.0a1 after navigating to CNN in multiple tabs. A screen recording is attached: attachment 9194874 (`fingerprinting_cfr.gif`).

Steps
1. Open the browser with a clean new profile and navigate to `https://edition.cnn.com/`.
2. Open 2 new tabs and navigate to CNN in both of them.
3. Navigate to CNN in a new tab and observe the behavior.

Expected
The "fingerprinters protection" CFR doorhanger is displayed.

Actual
The doorhanger is not displayed.



## Sample 94: ec1d1ebe484f0ffc72d533ba91e60ffc

Task: bug_report_refinement

### Original input

original_text:

created attachment 9019673
rec of the issue.gif

[affected versions]:
- firefox 63 build id - 20181018182531
- firefox 64.0b3 build id - 20181022150107
- firefox 65.0a1 build id - 20181023222913

[affected platforms]:
- all windows

[prerequisites]:
- have a new firefox profile.
- have the following prefs in the "about:config" page;
	- "browser.newtabpage.activity-stream.asrouter.messageproviders" pref set to "[{"id":"cfr", "cohort": "three_per_day", "frequency": {"custom": [{"period": "daily", "cap": 1}]}, "type":"local","localprovider":"cfrmessageprovider","enabled":true}]";
	- "browser.newtabpage.activity-stream.asrouter.devtoolsenabled" set to "true"

[steps to reproduce]:
1. open the browser with the profile from prerequisites.
2. open a new tab and click the "facebook" top site.
3. repeat step two another four times and restart the browser.
4. go to the "about:newtab#asrouter" page.
5. scroll down to the "facebook_container_3" section.
6. observe the number of the displayed impressions.
 
[expected result]:
- only one impression was displayed.

[actual result]:
- two impressions were displayed.

[notes]:
- this issue affects the "experiment 2" branch, where the recommendation should be displayed three times per add-on.
- this issue is also reproducible with the "cfr recommendation" for the "reddit" website.
- this issue is not reproducible on linux and mac.
- attached a screen recording of the issue.

### Output A

## Summary
Created attachment 9019673: screen recording of the issue.

Affected versions:
- Firefox 63 build id 20181018182531
- Firefox 64.0b3 build id 20181022150107
- Firefox 65.0a1 build id 20181023222913

Affected platforms:
- All Windows

Prerequisites:
- Have a new Firefox profile.
- Set the following prefs in `about:config`:
  - `browser.newtabpage.activity-stream.asrouter.messageproviders` to `[{"id":"cfr", "cohort": "three_per_day", "frequency": {"custom": [{"period": "daily", "cap": 1}]}, "type":"local","localprovider":"cfrmessageprovider","enabled":true}]`
  - `browser.newtabpage.activity-stream.asrouter.devtoolsenabled` to `true`

Additional context:
- This issue affects the "experiment 2" branch, where the recommendation should be displayed three times per add-on.
- The issue is also reproducible with the CFR recommendation for the "reddit" website.
- The issue is not reproducible on Linux and Mac.

## Steps
1. Open the browser with the profile from the prerequisites.
2. Open a new tab and click the "facebook" top site.
3. Repeat step 2 another four times and restart the browser.
4. Go to the `about:newtab#asrouter` page.
5. Scroll down to the `facebook_container_3` section.
6. Observe the number of the displayed impressions.

## Expected
- Only one impression was displayed.

## Actual
- Two impressions were displayed.

### Output B

## Summary
On Windows, Firefox shows an incorrect number of displayed impressions in the `about:newtab#asrouter` page for top site recommendations. With the specified configuration, the issue occurs in the `experiment 2` branch and can also be reproduced with the CFR recommendation for the `reddit` website.

## Steps to Reproduce
1. Open Firefox using a new profile.
2. Set the following prefs in `about:config`:
   - `browser.newtabpage.activity-stream.asrouter.messageproviders` = `[{"id":"cfr", "cohort": "three_per_day", "frequency": {"custom": [{"period": "daily", "cap": 1}]}, "type":"local","localprovider":"cfrmessageprovider","enabled":true}]`
   - `browser.newtabpage.activity-stream.asrouter.devtoolsenabled` = `true`
3. Open a new tab and click the `facebook` top site.
4. Repeat step 3 another four times and restart the browser.
5. Go to `about:newtab#asrouter`.
6. Scroll down to the `facebook_container_3` section.
7. Observe the number of displayed impressions.

## Expected Behavior
Only one impression should be displayed.

## Actual Behavior
Two impressions are displayed.

## Technical Context
- Affects versions:
  - Firefox 63 build ID `20181018182531`
  - Firefox 64.0b3 build ID `20181022150107`
  - Firefox 65.0a1 build ID `20181023222913`
- Affected platforms: all Windows
- The issue affects the `experiment 2` branch, where the recommendation should be displayed three times per add-on.
- The issue is also reproducible with the CFR recommendation for the `reddit` website.
- The issue is not reproducible on Linux and Mac.
- Attachment: `9019673` (`rec of the issue.gif`)

## Sample 95: f5f2276780d4525c5b78ac6e7eea99f6

Task: user_story_refinement

### Original input

original_text:

As a Consumer, I want to know that the data I am downloading is good and can be relied on, so that that I don't have to check it myself or run into annoying bugs later on.

### Output A

As a Consumer, I want to know that the data I am downloading is good and can be relied on, so that I don't have to check it myself or run into annoying bugs later on.

### Output B

As a Consumer, I want to know that the data I am downloading is reliable and of good quality, so that I do not have to verify it myself or encounter bugs later on.

## Sample 96: 6caf691271d20a1a1bfed24fe5582305

Task: bug_report_refinement

### Original input

original_text:

build: 6.0b6
device: iphone 6s
ios: 10.1.1

steps to reproduce:
1. go to google.com
2. tap the share button 
3. tap 'send tabs' 
4. tap cancel to dismiss send tabs list
5. repeat steps 2 to 4

actual results:
- the list with sync devices is not populated. this list will only be populated on the first attempt to send tabs. after a session restore the list will be populated again.

expected results:
- the list should be populated.

see video:
https://www.youtube.com/watch?v=qi9qep42pue

### Output A

## Summary
On build 6.0b6, the sync devices list in **Send Tabs** is not populated after dismissing it and trying again in the same session.

## Steps to Reproduce
1. Go to google.com.
2. Tap the share button.
3. Tap **Send Tabs**.
4. Tap **Cancel** to dismiss the Send Tabs list.
5. Repeat steps 2 to 4.

## Expected Behavior
The list should be populated.

## Actual Behavior
The list with sync devices is not populated. This list is only populated on the first attempt to send tabs. After a session restore, the list is populated again.

## Technical Context
- Build: 6.0b6
- Device: iPhone 6s
- iOS: 10.1.1
- Video: https://www.youtube.com/watch?v=qi9qep42pue

### Output B

Summary  
build: 6.0b6  
device: iPhone 6s  
iOS: 10.1.1  
Issue occurs with the Send Tabs sync device list after repeating the flow following a cancel action.

Steps  
1. Go to google.com.  
2. Tap the share button.  
3. Tap "send tabs".  
4. Tap cancel to dismiss the Send Tabs list.  
5. Repeat steps 2 to 4.

Expected  
The list should be populated.

Actual  
The list with sync devices is not populated. This list is only populated on the first attempt to send tabs. After a session restore, the list will be populated again.

## Sample 97: abcd625438caeaca2c6be1767a99f640

Task: user_story_refinement

### Original input

original_text:

As an Inspector, I want to Conduct Inspections, so that I can validate Customer compliance with code and regulations and provide results of the inspection to the Customer.

### Output A

As an Inspector, I want to conduct inspections, so that I can validate customer compliance with codes and regulations and provide the inspection results to the customer.

### Output B

As an Inspector, I want to conduct inspections, so that I can validate customer compliance with code and regulations and provide the results of the inspection to the customer.

## Sample 98: 6830ce31a03840b47e912218422ba55c

Task: bug_report_refinement

### Original input

original_text:

created attachment 9292036
rec of the issue.gif

**[affected versions]:**
- firefox nightly 106.0a1 - build id: 20220829094551

**[affected platforms]:**
- windows 10 x64
- macos 11.6.5
- linux mint 20.2 x64

**[prerequisites]:**
- have the "browser.newtabpage.activity-stream.asrouter.devtoolsenabled" pref set to "true" in the "about:config" page.
- have a custom theme enabled from "about:addons>themes".

**[steps to reproduce]:**
1. open the browser with the profile from the prerequisites.
2. navigate to the "about:newtab#asrouter" page and select the "targeting" section.
3. search for the "userenabledactivecolorway" parameter and observe the displayed value.

**[expected result]:**
- the "userenabledactivecolorway" parameter is set to "false".

**[actual result]:**
- the "userenabledactivecolorway" targeting parameter from the asrouter page has no value.

**[additional notes]:**
- if a colorway theme is applied the "userenabledactivecolorway" parameter is set to "true".
- if a browser default theme is applied the "userenabledactivecolorway" parameter is set to "false".
- attached a screen recording of the issue.

### Output A

**Summary**
In Firefox Nightly 106.0a1, on Windows 10 x64, macOS 11.6.5, and Linux Mint 20.2 x64, the `userenabledactivecolorway` targeting parameter on `about:newtab#asrouter` appears without a value when a custom theme is enabled and `browser.newtabpage.activity-stream.asrouter.devtoolsenabled` is set to `true`. Attachment 9292036 includes a screen recording of the issue.

**Steps**
1. Open the browser with the profile from the prerequisites.
2. Navigate to `about:newtab#asrouter` and select the `targeting` section.
3. Search for the `userenabledactivecolorway` parameter and observe the displayed value.

**Expected**
- The `userenabledactivecolorway` parameter is set to `false`.

**Actual**
- The `userenabledactivecolorway` targeting parameter from the asrouter page has no value.



### Output B

## Summary
In Firefox Nightly 106.0a1, the `userenabledactivecolorway` targeting parameter on the `about:newtab#asrouter` page does not show a value when a custom theme is enabled, even though it is expected to be `false`.

## Steps to Reproduce
1. Open the browser with a profile where:
   - `browser.newtabpage.activity-stream.asrouter.devtoolsenabled` is set to `true` in `about:config`
   - a custom theme is enabled from `about:addons > Themes`
2. Navigate to `about:newtab#asrouter`.
3. Select the `targeting` section.
4. Search for the `userenabledactivecolorway` parameter and observe the displayed value.

## Expected Behavior
The `userenabledactivecolorway` parameter is set to `false`.

## Actual Behavior
The `userenabledactivecolorway` targeting parameter on the asrouter page has no value.

## Technical Context
- Affected version:
  - Firefox Nightly 106.0a1, build ID `20220829094551`
- Affected platforms:
  - Windows 10 x64
  - macOS 11.6.5
  - Linux Mint 20.2 x64
- Prerequisites:
  - `browser.newtabpage.activity-stream.asrouter.devtoolsenabled` pref set to `true`
  - custom theme enabled from `about:addons > Themes`
- Additional notes:
  - If a colorway theme is applied, `userenabledactivecolorway` is set to `true`.
  - If a browser default theme is applied, `userenabledactivecolorway` is set to `false`.
  - A screen recording of the issue was attached.

## Sample 99: 49eb6b585204194a509732a7f81a9479

Task: user_story_refinement

### Original input

original_text:

As a Developer, I want to add the updates on a FABS submission to be modified when the publishStatus changes, so that I know when the status of the submission has changed.

### Output A

As a Developer, I want the updates on a FABS submission to be modified when the publishStatus changes, so that I know when the status of the submission has changed.

### Output B

As a Developer, I want updates to a FABS submission to be modified when the publishStatus changes, so that I know when the submission status has changed.

## Sample 100: 822fbe9f9e4ae100f393199dcbf973aa

Task: user_story_refinement

### Original input

original_text:

As a researcher, I want to recruit for the last round of user research, so that we can summarize our findings and synthesize results.

### Output A

As a researcher, I want to recruit for the last round of user research, so that we can summarize our findings and synthesize results.

### Output B

As a researcher, I want to recruit participants for the final round of user research, so that we can summarize our findings and synthesize the results.
