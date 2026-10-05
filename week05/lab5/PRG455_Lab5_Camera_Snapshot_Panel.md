# PRG455 — Event Driven Programming
## Lab 5: Camera Snapshot Panel

**Prerequisite:** Lecture 5 (The Camera & the Image Widget). You should
be comfortable with `camera.init()`, `camera.snapshot()`,
`M5.Lcd.show()`, `M5Image`, and the reasoning in Lecture 5 §1 about why
live preview and M5UI widgets use two different display paths before
starting this lab.

---

### Scenario

A small electronics hobby shop wants a quick "inspection panel" they
can point at a part or a label on a shelf, see a live view on the
CoreS3's screen, and snap a still photo that stays visible after the
live feed moves on — useful for double-checking what was captured
before writing it down or reordering. Your job is to build that panel.

### What You're Building

A single-screen M5UI application with:

1. A **title**.
2. A **live camera preview** filling most of the screen, drawn with
   `M5.Lcd.show()`.
3. A **Capture** button that, on press, saves the current frame as a
   JPEG file to flash and displays it in an `M5Image` widget.
4. A **status label** that reflects whether a photo has been captured
   yet this session.
5. A **Clear** button that removes the currently displayed captured
   photo from the `M5Image` widget (reverting it to a placeholder) and
   resets the status label — without needing to restart the program.

---

### Functional Requirements

**FR1 — Title.** Visible, legible, doesn't overlap the live preview,
button row, or status label at any point during normal operation.

**FR2 — Live camera preview.** Initialize the camera with
`camera.init(pixformat=camera.RGB565, framesize=camera.QVGA)` in
`setup()`. In `loop()`, capture a frame every iteration and draw it
with `M5.Lcd.show()` into a fixed rectangle that:
   - is at least 280px wide and 150px tall,
   - does not overlap the title, either button, the `M5Image` result
     widget, or the status label at any `x`/`y` combination — check
     both axes, per Lecture 5 §6.

**FR3 — Capture button.** On press, it must:
1. Capture a fresh frame with `camera.snapshot()` — not a frame left
   over from a previous loop iteration.
2. Encode it to JPEG with `jpg.encode(frame, N)` at a quality of your
   choosing, passed **positionally** (80 is a reasonable default;
   document your choice in a comment). This is a function from the
   separate `jpg` module — there is no `.to_jpeg()` method on the
   frame object itself, and using that name will raise
   `AttributeError` on the physical device. Passing quality as a
   keyword argument (`quality=80`) will raise `TypeError: function
   doesn't take keyword arguments` on this firmware, even though it
   appears as a keyword argument in M5Stack's published documentation.
3. Call `.bytearray()` on the `image.Image` that `jpg.encode()`
   returns, and write those bytes **in binary mode (`"wb"`)** to a
   file on `/flash`.
4. Call `set_image()` on your `M5Image` widget with that file's path,
   so the captured photo becomes visible immediately.
5. Update the status label to indicate a photo has been captured
   (e.g. "Status: Photo captured").

**FR4 — `M5Image` result widget.** Must be constructed in `setup()`
pointed at a valid placeholder image that ships with the firmware
(e.g. `/flash/res/img/uiflow.jpg`) — per Lecture 5 §5, constructing
`M5Image` with a path that doesn't yet exist is a crash, not a safe
no-op. The widget must be positioned so it never overlaps the live
preview rectangle from FR2.

**FR5 — Clear button.** On press, it must, in one action:
- call `set_image()` on the `M5Image` widget with the same placeholder
  path used in `setup()`, and
- update the status label back to its starting text
  (e.g. "Status: No photo yet").

Clear does **not** need to delete the JPEG file from flash — only reset
what's displayed and what the status label says.

**FR6 — Status label.** Starts at program launch reading something
like "Status: No photo yet", changes after a successful Capture, and
resets after Clear — always accurately reflecting whether the currently
displayed image in the `M5Image` widget is the placeholder or a
captured photo.

**FR7 — Touch-only operation.** The entire panel must be usable by
touch alone on the physical CoreS3, with the live preview updating
continuously throughout.

### Layout Guidance (not graded directly, but drives FR1/FR2/FR4)

A layout that satisfies the non-overlap requirements without much
fuss: title and both buttons in a row across the top ~36px, live
preview filling most of the middle of the screen, `M5Image` result
widget as a small thumbnail tucked in a corner **above or beside** the
preview's `y` range (not just outside its `x` range — see the
worked-example note in Lecture 5 §6 about checking both axes), and the
status label in the remaining space at the bottom. You are free to
choose your own arrangement as long as FR1, FR2, and FR4's overlap
conditions hold.

### Code Requirements

- **Required header block.** Every submitted `.py` file must begin
  with the following header, as comments, with all fields filled in —
  no placeholders left in the submitted version:

  ```python
  # File:                 prg455.263.lab5.py
  # Author:               first, lastname
  # Date Submitted:       mm/dd/yyyy
  # Purpose:              solution to lab5
  # Student Number:       Seneca Polytechnic student number
  # Seneca E-mail:        Seneca student e-mail address
  # Seneca username:      Seneca My.Seneca username
  # Course Code/Section:  PRG455X
  # GitHub URL:           Student GitHub web address
  # Core S3 Device MAC:   (eg. 1CFED5BD87D2)
  ```

  Align the second field five tabs from the first, exactly as shown
  above. This is the same header required on every lab, lab test, and
  project submission this term — only the `File:` and `Purpose:` lines
  change (`prg455.263.lab5.py` / `solution to lab5`).
- Standard `setup()` / `loop()` structure, `M5.begin()` → `m5ui.init()`
  → build widgets → `page0.screen_load()`, with the try/except
  error-reporting wrapper used throughout this course.
- Use **M5UI widgets** for everything except the live preview region,
  which uses `M5.Lcd.show()` as covered in lecture — this is the one
  approved exception to "M5UI widgets only" in this course, because no
  M5UI widget supports live video.
- **Write captured JPEG bytes in binary mode (`"wb"`)**, not text mode
  — `jpg.encode().bytearray()` returns binary data, and text mode is a
  type mismatch that can fail on real hardware.
- **Wrap the Capture button's handler body in its own `try`/`except`**
  and print any exception. An error inside an event handler does not
  reliably reach the `try`/`except` around `setup()`/`loop()`, so
  without this, a broken Capture button fails silently — nothing
  crashes, nothing prints, and the photo simply never appears on
  flash. See Lecture 5 §4 for why this matters here specifically.
- Comment your code — explain why the live preview and the `M5Image`
  widget use different display calls, and why the button handlers are
  structured the way they are.
- If you use an AI tool anywhere in building this: **commit your own
  working code before you modify it further with AI assistance**, and
  keep `PROMPTS.md` up to date with what you asked and what you used.
- **Test with Run Once repeatedly before ever using Run Always** — a
  crashing program set to Run Always can only be recovered by
  reflashing the device through M5Burner.
- **Remove the CoreS3 from the DIN Base before USB work** — leaving the
  DIN Base's power switch on during a USB session causes rapid
  power-cycling and serial disconnects, as documented since Week 2.

---

### Testing Checklist (self-check before you submit)

Run through this on your **physical CoreS3**, not just by reading the
code:

- [ ] Required header block is present at the top of the file, every
      field filled in (no placeholders), formatted as specified in
      Code Requirements.
- [ ] Title is visible and doesn't overlap any other element at any
      point during operation.
- [ ] Live preview updates continuously and fills at least 280×150px.
- [ ] Capture saves a new JPEG and the `M5Image` widget updates to show
      it within about a second of the button press.
- [ ] Pressing Capture a second time (pointing the camera at something
      different) replaces the displayed photo with the new one, not
      the old one.
- [ ] Status label correctly reads "no photo yet" at launch and updates
      after Capture.
- [ ] Clear reverts the `M5Image` widget to the placeholder and resets
      the status label, without restarting the program.
- [ ] No part of the live preview rectangle overlaps the title, either
      button, the `M5Image` widget, or the status label, checked at
      actual on-screen coordinates, not just assumed.
- [ ] Program survives at least 60 seconds of continuous Run Once
      operation, including multiple Capture/Clear cycles, without
      crashing or freezing.

---

### Submission Instructions

1. Create a `lab5/` directory in your course GitHub repository (the
   private repo with `danny-arroway` added as a collaborator).
2. Place your final `.py` file in `lab5/`.
3. Commit and push before the deadline: **[INSTRUCTOR: insert due date]**.
4. If you used AI assistance, `PROMPTS.md` must be present and current
   in your repo root.

---

### Marking Rubric — Out of 100

Graded by running the submitted program on a physical CoreS3 and
working through the checklist above.

| # | Criterion | What's checked | Points |
|---|---|---|---|
| 1 | Title | Present, legible, no overlap with any other element | 5 |
| 2 | Live camera preview | Initializes correctly, updates every loop iteration, meets minimum size, drawn via `M5.Lcd.show()` | 20 |
| 3 | Capture button correctness | Captures a fresh frame (not stale), converts to JPEG, saves to flash, updates the `M5Image` widget correctly on every press | 25 |
| 4 | `M5Image` widget setup and behaviour | Constructed with a valid placeholder path, correctly swaps to the captured photo, never overlaps the preview region | 15 |
| 5 | Clear button | Reverts `M5Image` to placeholder and resets status label in one tap, without restarting the program | 15 |
| 6 | Status label accuracy | Correctly reflects captured/not-captured state at all times, including after Clear | 10 |
| 7 | Code quality | Comments explain the two display paths and button logic; standard program structure; `PROMPTS.md` present if AI was used | 10 |
| | **Subtotal** | | **100** |
| — | **Required header block** | Deduction, not a scored criterion: **-10 points (10%) from the total above** if the required header block (see Code Requirements) is missing, incomplete, or has any placeholder text left in it | -10 |
| | **Total** | | **100** |
