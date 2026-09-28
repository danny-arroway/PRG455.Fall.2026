# PRG455 — Event Driven Programming
## Lab 4: IMU Tilt & Calibration Panel

**Prerequisite:** Lecture 4 (Motion Sensing & the IMU). You should be
comfortable with `M5.Imu.getAccel()`, the clamp-and-scale pattern,
`M5Bar`, `M5Switch`, and the poll-driven vs. event-driven update
patterns from Lecture 4 §5 before starting this lab.

---

### Scenario

A small robotics team needs a quick diagnostic panel for checking
whether a device is sitting level before it starts a run. Sitting
still on a bench, the panel should show, at a glance, how far off
level the device currently is — and let the operator switch into a
more sensitive mode when fine-tuning the final placement. Your job is
to build that diagnostic panel as a touchscreen app running directly
on the CoreS3.

### What You're Building

A single-screen M5UI application with:

1. A **title**.
2. **Three tilt bars** (`M5Bar`), one per accelerometer axis, each
   continuously reflecting that axis's current reading, read from the
   IMU in `loop()`:
   - **X-axis bar** — blue.
   - **Y-axis bar** — green.
   - **Z-axis bar** — red.
3. **Three live value labels**, one per axis, each showing that axis's
   current raw reading in g, updated on the same schedule as its bar.
4. A **calibration switch** (`M5Switch`) that toggles between **Normal**
   and **Sensitive** interpretation of the tilt, changing how all three
   raw readings are scaled onto their bars.
5. A **mode label** that updates, on toggle, to show which mode is
   currently active.

There is no Recommend/Reset button pair in this lab — the bars and
value labels update continuously and automatically, on their own,
without any button press, for as long as the program runs.

---

### Functional Requirements

**FR1 — Title.** Visible, legible, doesn't overlap other widgets.

**FR2 — Three tilt bars.** Three `M5Bar` widgets, each with
`min_value=0`, `max_value=100`, updated every pass through `loop()`
from a live IMU read — **not** from any button or touch event:

| Bar | Axis | Colour |
|---|---|---|
| X-axis bar | `ax` | Blue |
| Y-axis bar | `ay` | Green |
| Z-axis bar | `az` | Red |

Each bar's value must be produced by the **exact clamp-and-scale
formula in the Decision Logic section below**, applied independently
to that axis's own reading — this is not open to interpretation, since
it's what makes the lab gradable.

**FR3 — Three live value labels.** One `M5Label` per axis, each
showing that axis's current raw accelerometer reading, updated on the
same `loop()` pass as its bar, formatted to exactly three decimal
places with a trailing ` g` (e.g. `X-axis: 0.482 g`, `Y-axis: -0.033 g`,
`Z-axis: 0.981 g`). Negative readings must display their sign.

**FR4 — Calibration switch.** An `M5Switch` with two states:

| State | Meaning |
|---|---|
| Off (default) | **Normal** mode — full-scale range is ±1.0 g |
| On | **Sensitive** mode — full-scale range is ±0.5 g |

Toggling the switch must immediately change which range **all three**
bars' formulas use on the *next* `loop()` pass — there is no button to
press to "apply" the new mode. This must work reliably in both
directions: toggling **on** (Normal → Sensitive) and toggling **off**
(Sensitive → Normal) must each take effect on the very next `loop()`
pass, with no lag, no missed transition, and no case where the panel
gets stuck showing the previous mode's scaling after the switch has
visibly changed state.

> **Implementation note:** don't call the switch's state-reading method
> directly from `loop()` on every pass to decide which range to use.
> Track the current mode in your own variable, written only inside the
> switch's `VALUE_CHANGED` handler, and have `loop()` read that
> variable instead. Polling the widget's state repeatedly from `loop()`
> is a common way to end up with a panel that goes into Sensitive mode
> correctly but never comes back out of it.

**FR5 — Mode label.** An `M5Label`, next to or below the switch, that
updates the instant the switch is toggled (i.e. from the switch's
`VALUE_CHANGED` handler, not from `loop()`) to read exactly
`"Mode: Normal"` or `"Mode: Sensitive"` — correctly, in both
directions.

**FR6 — Touch-only operation.** The calibration switch must be usable
by touch alone on the physical CoreS3. (The bars and labels require no
touch interaction at all — that's the point of them.)

**FR7 — No blocking calls.** `loop()` must not contain `time.sleep()`
calls longer than a few milliseconds, or any other blocking operation.
The bars' live updates and the switch's touch response must both stay
responsive at all times.

### Decision Logic (required — implement exactly)

This reuses the clamp-and-scale pattern from Lecture 4 §2 and §6, with
one fixed formula per mode, applied identically and independently to
each of the three axes — every possible raw axis reading, in either
mode, has one unambiguous correct bar value, which is what matters for
grading.

**Step 1 — Choose the half-range for the current mode:**

| Mode | Switch state | Half-range (±g) |
|---|---|---|
| Normal | Off | 1.0 |
| Sensitive | On | 0.5 |

The same half-range applies to all three axes at once — there's one
mode for the whole panel, not one per bar.

**Step 2 — Clamp the raw axis reading to `[-half_range, +half_range]`.**
Readings beyond the half-range (from a hard bump or a fast motion) must
be pulled back to the nearest edge before Step 3 — an unclamped value
can otherwise scale to a bar value outside `0`–`100`. Apply this
separately to `ax`, `ay`, and `az`.

**Step 3 — Convert the clamped reading to a 0.0–1.0 fraction:**

```
fraction = (clamped_value + half_range) / (2 * half_range)
```

**Step 4 — Bar value (integer, 0–100):**

```
bar_value = int(fraction * 100)
```

Worked check (Normal mode, half-range = 1.0): a level device reading
`0.000` on some axis must produce `fraction = 0.5` and `bar_value = 50`
— that bar's exact midpoint. A reading of `1.000` on an axis must
produce `bar_value = 100` for that bar; `-1.000` must produce
`bar_value = 0`. This applies the same way whether it's the X, Y, or Z
axis and bar.

Worked check (Sensitive mode, half-range = 0.5): the same `0.000`
reading still produces `bar_value = 50` on any axis, but a reading of
`0.500` now produces `bar_value = 100` instead of requiring a full
1.0 g reading to reach the top of the bar — the whole point of the
more sensitive mode.

Worked check (toggle round-trip): starting in Normal mode with a
reading of `0.900` on some axis produces `bar_value = 95`. Toggling to
Sensitive mode with the same `0.900` reading (now clamped to `0.500`)
produces `bar_value = 100`. Toggling back to Normal with that same
`0.900` reading must produce `bar_value = 95` again — **not** a value
still computed as though Sensitive mode were active. A panel that
reaches Sensitive correctly but fails this last step (stuck showing
Sensitive-mode scaling after switching back to Normal) has not met
FR4.

### Code Requirements

- **Required header block.** Every submitted `.py` file must begin
  with the following header, as comments, with all fields filled in —
  no placeholders left in the submitted version:

  ```python
  # File:                 prg455.263.lab4.py
  # Author:               first, lastname
  # Date Submitted:       mm/dd/yyyy
  # Purpose:              solution to lab4
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
  change (`prg455.263.lab4.py` / `solution to lab4`).
- Standard `setup()` / `loop()` structure, `M5.begin()` → `m5ui.init()`
  → build widgets → `page0.screen_load()`, with the try/except
  error-reporting wrapper used throughout this course.
- Use **M5UI widgets only** — labels, bar, and switch, nothing else
  needed for this lab.
- Comment your code — explain the clamp-and-scale formula, the
  Normal/Sensitive half-range logic, and which parts of your code run
  from `loop()` versus from the switch's event handler.
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
- [ ] All three bars are present, correctly coloured (X blue, Y green,
      Z red), and don't overlap each other or any label.
- [ ] With the device flat on a table (screen up), the X and Y bars sit
      at or very near their midpoint (50), and the Z bar sits near its
      top (near 100, since gravity loads onto Z when flat) in Normal
      mode.
- [ ] Tilting the device along each axis in turn moves that axis's bar
      smoothly toward 0 or 100, with no jumps, freezes, or crashes —
      and the other two bars are not affected by a tilt that's purely
      along one axis.
- [ ] All three live value labels update continuously, in step with
      their bars, each showing three decimal places and a correct
      sign.
- [ ] Toggling the calibration switch **on** immediately changes the
      mode label to "Mode: Sensitive" and visibly changes how far the
      device must tilt to reach the same bar position on all three
      bars at once.
- [ ] Toggling the calibration switch **back off** immediately changes
      the mode label back to "Mode: Normal" and all three bars visibly
      return to Normal-mode scaling on the very next update — this
      direction specifically must be re-tested, not assumed to work
      just because toggling on worked.
- [ ] Toggle on and off several times in a row, tilting the device
      between toggles, to confirm the mode never gets stuck.
- [ ] All three bars keep updating and the switch stays responsive to
      touch at the same time — no stalls, no missed touches.
- [ ] No bar value ever leaves the 0-100 range, even under a hard bump
      or fast motion (clamp is working) on any axis.

---

### Submission Instructions

1. Create a `lab4/` directory in your course GitHub repository (the
   private repo with `danny-arroway` added as a collaborator).
2. Place your final `.py` file in `lab4/`.
3. Commit and push before the deadline: **[INSTRUCTOR: insert due date]**.
4. If you used AI assistance, `PROMPTS.md` must be present and current
   in your repo root.

---

### Marking Rubric — Out of 100

Graded by running the submitted program on a physical CoreS3 and
working through the checklist above, cross-referencing bar values
against the Decision Logic worked checks for spot checks in both
modes.

| # | Criterion | What's checked | Points |
|---|---|---|---|
| 1 | Title | Present, legible, no overlap | 5 |
| 2 | Three tilt bars present and correctly configured | Three `M5Bar` widgets, range 0-100, correctly coloured (X blue, Y green, Z red), each updates every `loop()` pass from its own IMU axis, not from a touch event | 15 |
| 3 | Clamp-and-scale formula correctness | Bar value matches the exact Decision Logic formula for arbitrary axis readings in both modes, independently per axis, including clamped edge cases | 20 |
| 4 | Three live value labels | Each updates in step with its bar, exactly three decimal places, correct sign, correct trailing unit, correct axis identified | 15 |
| 5 | Calibration switch and mode label | Switch present and touch-responsive; mode label updates immediately on toggle with the exact required text; half-range changes correctly across all three bars in **both** directions (Normal→Sensitive and Sensitive→Normal), verified by a toggle round-trip, not just a single toggle | 20 |
| 6 | Responsiveness | No blocking calls in `loop()`; all three bars keep updating and switch stays touch-responsive simultaneously | 10 |
| 7 | Code quality | Comments explain the clamp-and-scale formula, the poll-driven vs. event-driven split, and how the mode is tracked so it survives a toggle round-trip; standard program structure; `PROMPTS.md` present if AI was used | 15 |
| | **Subtotal** | | **100** |
| — | **Required header block** | Deduction, not a scored criterion: **-10 points (10%) from the total above** if the required header block (see Code Requirements) is missing, incomplete, or has any placeholder text left in it | -10 |
| | **Total** | | **100** |
