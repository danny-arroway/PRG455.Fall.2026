# PRG455 — Event Driven Programming
## Lab 6: Microphone Sound Level Meter & Word Counter

**Prerequisite:** Lecture 7 (Audio Input & the Microphone — the LED
Widget). You should be comfortable with `Mic.begin()`/`Mic.record()`/
`Mic.isRecording()`, unpacking a PCM buffer with `struct.unpack()`,
peak amplitude, the clamp-and-scale pattern, and `M5LED` before
starting this lab.

---

### Scenario

A campus makerspace wants a simple, always-on sound level indicator
for its shared workshop — nothing that logs data or connects to
anything, just a light that visibly brightens when the room gets
loud, so people glancing over from across the room get an immediate
sense of the noise level. The makerspace also wants a rough running
tally of how many words have been spoken at the station during a
session — useful, for example, for timing short presentation
rehearsals against a target word count. An operator should also be
able to flip a switch to make the loudness indicator more sensitive
when calibrating it in a quieter side room. Your job is to build that
indicator as a touchscreen app running directly on the CoreS3.

### What You're Building

A single-screen M5UI application with:

1. A **title**.
2. An **`M5LED`** that continuously reflects the current ambient sound
   level, read from the microphone in `loop()` — brighter for louder
   sound, dim or off for quiet.
3. A **live percentage label** showing the current sound level as a
   whole-number percentage, updated on the same schedule as the LED.
4. A **word count label** — blue background, white text — showing a
   running count of the number of spoken words detected, updated on
   the same schedule as the LED and percentage label.
5. A **sensitivity switch** (`M5Switch`) that toggles between
   **Normal** and **Sensitive** interpretation of the microphone
   signal, changing how loud a sound needs to be to fully brighten the
   LED.
6. A **mode label** that updates, on toggle, to show which mode is
   currently active.

There is no Recommend/Reset button pair in this lab — the LED, the
percentage label, and the word count all update continuously and
automatically, on their own, without any button press, for as long as
the program runs.

---

### Functional Requirements

**FR1 — Title.** Visible, legible, doesn't overlap other widgets.

**FR2 — Sound-driven LED.** One `M5LED` widget, updated every pass
through `loop()` from a freshly recorded microphone buffer — **not**
from any button or touch event. Brightness must be set with
`led0.set_brightness(percent)`, where `percent` is produced by the
**exact clamp-and-scale formula in the Decision Logic section below**.

**FR3 — Live percentage label.** One `M5Label` showing the current
sound level, updated on the same `loop()` pass as the LED, formatted
as a whole-number percentage with a trailing `%` (e.g. `Level: 42%`).
No decimal places.

**FR4 — Word count label.** One `M5Label` with a **blue background and
white text**, showing a running count of the number of spoken words
detected since the program started, updated on the same `loop()` pass
as the LED and percentage label. Formatted as a whole integer with a
leading label, e.g. `Words: 7`. The count must never decrease and must
never reset on its own while the program runs.

> **What "a word" means here.** This lab detects words by **silence
> gaps**, not by understanding speech: a "word" is any stretch of
> audio **louder than `WORD_AMPLITUDE_THRESHOLD`** (see Decision
> Logic Step 6 — a separate, stricter threshold than `NOISE_FLOOR`)
> that follows a confirmed pause of at least 250ms. This reliably
> counts **deliberately paused** speech — words spoken with a clear,
> brief gap between each one — the way you'd count aloud ("one...
> two... three..."). It is **not** a transcription system: fast,
> naturally connected speech where words run together with little or
> no pause between them may under-count, since a real gap of 250ms or
> more may not exist between every word pair in fluent speech. This
> is expected, documented behaviour, not a bug to engineer around.
>
> **Ambient noise must not register as a word.** Background sounds —
> HVAC hum, a chair creak, papers shuffling, a distant conversation —
> are typically much quieter than a word spoken directly at the
> microphone, but can still be louder than `NOISE_FLOOR`. Using
> `NOISE_FLOOR` as the word-detection threshold is **not
> acceptable** — it will register this kind of ambient noise as
> spoken words. `WORD_AMPLITUDE_THRESHOLD` must be a separate,
> stricter constant, chosen empirically on your own hardware to sit
> clearly above ordinary background noise and clearly below a normal
> spoken word's peak amplitude.

**FR5 — Sensitivity switch.** An `M5Switch` with two states:

| State | Meaning |
|---|---|
| Off (default) | **Normal** mode — a louder sound is needed to fully brighten the LED |
| On | **Sensitive** mode — a quieter sound is enough to fully brighten the LED |

Toggling the switch must immediately change which ceiling value the
formula uses on the *next* `loop()` pass — there is no button to press
to "apply" the new mode. This must work reliably in both directions:
toggling **on** (Normal → Sensitive) and toggling **off** (Sensitive →
Normal) must each take effect on the very next `loop()` pass, with no
lag, no missed transition, and no case where the meter gets stuck
showing the previous mode's scaling after the switch has visibly
changed state.

> **Implementation note — corrected.** `M5Switch.get_state()` is
> confirmed, on this hardware, to lag on the **OFF** transition —
> badly enough that even a single read taken at the exact moment the
> switch is toggled off cannot be trusted. **Never call
> `sensitive_switch.get_state()` anywhere in this program — not in
> `loop()`, and not inside the switch's own event handler.** Instead,
> maintain a module-level flag (e.g. `is_sensitive`) that starts
> `False`, and **flip it** — `is_sensitive = not is_sensitive` —
> inside the switch's `VALUE_CHANGED` handler. `loop()` then reads
> that flag, never the switch itself, to choose the ceiling. This is
> the same "explicit tracked flag, never re-derived from the widget"
> pattern required for the switch in Lab 4, applied here for the same
> reason: the widget's own state-reading method cannot be trusted as
> a live source of truth.

> **The sensitivity switch changes level scaling only, not the word
> counter.** `WORD_AMPLITUDE_THRESHOLD` (used by the word counter to
> decide silent vs. not-silent, see Decision Logic Step 6) is fixed
> and identical in both modes — only the ceiling used for the
> LED/percentage calculation changes with the switch. A word count
> that changes behaviour when the switch is toggled has not met this
> requirement.

**FR6 — Mode label.** An `M5Label`, next to or below the switch, that
updates the instant the switch is toggled (i.e. from the switch's
`VALUE_CHANGED` handler, not from `loop()`) to read exactly
`"Mode: Normal"` or `"Mode: Sensitive"` — correctly, in both
directions. Since the handler flips `is_sensitive` rather than reading
`get_state()` (see the implementation note above), the mode label text
must be derived from the same flipped flag, not from a separate read
of the switch.

**FR7 — Touch-only operation.** The sensitivity switch must be usable
by touch alone on the physical CoreS3. (The LED, percentage label, and
word count label require no touch interaction at all — that's the
point of them.)

**FR8 — No blocking calls beyond the recording itself.** Aside from
waiting for `Mic.isRecording()` to clear after a `Mic.record()` call,
`loop()` must not contain `time.sleep()` calls or any other blocking
operation. Your recording buffer must be small enough that this wait
is not perceptible as lag in the LED update, the word count, or the
switch's touch response — see the buffer size requirement below.

> **Flush the display every pass.** Call `M5.update()` once at the
> top of `loop()` (as always) **and again after your `set_text()` /
> `set_brightness()` calls**, before `loop()` returns. Without the
> second call, this pass's changes are not guaranteed to reach the
> physical screen until the *next* pass's `M5.update()` runs — an
> extra, avoidable display lag stacked on top of the buffer timing
> itself, and the word count label in particular will visibly lag
> behind the moment a word was actually detected if this is skipped.

### Decision Logic (required — implement exactly)

This reuses the clamp-and-scale pattern from Lecture 7 §3, applied to
the level meter, with one fixed ceiling per mode and a shared noise
floor. The word counter in Step 6 below uses the silence-gap state
machine from Lecture 7 §6.

**Step 1 — Record a buffer and compute its peak amplitude.** Use a
`bytearray` of exactly **1024 bytes**, recorded at **16000 Hz**, mono
(`stereo=False`). Unpack it as 16-bit signed little-endian samples and
take the largest absolute value found — this is `peak`.

**Step 2 — Choose the ceiling for the current mode:**

| Mode | Switch state | Ceiling |
|---|---|---|
| Normal | Off | 16000 |
| Sensitive | On | 6000 |

Both modes share the same **noise floor of 200**. There's one mode for
the whole meter, not a separate one per anything else.

**Step 3 — Clamp `peak` to `[noise_floor, ceiling]`.** A `peak` below
`200` must be treated as `200` (silence, not a negative or undefined
result); a `peak` above the current mode's ceiling must be treated as
that ceiling — an unclamped value can otherwise scale to a percentage
outside `0`–`100`.

**Step 4 — Convert the clamped peak to a 0.0–1.0 fraction:**

```
fraction = (clamped_peak - noise_floor) / (ceiling - noise_floor)
```

**Step 5 — Percentage (integer, 0–100):**

```
percent = int(fraction * 100)
```

Worked check (Normal mode, ceiling = 16000, noise floor = 200): a
`peak` of `200` or lower must produce `percent = 0`. A `peak` of
`16000` or higher must produce `percent = 100`. A `peak` of `8100`
(the floor-to-ceiling midpoint) must produce `percent = 50`.

Worked check (Sensitive mode, ceiling = 6000): the same `peak` of
`200` still produces `percent = 0`, but a `peak` of `3100` — far below
what Normal mode needs — now produces `percent = 50`, and a `peak` of
`6000` produces `percent = 100`, instead of requiring the much louder
`16000` Normal mode needs to fully brighten the LED.

Worked check (toggle round-trip): a room producing a steady `peak` of
`4000` shows `percent = 24` in Normal mode. Toggling to Sensitive mode
with that same `4000` `peak` produces `percent = 65`. Toggling back to
Normal with that same `4000` `peak` must produce `percent = 24` again
— **not** a value still computed as though Sensitive mode were active.
A meter that reaches Sensitive correctly but fails this last step
(stuck showing Sensitive-mode scaling after switching back to Normal)
has not met FR4.

**Step 6 — Word count via silence-gap detection.** Every `loop()` pass
also feeds `peak` (the same value from Step 1) into a small state
machine that tracks spoken words:

- A buffer is **silent, for word-detection purposes,** if
  `peak < WORD_AMPLITUDE_THRESHOLD` — **not** `NOISE_FLOOR`. This is a
  deliberately separate, stricter constant: `NOISE_FLOOR` only ever
  meant "treat this as 0% on the level meter" and sits close to the
  microphone's own electrical noise, so ordinary ambient sound
  (a chair creak, HVAC hum, a nearby conversation) can easily be
  louder than `NOISE_FLOOR` while still being much quieter than an
  actual word spoken at the mic. `WORD_AMPLITUDE_THRESHOLD` must be
  chosen empirically on your own hardware — the same "test it and
  defend your choice" approach used for the Normal/Sensitive ceilings
  — to sit clearly above typical background noise and clearly below a
  normal spoken word's peak amplitude.
- Track `silent_run`, a count of **consecutive** passes below
  `WORD_AMPLITUDE_THRESHOLD`.
- Track `in_word`, a flag for whether a word is currently in progress.
- **Once `silent_run` reaches `WORD_GAP_PASSES`, the gap is confirmed
  and `in_word` is cleared.** `WORD_GAP_PASSES` is the number of
  `loop()` passes closest to a 250ms gap, given your buffer's actual
  duration — for the required 1024-byte/16000 Hz buffer (≈32ms per
  pass), that's **`WORD_GAP_PASSES = 8`** (≈256ms; 250 does not divide
  evenly by ≈32ms, so this rounding is expected).
- **The moment a buffer at or above `WORD_AMPLITUDE_THRESHOLD` arrives
  while `in_word` is `False`,** that is the start of a new word:
  increment `word_count` by exactly one, and set `in_word` to `True`.
  Every such buffer after that, until the next confirmed gap, belongs
  to the *same* word and must **not** increment the count again.

Worked check (ambient noise ignored): a stream of buffers with `peak`
values above `NOISE_FLOOR` but below `WORD_AMPLITUDE_THRESHOLD` — e.g.
a steady `peak` of `500` with `WORD_AMPLITUDE_THRESHOLD = 1500` —
must produce a final `word_count` of `0`, no matter how long the
stream runs. A solution that reuses `NOISE_FLOOR` as the
word-detection threshold and therefore counts this as a word has not
met Step 6.

Worked check (three clean words): three words, each several loop()
passes long, separated by silence runs of exactly `WORD_GAP_PASSES`
passes, must produce a final `word_count` of `3` — not more, not
fewer.

Worked check (no false split): a single word containing one brief dip
in volume lasting *fewer* than `WORD_GAP_PASSES` consecutive silent
passes (e.g. a stop consonant or a short intake of breath mid-word)
must still count as **one** word, not two — the gap must be confirmed
for the full `WORD_GAP_PASSES` before a new word can start.

Worked check (background noise): a stream that is silent for its
entire duration, or that contains only a single sustained non-silent
sound with no confirmed gap anywhere in it, must produce a
`word_count` of `0` or `1` respectively — never a count that increases
on its own from steady background noise or a single held tone.

Worked check (counted without a trailing gap): a word that is still
in progress when the program is observed — i.e. no confirmed gap has
happened yet *after* that word — must still be included in
`word_count`. Counting happens on the **rising edge out of a confirmed
gap**, not on the gap that follows a word, so the most recent word
does not need a trailing pause to be counted.

---

### Code Requirements

- **Required header block.** Every submitted `.py` file must begin
  with the following header, as comments, with all fields filled in —
  no placeholders left in the submitted version:

  ```python
  # File:                 prg455.263.lab6.py
  # Author:               first, lastname
  # Date Submitted:       mm/dd/yyyy
  # Purpose:              solution to lab6
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
  change (`prg455.263.lab6.py` / `solution to lab6`).
- Standard `setup()` / `loop()` structure, `M5.begin()` → `m5ui.init()`
  → build widgets → `page0.screen_load()`, with the try/except
  error-reporting wrapper used throughout this course.
- `Mic.begin()` must be called once, in `setup()`. Do not call it
  repeatedly from `loop()`.
- Recording buffer must be a `bytearray(1024)`, recorded at `16000` Hz,
  mono — exactly as specified in Decision Logic Step 1. A different
  buffer size or sample rate changes how quickly the meter responds
  **and** changes `WORD_GAP_PASSES` (the buffer duration must still
  divide into the required ~250ms gap sensibly) and is not acceptable
  for grading purposes.
- The word counter's state (`silent_run`, `in_word`, `word_count`)
  must be tracked across `loop()` passes — e.g. as module-level
  variables updated with the `global` keyword — the same pattern
  already used for tracked state in Lab 4. Do not recompute the count
  from scratch each pass; it must accumulate over the program's
  entire run.
- `WORD_AMPLITUDE_THRESHOLD` must be its own named constant, distinct
  from `NOISE_FLOOR`, used only by the word counter's silence check.
  Reusing `NOISE_FLOOR` for word detection is not acceptable — see the
  worked check above.
- **Never call `sensitive_switch.get_state()` anywhere in this
  program.** Maintain a module-level flag (e.g. `is_sensitive`) that
  is **flipped** — not read from the switch — inside the switch's
  `VALUE_CHANGED` handler, and have both the mode label and `loop()`'s
  ceiling selection use that flag. See the Implementation Note under
  FR5.
- Call `M5.update()` a second time at the end of `loop()`, after your
  `set_text()`/`set_brightness()` calls, so this pass's changes are
  flushed to the screen immediately rather than waiting for the next
  pass. See the note under FR8.
- Use **M5UI widgets only** — labels, LED, and switch, nothing else
  needed for this lab.
- Comment your code — explain the peak-amplitude calculation, the
  clamp-and-scale formula, the Normal/Sensitive ceiling logic, the
  silence-gap word-counting state machine and why it uses a separate
  amplitude threshold, why the switch's mode is tracked with a flipped
  flag rather than `get_state()`, and which parts of your code run
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
- [ ] The LED is present and doesn't overlap any label or the switch.
- [ ] In a quiet room, in Normal mode, the LED sits at or near fully
      dim/off and the percentage label reads at or near `0%`.
- [ ] Making a sustained loud sound near the device (talking directly
      at it, a hand clap close to the mic) visibly and smoothly
      brightens the LED and raises the percentage, with no jumps,
      freezes, or crashes.
- [ ] The percentage label updates continuously, in step with the LED,
      as a whole-number percentage with no decimal places.
- [ ] The word count label has a **blue background and white text**
      and is clearly legible.
- [ ] Starting from a quiet room, saying five words slowly and clearly
      **with a deliberate pause between each one** (e.g. counting
      "one... two... three... four... five" with a visible gap between
      each) results in the word count reading `5`.
- [ ] Speaking a single sustained sound with no gaps (a held "ahh")
      increases the word count by exactly `1`, not more.
- [ ] Sitting quietly with normal room/background noise present (not
      dead silence — HVAC hum, computer fans, distant hallway noise)
      does **not** increase the word count on its own. This is a
      distinct check from pure silence — ambient noise is the
      specific failure mode `WORD_AMPLITUDE_THRESHOLD` exists to
      prevent.
- [ ] The word count **never decreases** and never resets back to `0`
      on its own while the program keeps running.
- [ ] The word count label updates **immediately**, in the same visual
      frame as the LED and percentage label — not one or more passes
      later. If it visibly trails behind an obviously spoken word,
      confirm `M5.update()` is called both at the top of `loop()` and
      again after your `set_text()` calls.
- [ ] Toggling the sensitivity switch does **not** change how the word
      count behaves — only the LED/percentage scaling changes.
- [ ] Toggling the sensitivity switch **on** immediately changes the
      mode label to "Mode: Sensitive" and visibly makes the LED reach
      full brightness at a noticeably quieter sound level than in
      Normal mode.
- [ ] Toggling the sensitivity switch **back off** immediately changes
      the mode label back to "Mode: Normal" and the LED visibly
      returns to needing a louder sound to reach full brightness on
      the very next update — this direction specifically must be
      re-tested, not assumed to work just because toggling on worked.
- [ ] Toggle on and off **at least five times in a row**, making
      sounds at varying volume between toggles, to confirm the mode
      never gets stuck on Sensitive after switching back to Normal —
      this was a known failure mode caused by relying on
      `sensitive_switch.get_state()`, and must be verified by repeated
      toggling, not a single on/off pass.
- [ ] Reading through your own code, confirm `sensitive_switch.get_state()`
      is never called anywhere — not in `loop()`, not in the event
      handler. The mode must come only from a flag flipped inside the
      handler.
- [ ] The LED, word count, and switch all keep updating and stay
      responsive at the same time — no stalls, no missed touches, no
      perceptible lag from the recording buffer.
- [ ] The percentage never leaves the 0–100 range, even under a very
      loud sound close to the microphone (clamp is working).

---

### Submission Instructions

1. Create a `lab6/` directory in your course GitHub repository (the
   private repo with `danny-arroway` added as a collaborator).
2. Place your final `.py` file in `lab6/`.
3. Commit and push before the deadline: **[INSTRUCTOR: insert due date]**.
4. If you used AI assistance, `PROMPTS.md` must be present and current
   in your repo root.

---

### Marking Rubric — Out of 100

Graded by running the submitted program on a physical CoreS3 and
working through the checklist above, cross-referencing percentage
values against the Decision Logic worked checks for spot checks in
both modes, using controlled test sounds at known relative volumes.

| # | Criterion | What's checked | Points |
|---|---|---|---|
| 1 | Title | Present, legible, no overlap | 5 |
| 2 | Sound-driven LED present and correctly configured | One `M5LED` widget, updates every `loop()` pass from a freshly recorded microphone buffer, not from a touch event; buffer size and sample rate match spec | 10 |
| 3 | Peak amplitude & clamp-and-scale formula correctness | `peak` computed correctly from the PCM buffer (largest absolute 16-bit sample); percentage matches the exact Decision Logic formula for arbitrary peak values in both modes, including clamped edge cases | 15 |
| 4 | Live percentage label | Updates in step with the LED, whole-number percentage, correct trailing `%`, no decimals | 10 |
| 5 | Word count label and detection correctness | Blue background, white text, legible; count increments correctly on confirmed ~250ms silence gaps per the exact Decision Logic Step 6 state machine, using a dedicated `WORD_AMPLITUDE_THRESHOLD` (not `NOISE_FLOOR`) so ordinary ambient noise is not counted; does not falsely split a single word on a brief dip; never decreases; unaffected by the sensitivity switch; updates immediately, without visible display lag | 25 |
| 6 | Sensitivity switch and mode label | Switch present and touch-responsive; `sensitive_switch.get_state()` is never called anywhere in the program; mode tracked via a flag flipped inside the event handler; mode label updates immediately on toggle with the exact required text; ceiling changes correctly in **both** directions (Normal→Sensitive and Sensitive→Normal), verified by **repeated** toggling (at least five on/off cycles), not just a single toggle | 15 |
| 7 | Responsiveness | No blocking calls beyond the recording wait itself; `M5.update()` called both before recording and after this pass's `set_text()`/`set_brightness()` calls so changes flush immediately; LED, word count, and switch all stay responsive simultaneously; buffer size/sample rate keep the wait imperceptible | 10 |
| 8 | Code quality | Comments explain the peak-amplitude calculation, the clamp-and-scale formula, the silence-gap word-counting state machine and its separate amplitude threshold, why the switch's mode is tracked via a flipped flag rather than `get_state()`, the poll-driven vs. event-driven split, and the double `M5.update()` call; standard program structure; `PROMPTS.md` present if AI was used | 10 |
| | **Subtotal** | | **100** |
| — | **Required header block** | Deduction, not a scored criterion: **-10 points (10%) from the total above** if the required header block (see Code Requirements) is missing, incomplete, or has any placeholder text left in it | -10 |
| | **Total** | | **100** |
