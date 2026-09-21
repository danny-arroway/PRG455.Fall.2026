# PRG455 — Event Driven Programming
## Lab 3: Local AI GPU Advisor

**Prerequisite:** Lecture 3 (Basic GUI Widgets & Touch Input). You should
be comfortable with `M5Label`, `M5Button`, `M5Slider`, the
`VALUE_CHANGED` event pattern, and the text-wrapping technique from
Lecture 3 §4 before starting this lab.

---

### Scenario

A small AI lab is helping researchers pick which GPU to buy for running
local Qwen models on their own hardware, based on the model they plan
to run, how it's quantized, and how much context window they need. Your
job is to build that advisor as a touchscreen panel running directly on
the CoreS3.

### What You're Building

A single-screen M5UI application with:

1. A **title**.
2. Three **sliders**, each paired with a label that shows the currently
   selected value in readable form:
   - **Model** — one of six Qwen models (see table below).
   - **Quantization** — 4-bit (partial) or 16-bit (full).
   - **Context window** — 8K tokens or 256K tokens.
3. A **Recommend** button that computes a GPU recommendation from the
   three current slider values and displays it.
4. A **Reset** button that returns all three sliders (and their labels)
   to their starting position and clears the recommendation.

---

### Functional Requirements

**FR1 — Title.** Visible, legible, doesn't overlap other widgets.

**FR2 — Model slider.** An `M5Slider` with 6 positions (`min_value=0`,
`max_value=5`), each position corresponding to one of these models in
this order:

| Position | Model |
|---|---|
| 0 | Qwen2-VL-2B |
| 1 | Qwen2.5-3B |
| 2 | Qwen3-4B |
| 3 | Qwen2.5-7B |
| 4 | Qwen2.5-14B |
| 5 | Qwen2.5-32B |

A label next to or below the slider must update live, as the slider is
dragged, to show the current model's name (e.g. "Model: Qwen2.5-7B").

**FR3 — Quantization slider.** An `M5Slider` with 4 positions
(`min_value=0`, `max_value=3`), corresponding to:

| Position | Quantization |
|---|---|
| 0 | 4-bit |
| 1 | 8-bit |
| 2 | 12-bit |
| 3 | 16-bit |

A label must update live to show the current selection.

**FR4 — Context window slider.** An `M5Slider` with 6 positions
(`min_value=0`, `max_value=5`), corresponding to:

| Position | Context |
|---|---|
| 0 | 8K tokens |
| 1 | 16K tokens |
| 2 | 32K tokens |
| 3 | 64K tokens |
| 4 | 128K tokens |
| 5 | 256K tokens |

A label must update live to show the current selection.

**FR5 — Recommend button.** On press, it must:
1. Read the current position of all three sliders.
2. Compute the estimated VRAM requirement using the **exact formula in
   the Decision Logic section below** — this is not open to
   interpretation, since it's what makes the lab gradable.
3. Display the matching recommendation string (one of the four listed
   in Decision Logic) in the result area.
4. **Wrap the displayed text** using the technique from Lecture 3 §4 —
   none of the four possible recommendation strings fit on one line at
   a readable font size, and the result area must be sized with enough
   vertical room for the wrapped text, entirely within the visible
   240px screen height. No part of the result may be cut off or run
   past the bottom edge of the screen.

**FR6 — Reset button.** On press, it must, in one action:
- return all three sliders to position 0,
- update all three labels back to their position-0 text
  ("Model: Qwen2-VL-2B", "Quantization: 4-bit", "Context: 8K tokens"),
  and
- clear the result area completely.

**FR7 — Touch-only operation.** The entire panel must be usable by
touch alone on the physical CoreS3.

### Decision Logic (required — implement exactly)

This is a simplified estimation model for teaching purposes, not a
precise real-world VRAM calculator, but it's internally consistent and
every one of the 144 possible input combinations (6 models × 4
quantization levels × 6 context sizes) has one unambiguous correct
answer, which is what matters for grading.

**Step 1 — Base VRAM (GB), from model parameter count at 16-bit:**

| Model | Parameters (B) | Base VRAM (params × 2) |
|---|---|---|
| Qwen2-VL-2B | 2 | 4 GB |
| Qwen2.5-3B | 3 | 6 GB |
| Qwen3-4B | 4 | 8 GB |
| Qwen2.5-7B | 7 | 14 GB |
| Qwen2.5-14B | 14 | 28 GB |
| Qwen2.5-32B | 32 | 64 GB |

**Step 2 — Quantization multiplier = bits ÷ 16** (16-bit is the
reference, full-precision case):

| Quantization | Multiplier |
|---|---|
| 4-bit | 0.25 |
| 8-bit | 0.5 |
| 12-bit | 0.75 |
| 16-bit | 1.0 |

**Step 3 — Context window addition (GB) = context in thousands of
tokens ÷ 16** (a simplified stand-in for KV-cache growth):

| Context | Addition |
|---|---|
| 8K | 0.5 GB |
| 16K | 1.0 GB |
| 32K | 2.0 GB |
| 64K | 4.0 GB |
| 128K | 8.0 GB |
| 256K | 16.0 GB |

Note: Steps 2 and 3 both divide by 16, but for unrelated reasons — 16
is the reference bit-depth in Step 2, and a chosen scaling constant in
Step 3. Don't read a deeper connection into that; it's a coincidence of
these particular numbers.

**Step 4 — Estimated VRAM (GB) = (Base VRAM × Quantization multiplier) + Context addition**

**Step 5 — GPU selection**, smallest tier that's large enough:

| If estimated VRAM is... | Recommendation string to display |
|---|---|
| ≤ 16 GB | `16GB, GeForce RTX 5080, NVIDIA, $1,200 - $1,450` |
| ≤ 24 GB | `24GB, GeForce RTX 4090, NVIDIA, $1,850 - $2,100` |
| ≤ 32 GB | `32GB, GeForce RTX 5090, NVIDIA, $2,000 - $2,900+` |
| > 32 GB | `64GB+, Radeon Pro W7900 / RTX 6000 Ada, AMD / NVIDIA, $3,500 - $7,000+` |

Use a plain hyphen (`-`), not an en dash, in the displayed strings —
CoreS3's built-in fonts only cover ASCII 32–126, and an en dash will
render as a box rather than the character you intended.

### Code Requirements

- **Required header block.** Every submitted `.py` file must begin with
  the following header, as comments, with all fields filled in — no
  placeholders left in the submitted version:

  ```python
  # File:                 prg455.263.lab3.py
  # Author:               first, lastname
  # Date Submitted:       mm/dd/yyyy
  # Purpose:              solution to lab3
  # Student Number:       Seneca Polytechnic student number
  # Seneca E-mail:        Seneca student e-mail address
  # Seneca username:      Seneca My.Seneca username
  # Course Code/Section:  PRG455X
  # GitHub URL:           Student GitHub web address
  # Core S3 Device MAC:   (eg. 1CFED5BD87D2)
  ```

  Align the second field five tabs from the first, exactly as shown
  above. This header is required on every lab, lab test, and project
  submission for the rest of the course, not just Lab 3 — update the
  `File:` and `Purpose:` lines to match each new submission
  (`prg455.263.labX.py`, `prg455.263.testY.py`, `prg455.263.projectZ.py`,
  and `solution to labX` / `testY` / `projectZ` respectively).
- Standard `setup()` / `loop()` structure, `M5.begin()` → `m5ui.init()`
  → build widgets → `page0.screen_load()`, with the try/except
  error-reporting wrapper used throughout this course.
- Use **M5UI widgets only** — labels, buttons, and sliders, nothing
  else needed for this lab.
- Comment your code — explain the VRAM formula and the slider-to-label
  mapping logic in your own words.
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
- [ ] Dragging the Model slider updates its label correctly at all 6
      positions.
- [ ] Dragging the Quantization slider updates its label correctly at
      all 4 positions.
- [ ] Dragging the Context slider updates its label correctly at all 6
      positions.
- [ ] Recommend produces the correct GPU string for at least 4
      different slider combinations, cross-checked against the
      Decision Logic appendix table.
- [ ] The full recommendation text is visible on screen with no part
      cut off at the bottom edge, for the longest possible string
      (the 64GB+ option).
- [ ] Reset returns all three sliders and labels to their defaults and
      clears the result, in one tap.

---

### Submission Instructions

1. Create a `lab3/` directory in your course GitHub repository (the
   private repo with `danny-arroway` added as a collaborator).
2. Place your final `.py` file in `lab3/`.
3. Commit and push before the deadline: **[INSTRUCTOR: insert due date]**.
4. If you used AI assistance, `PROMPTS.md` must be present and current
   in your repo root.

---

### Marking Rubric — Out of 100

Graded by running the submitted program on a physical CoreS3 and
working through the checklist above, cross-referencing outputs against
the appendix decision table for spot checks.

| # | Criterion | What's checked | Points |
|---|---|---|---|
| 1 | Title | Present, legible, no overlap | 5 |
| 2 | Three sliders present with correct ranges | Model (0-5), Quantization (0-3, four levels), Context (0-5, six levels) | 15 |
| 3 | Live label updates | All three labels correctly reflect their slider's current position at every valid value (6 + 4 + 6 = 16 positions total) | 20 |
| 4 | VRAM formula correctness | Recommend produces the exact correct output for arbitrary slider combinations, matching the Decision Logic table | 25 |
| 5 | Result display | Full text visible, correctly wrapped, no clipping at the screen edge | 10 |
| 6 | Reset button | All three sliders, all three labels, and the result area correctly reset in one tap | 15 |
| 7 | Code quality | Comments explain the formula and slider-label logic; standard program structure; `PROMPTS.md` present if AI was used | 10 |
| | **Subtotal** | | **100** |
| — | **Required header block** | Deduction, not a scored criterion: **-10 points (10%) from the total above** if the required header block (see Code Requirements) is missing, incomplete, or has any placeholder text left in it | -10 |
| | **Total** | | **100** |
