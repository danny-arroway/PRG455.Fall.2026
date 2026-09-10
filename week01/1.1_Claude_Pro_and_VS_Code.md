# PRG455 — Subscribing to Claude Pro and Integrating It with VS Code

**Week 1 · Student handout · Complete before your Week 2 lab**

This course requires an active **Claude Pro** subscription. This handout takes you from having
no account to having Claude working inside Visual Studio Code and in your terminal.

Read Part 1 before you pay for anything. There is a billing trap in the checkout flow and it
costs $200 if you fall into it.

**Estimated time:** 30–45 minutes.

---

## Part 1 — Before you pay: read this

### Why Pro and not the free plan

Claude Code — the tool you will use from VS Code and from the terminal — is **not included in
the free plan**. The free tier gives you the chat interface only. Pro is the minimum plan that
works for this course.

### Cost

Pro is **CAN $28 + tax per month** on monthly billing. Check the currency and amount shown at
checkout before confirming; if you are billed in USD, your card issuer may add a foreign
transaction fee of roughly 2.5%. Budget accordingly.

### ⚠️ Buy the MONTHLY plan, not the annual plan

**The annual plan is charged as a single up-front payment for the whole year.** If you click
through the checkout without reading it, you can be charged over $200 at once instead of $20.

This course runs for one semester. You want **monthly**. Slow down at the plan selection screen
and confirm that it says *monthly* before you enter a card.

If you do accidentally purchase the annual plan, do not ignore it. Open Claude, click your
initials, and look for the help or support option to request a refund. The sooner you ask, the
better the outcome.

### ⚠️ Subscribe on the web, not through a phone app

Buy your subscription at **claude.ai in a desktop browser**.

If you subscribe through the iPhone or Android app, Apple or Google handles the billing, and
you must then cancel through the App Store or Play Store rather than through Claude. Students
every term discover in January that they are still being charged because they cancelled in the
wrong place. Web purchase, web cancellation, one place to manage it.

### Payment method

Web subscriptions accept **credit or debit cards** only. No PayPal. A prepaid card may work but
will fail on renewal if it has no balance, which will lock you out mid-term.

### Age

Anthropic's Consumer Terms set a minimum age for holding an account. Read them before
subscribing. If you are not old enough, speak to your instructor before paying — do not create
an account with a false date of birth.

### Cost is a barrier?

Speak to your instructor privately in the first two weeks. Do not simply fall behind and
explain in Week 8.

---

## Part 2 — Create your Claude account (10 min)

1. In a **desktop browser**, go to **claude.ai**.
2. Click **Sign up**.
3. Sign up with an email address, or with Google. Either is fine — but **write down which one
   you used**. Signing in with Google in one place and email in another creates two separate
   accounts, and only one of them will have your subscription on it. This is the single most
   common support problem in Week 2.
4. Verify your email if prompted.
5. Complete the onboarding questions.
6. Send one message — anything — to confirm the account works.

### Verification 1

You can send a message and receive a reply at claude.ai. Note the exact sign-in method you
used.

---

## Part 3 — Subscribe to Pro, monthly (10 min)

1. In the **lower-left corner** of claude.ai, click your **name or initials**.
2. Select **Settings**.
3. Go to the **Billing** section.
4. Choose the **Pro** plan.
5. **On the plan screen, select MONTHLY billing.** Read the screen. Confirm it shows a monthly
   charge of about CAN $28 + tax and not a yearly total. If you see a figure in the hundreds, you are
   looking at the annual plan — switch it.
6. Enter your card details and billing address. The billing address must match the address your
   card is registered to, or the payment will be declined.
7. Review the summary one final time: **plan = Pro, billing = monthly, amount ≈ CAN $28**.
8. Confirm.

### Verification 2

Return to **Settings → Billing**. It should show:

- Plan: **Pro**
- Billing period: **Monthly**
- A **next billing date** roughly one month from today

**Write that renewal date down.** You will need it in December.

---

## Part 4 — Cancelling at the end of the course (read now, act later)

You are not obliged to keep this subscription after the course ends. Cancelling is
straightforward, but there is a timing rule:

1. claude.ai → your initials (lower left) → **Settings** → **Billing**
2. Click **Cancel**
3. Complete the confirmation dialog. **Closing the dialog does not cancel anything** — you must
   finish it.

**Cancel at least 24 hours before your next billing date**, or you will be charged for another
month. Your Pro access continues to the end of the period you have already paid for, and your
conversation history is not deleted.

Put a calendar reminder in now, dated a few days before your December renewal date. Do it while
you are thinking about it.

---

## Part 5 — Install Visual Studio Code (5 min)

Skip this part if VS Code is already installed and up to date.

1. Go to **code.visualstudio.com** and download the version for your operating system.
   - **macOS:** drag **Visual Studio Code** into your **Applications** folder before launching
     it.
2. Launch VS Code.
3. Check the version: **Help → About** (Windows) or **Code → About Visual Studio Code**
   (macOS). You need **1.98.0 or newer** for the Claude Code extension. If you are older than
   that, update before continuing.
4. Install the **Python** extension published by **Microsoft** (`Ctrl+Shift+X` /
   `Cmd+Shift+X`, search "Python").

---

## Part 6 — Install the Claude Code extension in VS Code (10 min)

### Step 6.1 — Open your project folder first

Claude Code works on a **folder**, not on loose files. Open your course repository:

**File → Open Folder…** → select `PRG455.263`

Do this before installing, so the extension has something to look at.

### Step 6.2 — Install the extension

1. Press `Ctrl+Shift+X` (Windows/Linux) or `Cmd+Shift+X` (macOS) to open the Extensions view.
2. Search for **Claude Code**.
3. **Check the publisher: it must say `Anthropic`.** There are imitation extensions with
   similar names and icons. Install the wrong one and you will be typing your credentials into
   someone else's software.
4. Click **Install**.

### Step 6.3 — Sign in

1. Click the Claude Code icon in the VS Code sidebar to open the panel.
2. When prompted, sign in. Your browser opens.
3. **Sign in with exactly the same account and the same method you used in Part 2** — the one
   with the Pro subscription on it. If you signed up with Google, use Google here.
4. Return to VS Code when the browser tells you to.

### Verification 3

In the Claude Code panel, type:

```
What files and folders are in this repository?
```

A correct response lists your `lab0` through `project2` folders. If it does, the extension is
installed, authenticated, and pointed at the right folder.

### Step 6.4 — Try one real edit

1. Open `lab0/README.md` in the editor.
2. In the Claude Code panel, ask it to add a line describing what Lab 0 covers.
3. **Look at the diff it proposes before accepting it.** Green is added, red is removed.
4. Accept the change.
5. Switch to GitHub Desktop. The change appears under **Changes**. Commit it as
   `claude: add lab0 description` and push.

You have now completed the full loop this course runs on: prompt → review → accept → commit →
push.

---

## Part 7 — Install Claude Code in the terminal (10 min)

You will use Claude from the command line later in the course, so install it now while you are
set up for it.

> **Ignore any guide that tells you to install Node.js and run `npm install -g`.** That method
> is deprecated. Use the commands below.

### Step 7.1 — Install

**macOS, Linux, or WSL** — open Terminal:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows PowerShell:**

```powershell
irm https://claude.ai/install.ps1 | iex
```

**Windows CMD:**

```
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

> **Which shell am I in?** Your prompt shows `PS C:\...` in PowerShell and `C:\...` without the
> `PS` in CMD. If you get *"The token '&&' is not a valid statement separator"*, you ran the CMD
> command in PowerShell. If you get *"'irm' is not recognized"*, you ran the PowerShell command
> in CMD.

On Windows, installing **Git for Windows** (git-scm.com) first is recommended.

### Step 7.2 — Verify

**Close your terminal and open a new one** — an existing window will not pick up the new PATH.
Then:

```
claude --version
```

You should see a version number such as `2.1.211 (Claude Code)`.

```
claude doctor
```

This prints a diagnostic report on your installation and configuration. Read it. Keep it — it
is the first thing to check whenever something stops working.

### Step 7.3 — Sign in and check your allowance

Navigate to your repository and start a session:

```
cd Documents/Seneca/PRG455.263
claude
```

Sign in through the browser with the same Pro account. Then, inside the session:

```
/status
```

This shows your plan and remaining usage. Exit with `/exit`.

---

## Part 8 — Two things that will cost you money or time

### Do not set `ANTHROPIC_API_KEY`

If an environment variable called `ANTHROPIC_API_KEY` exists on your machine, Claude Code uses
it **instead of your Pro subscription** — and API usage is billed separately, per token, to
whatever account that key belongs to. You are paying $20 for the subscription; do not
accidentally bypass it. If a tutorial tells you to create an API key, you do not need one for
this course.

### Understand your usage allowance

Your Pro allowance runs on a **rolling five-hour window plus a weekly cap**, and it is
**shared** across claude.ai in the browser, Claude Desktop, and Claude Code in VS Code and the
terminal. They all draw from one pool. Coding sessions consume it much faster than chat,
because file contents get read repeatedly.

Three habits, starting now:

1. Keep the context small — do not attach files the task does not need.
2. Use `/clear` when you switch to an unrelated task.
3. Check `/status` before starting a lab.

**Every lab in this course is designed so that once your code exists, you can finish the lab
without generating anything further.** Exhausting your allowance mid-lab is a planning problem,
not grounds for an extension.

---

## Troubleshooting

**The Claude Code panel says I have no access / prompts me to upgrade.**
You are signed into a different account from the one carrying the subscription. This is almost
always the Google-versus-email problem from Part 2. Check which account is active in claude.ai
under Settings → Billing, sign out of the extension, and sign in with that one.

**My card was declined.**
The billing address must match your card's registered address. Check with your bank that
international online transactions are permitted — many student debit cards block them by
default.

**I was charged more than $28.**
You selected the annual plan. Open Claude, click your initials, and look for the help or
support option to request a refund. Do this immediately.

**`claude` is not recognised after installing.**
Close every terminal window and open a fresh one. If it persists, run `claude doctor`. On macOS
and Linux, confirm `~/.local/bin` is on your PATH.

**The browser sign-in opens but never completes.**
Make sure you are logged into the same Claude account in that browser. Campus networks sometimes
block the callback — try from home.

**The extension does not appear after installing.**
Reload the window: `Ctrl+Shift+P` / `Cmd+Shift+P` → **Developer: Reload Window**.

**I subscribed on my phone by mistake.**
You are billed by Apple or Google. You can still use the subscription normally, but you must
cancel through the App Store or Play Store, not through claude.ai. Note this somewhere you will
see it in December.

---

## Sign-off checklist

Bring your machine to the lab. Your instructor will check:

| # | Check | Initials |
|---|---|---|
| 1 | claude.ai → Settings → Billing shows **Pro**, **Monthly**, with a renewal date | |
| 2 | Student knows which sign-in method their account uses | |
| 3 | Renewal date recorded and a December cancellation reminder set | |
| 4 | VS Code 1.98.0 or newer, with the Microsoft Python extension | |
| 5 | Claude Code extension installed, publisher confirmed as Anthropic | |
| 6 | Extension signed in and correctly lists the repository contents | |
| 7 | `claude --version` returns a version in the terminal | |
| 8 | `/status` shows an active Pro subscription | |
| 9 | One Claude-generated edit committed and pushed to `PRG455.263` | |

Check 9 is the one that matters. It proves the whole toolchain works end to end.
