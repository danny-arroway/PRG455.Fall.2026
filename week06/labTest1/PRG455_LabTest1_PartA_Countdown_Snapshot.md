# PRG455 — Event Driven Programming
## Lab Test 1 — Part A: Countdown Snapshot

**Marks:** 15 of the 100-point Lab Test 1 rubric (Lab Test 1 as a
whole is worth 22% of the final course grade) · **Scope:** Weeks 1–5
(environment/firmware, MicroPython & Run Once, label/button, camera &
image widget)

---

### Scenario

You're building a simple "photo booth" program for the CoreS3: press
one button, get a few seconds to get ready, and the device takes your
picture automatically — no need to hold a pose while fumbling for a
second button press.

### What You're Building

A single-screen M5UI application with:

1. A **title**.
2. A button labelled exactly **"Snapshot"**.
3. A **live camera preview**, visible before Snapshot is pressed, so
   you can actually see what you're about to photograph.
4. A **countdown display** that appears when Snapshot is pressed,
   showing `5`, `4`, `3`, `2`, `1`, `0`, one value per second, in that
   exact order, then captures a photo the instant it reaches `0`.
5. The captured photo, saved to the CoreS3's flash filesystem as
   **`photo.jpg`**.

There is no `M5Image` redisplay requirement in Part A — the point of
this part is the countdown-then-capture sequence and successfully
retrieving the result afterward, not building another photo viewer.
(Lab 5 already covered displaying a captured photo back on the
device — this part deliberately asks you to do something Lab 5
didn't: get the file **off** the device.)

---

### Functional Requirements

**FR1 — Title.** Visible, legible, doesn't overlap the Snapshot
button or the countdown display.

**FR2 — Snapshot button.** A button whose visible label is exactly
**"Snapshot"** (capital S, no other text). Pressing it starts the
sequence in FR4. Pressing it again while a countdown is already in
progress is undefined behaviour — you do not need to guard against
it, but your program must not crash if a student's test script or a
double-tap triggers it.

**FR3 — Live camera preview.** Before Snapshot is pressed, and
whenever a countdown isn't actively running, the screen must show a
**live camera feed** — not a blank or static area — so the person
using the device can see what they're about to photograph. Use the
same `M5.Lcd.show()` pattern from Lecture 5 §3, called every `loop()`
pass. Per Lecture 5 §1, this draws directly to raw screen coordinates,
bypassing M5UI entirely, so its rectangle must not overlap any M5UI
widget's position, on either axis — including the countdown display
in FR4.

**FR4 — Countdown sequence.** On Snapshot press, in order:

1. Display `5` somewhere clearly visible on screen, in a region that
   does **not** overlap the live preview rectangle from FR3 — while
   the countdown handler is running, `loop()` isn't executing, so the
   preview will show whatever its last frame was during the count;
   the countdown digit still must not visually collide with that
   region.
2. Wait one second.
3. Display `4`.
4. Wait one second.
5. Continue this pattern through `3`, `2`, `1`, `0` — six numbers
   total, five one-second waits between them.
6. The instant `0` is displayed, capture a photo with
   `camera.snapshot()`.

This is a **blocking** sequence — it is acceptable, and expected at
this stage of the course, for the rest of the UI to be unresponsive
while the countdown runs. You do not need `loop()`-driven timing for
this part. A straightforward `time.sleep(1)` between each displayed
number is sufficient and is exactly what's expected here.

**A gotcha specific to this part:** setting a label's text with
`set_text()` only marks it dirty — it does not, by itself, paint
anything to the physical screen. The actual screen refresh happens as
part of `M5.update()`, the same call responsible for touch polling in
every `loop()` you've written so far. If your countdown handler calls
`set_text()` six times back-to-back with only `time.sleep()` in
between and **no `M5.update()` call inside the loop**, all six values
will be computed and set correctly in code, but **none of them will
ever appear on the physical screen** — the display will jump straight
from blank to whatever the final state is once the handler returns.
This is a real, confirmed failure mode on this hardware, not a
hypothetical: call `M5.update()` after every `set_text()` inside the
countdown loop, before the `time.sleep()` that follows it.

**FR5 — Save the photo as `photo.jpg`.** Encode the captured frame to
JPEG and write it to `/flash/photo.jpg` — this exact filename, not a
variation, since retrieval in FR6 depends on knowing the name in
advance. Use the encode-and-write pattern from Lecture 5 §4: positional
`jpg.encode(frame, quality)`, binary write mode (`"wb"`), and a
`try`/`except` around the whole capture-and-save step so a failure
here doesn't crash the program silently.

**FR6 — Retrieve the photo to your laptop.** After confirming
`photo.jpg` exists on the device (e.g. with `os.listdir("/flash")` and
`os.stat("/flash/photo.jpg")` from the WebTerminal, per Lecture 5
§4.1), get the actual image file off the CoreS3 and onto your laptop,
by whatever means the UIFlow2 web editor's device file browser
provides. **This step is graded** — see Submission Instructions and
the rubric.

**FR7 — Camera initialization.** `camera.init(pixformat=camera.RGB565,
framesize=camera.QVGA)` in `setup()`, exactly as covered in Lecture 5.

---

### Code Requirements

- **Required header block.** Every submitted `.py` file must begin
  with the following header, as comments, with all fields filled in —
  no placeholders left in the submitted version:

  ```python
  # File:                 prg455.263.testX_partA.py
  # Author:               first, lastname
  # Date Submitted:       mm/dd/yyyy
  # Purpose:              solution to Lab Test 1, Part A
  # Student Number:       Seneca Polytechnic student number
  # Seneca E-mail:        Seneca student e-mail address
  # Seneca username:      Seneca My.Seneca username
  # Course Code/Section:  PRG455X
  # GitHub URL:           Student GitHub web address
  # Core S3 Device MAC:   (eg. 1CFED5BD87D2)
  ```

  Align the second field five tabs from the first, exactly as shown
  above — the same header required on every lab, lab test, and
  project submission this term. This header is required in **this**
  `.py` file specifically; it's independent of anything Part B does.
- Standard `setup()` / `loop()` structure, `M5.begin()` → `m5ui.init()`
  → build widgets → `page0.screen_load()`, with the try/except
  error-reporting wrapper used throughout this course.
- `time.sleep()` is permitted and expected in the Snapshot handler for
  this part only — this is the one place in the course so far where a
  blocking call inside an event handler is the correct, intended
  design, not a mistake to avoid.
- Comment your code — explain why a blocking countdown is acceptable
  here specifically, and what would need to change if it weren't
  (tie this back to Lecture 6 §2's poll-driven/event-driven
  distinction, even though you aren't required to implement the
  non-blocking version).
- If you use an AI tool anywhere in building this: **commit your own
  working code before you modify it further with AI assistance**, and
  keep `PROMPTS.md` up to date — same standard as every lab this term.

---

### Submission Instructions

1. Create a `labTest1/partA/` directory in your course GitHub
   repository (the private repo with `danny-arroway` added as a
   collaborator).
2. Place your final `.py` file **and** the retrieved `photo.jpg` in
   `labTest1/partA/`. The photo must be the actual file pulled off
   your CoreS3 for this test session — not a placeholder, a photo from
   a previous lab, or an image from another source.
3. Commit and push before the end of the test window —
   **[INSTRUCTOR: insert exact cutoff time]**.
4. `PROMPTS.md` (shared with Part B, in your repo root) must be
   present and current if you used AI assistance.

---

### Marking Rubric — 15 Points (of Lab Test 1's 100-point total)

| # | Criterion | What's checked | Points |
|---|---|---|---|
| 1 | Title and Snapshot button | Title visible, no overlap; button present and labelled exactly "Snapshot" | 2 |
| 2 | Live camera preview | Visible and updating continuously before Snapshot is pressed, drawn via `M5.Lcd.show()`, never overlapping any M5UI widget | 2 |
| 3 | Countdown sequence correctness | Displays 5,4,3,2,1,0 in order, one per second, visible and legible at each step — i.e. actually appears on the physical screen, not just set in code | 4 |
| 4 | Capture timing | Photo is captured at the instant `0` is displayed — not before, not after an extra delay | 2 |
| 5 | Save correctness | Saved as exactly `/flash/photo.jpg`; positional `jpg.encode()` quality; binary write mode; wrapped in `try`/`except` | 3 |
| 6 | Retrieval | `photo.jpg` is present in `labTest1/partA/` in the submitted repository, and is the actual photo taken during this test session | 2 |
| | **Part A Subtotal** | | **15** |
