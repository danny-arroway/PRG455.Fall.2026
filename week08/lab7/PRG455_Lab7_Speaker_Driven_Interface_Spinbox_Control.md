# PRG455 — Event Driven Programming
## Lab 7: Speaker-Driven Interface (Spinbox Control)

**Prerequisite:** Lecture 8 (Audio Output & the Speaker — the Spinbox
Widget). You should be comfortable with `Speaker.begin()`/
`Speaker.tone()`, `M5Spinbox`'s built-in `min_value`/`max_value` range
enforcement, why `set_step()` only accepts powers of ten, why trying
to fake a non-power-of-ten step by snapping the value back inside
`VALUE_CHANGED` freezes the spinbox, why `get_value()` can return a
`float` and what that means for calling `Speaker.tone()`, and the
`VALUE_CHANGED` event pattern shared with `M5Switch` before starting
this lab.

**Due:** Monday, November 9, 2026 (one week after this lab's
introduction on Monday, November 2, 2026).

---

### Scenario

A campus makerspace wants a simple hands-on tone generator station for
its electronics bench — something students can use to dial in a
specific test frequency and play it back, useful for quick checks of
speakers, buzzers, and audio circuits without needing a full signal
generator. The station should let someone set a frequency using clear
increment/decrement controls (no typing — this is a touchscreen
kiosk, not a keyboard), see the currently selected frequency at a
glance, and play it on demand. Your job is to build that tone
generator as a touchscreen app running directly on the CoreS3.

### What You're Building

A single-screen M5UI application with:

1. A **title**.
2. An **`M5Spinbox`** that lets the user select a frequency, adjusted
   only by its own increment/decrement controls — never by free text
   entry.
3. A **live frequency label** showing the spinbox's currently selected
   value, updated the instant the spinbox changes.
4. A **Play button** that, when pressed, plays the currently selected
   frequency through the speaker for a fixed duration.
5. A **status label** that shows whether a tone is currently playing.

This lab is **entirely event-driven** — unlike Labs 4 through 6, there
is no sensor to poll and no meaningful work required in `loop()`
beyond `M5.update()`. Every visible change in this program happens in
response to a spinbox adjustment or a button press.

---

### Functional Requirements

**FR1 — Title.** Visible, legible, doesn't overlap other widgets.

**FR2 — Frequency spinbox.** One `M5Spinbox` with:

| Property | Required value |
|---|---|
| `min_value` | 100 |
| `max_value` | 5000 |
| step | 10 |
| starting `value` | 440 |

The step of `10` is set with `spinbox0.set_step(10)` — `10` is a valid
power-of-ten step, so no extra logic is required to enforce it (see
the Decision Logic section for why a step of `50` is not achievable
this way, and why attempting to fake it by rewriting the spinbox's
value from inside its own `VALUE_CHANGED` handler must be avoided).

The spinbox must only be adjustable through its own built-in
increment/decrement controls on the physical touchscreen — no code in
this lab may open the on-screen keyboard or accept free-typed digits
for this value.

**FR3 — Live frequency label.** One `M5Label` that updates **the
instant the spinbox's value changes** (i.e. from the spinbox's
`VALUE_CHANGED` handler, not from `loop()`) to read exactly
`"Frequency: <value> Hz"`, e.g. `Frequency: 440 Hz`. This label must
always match the spinbox's actual current value — pressing
increment/decrement and immediately checking the label must never show
a stale number.

**FR4 — Play button.** One `M5Button` that, when pressed, reads the
spinbox's **current** value at the moment of the press and calls
`Speaker.tone()` with that frequency for exactly **300 milliseconds**.
Pressing Play must always use whatever frequency the spinbox currently
shows — not a value captured earlier, and not a value that requires
the user to press Play a second time to "apply."

**FR5 — Status label.** One `M5Label` that reads `"Status: Playing"`
while a tone triggered by this program is sounding, and reads back to
`"Status: Ready"` once that tone has finished. This requires checking
`Speaker.isPlaying()` — since `Speaker.tone()` itself does not block,
the status cannot simply be set to "Playing" and back to "Ready" on
either side of the `Speaker.tone()` call in the button handler; by the
time that call returns, the tone has barely started.

> **Implementation note.** `Speaker.tone()` returns immediately, so
> the moment your Play handler calls it, `Speaker.isPlaying()` should
> read `True`. Something still needs to poll `Speaker.isPlaying()`
> repeatedly to notice when it becomes `False` again and switch the
> status label back — this is the **one** place in this lab where
> `loop()` needs to do real work, and it is a poll-driven check
> layered on top of an otherwise event-driven program, not a
> contradiction of FR-level "no sensor to poll."

**FR6 — Touch-only operation.** The spinbox's increment/decrement
controls and the Play button must both be usable by touch alone on
the physical CoreS3.

**FR7 — No blocking waits.** Do not use `time.sleep()` or any other
blocking call to "wait out" the tone's duration. Whatever mechanism
FR5 uses to detect that the tone has finished must not freeze the UI
or prevent the spinbox and Play button from responding to touch while
a tone is playing (or not playing).

---

### Decision Logic (required — implement exactly)

The spinbox's own `min_value`/`max_value` already guarantee its value
never leaves the required range, exactly as described in Lecture 8
§2 — that part needs no code of your own. The **step** is set once,
directly, with no extra logic needed:

**Step 1 — Set a valid native step.** Call `spinbox0.set_step(10)` in
`setup()`, right after constructing the spinbox. `10` is a valid
power-of-ten step, so the widget's own increment/decrement controls
move the value by exactly `10` on every press, with no further code
required.

> **Do not attempt to fake a step of `50` by snapping the value back
> inside the spinbox's `VALUE_CHANGED` handler** (e.g. rounding the
> raw value to the nearest multiple of `50` and writing it back with
> `spinbox0.set_value()`). This looks safe in isolation but **freezes
> the spinbox** the moment its value lands on an exact multiple of
> `50`: from that point on, every further press moves the raw value by
> the widget's own native step, the handler snaps it back down to the
> same multiple of `50` every time, and the displayed value can never
> change again in either direction. A submission built this way will
> fail the range-enforcement worked check below the first time testing
> crosses a multiple of `50`.

**Step 2 — Reading the frequency.** Whenever the Play button is
pressed, read the spinbox's value with `spinbox0.get_value()` at that
moment — do not cache a frequency value anywhere else and use the
cached copy instead. **Cast this value with `int()` before using it**
— `get_value()` is documented to return `float | int`, and
`Speaker.tone()` requires an integer frequency; skipping the cast can
raise `TypeError: can't convert float to int` even when the spinbox
displays a whole number.

**Step 3 — Triggering the tone.** Call
`Speaker.tone(int(freq), 300)` — `300` (milliseconds) is a fixed
constant, not configurable by the user in this lab.

**Step 4 — Status label sequencing.** Every `loop()` pass, check
`Speaker.isPlaying()`:

- If it is `True` and the status label does not already read
  `"Status: Playing"`, set it to `"Status: Playing"`.
- If it is `False` and the status label does not already read
  `"Status: Ready"`, set it to `"Status: Ready"`.

Worked check (spinbox range enforcement): starting from `value=440`
and pressing decrement repeatedly must land exactly on `100` and stop
there — never below it, and never getting stuck at any value above
`100`. Similarly, incrementing repeatedly from anywhere in the range
must land exactly on `5000` and stop there, never above it. This check
must pass under **sustained repeated pressing that crosses several
multiples of 50** (e.g. continuing well past `450`, `500`, `550`, and
so on) — a submission that freezes at any such point has not met FR2.

Worked check (no `TypeError` on Play): pressing Play must never raise
`TypeError: can't convert float to int`, even if `spinbox0.get_value()`
happens to return a float at that moment. A submission where Play
raises this error, or silently fails to play a tone because of it, has
not met FR4.

Worked check (status sequencing): immediately after pressing Play, the
status label must read `"Status: Playing"` within one `loop()` pass —
not require a second button press or a delay before it updates. After
approximately 300ms (the fixed tone duration), the label must return
to `"Status: Ready"` on its own, without any further touch input.

Worked check (rapid Play presses): pressing Play again while a tone
from a previous press is still playing must not crash the program or
leave the status label stuck on "Playing" forever — the status label
must still correctly reflect `Speaker.isPlaying()` once all triggered
tones have finished.

---

### Code Requirements

- **Required header block.** Every submitted `.py` file must begin
  with the following header, as comments, with all fields filled in —
  no placeholders left in the submitted version:

  ```python
  # File:                 prg455.263.lab7.py
  # Author:               first, lastname
  # Date Submitted:       mm/dd/yyyy
  # Purpose:              solution to lab7
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
  change (`prg455.263.lab7.py` / `solution to lab7`).
- Standard `setup()` / `loop()` structure, `M5.begin()` → `m5ui.init()`
  → build widgets → `page0.screen_load()`, with the try/except
  error-reporting wrapper used throughout this course.
- `Speaker.begin()` must be called once, in `setup()`.
- The spinbox must be constructed with `min_value=100` and
  `max_value=5000` as constructor arguments, with `digit_count` and
  `prec` set appropriately (4 digits, 0 decimal places, to display
  whole-Hz values up to `5000`), and starting `value=440` exactly as
  specified in FR2 — do not substitute different bounds.
- Set the step with `spinbox0.set_step(10)`, called once in `setup()`
  right after constructing the spinbox. **Do not** attempt to produce
  a step of `50` by rounding the value inside the `VALUE_CHANGED`
  handler and writing it back with `set_value()` — this freezes the
  spinbox the moment its value reaches a multiple of `50`, since the
  widget's own increment/decrement controls keep nudging the value by
  their own native step on every subsequent press, fighting the
  snap-back forever. See Decision Logic Step 1.
- **Cast `spinbox0.get_value()` to `int()` before passing it to
  `Speaker.tone()`.** `get_value()` is documented to return
  `float | int`; skipping the cast can raise `TypeError: can't
  convert float to int`.
- Use **M5UI widgets only** — label, spinbox, and button, nothing else
  needed for this lab.
- Comment your code — explain why this program is event-driven rather
  than poll-driven, why the status label still needs a `loop()` check
  despite that, how the spinbox's own range enforcement removes the
  need for a manual clamp-and-scale step, why `set_step(10)` was
  chosen over a non-power-of-ten value, and why the `int()` cast
  before `Speaker.tone()` is necessary.
- If you use an AI tool anywhere in building this: **commit your own
  working code before you modify it further with AI assistance**, and
  keep `PROMPTS.md` up to date with what you asked and what you used.
- **Test with Run Once repeatedly before ever using Run Always** — a
  crashing program set to Run Always can only be recovered by
  reflashing the device through M5Burner.

---

### Testing Checklist (self-check before you submit)

Run through this on your **physical CoreS3**, not just by reading the
code:

- [ ] Required header block is present at the top of the file, every
      field filled in (no placeholders), formatted as specified in
      Code Requirements.
- [ ] Title is visible and doesn't overlap other widgets.
- [ ] The spinbox starts at `440`, and its increment/decrement
      controls are usable by touch.
- [ ] Repeatedly decrementing the spinbox stops at `100` and does not
      go lower, even after many extra presses.
- [ ] Repeatedly incrementing the spinbox stops at `5000` and does not
      go higher, even after many extra presses.
- [ ] Watching the value as you press increment/decrement confirms it
      moves in steps of `10`, smoothly, in both directions.
- [ ] Press increment or decrement continuously through several
      multiples of `50` (e.g. `450`, `500`, `550`) and confirm the
      value keeps moving normally past each one — it must never get
      stuck at any point.
- [ ] The frequency label updates immediately on every spinbox change
      and always matches the spinbox's current value exactly.
- [ ] Pressing Play never raises an error and never silently fails to
      play a tone — specifically check that no `TypeError` about
      converting a float to an int appears in the console.
- [ ] Pressing Play produces an audible tone at the frequency shown on
      the label at the moment of the press.
- [ ] Changing the spinbox, then pressing Play, plays the **new**
      frequency — not whatever frequency was selected the first time
      the app was opened.
- [ ] The status label reads "Status: Playing" as soon as Play is
      pressed, and returns to "Status: Ready" on its own once the tone
      finishes — with no further touch input required.
- [ ] Pressing Play again while a tone is already playing does not
      crash the program, and the status label still correctly settles
      back to "Status: Ready" afterward.
- [ ] The spinbox and Play button both remain touch-responsive at all
      times, including while a tone is playing — no freezing, no
      missed touches.
- [ ] No `time.sleep()` or other blocking wait is used anywhere in the
      program.

---

### Submission Instructions

1. Create a `lab7/` directory in your course GitHub repository (the
   private repo with `danny-arroway` added as a collaborator).
2. Place your final `.py` file in `lab7/`.
3. Commit and push before the deadline: **Monday, November 9, 2026.**
4. If you used AI assistance, `PROMPTS.md` must be present and current
   in your repo root.

---

### Marking Rubric — Out of 100

Graded by running the submitted program on a physical CoreS3 and
working through the checklist above, including repeated
increment/decrement presses at both range boundaries and repeated
Play presses under normal and rapid-fire conditions.

| # | Criterion | What's checked | Points |
|---|---|---|---|
| 1 | Title | Present, legible, no overlap | 5 |
| 2 | Spinbox configuration and range enforcement | Correct `min_value`/`max_value`/starting `value` exactly per FR2; range is enforced by the widget itself at both boundaries under repeated presses; touch-responsive | 15 |
| 3 | Step correctness and stability | The spinbox's value moves in steps of `10`, set via `spinbox0.set_step(10)`; the spinbox never freezes or gets stuck at any value, including at multiples of `50`, under sustained repeated increment/decrement presses in both directions | 15 |
| 4 | Live frequency label | Updates immediately on every spinbox change via the `VALUE_CHANGED` handler (not `loop()`); text matches the exact required format and always reflects the spinbox's current value | 10 |
| 5 | Play button and tone playback | Reads the spinbox's current value at the moment of the press (not a cached/stale value); casts it with `int()` before calling `Speaker.tone()`, never raising `TypeError: can't convert float to int`; calls `Speaker.tone()` with the correct frequency and the fixed 300ms duration; touch-responsive | 20 |
| 6 | Status label sequencing | Reads "Status: Playing" immediately after Play is pressed; correctly returns to "Status: Ready" on its own once the tone finishes, via a `loop()`-driven check of `Speaker.isPlaying()`; survives rapid repeated Play presses without getting stuck | 15 |
| 7 | Responsiveness | No blocking waits anywhere; spinbox and Play button remain touch-responsive throughout, including while a tone plays | 10 |
| 8 | Code quality | Comments explain why the program is event-driven, why the status label still needs a `loop()` check, how the spinbox's built-in range removes the need for manual clamp-and-scale, why `set_step(10)` was chosen over a non-power-of-ten value, and why the `int()` cast before `Speaker.tone()` is necessary; standard program structure; `PROMPTS.md` present if AI was used | 10 |
| | **Subtotal** | | **100** |
| — | **Required header block** | Deduction, not a scored criterion: **-10 points (10%) from the total above** if the required header block (see Code Requirements) is missing, incomplete, or has any placeholder text left in it | -10 |
| | **Total** | | **100** |
