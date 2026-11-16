# PRG455 — Event Driven Programming
## Lab 8: Connectivity-Driven Interface (Dropdown Control) — Encrypted Credentials & Quote Fetcher

**Prerequisite:** Lecture 9 (Wireless Connectivity — the Dropdown
Widget) and `9.2_agentic_AI_and_Claude_Code.md` (Agentic AI and Claude
Code). You should be comfortable with `network.WLAN`'s connection
lifecycle, the confirmed `safe_connect()` pattern for guarding
`.connect()` calls, `M5Dropdown`'s `VALUE_CHANGED` event pattern, and
the distinction between a conversational prompt and an agentic task
before starting this lab.

**Due:** Monday, November 16, 2026 (one week after this lab's
introduction on Monday, November 9, 2026).

---

### Feasibility Note (read before starting)

Every functional requirement below has been checked against confirmed
UIFlow2 MicroPython APIs before being assigned. Four things are worth
knowing up front, because they shape how this lab should be built:

1. **`ucryptolib.aes` exists on this hardware**, but it requires
   fixed-size keys (16 or 32 bytes) and block-aligned padding — a lot
   of fiddly bookkeeping for a first encryption exercise. Since the
   lab's own instructions state the algorithm is arbitrary, this spec
   allows a much simpler **XOR stream cipher** derived from the
   passphrase as the default path, with AES available as an optional
   extension for students who want the added complexity. Decision
   Logic Step 2 below gives the exact XOR approach.
2. **HTTP requests on this hardware use the `requests2` module**, not
   bare `urequests` — some UIFlow2 firmware versions do not expose
   `urequests` directly and raise an import error if it's used. Use
   `import requests2` and `requests2.get(url)`.
3. **Every HTTP response object must be closed with `.close()`
   immediately after its text is read.** This is not a style
   preference — repeated `requests2.get()` calls without closing the
   response are a confirmed, documented cause of memory exhaustion on
   ESP32-based MicroPython devices, and this lab's Get Quote button is
   pressed repeatedly by design. Skipping `.close()` will eventually
   crash the program, likely partway through a demo.
4. **UIFlow2 deploys and runs a single uploaded `.py` file — it does
   not sync the rest of the project folder onto the device.** Two
   confirmed consequences, both non-obvious until you hit them on real
   hardware:
   - A cross-file `from encrypt_credentials import xor_cipher` in the
     main application raises `ImportError: no module named
     'encrypt_credentials'` on-device, even though both files sit
     side by side locally. The main application must define its own
     copy of `xor_cipher` rather than importing it.
   - A bare relative filename like `open(".credentials.sys", "rb")`
     raises `OSError: [Errno 2] ENOENT` on-device. The main
     application must use an absolute `/flash/` path
     (`/flash/.credentials.sys`), matching this course's established
     on-device path convention (see the camera lab's
     `/flash/photo.jpg`) — and the encrypted `.credentials.sys` must
     itself be uploaded to `/flash/` on the device, not just present
     in the local project folder. `encrypt_credentials.py`, by
     contrast, is meant to run on your laptop against the local
     project folder, so it correctly keeps using a plain relative
     path there.

> **A note on what this lab teaches about encryption, honestly.**
> Hardcoding the passphrase as a constant in the `.py` source file
> means the encrypted `.credentials.sys` file is only as secure as
> the source file itself — anyone who can read the program can decrypt
> the credentials. This is a reasonable, contained way to practice the
> *mechanics* of symmetric encryption (the same key locks and unlocks
> the data), but it is **not** how a real system would protect a
> secret. Say this to students directly rather than letting the
> exercise imply otherwise.

With those three points addressed, the specification as requested is
**feasible**, and is written below accordingly.

---

### Scenario

A campus IT helpdesk wants a simple kiosk app for testing whether a
demo device can reach the internet over a personal mobile hotspot,
and — once connected — wants that same kiosk to display a rotating
motivational quote from an internal web service, useful as a quick
"yes, the network and the display both work" smoke test before a
public demo. Because a hotspot password is sensitive information, it
must never sit in the repository as plain text — it has to be
encrypted at rest and only decrypted in memory when the program
actually needs to connect.

This lab is also the first in this course built using an **agentic
workflow**: instead of asking Claude for one function at a time, you
will hand Claude Code the whole task, in stages, reviewing its plan
and its diffs at each checkpoint, per `9.2_agentic_AI_and_Claude_Code.md`.

---

### What You're Building

A multi-stage touchscreen application:

1. **A one-time, manually-created credentials file** (`.credentials.sys`)
   containing your hotspot's SSID and password as plain text, created
   by hand before any code runs.
2. **An encryption utility** (built first, as its own Claude Code task)
   that prompts for a passphrase and encrypts `.credentials.sys` in
   place, so the plain-text version never remains on disk.
3. **A network-selector screen** — an `M5Dropdown` populated by a live
   Wi-Fi scan, connecting using a password decrypted from
   `.credentials.sys` at the moment it's needed.
4. **A quote-fetcher screen** — replacing the network selector once
   connected — with a bordered text area, a "Get Quote" button that
   fetches and displays text from a fixed URL, and a "Disconnect"
   button that ends the session.

---

### Part 1 — Manual Setup (no code, no AI assistance)

1. Create a folder named exactly `prg455.263.lab8` in your working
   directory.
2. Inside it, create a file named exactly `.credentials.sys`
   containing exactly two lines:
   - **Line 1:** your mobile phone's hotspot SSID
   - **Line 2:** your hotspot's password
3. Do **not** commit this plain-text file to GitHub. Add
   `.credentials.sys` to `.gitignore` in this lab's folder before your
   first commit — a plain-text password in version control history is
   a mistake even a later encryption step cannot undo, since the
   plain-text version remains in the repository's history.

---

### Part 2 — Encryption Utility (first agentic Claude Code task)

**FR1 — Passphrase prompt.** A separate script (e.g. `encrypt_credentials.py`)
must prompt whoever runs it to enter a passphrase — this passphrase is
**not** the hotspot password, and is never written to any file.

**FR2 — Encrypt in place.** Using the entered passphrase as a key, the
script must read the plain-text `.credentials.sys`, encrypt its
contents, and overwrite the file with the encrypted bytes. Once this
step is complete, `.credentials.sys` must **not** be human-readable —
opening it in a text editor must show unintelligible bytes, not the
original SSID and password.

**FR3 — Same passphrase decrypts it.** The encryption method chosen
must be reversible using the **same** passphrase — this lab does not
require a decryption script as a separate deliverable (the main
application decrypts the file itself, per FR8), but the encryption
step and the application's decryption step must use the identical
algorithm and the identical passphrase-to-key derivation.

**Agentic task framing for this part:** this is a good first exercise
in giving Claude Code a bounded, single-purpose task. A reasonable
prompt shape (per `9.2_agentic_AI_and_Claude_Code.md` §3):

```
CONTEXT: MicroPython on M5Stack Core S3. I have a plain-text file,
.credentials.sys, containing an SSID on line 1 and a password on
line 2.

TASK: Write a script that prompts for a passphrase, then encrypts
.credentials.sys in place using that passphrase as a key, so the
file's contents are no longer human-readable. The same passphrase
must be able to reverse the encryption later.

CONSTRAINTS: Use a simple, well-commented symmetric method (e.g. XOR
the file's bytes against a repeating key derived from the
passphrase) rather than a complex cryptographic library -- this is a
learning exercise in the mechanics of symmetric encryption, not a
production security tool. Never print or log the plaintext password
after encryption completes.

ACCEPTANCE: Running the script once prompts for a passphrase and
turns .credentials.sys into unreadable bytes. Running a corresponding
decrypt function with the same passphrase reproduces the original
two lines exactly.
```

---

### Part 3 — Network Selector Screen

**FR4 — Wi-Fi scan populating the dropdown.** On startup, scan for
available networks with `wlan.scan()` and populate an `M5Dropdown`
with the discovered SSIDs. `wlan.scan()` returns a list of tuples;
each tuple's first element is the SSID as bytes — decode it to a
string before adding it to the dropdown's options.

> **Confirmed on hardware — filter empty and duplicate SSIDs.** Hidden
> networks broadcast an empty SSID (`b""`); decoded, that's `""`,
> which shows up as a blank, unselectable dropdown row if not filtered
> out. Dual-band routers and mesh systems also commonly broadcast the
> same SSID more than once (2.4GHz + 5GHz, or per mesh node), which
> clutters the list with repeats. Drop empty-string SSIDs and
> de-duplicate before populating the dropdown's `options`.
>
> Separately — not a code issue, but a common source of "my phone's
> hotspot doesn't show up" confusion during testing: iOS Personal
> Hotspot can stop broadcasting its SSID when idle unless a device is
> already connected or the Settings → Personal Hotspot screen is open
> on the phone. Since the scan happens once, on startup, the hotspot
> also needs to already be broadcasting *before* the app starts —
> turning it on afterward means restarting the app to see it.

**FR5 — Selecting your hotspot connects to it.** When the dropdown's
selection changes, the program must:
1. Decrypt `.credentials.sys` in memory using the hardcoded passphrase
   constant (see FR7) to recover the SSID and password.
2. Confirm the decrypted SSID matches the dropdown's selected option
   (this guards against connecting with the wrong stored credentials
   if the file ever contains a different network than the one
   selected).
3. Call `safe_connect(ssid, password)` — reusing the exact guarded
   pattern confirmed in Lecture 9 §2, since selecting a dropdown
   option is exactly the kind of event that could otherwise call
   `.connect()` while a previous attempt is still resolving.

> **Confirmed on hardware — a wrong `DECRYPTION_PASSPHRASE` must not
> crash the handler.** XOR-ing with the wrong passphrase turns
> `decrypted` into effectively random bytes. `.decode("utf-8")` can
> raise `UnicodeError` on those bytes, and even when it doesn't,
> random bytes very likely contain no `"\n"` at all — `IndexError` on
> `lines[1]` — reproduced directly on this hardware from a passphrase
> mismatch between `encrypt_credentials.py`'s run and
> `DECRYPTION_PASSPHRASE`. Because this happens inside the dropdown's
> own event handler, an unguarded exception here freezes the whole
> app exactly like the unguarded `wlan.connect()` case in Lecture 9.
> Wrap the decode/split step in `try`/`except (UnicodeError,
> IndexError)` and treat a failure the same as an SSID mismatch (Step
> 3 below) — never let it propagate.

**FR6 — Poll-driven connection status.** While on this screen, a
status label must reflect `wlan.isconnected()`, re-checked every
`loop()` pass, exactly as established in Lecture 9.

**FR7 — Hardcoded passphrase constant.** The passphrase used to
decrypt `.credentials.sys` must be a single named constant near the
top of the program (e.g. `DECRYPTION_PASSPHRASE = "fill-this-in"`),
left as a clearly-marked placeholder for the student to fill in by
hand — this value must **never** be requested from, or written by,
Claude Code, since it is meant to be a manually-entered secret,
analogous to the API keys and credentials this course has already
told students never to hand to an AI tool.

---

### Part 4 — Quote Fetcher Screen

**FR8 — Screen transition on successful connection.** The instant
`wlan.isconnected()` becomes `True`, clear the network-selector screen
and build the quote-fetcher screen described below. This is a
one-time transition, not something re-checked every pass once it has
happened.

**FR9 — Quote fetcher layout.** A single-screen M5UI application with:
- A bordered `M5TextArea`, exactly 200×200 pixels, with a black
  border, used to display quote text.
- A **"Get Quote"** `M5Button` — white text on a red background.
- A **"Disconnect"** `M5Button` — white text on a red background,
  positioned beside the Get Quote button, using identical colors.

**FR10 — Fetching and displaying a quote.** When "Get Quote" is
pressed:
1. Clear the text area's current contents.
2. Perform `requests2.get("https://matrix.senecapolytechnic.ca/~danny.abesdris/cgi-bin/quote2025.cgi")`.
3. Read the response's text, **close the response with `.close()`**,
   and set the text area's contents to the retrieved text. Long text
   must wrap within the 200×200 area rather than being clipped or
   overflowing — `M5TextArea` wraps automatically by default; do not
   disable that behavior.
4. Every subsequent press must repeat this sequence from a cleared
   text area — never append to previously displayed text.

**FR11 — Response must always be closed.** Every single
`requests2.get()` call, with no exceptions, must have its response
object closed with `.close()` before the handler returns — including
on a failed or empty response. Structure this with a `try`/`finally`
so `.close()` still runs even if reading the response text raises an
error.

**FR12 — Disconnecting.** When "Disconnect" is pressed:
1. Call `wlan.disconnect()`.
2. Clear the entire screen (remove or hide the text area and both
   buttons).
3. Display the text `"Lab 8 Completed..."` as a label, horizontally
   and vertically centered on the screen.
4. No further interaction is required after this point — the program
   does not need to return to the network selector screen.

---

### Decision Logic (required — implement exactly)

**Step 1 — Reading the two-line credentials file.** `.credentials.sys`
contains the SSID on line 1 and the password on line 2 as plain text
before encryption. After decryption in memory, split on the newline
character to recover both values — do not assume a fixed byte length
for either field, since SSIDs and passwords vary in length. In the
main application, open the file with an absolute `/flash/` path
(`/flash/.credentials.sys`), confirmed required per the Feasibility
Note above — a bare relative filename raises `OSError: ENOENT`
on-device. Guard the decode/split against `UnicodeError` and
`IndexError` (see FR5's hardware note) rather than assuming
well-formed output.

**Step 2 — XOR-based encryption (default approach).** Encrypt by
XOR-ing each byte of the file against a repeating key derived from the
passphrase:

```python
def xor_cipher(data: bytes, passphrase: str) -> bytes:
    key = passphrase.encode("utf-8")
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
```

This function is its own inverse: calling it a second time with the
same passphrase on its own output reproduces the original bytes
exactly — `xor_cipher(xor_cipher(data, p), p) == data` for any
passphrase `p`. This is what makes it usable for both the encryption
utility (Part 2) and the application's in-memory decryption (FR5)
without needing two separate implementations.

Worked check: encrypting the two-line file
`b"MyHotspot\nMyPassword123\n"` with passphrase `"correct horse
battery staple"` and then decrypting the result with the same
passphrase must reproduce the original bytes exactly, including both
newlines.

**Step 3 — SSID confirmation before connecting.** Before calling
`safe_connect()`, compare the decrypted SSID against
`dropdown0.get_selected_str()`. If they don't match, do not attempt a
connection — show an error state instead (e.g. a status label reading
`"Credentials do not match selected network"`) rather than silently
attempting to connect with mismatched credentials.

**Step 4 — Guarded reconnect.** Reuse `safe_connect()` from Lecture 9
§2 verbatim:

```python
def safe_connect(ssid, password):
    try:
        if wlan.isconnected():
            wlan.disconnect()
        wlan.connect(ssid, password)
        return True
    except OSError:
        return False
```

**Step 5 — Response lifecycle for each quote fetch.**

```python
def fetch_quote():
    response = requests2.get(QUOTE_URL)
    try:
        return response.text
    finally:
        response.close()
```

The `finally` block guarantees `.close()` runs whether reading `.text`
succeeds or raises — this is the confirmed, required pattern for
avoiding the ESP32 memory-leak behavior described in the Feasibility
Note.

---

### Code Requirements

- **Required header block.** Every submitted `.py` file must begin
  with the following header, as comments, with all fields filled in —
  no placeholders left in the submitted version:

  ```python
  # File:                 prg455.263.lab8.py
  # Author:               first, lastname
  # Date Submitted:       mm/dd/yyyy
  # Purpose:              solution to lab8
  # Student Number:       Seneca Polytechnic student number
  # Seneca E-mail:        Seneca student e-mail address
  # Seneca username:      Seneca My.Seneca username
  # Course Code/Section:  PRG455X
  # GitHub URL:           Student GitHub web address
  # Core S3 Device MAC:   (eg. 1CFED5BD87D2)
  ```

  Align the second field five tabs from the first, exactly as shown
  above. The same header applies to `encrypt_credentials.py`, with
  `Purpose: encryption utility for lab8`.
- `.credentials.sys` must **never** be committed to GitHub in
  plain-text form. Add it to `.gitignore` before your first commit in
  this lab's folder.
- The passphrase used for decryption (FR7) must be a hardcoded
  constant filled in manually by the student — never generated,
  requested, or written by Claude Code.
- Use `requests2`, not bare `urequests`, for the HTTP GET in FR10 —
  confirmed to avoid an import error present in some UIFlow2 firmware
  versions.
- Every `requests2.get()` response must be closed with `.close()`
  inside a `try`/`finally`, with no exceptions, per FR11 and Decision
  Logic Step 5.
- Reuse `safe_connect()` exactly as confirmed in Lecture 9 — do not
  call `wlan.connect()` directly anywhere in this program.
- Standard `setup()` / `loop()` structure, with the try/except
  error-reporting wrapper used throughout this course.
- **The main application must be self-contained** — define its own
  `xor_cipher()` rather than importing it from `encrypt_credentials.py`
  (algorithm must still be identical, per FR3), and open
  `.credentials.sys` via an absolute `/flash/` path. Confirmed on
  hardware: UIFlow2 only deploys the single file it runs, so a
  cross-file import or a relative-path file read that works locally
  fails on the device (see Feasibility Note point 4).
- **`PROMPTS.md` is required for this lab, at every agentic stage** —
  document the encryption-utility task (Part 2), the network-selector
  task (Part 3), and the quote-fetcher task (Part 4) as separate,
  logged interactions, per `9.2_agentic_AI_and_Claude_Code.md` §8.
  Document what you asked for, whether you asked for a plan first,
  and what you kept from each response.
- **Test with Run Once repeatedly before ever using Run Always** — a
  crashing program set to Run Always can only be recovered by
  reflashing the device through M5Burner.

---

### Testing Checklist (self-check before you submit)

Run through this on your **physical CoreS3**, not just by reading the
code:

- [ ] `.credentials.sys` exists, contains your real hotspot SSID and
      password on two lines, and is listed in `.gitignore` before any
      commit.
- [ ] After running the encryption utility once, opening
      `.credentials.sys` in a text editor shows unreadable bytes, not
      your SSID and password.
- [ ] The main application, using the hardcoded passphrase constant,
      correctly decrypts `.credentials.sys` back to the original two
      lines — verify this by temporarily printing the decrypted
      values during development, then removing that debug output
      before final submission.
- [ ] The dropdown is populated with real, currently-visible Wi-Fi
      networks from a live `wlan.scan()` — not a hardcoded list — with
      no blank rows (filtered hidden/empty SSIDs) and no repeated
      entries for the same network.
- [ ] `.credentials.sys` was uploaded to `/flash/` on the device
      itself (not just present in the local project folder) before
      running the main application.
- [ ] Selecting your hotspot's SSID from the dropdown successfully
      connects, using the password recovered from the decrypted file.
- [ ] Selecting a different network (not matching the decrypted SSID)
      does not attempt a connection and shows the mismatch error
      state instead.
- [ ] Temporarily set `DECRYPTION_PASSPHRASE` to the wrong value and
      confirm selecting a network shows the mismatch error state
      rather than crashing/freezing the app — then set it back to the
      correct value before final submission.
- [ ] The connection status label updates correctly and continuously
      while on the network selector screen.
- [ ] The instant the connection succeeds, the screen clears and the
      quote-fetcher screen appears — text area (200×200, black
      border), Get Quote button (white on red), Disconnect button
      (white on red, same size/style, beside Get Quote).
- [ ] Pressing Get Quote clears the text area, fetches from the exact
      required URL, and displays the returned text with visible word
      wrapping if the quote is long enough to need it.
- [ ] Pressing Get Quote multiple times in a row each time clears the
      previous quote and shows a freshly fetched one — text never
      accumulates or appends.
- [ ] Press Get Quote **at least ten times in a row** to confirm no
      crash or slowdown from unclosed HTTP responses — this is the
      specific failure mode FR11 exists to prevent.
- [ ] Pressing Disconnect disconnects from Wi-Fi, clears the screen
      entirely (no leftover text area or buttons visible), and shows
      "Lab 8 Completed..." centered on the screen.
- [ ] `PROMPTS.md` documents all three agentic Claude Code tasks
      (encryption utility, network selector, quote fetcher)
      separately.

---

### Submission Instructions

1. Ensure `prg455.263.lab8/` contains your final `.py` file(s),
   `PROMPTS.md`, and `.gitignore` (excluding `.credentials.sys`) — but
   **not** `.credentials.sys` itself.
2. Commit and push before the deadline: **Monday, November 16, 2026.**
3. Double-check your pushed repository does not contain
   `.credentials.sys` in any commit — if it was ever committed before
   `.gitignore` was added, removing it from the working directory is
   not sufficient; that history must be cleaned or the repository
   recreated, since the plain-text password remains recoverable from
   git history otherwise.

---

### Marking Rubric — Out of 100

Graded by running the submitted program on a physical CoreS3 and
working through the checklist above.

| # | Criterion | What's checked | Points |
|---|---|---|---|
| 1 | Credentials file handling | `.credentials.sys` present, correctly formatted, git-ignored, never committed in plain text | 5 |
| 2 | Encryption utility correctness | Prompts for a passphrase, encrypts the file in place, file is unreadable afterward, round-trips correctly with the same passphrase | 15 |
| 3 | Wi-Fi scan and dropdown | Dropdown populated from a live `wlan.scan()`, not a hardcoded list; correct string decoding of scan results | 10 |
| 4 | Decryption and SSID confirmation | Decryption constant hardcoded and never AI-generated; decrypted SSID compared against the dropdown selection before connecting; mismatch handled without attempting a bad connection | 15 |
| 5 | Guarded connection | `safe_connect()` reused exactly as confirmed in Lecture 9; no direct `wlan.connect()` calls elsewhere; poll-driven status label correct | 10 |
| 6 | Screen transition | Clean, one-time transition from network selector to quote fetcher on successful connection | 5 |
| 7 | Quote fetcher UI | Text area exactly 200×200 with a black border; Get Quote and Disconnect buttons correctly styled (white on red) and positioned beside each other | 10 |
| 8 | Quote fetching correctness | Correct URL, text area cleared before each new quote, word wrap functions correctly, repeated presses never accumulate text | 10 |
| 9 | Response lifecycle safety | Every `requests2.get()` response closed via `try`/`finally`; verified stable under at least ten repeated presses with no crash | 10 |
| 10 | Disconnect behavior | Wi-Fi disconnected, screen fully cleared, "Lab 8 Completed..." correctly centered | 5 |
| 11 | Agentic workflow documentation | `PROMPTS.md` documents all three Claude Code tasks separately, with enough detail to show a task-based (not just conversational) workflow was used | 5 |
| | **Subtotal** | | **100** |
| — | **Required header block** | Deduction, not a scored criterion: **-10 points (10%) from the total above** if the required header block (see Code Requirements) is missing, incomplete, or has any placeholder text left in it | -10 |
| | **Total** | | **100** |
