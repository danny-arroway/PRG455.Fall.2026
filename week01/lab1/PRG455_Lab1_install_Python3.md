# PRG455 — Lab 1 Installing Python 3 on your personal Laptop/Desktop computer

**Week 1 · Student handout · Complete before your Week 2 lab**

This handout details installing Python 3 on your computer and verifies that everything this course needs
actually works. Do this **first**, before the Claude Pro / VS Code handout and before the Core S3
handout — both of them assume a working Python.

**Estimated time:** 30–45 minutes.

Jump to your operating system, then do **Part 4 (Verification) and Part 5 (Packages) regardless
of platform.** Those two parts are not optional and they are where the real problems surface.

### Where does the GUI happen?

Not here. The on-screen interface students build in this course runs **on the Core S3 itself**,
using **M5UI** inside **UIFlow2 MicroPython** — that's a device-side framework, not something you
`pip install` on your laptop. It's covered in the Core S3 handout, not this one.

The Python you install today is a plain, ordinary desktop Python. Its job is running your own
scripts and talking to the Core S3 over USB serial (Part 5). It does not need a GUI toolkit, so
skip any step elsewhere that mentions Tkinter, Tcl/Tk, or similar — that used to be relevant,
it no longer is.

---

## Part 0 — Read this before you install anything

### The course standard version

```
COURSE STANDARD: Python 3.14.x
Latest release at time of writing: 3.14.7 (5 August 2026)
MINIMUM ACCEPTABLE: Python 3.12
```

### ⚠️ Do not install Python 3.15

Python 3.15 is scheduled for release on **1 October 2026 — during this semester.** When it
appears, python.org will offer it prominently and it will look like the obvious choice.

**Do not install it mid-term.** Third-party packages take weeks to months to publish builds for
a brand-new Python version, and the failure mode is an incomprehensible compiler error during
`pip install` on a lab night. Stay on 3.14.x until the course ends in December.

Right now, if you see a version number containing `rc`, `a`, `b`, or the words "pre-release",
you are on the wrong download.

### ⚠️ Four things not to install

| Do not use | Why |
|---|---|
| **Microsoft Store Python** (Windows) | Sandboxed file access causes strange permission failures when talking to serial ports and USB devices. Later in this course, that matters. |
| **Anaconda / Miniconda** | A separate package ecosystem that conflicts with `pip`. Excellent for data science, wrong for this course. |
| **The Python already on your Mac** | Apple's bundled Python is old and is there for the operating system's use, not yours. |
| **Any Python 2.x** | Discontinued in 2020. Nothing in this course works on it. |

### If you already have Python installed

Do not immediately uninstall it. Go to **Part 4** first and check the version. If it reports
3.12 or newer, you are already done — skip to Part 5.

---

## Part 1 — Windows

### Step 1.1 — Turn off the App Execution Aliases first

Windows ships fake `python.exe` and `python3.exe` stubs whose only function is to open the
Microsoft Store. If you leave them on, typing `python` after a successful install may still open
the Store, and you will conclude the install failed when it did not.

1. Press **Start** and type `Manage app execution aliases`. Open it.
2. Find **App Installer — python.exe** and **App Installer — python3.exe**.
3. Turn **both OFF**.

Do this before installing, not after.

### Step 1.2 — Download

1. Go to **python.org/downloads/windows**.
2. Under **Stable Releases**, find **Python 3.14.7** (or the newest 3.14.x).
3. Download **Windows installer (64-bit)** — the file is named `python-3.14.7-amd64.exe`.
   - On a Surface or another ARM-based Windows machine, take the **ARM64** installer instead.
   - Ignore the 32-bit and "embeddable package" downloads.

> **You may notice python.org also offers the "Python install manager."** That is a newer tool
> for managing several Python versions side by side. It works, but this course standardises on
> the plain installer so that everyone's machine behaves identically during lab tests.
> **Install one or the other, not both.**

### Step 1.3 — Install

Run the downloaded `.exe`. On the first screen:

1. **☑ TICK "Add python.exe to PATH"** at the bottom. This is the single most important check
   box in this entire handout. Without it, `python` will not work in any terminal, in VS Code,
   or in Claude Code.
2. **☑ TICK "Use admin privileges when installing py.exe"** if offered.
3. Click **Install Now**.
4. If the final screen offers **"Disable path length limit,"** click it.

### Step 1.4 — Open a fresh terminal

Close every terminal, PowerShell window, and VS Code window that was open during installation.
They are still holding the old PATH. Open a new PowerShell window.

**Go to Part 4.**

---

## Part 2 — macOS

### Step 2.1 — Check what you have

Open **Terminal** (Applications → Utilities, or Spotlight and type "Terminal"):

```bash
python3 --version
```

If this reports 3.9.x, that is Apple's system Python. Leave it alone — do not delete it, do not
try to upgrade it. You are going to install a separate one alongside it.

### Step 2.2 — Download and install

1. Go to **python.org/downloads/macos**.
2. Download the **macOS 64-bit universal2 installer** for **Python 3.14.7** (or the newest
   3.14.x). One installer covers both Apple Silicon and Intel Macs.
3. Open the `.pkg` and follow the installer. Accept the defaults.
4. When it finishes, a Finder window opens showing the installed folder.

The python.org installer is self-contained and behaves identically across every student's
machine, which is why this course standardises on it rather than the Homebrew version.

### Step 2.3 — ⚠️ Run the certificate installer

In that Finder window, double-click **`Install Certificates.command`**.

A Terminal window opens, runs briefly, and closes. **Do not skip this.** Without it, `pip` fails
later with SSL certificate errors that look nothing like a certificate problem, and you will
lose half an hour to it.

If you closed the Finder window, the file is at:
`/Applications/Python 3.14/Install Certificates.command`

### Step 2.4 — Which command do you use?

On macOS, `python3` is your new install and `python` may not exist at all. Use **`python3`**
and **`pip3`** everywhere in this course, wherever the instructions say `python` and `pip`.

Open a **new** Terminal window and go to **Part 4**.

### If you prefer Homebrew

Homebrew works fine for this course:

```bash
brew install python@3.14
```

Then verify with Part 4 as normal.

---

## Part 3 — Linux

### Step 3.1 — Check what you have

```bash
python3 --version
```

Most current distributions ship 3.12 or newer, which meets the course minimum. **If you are at
3.12 or above, you do not need to install a different Python** — go to Step 3.2 and install the
supporting packages.

### Step 3.2 — Install the supporting packages

**Ubuntu / Debian / Linux Mint / Pop!\_OS:**

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Fedora / RHEL:**

```bash
sudo dnf install python3 python3-pip
```

**Arch / Manjaro:**

```bash
sudo pacman -S python python-pip
```

### Step 3.3 — Do not remove or replace the system Python

On Linux, the system depends on its own Python. Removing it, replacing it, or overwriting
`/usr/bin/python3` breaks package management and, on some distributions, the desktop
environment. If you need a different version, install it *alongside*:

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.14 python3.14-venv
```

Then use `python3.14` explicitly rather than changing what `python3` points to.

### Step 3.4 — `pip` may refuse to install packages

Recent distributions mark the system Python as "externally managed" and `pip install` fails with
a long message about it. This is deliberate, and it is protecting you. See Part 5 for the
virtual environment approach, which is the correct fix.

**Go to Part 4.**

---

## Part 4 — Verification (all platforms)

Do every step. Each one catches a different failure, and each failure costs a lab period later.

Throughout: **Windows users type `python`, macOS and Linux users type `python3`.** Whichever
works on your machine, that is the command you use for the rest of the course. Write it down.

### Check 1 — Python runs and is the right version

```
python --version
```

Expect `Python 3.14.7` or similar. **If Windows opens the Microsoft Store**, return to Step 1.1
and turn off the App Execution Aliases.

If `python` is not recognised on Windows, try `py --version`. If `py` works but `python` does
not, the PATH check box was missed during installation — re-run the installer, choose
**Modify**, and tick it.

### Check 2 — pip works

```
python -m pip --version
```

Then upgrade it:

```
python -m pip install --upgrade pip
```

> Use `python -m pip` rather than a bare `pip`. On a machine with more than one Python, a bare
> `pip` can install packages into a completely different interpreter from the one running your
> code — which produces the maddening result of a package that is definitely installed and
> definitely cannot be imported.

### Check 3 — The interactive interpreter

```
python
```

At the `>>>` prompt:

```python
>>> import sys
>>> sys.version
>>> sys.executable
```

`sys.executable` prints the exact path of the Python that is running. When something confusing
happens later in the term, this is the first thing to check. Exit with:

```python
>>> exit()
```

---

## Part 5 — Install the course packages

This course needs two packages beyond the standard library:

| Package | What it does |
|---|---|
| `pyserial` | Lets your desktop Python scripts talk to the Core S3 over USB (Week 7 onward) |
| `mpremote` | Command-line tool for the MicroPython device (Lab 0 Part B) |

### Windows and macOS

```
python -m pip install pyserial mpremote
```

### Linux

If `pip install` succeeds, you are done. If it refuses with an "externally managed environment"
message, use a virtual environment — this is the intended solution, not a workaround:

```bash
cd ~/Documents/Seneca/PRG455.263
python3 -m venv .venv
source .venv/bin/activate
pip install pyserial mpremote
```

Your prompt now shows `(.venv)`. **You must run `source .venv/bin/activate` every time you open
a new terminal for this course.** Add `.venv/` to your `.gitignore` — never commit it.

### Verify

```
python -c "import serial; print('pyserial', serial.__version__)"
mpremote --help
```

### ⚠️ Two things that will bite you

**The package is `pyserial` but the module is `serial`.** You install `pyserial` and then write
`import serial`. Installing a package called `serial` instead gives you a completely different,
unrelated library and a wall of confusing errors. If you have ever run `pip install serial`, run
`pip uninstall serial` now.

**Never name one of your own files `serial.py`.** Python searches your current folder before the
installed packages, so a file called `serial.py` in your lab folder replaces the real library for
every program in that folder. The same applies to `time.py`, `queue.py`, and any other module
name. This is a genuinely common and genuinely baffling bug.

---

## Part 6 — Point VS Code at the right Python

VS Code does not always pick the interpreter you expect, especially if you had an older Python
installed before today.

1. Open your `PRG455.263` folder in VS Code.
2. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS).
3. Type `Python: Select Interpreter` and choose it.
4. Select the **3.14.x** entry. On Linux with a virtual environment, choose the one showing
   `.venv`.
5. The selected version appears in the status bar at the bottom of the window. Check it matches.

If VS Code runs a different Python from your terminal, the symptom is a package that imports fine
in one place and not the other. When that happens, come back here.

---

## Part 7 — Record the evidence

Create `lab0/SETUP.md` in your `PRG455.263` repository and paste the **actual output** of each
command — not a tick, the text your machine produced:

```markdown
# Lab 0 — Python Setup Verification

**Name:**
**Operating system and version:**
**The Python command I use on this machine:** (python / python3 / py)

## Version
$ python --version
[paste]

## Interpreter path
>>> sys.executable
[paste]

## pip
$ python -m pip --version
[paste]

## Packages
$ python -c "import serial; print('pyserial', serial.__version__)"
[paste]

## Problems I hit and how I solved them
[Anything that did not work first time — the exact error text, not "it didn't work".
 This helps your instructor help the next person, and helps you when it recurs in Week 7.]
```

Commit and push:

```
setup: python install verification
```

---

## Troubleshooting

**`python` opens the Microsoft Store (Windows).**
App Execution Aliases are still on. Step 1.1.

**`python` is not recognised (Windows).**
PATH was not set during install. Re-run the installer → **Modify** → tick "Add Python to
environment variables". Then open a **new** terminal — existing windows keep the old PATH.

**`pip` SSL certificate errors (macOS).**
You skipped `Install Certificates.command`. Step 2.3.

**"externally managed environment" (Linux).**
Use a virtual environment. Part 5.

**A package installs successfully but will not import.**
You have more than one Python. Run `python -c "import sys; print(sys.executable)"` and
`python -m pip --version` and compare the paths. Use `python -m pip install` from now on.

**`import serial` fails with a strange error.**
Either you installed the wrong package (`serial` instead of `pyserial`), or you have a file
named `serial.py` in your folder. Both are in Part 5.

**VS Code says a module is missing but the terminal is fine.**
VS Code is using a different interpreter. Part 6.

**I installed Python 3.15 by accident.**
Uninstall it and install 3.14.x. On Windows, uninstall through Settings → Apps. On macOS,
install 3.14 alongside and select it explicitly in VS Code.

**I have four Pythons on this machine and no idea which is which.**
This happens. Bring the laptop to the lab — it is a five-minute fix in person and a long
conversation over email.

---

## Sign-off checklist

Bring your machine to the lab.

| # | Check | Initials |
|---|---|---|
| 1 | `python --version` reports 3.12 or newer (3.14.x preferred) | |
| 2 | Student can state which command their machine uses: `python`, `python3`, or `py` | |
| 3 | `python -m pip --version` works | |
| 4 | `import serial` succeeds and prints a version | |
| 5 | `mpremote --help` runs | |
| 6 | VS Code status bar shows the same interpreter as the terminal | |
| 7 | `lab0/SETUP.md` committed and pushed with real pasted output | |

This handout only covers your laptop's Python. The on-device GUI work with M5UI on the Core S3
is verified separately, in the Core S3 handout.
