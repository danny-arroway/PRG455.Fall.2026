# PRG455 — Event Driven Programming
## Lab Test 1 (Alternate Version): Equipment Loan Kiosk

**Marks:** 100-point Lab Test 1 rubric (Lab Test 1 is worth 22% of
the final course grade) · **Scope:** Weeks 1–5 (environment/firmware,
MicroPython & Run Once, label/button/slider, camera & image widget),
plus independent research into one new API not yet covered in lecture
(see FR12)

This version of Lab Test 1 is a **single part**: one program, one
`.py` file, one submission. Everything below is built on one M5UI
screen.

---

### Scenario

The electronics lab lends out bench equipment to students, and the
paper sign-out sheet keeps going missing. You're turning a CoreS3 into
a self-serve **loan kiosk**. A student places the item in front of the
camera, presses one button, and gets a few seconds to take their
hands off the item and step back before the kiosk photographs it
automatically. The student then uses three sliders to pick the item
type, the loan period, and the item's condition, and presses one more
button to generate a Markdown **loan tag** file.

Each tag records which kiosk issued the loan, so the tag must also
contain the CoreS3's own MAC address. Only the device can supply that
value, and it must be read from the hardware at runtime. It must never
be typed in by hand.

### What You're Building

A single-screen M5UI application with:

1. A **title label** reading exactly **"Loan Kiosk"**.
2. A button labelled exactly **"Photo"**.
3. A **live camera preview** of the item, visible before Photo is
   pressed.
4. A **countdown display** that appears when Photo is pressed. It
   shows `5`, `4`, `3`, `2`, `1`, `0`, one value per second, in that
   exact order, and captures a photo the instant it reaches `0`.
5. The captured photo, saved to the CoreS3's flash filesystem as
   **`item.jpg`**.
6. An **Item slider** with 4 positions, selecting one of
   **"Oscilloscope"**, **"Multimeter"**, **"Power Supply"**,
   **"Signal Gen"**.
7. A **Loan Period slider** with 12 positions, selecting one of
   **"1 day"**, **"2 days"**, **"3 days"**, **"4 days"**,
   **"5 days"**, **"1 week"**, **"2 weeks"**, **"3 weeks"**,
   **"1 month"**, **"2 months"**, **"3 months"**, **"Full term"**,
   in that order.
8. A **Condition slider** with 5 positions, selecting one of
   **"New"**, **"Good"**, **"Worn"**, **"Damaged"**, **"Untested"**.
9. A button labelled exactly **"Issue Loan"**. Pressing it generates
   `loan_tag.md` on the CoreS3's flash filesystem, containing the
   information in FR10.

Each slider needs its own label. The label shows the currently
selected option in words, not the raw numeric slider position, and
updates immediately as the slider moves left or right to any of its
positions.

There is no `M5Image` redisplay requirement. Lab 5 already covered
displaying a captured photo back on the device. This test asks for
two things Lab 5 didn't: getting the generated files **off** the
device, and fitting a live preview and a full control panel onto one
320×240 screen.

---

### Functional Requirements — Capture Sequence

**FR1 — Photo button.** A button whose visible label is exactly
**"Photo"** (capital P, no other text). Pressing it starts the
sequence in FR4. Pressing it again while a countdown is already
running is undefined behaviour. You do not need to guard against it,
but your program must not crash if a test script or a double-tap
triggers it.

**FR2 — Camera initialization.** In `setup()`, call
`camera.init(pixformat=camera.RGB565, framesize=camera.QQVGA)`.
Note that this is **QQVGA (160×120), not QVGA**. This screen has to
hold a preview *and* a full control panel, so the preview is a quarter
of the screen, not most of it. Lecture 5 §2 covers what changes when
you choose a smaller frame size.

**FR3 — Live camera preview.** Before Photo is pressed, and whenever
a countdown isn't running, the screen must show a **live camera feed**
so the student can line up the item. A blank or static area does not
count. Use the `M5.Lcd.show()` pattern from Lecture 5 §3, called on
every `loop()` pass, with a rectangle of exactly **160×120** to match
the QQVGA frame. Lecture 5 §1 explains that this call draws straight
to raw screen coordinates and bypasses M5UI. Its rectangle therefore
must not overlap any M5UI widget's position. Check both axes, and
include the countdown display, all three sliders, and their labels
in the check.

**FR4 — Countdown sequence.** On Photo press, in order:

1. Display `5` somewhere clearly visible on screen, outside the live
   preview rectangle from FR3. While the countdown handler runs,
   `loop()` isn't executing, so the preview keeps showing its last
   frame for the whole count. The countdown digit still must not
   visually collide with that region.
2. Wait one second.
3. Display `4`.
4. Wait one second.
5. Continue this pattern through `3`, `2`, `1`, `0`: six numbers in
   total, with five one-second waits between them.
6. The instant `0` is displayed, capture a photo with
   `camera.snapshot()`.

This is a **blocking** sequence. At this stage of the course it is
acceptable, and expected, for the rest of the UI to be unresponsive
while the countdown runs, sliders included. You do not need
`loop()`-driven timing for this requirement. A plain `time.sleep(1)`
between each displayed number is sufficient and is exactly what's
expected here.

**A gotcha specific to this requirement:** setting a label's text
with `set_text()` only marks the label dirty. It does not paint
anything to the physical screen by itself. The actual screen refresh
happens inside `M5.update()`, the same call that handles touch
polling in every `loop()` you've written so far. Suppose your
countdown handler calls `set_text()` six times back-to-back, with only
`time.sleep()` in between and **no `M5.update()` call inside the
loop**. All six values will be set correctly in code, but **none of
them will ever appear on the physical screen**. The display will jump
straight to its final state once the handler returns. This failure
mode has been confirmed on this hardware. The fix is to call
`M5.update()` after every `set_text()` inside the countdown loop,
before the `time.sleep()` that follows it.

**FR5 — Save the photo as `item.jpg`.** Encode the captured frame to
JPEG and write it to `/flash/item.jpg`. Use this exact filename, with
no variation, because FR10 and FR14 both depend on it. Use the
encode-and-write pattern from Lecture 5 §4:

- pass the quality positionally: `jpg.encode(frame, quality)`;
- open the file in binary write mode (`"wb"`);
- wrap the whole capture-and-save step in a `try`/`except`, so a
  failure here doesn't crash the program silently.

**FR6 — Retrieve the photo to your laptop.** First confirm that
`item.jpg` exists on the device, for example with
`os.listdir("/flash")` and `os.stat("/flash/item.jpg")` from the
WebTerminal (Lecture 5 §4.1). Then copy the image file off the CoreS3
and onto your laptop, using the UIFlow2 web editor's device file
browser or any other method it provides. **This step is graded.** See
Submission Instructions and the rubric.

---

### Functional Requirements — Loan Tag

**FR7 — Title.** A label reading exactly `"Loan Kiosk"`. It must be
visible, legible, and must not overlap any other widget or the
preview rectangle.

**FR8 — Item slider.** An `M5Slider` with **4 positions**
(`min_value=0`, `max_value=3`) mapped to `["Oscilloscope",
"Multimeter", "Power Supply", "Signal Gen"]` in that order (position
0 = "Oscilloscope", position 3 = "Signal Gen"). Its label must update
immediately, in both directions, to show the currently selected item
as the slider is dragged.

**FR9 — Loan Period and Condition sliders.**

- **Loan Period:** an `M5Slider` with **12 positions**
  (`min_value=0`, `max_value=11`) mapped to `["1 day", "2 days",
  "3 days", "4 days", "5 days", "1 week", "2 weeks", "3 weeks",
  "1 month", "2 months", "3 months", "Full term"]` in that order.
- **Condition:** an `M5Slider` with **5 positions** (`min_value=0`,
  `max_value=4`) mapped to `["New", "Good", "Worn", "Damaged",
  "Untested"]` in that order.

Both sliders have the same live label-update requirement as FR8, in
both directions.

All three sliders use the same underlying pattern. An `M5Slider`'s
`get_value()` returns an integer index. You use that index to look up
a string in a fixed list, then display the string in a label with
`set_text()` on `VALUE_CHANGED`. Once one slider's label updates
correctly, the other two follow the same pattern with a different
list. The Loan Period list can't be computed from the index
arithmetically, so look it up from the list as well.

Plan the label space for the **longest** string each slider can show,
for example "Power Supply" and "Full term". An `M5Label` has no `w`
or `h` and grows to fit its text (Lecture 6 §3, gotcha 1).

**FR10 — Issue Loan button.** On press, generate a file at
`/flash/loan_tag.md` containing, **in this order**:

1. **The 10-field header block used in every lab this term:** File,
   Author, Date Submitted, Purpose, Student Number, Seneca E-mail,
   Seneca username, Course Code/Section, GitHub URL, and Core S3
   Device MAC. Write it as regular Markdown text in the file, not as
   Python comments, because `loan_tag.md` is not a `.py` file.

   **Nine of these ten fields are static, personal information you
   already know before you run your program**, the same way you fill
   in the `.py` header's `Author:` and `Date Submitted:` by hand
   before submitting a lab. Type your real values for File, Author,
   Date Submitted, Purpose, Student Number, Seneca E-mail, Seneca
   username, Course Code/Section, and GitHub URL directly into your
   source code, for example as literal strings you build the file's
   content from, **before** you run the program on your CoreS3. You
   don't need to collect any of these nine fields through a widget, a
   prompt, or any other on-device input. Hard-coding them is correct
   and expected, exactly like the `.py` header itself.

   **The tenth field, `Core S3 Device MAC`, is the one exception.** It
   must be obtained **programmatically, at runtime, from the device
   itself** (see FR12). Never type it in as a literal string, even
   though it looks like ordinary text next to the other nine. If your
   header block reads correctly but the MAC address is a value you
   copy-pasted or typed in by hand, this field does not meet FR10 or
   FR12. That holds even if the value happens to be your device's real
   MAC.
2. **The three slider selections** (item, loan period, and
   condition), clearly labelled and written in words, for example
   "Item: Multimeter", never as raw slider positions. Unlike the nine
   static header fields above, these three **must** come from reading
   each slider's current value at the moment Issue Loan is pressed.
   They are the part of the file that is supposed to change based on
   what happens on the device during the test.
3. **A reference to the item photo** captured by the Photo sequence,
   `item.jpg`. Don't capture another photo when Issue Loan is
   pressed; reference the `item.jpg` already saved to `/flash`. A
   Markdown image link such as `![item](item.jpg)` or a line naming
   the file is acceptable, as long as the reference is clearly
   present and points at the correct file. You may assume Photo has
   been pressed at least once before Issue Loan. If it hasn't, the
   tag may reference a file that doesn't exist yet, but your program
   must not crash.

The file must be **plain Markdown text** that opens and reads
correctly in any text editor or Markdown viewer. JSON, a binary
format, or Python source do not meet this requirement.

**FR11 — Issue Loan handler safety.** Wrap the Issue Loan handler body
in its own `try`/`except`, following Lecture 5 §4. File generation is
exactly the kind of operation that can fail silently inside an event
handler if you don't.

**FR12 — Programmatic MAC address (new API, not covered in lecture).**
The `Core S3 Device MAC` field in FR10 must be obtained **at runtime,
from the device**. It may not be hand-typed from a label or copied
from a previous lab's header. Getting it requires a MicroPython
networking call that this course hasn't covered yet. You are expected
to find that call yourself, the way you would research an unfamiliar
API on the job: search the UIFlow2 and MicroPython documentation, or
ask Claude. Before you trust whatever you find, verify that it
actually works on your physical CoreS3, the same verify-on-hardware
habit this course has asked for since Lecture 2. A few things worth
knowing before you start looking:

- The relevant functionality lives in a module you `import`
  separately from `M5`, `m5ui`, `lvgl`, `camera`, and `jpg`. You
  haven't imported this module in any previous lab.
- Whatever object or interface you find will very likely need to be
  explicitly turned on before it reports a usable value. An inactive
  interface is a common reason this kind of call returns nothing
  useful or raises an error.
- You do **not** need to connect to a Wi-Fi network or provide an
  SSID or password to get a MAC address. The value comes from the
  hardware itself, not from a network connection.
- The value you get back may not be in the readable hex format used
  everywhere else in this course (e.g. `1CFED5BD87D2`), so you may need
  to format it yourself.
- If you used AI to help find or debug this, record in `PROMPTS.md`
  what you tried, what worked, and what didn't. This is exactly the
  kind of verification work the course has asked you to record all
  term.

**FR13 — Layout.** No two widgets may overlap at any point during
normal operation. Neither may any widget and the live preview
rectangle. This covers:

- the title;
- both buttons;
- the countdown display;
- all three sliders and their labels, at their longest text;
- the 160×120 preview region.

Sketch your coordinates before you place anything. The 320×240
screen is tight for this many elements, and the layout is part of
what's being tested.

**FR14 — Retrieve the loan tag.** Retrieve `loan_tag.md` to your
laptop the same way you retrieved `item.jpg` in FR6.

**FR15 — Touch-only operation.** The entire kiosk must be usable by
touch alone on the physical CoreS3.

---

### Code Requirements

- **Required header block.** Your submitted `.py` file must begin
  with the following header, as comments, with every field filled
  in and no placeholders left:

  ```python
  # File:                 prg455.263.testX.py
  # Author:               first, lastname
  # Date Submitted:       mm/dd/yyyy
  # Purpose:              solution to Lab Test 1
  # Student Number:       Seneca Polytechnic student number
  # Seneca E-mail:        Seneca student e-mail address
  # Seneca username:      Seneca My.Seneca username
  # Course Code/Section:  PRG455X
  # GitHub URL:           Student GitHub web address
  # Core S3 Device MAC:   (eg. 1CFED5BD87D2)
  ```

  Align the second field five tabs from the first, exactly as shown
  above. This is the same header required on every lab, lab test,
  and project submission this term. It is separate from, and in
  addition to, the header block that FR10 requires *inside* the
  generated `loan_tag.md`. One is a comment block in your source
  code. The other is Markdown content in a file your program
  produces. They are different requirements even though the fields
  are identical.
- Use the standard `setup()` / `loop()` structure: `M5.begin()` →
  `m5ui.init()` → `camera.init()` → build widgets →
  `page0.screen_load()`, with the try/except error-reporting wrapper
  used throughout this course.
- Use **M5UI widgets only**, with two exceptions: the live preview
  drawn with `M5.Lcd.show()` (FR3), and whatever module FR12
  requires. The `camera`, `jpg`, `time`, and `os` modules are
  permitted as supporting imports.
- `time.sleep()` is permitted and expected in the Photo handler only.
  This is the one place in the course so far where a blocking call
  inside an event handler is the correct, intended design rather
  than a mistake to avoid. Don't use it anywhere else, including in
  the slider or Issue Loan handlers.
- Comment your code. Your comments must explain:
  - why a blocking countdown is acceptable here, and what would need
    to change if it weren't. Tie this to Lecture 6 §2's
    poll-driven/event-driven distinction; you don't need to implement
    the non-blocking version;
  - how each slider's index maps to its option list;
  - what you found out about the MAC address API and how you
    verified that it works.
- If you use an AI tool anywhere in building this, **commit your own
  working code before you modify it further with AI assistance**, and
  keep `PROMPTS.md` up to date. This is the same standard as every lab
  this term, and it is specifically required for FR12's research step.

---

### Testing Checklist (self-check before you submit)

Run through this on your **physical CoreS3**:

- [ ] Required header block present in the `.py` file, complete, no
      placeholders.
- [ ] Title reads exactly "Loan Kiosk"; Photo button labelled exactly
      "Photo"; Issue Loan button labelled exactly "Issue Loan".
- [ ] Live preview is visible and updating before Photo is pressed,
      drawn at 160×120, and never paints over any widget.
- [ ] Countdown shows 5, 4, 3, 2, 1, 0 **on the physical screen**,
      one per second, and the photo is captured the instant `0`
      appears.
- [ ] `/flash/item.jpg` exists afterwards (`os.listdir` /
      `os.stat`).
- [ ] All three sliders' labels update correctly and immediately, in
      both directions, at every position. Test each slider across its
      full range, not just one or two positions.
- [ ] Issue Loan generates `/flash/loan_tag.md` containing, in order:
  - the 10-field header: nine fields hard-coded into your source
    ahead of time with your real information, plus a MAC address
    obtained from the device rather than typed by hand;
  - the three slider selections in words;
  - a reference to `item.jpg`.
- [ ] The MAC address in the generated file matches the MAC address
      you can confirm independently, for example from the UIFlow2 web
      editor's device info. It isn't a placeholder or a copy-pasted
      value.
- [ ] `loan_tag.md` opens and displays correctly as plain text or
      Markdown: not garbled, not empty, and not missing any of the
      three required sections.
- [ ] No two widgets overlap at any point, and no widget sits inside
      the preview rectangle, even with every slider label at its
      longest text.
- [ ] Program survives repeated slider adjustments, multiple Photo
      presses, and multiple Issue Loan presses without crashing.
- [ ] Both `item.jpg` and `loan_tag.md` have been retrieved to your
      laptop.

---

### Submission Instructions

1. Create a `labTest1/` directory in your course GitHub repository
   (the private repo with `danny-arroway` added as a collaborator).
2. Place three files in `labTest1/`:
   - your final `.py` file;
   - the retrieved `item.jpg`;
   - the retrieved `loan_tag.md`.

   Both retrieved files must be the actual files your program
   produced on your CoreS3 during this test session. Placeholders,
   photos from a previous lab, images from another source, and
   hand-edited tag files do not count.
3. Commit and push before the end of the test window:
   **[INSTRUCTOR: insert exact cutoff time]**.
4. If you used AI assistance, `PROMPTS.md` must be present and
   current in your repo root. This is especially expected for FR12's
   research step.

```
labTest1/
├── <your file>.py
├── item.jpg
└── loan_tag.md
PROMPTS.md          (repo root)
```

---

### Marking Rubric — 100 Points

| # | Criterion | What's checked | Points |
|---|---|---|---|
| 1 | Photo button and countdown display | Photo button present and labelled exactly "Photo"; countdown display visible and not overlapping the title or the Photo button | 2 |
| 2 | Live camera preview | Visible and updating continuously before Photo is pressed, drawn via `M5.Lcd.show()` at 160×120, never overlapping any M5UI widget | 2 |
| 3 | Countdown sequence correctness | Displays 5,4,3,2,1,0 in order, one per second, visible and legible at each step, meaning it actually appears on the physical screen and isn't just set in code | 4 |
| 4 | Capture timing | Photo is captured at the instant `0` is displayed: not before it, and not after an extra delay | 2 |
| 5 | Save correctness | Saved as exactly `/flash/item.jpg`; positional `jpg.encode()` quality; binary write mode; wrapped in `try`/`except` | 3 |
| 6 | Photo retrieval | `item.jpg` is present in `labTest1/` in the submitted repository, and is the actual photo taken during this test session | 2 |
| 7 | Title | "Loan Kiosk" title present, exact text, no overlap with anything | 5 |
| 8 | Item slider (FR8) | 4 correct positions, mapped to the exact list and order specified; label updates correctly and immediately in both directions across the full range | 8 |
| 9 | Loan Period slider (FR9) | 12 correct positions, mapped to the exact list and order specified; label updates correctly and immediately in both directions across the full range | 8 |
| 10 | Condition slider (FR9) | 5 correct positions, mapped to the exact list and order specified; label updates correctly and immediately in both directions across the full range | 8 |
| 11 | Issue Loan button wiring | Button present and labelled exactly "Issue Loan", correctly dispatches on `CLICKED`, handler wrapped in its own `try`/`except` per Lecture 5 §4 | 6 |
| 12 | `loan_tag.md`: header section | Contains the full 10-field header as Markdown content. The 9 static fields (File, Author, Date Submitted, Purpose, Student Number, Seneca E-mail, Seneca username, Course Code/Section, GitHub URL) are correctly hard-coded with real information, and the MAC field is not a hand-typed or copy-pasted value (checked jointly with criterion 15) | 12 |
| 13 | `loan_tag.md`: slider selections section | All three slider selections present, shown in words (not raw index values), clearly labelled | 8 |
| 14 | `loan_tag.md`: photo reference section | Clear, correctly pointing reference to `item.jpg` | 6 |
| 15 | Programmatic MAC address (FR12) | MAC address is obtained at runtime from the device (not hand-typed), correctly formatted, and verified to match the device's actual MAC | 16 |
| 16 | Layout | No two widgets overlap, and no widget sits inside the preview rectangle, at any point during normal operation | 4 |
| 17 | Loan tag retrieval | `loan_tag.md` is present in `labTest1/` in the submitted repository, and is the actual file generated during this test session | 2 |
| 18 | Code quality | Comments explain the blocking countdown, the slider-index pattern, and the MAC lookup; `PROMPTS.md` is current, especially for the FR12 research step | 2 |
| | **Lab Test 1 Total** | | **100** |

The 100-point total maps to **22% of the final course grade**, as
shown in the course outline and addendum. Criteria 1–6 (15 points)
cover the capture sequence, and criteria 7–18 (85 points) cover the
loan tag. This is the same internal breakdown as the two-part version
of Lab Test 1, with no separate weighting on top of the 22%.
