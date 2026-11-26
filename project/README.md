# PRG455 Final Project — Currency Conversion Kiosk

## Overview

For this project you will build a small, touch-only GUI application for the M5Stack CoreS3 that works like a storefront currency-exchange kiosk. It runs on MicroPython using the UIFlow2/m5ui framework and builds directly on the Wi-Fi connectivity pattern from Lab 8.

At a high level, your app must:

1. **Connect to Wi-Fi automatically** on startup, using Wi-Fi credentials that are stored on the device in **encrypted** form (same approach as Lab 8 — never save the plaintext password to the device or commit it to your repository).
2. **Fall back to a network-selection screen** (a list of buttons, with a RE-SCAN option) if the saved network can't be found.
3. Once connected, show a **main screen** with:
   - A default currency (starting point is up to you to decide, e.g. CAD) and an amount, with a flag icon.
   - A list of 6 other currencies, each showing a flag, a short label, and the live converted value.
   - The current date and time.
4. Let the user **tap the amount** to bring up a **number pad** and type in a new amount, which updates every currency's converted value.
5. Let the user **tap the currency list** to bring up a **grid of flags** and pick a new default currency, which rebuilds the main screen around that choice.

Exchange rates come from a live, free, keyless public API — not hardcoded or fake values.

## Why this project is structured this way

This spec is based on a real, working solution that was built and debugged on actual CoreS3 hardware. A number of design choices in the spec — landscape-only orientation, the exact list of 7 currencies, pre-resizing flag images instead of resizing them on the device, writing your own zip-extraction script — aren't arbitrary. They're there because the alternatives were tried first and confirmed, on real hardware, not to work reliably on this firmware. The **Feasibility Note** at the top of `PRG455_final_project.md` explains each of these up front so you don't have to rediscover them yourself through trial and error. Read it before you start designing your screens.

## What you need to submit

- Your MicroPython source files (each with the required header-block comment)
- A host-side script that pre-resizes your flag images (e.g. using Pillow)
- Your pre-resized flag images (and, if you package them as a zip for upload, your on-device extraction script)
- A `.gitignore` that keeps your plaintext Wi-Fi credentials file out of your repository
- A `PROMPTS.md` file documenting your AI-assisted workflow, if you used one
- This `README.md`, describing how to run your project and any known limitations

## Where to find the full requirements

See `PRG455_final_project.md` in this same folder for the complete specification: functional requirements for each screen, required code patterns, a testing checklist, submission instructions, and the full marking rubric (out of 100 points).
