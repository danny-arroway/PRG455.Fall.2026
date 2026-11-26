# PRG455

## Final Project: Connectivity-Driven Currency Conversion Kiosk

**Prerequisite:** Lab 8 (Connectivity-Driven Interface / Dropdown Control)
**Due date:** See course schedule / LMS

---

## Feasibility Note

Read this section before you start. It lists what has already been confirmed to work (and what has been confirmed to *not* work) on the CoreS3's current UIFlow2/MicroPython firmware. These are not style suggestions — they are hardware-tested facts. Designing around them from the start will save you a large amount of debugging time.

1. **Orientation is fixed: native landscape (320 × 240).** The CoreS3 panel is natively 320 wide × 240 high. Software-rotated portrait mode (240 × 320) has been confirmed to break under this firmware's widget set — specifically, calling `page.set_size(240, 320)` on an `M5Page` silently reverts the display to landscape, and using an `M5Dropdown` anywhere in the UI does the same (a known interaction between LVGL v9.3 dropdown/roller widgets and software-rotated displays). **Do not attempt portrait orientation for this project.** Design every screen for 320 × 240.
2. **`M5Page` is scrollable by default.** If you don't need scrolling, call `page.remove_flag(lv.obj.FLAG.SCROLLABLE)` on every page you create. Leaving this out has been confirmed to cause slow, jittery, pixel-by-pixel redraws that look like a rendering bug but are actually unwanted scroll/inertia handling.
3. **`M5Image.set_scale()` does not work reliably on this firmware.** It has been confirmed, at multiple scale factors and both before and after `screen_load()`, to make the image disappear entirely rather than resize it. `M5Image.set_size()` also does not rescale the underlying bitmap — it only changes the widget's layout box, not what's drawn inside it. **Do not scale flag images at runtime.** Pre-resize every image to its exact target display size (see Part 3) and load each pre-sized file directly.
4. **Widget constructors are inconsistent about keyword arguments.** `M5Label(...)` does **not** accept `w=`/`h=` kwargs (use `.set_size()` after construction). `M5Button(...)` does **not** accept a `bg_opa=` kwarg (use `.set_style_bg_opa(opa, part_and_state)` after construction). If a widget constructor raises `TypeError: unexpected keyword argument '...'`, assume the style/size has to be set post-construction, not passed in.
5. **`M5.Lcd.width()` / `M5.Lcd.height()` report the native panel size (320 × 240) regardless of rotation**, and a widget's `get_width()`/`get_height()` immediately after construction can report stale values. Don't use either as a live orientation or layout check inside your code.
6. **Wi-Fi scan results can be stale**, particularly with a phone hotspot that stops broadcasting its SSID while the phone is locked. Your network-selection screen must let the student re-scan without restarting the app.
7. **MicroPython has no `zipfile` module.** If you deliver image assets as a zip archive, you must also deliver (and justify) your own extraction code.

---

## Scenario

A currency-exchange kiosk needs a small, self-contained touchscreen display suitable for a storefront counter: it connects to Wi-Fi automatically using saved, encrypted credentials; shows a default "home" currency with a live converted amount; lists several other currencies at a glance; and lets a customer tap the screen to either type in a new amount or change which currency is shown as the default. No keyboard, no mouse — touch only.

## What You're Building

A four-screen MicroPython GUI application for the M5Stack CoreS3, built with UIFlow2/m5ui, that:

1. Reads an **encrypted** Wi-Fi credentials file (same XOR-cipher + hardcoded-passphrase pattern as Lab 8) and connects automatically on startup.
2. If connection fails or no SSID is visible, shows a **network-selection screen** (button list, not a dropdown — see Feasibility Note #1) with a **RE-SCAN** button.
3. Once connected, shows a **main kiosk screen**: a default currency/amount header and a list of other currencies with live converted values, each fetched from a public exchange-rate API.
4. Supports **tapping the amount** to open a **numeric keypad screen** for entering a new base amount, which then re-renders the main screen's conversions.
5. Supports **tapping the currency list/header** to open a **currency-picker screen** (a grid of flag icons) to change which currency is treated as the default, which then re-renders the main screen around the new default.

---

## Part 1 — Wi-Fi Connectivity (builds directly on Lab 8)

### Functional Requirements

- **FR1.1** — Wi-Fi credentials (SSID and password) must be stored on the device only in **encrypted** form, using the same XOR stream-cipher approach as Lab 8: a hardcoded passphrase repeated/truncated to the ciphertext length, XORed byte-for-byte. The passphrase must be written directly in your source code by you — **not** generated or chosen by an AI tool — and the plaintext credentials file must never be committed to your repository.
- **FR1.2** — On startup, the app decrypts the credentials and attempts to connect automatically, without requiring the student/user to type anything, using a guarded connect pattern (disconnect-then-connect, wrapped in `try/except OSError`) so a bad prior connection state doesn't hang the app.
- **FR1.3** — If automatic connection fails, or if the saved SSID is not currently visible, the app must show a **network-selection screen**: a scrollable list of **buttons**, one per visible SSID (from `wlan.scan()`, with empty and duplicate SSIDs filtered out) — **not** an `M5Dropdown` (see Feasibility Note #1).
- **FR1.4** — The network-selection screen must include a **RE-SCAN** button that re-runs `wlan.scan()` and rebuilds the button list, to handle devices (e.g., phone hotspots) whose SSID broadcast is inconsistent.

> **Hardware-confirmed:** `M5Dropdown` breaks software-rotated portrait displays, which is moot here since this project requires native landscape — but it's a good general reminder that this firmware's widget set has gaps relative to its documentation. Verify any widget you haven't used before with a small REPL test before building a whole screen around it.

### Decision Logic (required — implement exactly)

**Step 1 — Decrypt and connect on startup.**
```python
def xor_cipher(data: bytes, passphrase: str) -> bytes:
    key = passphrase.encode()
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

def safe_connect(wlan, ssid, password, timeout_s=10):
    try:
        if wlan.isconnected():
            wlan.disconnect()
    except OSError:
        pass
    wlan.connect(ssid, password)
    start = time.ticks_ms()
    while not wlan.isconnected():
        if time.ticks_diff(time.ticks_ms(), start) > timeout_s * 1000:
            return False
        time.sleep_ms(200)
    return True
```

**Step 2 — Fall back to the network-selection screen on failure.**
```python
if not safe_connect(wlan, saved_ssid, saved_password):
    build_network_screen()   # button list + RE-SCAN, per FR1.3/FR1.4
else:
    build_main_screen_page()
```

---

## Part 2 — Main Kiosk Screen and Live Conversion

### Functional Requirements

- **FR2.1** — The screen must be laid out for **320 × 240 native landscape** (see Feasibility Note #1). No `Widgets.setRotation()` call and no software-rotation workaround.
- **FR2.2** — A full-width row at the top of the screen shows the current date and time (synced via NTP on connect).
- **FR2.3** — Below the date/time row, a two-column layout: a left column showing the **default currency** (flag icon, label, and current base amount) and a right column listing the **other supported currencies**, each row showing a flag icon, a shortened currency label, and a right-justified converted value, with a separator line between rows.
- **FR2.4** — Exactly **7 currencies** are supported in total (1 default + 6 others, selectable — see Part 4): **CAD, USD, EUR, GBP, CHF, AUD, CNY**. Do not include JPY, NZD, or RUB — they are explicitly out of scope for this project, regardless of what any general-purpose currency-API example online includes.
- **FR2.5** — Currency labels must be **shortened** to fit the 320-pixel-wide layout (e.g., `Euro (EUR)`, not `European Union Euro (EUR)`). Verify your longest label actually fits at your chosen font size before finalizing the layout — don't assume.
- **FR2.6** — Converted values are fetched from a **live, public, keyless exchange-rate API** (e.g., `https://open.er-api.com/v6/latest/<BASE>`), which returns a `rates` dictionary keyed by ISO currency code.
- **FR2.7** — Every HTTP request must use `requests2` (not `urequests`) and must close its response in a `try/finally` block. Failing to close responses has been confirmed to exhaust ESP32 memory after a handful of requests.
- **FR2.8** — Tapping anywhere in the amount/header area opens the keypad screen (Part 3). Tapping anywhere in the currency list opens the currency-picker screen (Part 4).

> **Hardware-confirmed:** Call `page.remove_flag(lv.obj.FLAG.SCROLLABLE)` on this page. Without it, the screen redraws extremely slowly and appears jittery, as if being redrawn pixel-by-pixel — this is default scroll/inertia handling on an `M5Page`, not a bug in your layout code.

> **Hardware-confirmed:** `ntptime.client()` does not exist on this firmware's `ntptime` module — use `ntptime.settime()`, which sets the RTC to UTC, and apply your local UTC offset manually via a `time.mktime()` / `time.localtime()` round-trip (this module has no built-in timezone support).

### Decision Logic (required — implement exactly)

**Step 1 — Fetch and parse rates, always closing the response.**
```python
def fetch_rates(base_code):
    url = "https://open.er-api.com/v6/latest/" + base_code
    response = None
    try:
        response = requests2.get(url)
        data = response.json()
        return data.get("rates", {})
    finally:
        if response:
            response.close()
```

**Step 2 — Render the right-column list from the fetched rates.**
```python
def refresh_currency_list(base_code, base_amount, rates):
    for code in OTHER_CODES:  # the 6 non-default currencies, FR2.4
        rate = rates.get(code)
        if rate is None:
            continue
        converted = base_amount * rate
        render_currency_row(code, converted)  # flag + label + right-justified value
```

---

## Part 3 — Amount Entry (Numeric Keypad)

### Functional Requirements

- **FR3.1** — Tapping the amount/header area on the main screen opens a dedicated keypad screen sized to fit entirely within 320 × 240 with no scrolling and no truncation.
- **FR3.2** — The keypad starts **empty** (not pre-filled with the previous amount) and accepts digits and a decimal point.
- **FR3.3** — An **OK** (or equivalent confirm) button commits the entered amount and returns to the main screen, which must re-fetch/re-render conversions using the new base amount.
- **FR3.4** — A **Cancel** (or equivalent) control returns to the main screen without changing the amount.
- **FR3.5** — You may choose your own key sizes, spacing, and exact numeric-entry UX — there is no required pixel specification for this screen — but every control must be fully visible and tappable on the real device, in landscape, with no overlap.

> **Hardware-confirmed:** if a button's constructor raises `TypeError: unexpected keyword argument 'bg_opa'`, set that style after construction with `.set_style_bg_opa(opa, part_and_state)` instead of passing it as a kwarg.

### Decision Logic (required — implement exactly)

**Step 1 — Accumulate keypresses into a string, not a float, until confirmed.**
```python
entered_amount_str = ""

def keypad_key_pressed(key):
    global entered_amount_str
    if key == "OK":
        commit_amount(float(entered_amount_str) if entered_amount_str else 0.0)
        return
    if key == "CANCEL":
        build_main_screen_page()
        return
    if key == "." and "." in entered_amount_str:
        return  # only one decimal point allowed
    entered_amount_str += key
    update_amount_display(entered_amount_str)
```

---

## Part 4 — Currency Picker (Change the Default)

### Functional Requirements

- **FR4.1** — Tapping the currency list on the main screen opens a currency-picker screen showing all 7 supported currencies (FR2.4) as a grid of flag icons, each tappable.
- **FR4.2** — Selecting a flag sets that currency as the new default and returns to the main screen, which must rebuild its header (flag, label, amount) and its list of the other 6 currencies around the new default.
- **FR4.3** — The previously-entered base amount (Part 3) is preserved across a default-currency change — only the currency being converted *from* changes, not the amount itself.
- **FR4.4** — All flag images on this screen and the main screen must be **pre-resized on your own computer** before upload — see Part 5. Do not call `set_scale()` at runtime (Feasibility Note #3).

> **Hardware-confirmed:** the apparent "native" size of these flag images is **56 × 56 px**, not whatever size the source files claim — check your actual source assets directly (e.g., open them in an image tool, or inspect pixel dimensions in Python) rather than assuming. Some publicly available flag icon sets also mislabel JPEG data with a `.png` extension; if a "PNG" won't load cleanly, check its real format.

### Decision Logic (required — implement exactly)

**Step 1 — Rebuild the main screen around a newly selected default.**
```python
def currency_picker_selected(code):
    global default_currency_code
    default_currency_code = code
    build_main_screen_page()  # re-fetches/re-renders using the preserved amount
```

---

## Part 5 — Image Asset Pipeline (Host-Side Pre-Resizing)

### Functional Requirements

- **FR5.1** — You must pre-resize every flag icon to each exact pixel size it is displayed at (e.g., a small icon size for the currency list, a larger size for the main header, and a picker-grid size), using an image library on your own computer (e.g., Pillow), **before** uploading to the device. Do not rely on any runtime resizing.
- **FR5.2** — Your resize script must produce clearly named output files (e.g., a `<name>_<size>.png` convention) so your on-device code can select the correctly-sized file for each context without guesswork.
- **FR5.3** — If your source flag images contain any solid-color margin or border baked into the pixel data itself, you must detect and crop it out before resizing — a "border" showing up around a displayed image is not necessarily a code or widget bug; inspect the source pixels directly to find out.
- **FR5.4** — Because the UIFlow2 web file uploader only accepts one file at a time, and your asset set includes multiple images at multiple sizes, you must package your resized assets as a single zip archive and **write your own MicroPython extraction script** to unzip it on-device after a single upload (see Decision Logic below). MicroPython does not include a `zipfile` module — using `struct` and manual file I/O to parse the zip's local file headers is an acceptable and confirmed-working approach, provided your archive uses STORE (uncompressed) compression for its entries.

> **Hardware-confirmed:** a hand-written extractor using only `struct` and file I/O has been confirmed working on-device for a STORE-compressed zip. If you choose DEFLATE compression instead, you are responsible for sourcing or writing your own inflate implementation — budget real time for this if you go that route, or simply zip with STORE/no-compression to avoid the problem entirely.

### Decision Logic (required — implement exactly)

**Step 1 — Resize and crop on your own computer (not on the device).**
```python
from PIL import Image

def resize_flag(source_path, output_path, target_px):
    img = Image.open(source_path).convert("RGBA")
    img = crop_solid_margin(img)              # FR5.3
    img = img.resize((target_px, target_px), Image.LANCZOS)
    img.save(output_path)
```

**Step 2 — Extract the uploaded zip on-device.**
```python
def extract_zip(zip_path, output_dir):
    with open(zip_path, "rb") as f:
        data = f.read()
    pos = 0
    while True:
        pos = _read_local_header(data, pos, output_dir)  # writes each entry
        if pos is None:
            break
```

---

## Code Requirements

- Every submitted `.py` file must begin with a header-block comment containing, at minimum: your full name, student ID, course/section, assignment name, and date.
- Your Wi-Fi passphrase must be a literal string you wrote yourself, hardcoded in your source — never AI-generated, never derived from a prompt, and never the same passphrase used in Lab 8.
- The plaintext credentials file must **never** appear in your submitted repository. Include a `.gitignore` entry for it and verify it is not tracked before submitting.
- If you used an AI tool (including Claude) to help build this project, you must include a `PROMPTS.md` file documenting, at minimum, the major prompts/stages of your agentic workflow — e.g., initial build, specific bug reports with the actual device output/error you received, and any design decisions you made in response (such as switching orientation, dropping a currency, or changing an asset pipeline). Copy-pasted error tracebacks and your own one-line description of what you changed in response are sufficient; a full transcript is not required.
- All image assets must be pre-resized per Part 5 — no runtime `set_scale()` calls anywhere in your submission.
- Code must run without unhandled exceptions on the actual CoreS3 hardware, in native landscape orientation.

---

## Testing Checklist

- [ ] Device connects automatically on power-up using the encrypted, saved Wi-Fi credentials
- [ ] If the saved network isn't visible, the network-selection screen appears with a working button list
- [ ] The RE-SCAN button successfully finds a network that didn't appear on the first scan (test with a phone hotspot, locking/unlocking the phone between scans)
- [ ] Main screen renders fully in landscape (320 × 240), with no overlapping text and no scrolling required
- [ ] Date and time display correctly and are not obscured by any other element
- [ ] Default currency header and all 6 other currency rows display their correct flag, label, and a plausible converted value
- [ ] No row's label is truncated or overlaps the value column
- [ ] Tapping the amount/header opens the keypad screen; keypad starts empty
- [ ] Entering a new amount and pressing OK returns to the main screen with all conversions updated to the new amount
- [ ] Cancelling the keypad returns to the main screen with the amount unchanged
- [ ] Tapping the currency list opens the currency-picker grid showing all 7 flags
- [ ] Selecting a new default currency rebuilds the main screen around it, preserving the previously entered amount
- [ ] No flag image shows a visible border, margin, or incorrect crop
- [ ] App remains responsive after at least 10 consecutive currency-amount changes (checking for memory exhaustion from unclosed HTTP responses)
- [ ] Every submitted `.py` file has a correctly formatted header-block comment
- [ ] Plaintext credentials file is absent from the submitted repository

---

## Submission Instructions

1. Submit a single repository (or zip) containing all required `.py` files, your `resize_flags.py` host-side script, your pre-resized flag assets (or the zip you upload to the device plus your on-device unzip script), and your `.gitignore`.
2. Include your `PROMPTS.md` if you used an AI tool, per Code Requirements.
3. Include a short `README.md` describing how to run your project and any known limitations.
4. Confirm your plaintext credentials file is **not** present anywhere in the submission before you submit.
5. Submit via the course LMS by the due date listed at the top of this document.

---

## Marking Rubric — Out of 100

| Criterion | What's checked | Points |
|---|---|---|
| Wi-Fi auto-connect (encrypted credentials) | Decrypts and connects automatically on startup using the Lab 8 XOR-cipher pattern with a student-authored passphrase | 10 |
| Network-selection fallback screen | Button-list (not dropdown) screen appears on failed/missing connection, correctly lists visible SSIDs | 8 |
| RE-SCAN functionality | Re-scan button successfully refreshes the SSID list on demand | 5 |
| Main screen layout (landscape, no overlap) | Full 320×240 layout renders with no overlapping or truncated elements, no unwanted scrolling | 12 |
| Date/time display | NTP-synced date and time display correctly and remain unobscured | 5 |
| Currency list correctness | Exactly the 7 required currencies, correct shortened labels, correct flags, right-justified values, separator lines | 10 |
| Live rate conversion | Values are fetched from a live public API and reflect real, current exchange rates | 10 |
| HTTP response handling | Every request uses `requests2` and closes its response in `try/finally`; app survives repeated requests without crashing | 8 |
| Amount-entry keypad | Opens on tap, starts empty, OK/Cancel both work correctly, main screen updates on confirm | 10 |
| Currency picker | Flag grid opens on tap, selecting a flag correctly changes the default and preserves the entered amount | 10 |
| Image asset pipeline | Flags are pre-resized host-side to exact display sizes with no visible border/margin; zip + on-device unzip script both work | 8 |
| Code quality & documentation | Clean, readable code; accurate `PROMPTS.md` (if used); clear `README.md` | 4 |
| **Header-block deduction** | **−5 points per `.py` file submitted without the required header-block comment** | up to −20 |
| **Total** | | **100** |
