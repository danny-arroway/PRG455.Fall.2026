# PRG455 — Event Driven Programming
## Lab Test 1 — Part B: About Me Profile

**Marks:** 85 of the 100-point Lab Test 1 rubric (Lab Test 1 as a
whole is worth 22% of the final course grade) · **Scope:** Weeks 1–5,
plus independent research into one new API not yet covered in lecture
(see FR6)

---

### Scenario

Build a small on-device "profile card" program that collects a few
choices about you via touch, then generates a Markdown file
summarizing them — the kind of self-reported metadata an instructor
might collect at the start of a course, but gathered entirely through
the device's own touchscreen, with the device also reporting a fact
about itself (its MAC address) that only it can know.

### What You're Building

A single-screen M5UI application with:

1. A **title label** reading exactly **"About Me"**.
2. A **Program slider** — 4 positions, selecting one of **"EET"**,
   **"ECT"**, **"ECTC"**, **"EEN"**.
3. A **Grade slider** — 12 positions, selecting one of **"A+"**,
   **"A"**, **"A-"**, **"B+"**, **"B"**, **"B-"**, **"C+"**, **"C"**,
   **"C-"**, **"D+"**, **"D"**, **"F"**, in that order.
4. A **Claude Model slider** — 5 positions, selecting one of
   **"Opus 4.8"**, **"Opus 5"**, **"Sonnet 5"**, **"Haiku 4.5"**,
   **"Other"**.
5. A button labelled **"Create Profile"** that, on press, generates
   `about_me.md` on the CoreS3's flash filesystem, containing the
   information in FR6.

Each slider needs its own label showing the currently selected option
in words — not the raw numeric slider position — updating immediately
as the slider moves, left or right, to any of its positions.

---

### Functional Requirements

**FR1 — Title.** A label reading exactly `"About Me"`, visible,
legible, not overlapping any other widget.

**FR2 — Program slider.** An `M5Slider` with **4 positions**
(`min_value=0`, `max_value=3`) mapped to `["EET", "ECT", "ECTC",
"EEN"]` in that order (position 0 = "EET", position 3 = "EEN"). Its
label must update immediately, in both directions, to show the
currently selected program name as the slider is dragged.

**FR3 — Grade slider.** An `M5Slider` with **12 positions**
(`min_value=0`, `max_value=11`) mapped to `["A+", "A", "A-", "B+",
"B", "B-", "C+", "C", "C-", "D+", "D", "F"]` in that order. Same live
label-update requirement as FR2, in both directions.

**FR4 — Claude Model slider.** An `M5Slider` with **5 positions**
(`min_value=0`, `max_value=4`) mapped to `["Opus 4.8", "Opus 5",
"Sonnet 5", "Haiku 4.5", "Other"]` in that order. Same live
label-update requirement as FR2 and FR3, in both directions.

Every slider in this program uses the same underlying pattern — an
`M5Slider` with `get_value()` returning an integer index, used to look
up a string in a fixed list, displayed in a label via `set_text()` on
`VALUE_CHANGED`. If you get one slider's label updating correctly,
the other two are the same pattern with a different list.

**FR5 — Create Profile button.** On press, generates a file at
`/flash/about_me.md` containing, **in this order**:

1. **The same 10-field header block** used in every lab this term
   (File, Author, Date Submitted, Purpose, Student Number, Seneca
   E-mail, Seneca username, Course Code/Section, GitHub URL, Core S3
   Device MAC) — written as regular Markdown text in the file, not as
   Python comments, since `about_me.md` is not a `.py` file.

   **Nine of these ten fields are static, personal information you
   already know before you ever run your program** — the same way you
   fill in the `.py` header's `Author:`, `Date Submitted:`, etc. by
   hand before submitting a lab. Type your real values for File,
   Author, Date Submitted, Purpose, Student Number, Seneca E-mail,
   Seneca username, Course Code/Section, and GitHub URL directly into
   your source code — e.g. as literal strings you build the file's
   content from — **before** you run the program on your CoreS3.
   There is no requirement to collect any of these nine fields through
   a widget, a prompt, or any other on-device input; hard-coding them
   is correct and expected, exactly like the `.py` header itself.

   **The tenth field, `Core S3 Device MAC`, is the one exception.** It
   must be obtained **programmatically, at runtime, from the device
   itself** — see FR6 — never typed in as a literal string, even
   though it looks like ordinary text sitting next to the other nine.
   If your header block reads correctly but the MAC address is a
   value you copy-pasted or typed in by hand, this field does not meet
   FR5 or FR6, regardless of whether the number happens to be your
   device's real MAC.
2. **The three slider selections** — program, expected grade, and
   Claude model used — clearly labelled, in words (e.g. "Program:
   ECT"), not as raw slider positions. Unlike the nine static header
   fields above, these three **must** come from reading each slider's
   current value at the moment Create Profile is pressed — they are
   the one part of the header-and-selections content that is supposed
   to change based on what happens on the device during the test.
3. **A reference to the photo** taken in Part A. You do not need to
   re-capture a photo in Part B — reference the `photo.jpg` already
   saved to `/flash` in Part A (e.g. a Markdown image link
   `![photo](photo.jpg)`, or a line noting the filename — either is
   acceptable, as long as it's clearly present and points at the
   correct file).

The file must be **plain Markdown text**, openable and readable in any
text editor or Markdown viewer — not JSON, not a binary format, not
Python source.


**FR6 — Programmatic MAC address (new API — not covered in lecture).**
The `Core S3 Device MAC` field in FR5 must be obtained **at runtime,
from the device**, not hand-typed from a label or a previous lab's
header. This requires a MicroPython networking call this course
hasn't covered yet. You are expected to find it yourself, the same way
you'd research an unfamiliar API on the job: search the UIFlow2 /
MicroPython documentation, or ask Claude, and verify whatever you find
actually works on your physical CoreS3 before trusting it — the same
verify-on-hardware habit this course has asked for since Lecture 2. A
few things worth knowing before you start looking:

- The relevant functionality lives in a module you `import` separately
  from `M5`, `m5ui`, and `lvgl` — one you haven't imported in any
  previous lab.
- Whatever object or interface you find will very likely need to be
  explicitly turned on before it reports a usable value — an inactive
  interface is a common reason this kind of call returns nothing
  useful, or raises an error.
- You do **not** need to connect to a Wi-Fi network, provide an SSID,
  or provide a password to get a MAC address — the value comes from
  the hardware itself, not from a network connection.
- The value you get back may not initially be in the readable
  colon-or-no-separator hex format used everywhere else in this course
  (e.g. `1CFED5BD87D2`) — you may need to format it yourself.
- Document what you tried, what worked, and what didn't in
  `PROMPTS.md` if you used AI to help find or debug this — this is
  exactly the kind of verification work the course has asked you to
  record all term.

**FR7 — Layout.** No two widgets may overlap at any point during
normal operation, including all three sliders and their labels.

**FR8 — Touch-only operation.** The entire panel must be usable by
touch alone on the physical CoreS3.

---

### Code Requirements

- **Required header block** in the `.py` file itself:

  ```python
  # File:                 prg455.263.testX_partB.py
  # Author:               first, lastname
  # Date Submitted:       mm/dd/yyyy
  # Purpose:              solution to Lab Test 1, Part B
  # Student Number:       Seneca Polytechnic student number
  # Seneca E-mail:        Seneca student e-mail address
  # Seneca username:      Seneca My.Seneca username
  # Course Code/Section:  PRG455X
  # GitHub URL:           Student GitHub web address
  # Core S3 Device MAC:   (eg. 1CFED5BD87D2)
  ```

  Align the second field five tabs from the first, exactly as shown
  above. This is separate from, and in addition to, the header block
  FR5 requires *inside* the generated `about_me.md` — one is a comment
  block in your source code, the other is Markdown content in a file
  your program produces, and the two are not the same requirement even
  though the fields are identical.
- Standard `setup()` / `loop()` structure, `M5.begin()` → `m5ui.init()`
  → build widgets → `page0.screen_load()`, with the try/except
  error-reporting wrapper used throughout this course.
- Use **M5UI widgets only**, except for whatever module FR6 requires
  — no other exceptions.
- Wrap the Create Profile button's handler body in its own
  `try`/`except`, per the pattern from Lecture 5 §4 — file generation
  is exactly the kind of operation that can fail silently inside an
  event handler if you don't.
- Comment your code — explain how each slider's index maps to its
  option list, and what you found out about the MAC address API and
  how you verified it actually works.
- If you use an AI tool anywhere in building this: **commit your own
  working code before you modify it further with AI assistance**, and
  keep `PROMPTS.md` up to date — same standard as every lab this term,
  and specifically required for FR6's research step.

---

### Testing Checklist (self-check before you submit)

Run through this on your **physical CoreS3**:

- [ ] Required header block present in the `.py` file, complete, no
      placeholders.
- [ ] Title reads exactly "About Me", no overlaps with anything.
- [ ] All three sliders' labels update correctly and immediately, in
      both directions, at every position — test each slider across
      its full range, not just one or two positions.
- [ ] Create Profile button generates `/flash/about_me.md` containing,
      in order: the 10-field header (9 fields hard-coded into your
      source ahead of time with your real information, plus a
      device-obtained MAC address — not a hand-typed one), the three
      slider selections in words, and a reference to `photo.jpg`.
- [ ] The MAC address in the generated file matches the MAC address
      you can confirm independently (e.g. from the UIFlow2 web
      editor's device info, or from `os.stat`/`dir()` exploration) —
      it isn't a placeholder or a copy-pasted value.
- [ ] `about_me.md` opens and displays correctly as plain text/Markdown
      — not garbled, not empty, not missing any of the three required
      sections.
- [ ] No two widgets overlap at any point.
- [ ] Program survives repeated slider adjustments and multiple
      Create Profile presses without crashing.

---

### Submission Instructions

1. Create a `labTest1/partB/` directory in your course GitHub
   repository.
2. Place your final `.py` file **and** the retrieved `about_me.md` in
   `labTest1/partB/`. As with Part A's `photo.jpg`, this must be the
   actual file your program generated on your device during this test
   session, retrieved the same way you retrieved `photo.jpg` in Part A.
3. Commit and push before the end of the test window —
   **[INSTRUCTOR: insert exact cutoff time]**.
4. `PROMPTS.md` (shared with Part A, in your repo root) must be
   present and current if you used AI assistance — this is especially
   expected for FR6's research step.

---

### Marking Rubric — 85 Points (of Lab Test 1's 100-point total)

| # | Criterion | What's checked | Points |
|---|---|---|---|
| 1 | Title | "About Me" title present, exact text, no overlap with anything | 5 |
| 2 | Program slider (FR2) | 4 correct positions, mapped to the exact list and order specified; label updates correctly and immediately in both directions across the full range | 8 |
| 3 | Grade slider (FR3) | 12 correct positions, mapped to the exact list and order specified; label updates correctly and immediately in both directions across the full range | 8 |
| 4 | Claude Model slider (FR4) | 5 correct positions, mapped to the exact list and order specified; label updates correctly and immediately in both directions across the full range | 8 |
| 5 | Create Profile button wiring | Button present, correctly dispatches on `CLICKED`, handler wrapped in its own `try`/`except` per Lecture 5 §4 | 6 |
| 6 | `about_me.md` — header section | Contains the full 10-field header, as Markdown content; the 9 static fields (File, Author, Date Submitted, Purpose, Student Number, Seneca E-mail, Seneca username, Course Code/Section, GitHub URL) are correctly hard-coded with real information, and the MAC field is not a hand-typed/copy-pasted value (checked jointly with criterion 9) | 12 |
| 7 | `about_me.md` — slider selections section | All three slider selections present, shown in words (not raw index values), clearly labelled | 8 |
| 8 | `about_me.md` — photo reference section | Clear, correctly-pointing reference to `photo.jpg` from Part A | 6 |
| 9 | Programmatic MAC address (FR6) | MAC address is obtained at runtime from the device (not hand-typed), correctly formatted, and verified to match the device's actual MAC | 16 |
| 10 | Layout | No two widgets overlap at any point during normal operation | 4 |
| 11 | Retrieval | `about_me.md` is present in `labTest1/partB/` in the submitted repository, and is the actual file generated during this test session | 2 |
| 12 | Code quality | Comments explain the slider-index pattern and the MAC lookup; `PROMPTS.md` current, especially for the FR6 research step | 2 |
| | **Part B Subtotal** | | **85** |

---

### Lab Test 1 — Combined Rubric Total

| Part | Points |
|---|---|
| Part A — Countdown Snapshot | 15 |
| Part B — About Me Profile | 85 |
| **Lab Test 1 Total** | **100** |

Lab Test 1's 100-point rubric total maps to **22% of the final course
grade**, as shown in the course outline and addendum — the 15/85 split
above is the internal marking breakdown between the two parts, not a
separate weighting on top of the 22%.
