# Setup Guide: macOS

Workshop "AI Agents for Social Science Research", Department of Sociology
(SUZ), University of Zurich. Tuesday, 8 September 2026, 9:00-17:00.

Complete this guide before the workshop. Plan for 30 to 45 minutes,
including account creation and download times. You do not need any prior
experience with programming or the command line; every step below tells
you exactly what to type or click and what you should see afterwards.

If any step fails and the troubleshooting section at the end does not
resolve it, stop there and bring your laptop to the help desk on workshop
day: the room opens at 8:30, and we will fix the remaining steps together
before we start at 9:00.

Requirements: macOS 13 (Ventura) or newer, an internet connection, and
about 2 GB of free disk space. Both Apple Silicon (M1 and later) and
Intel Macs work.

## What you will install

- A Claude account on the Pro plan (USD 20 per month)
- The Claude Desktop app (graphical interface)
- Claude Code (the same agent, run from the command line)
- Git (version control; needed to download the workshop repository)
- uv (the Python manager used by the workshop projects; it installs
  Python itself if your machine has none)

You will use either the Desktop app or the command-line version during
the workshop, but install both: they share one login and one
configuration, and having both lets you switch if one gives you trouble.

## 1. Create a Claude account and choose a plan

Claude Code and the Desktop app's Code tab require a paid plan; the free
plan does not include them. The Pro plan at USD 20 per month is
sufficient for the entire workshop.

You can skip this section if you already have a Pro (or Max) subscription.

1. Go to <https://claude.ai> in your browser.
2. Click to sign up and create an account with your email address or a
   Google account.
3. Go to <https://claude.com/pricing> and subscribe to the **Pro** plan.
   If you are unwilling or unable to acquire a pro account subscription
   contact Nico or Paul, we have some free passes that we can send you
   which should give you enough usage for the workshop.
4. Confirm the subscription is active: your account settings should show
   the Pro plan (or the free usage pass).

## 2. Install the Claude Desktop app

1. Go to <https://claude.com/download>.
2. Click **Download for macOS** (the installer works for both Apple
   Silicon and Intel Macs).
3. Open the downloaded `.dmg` file and, when the window appears, drag
   the Claude icon into your Applications folder.
4. Launch Claude from the Applications folder.
5. Sign in with the account you created in section 1.

You should now see the Claude app with tabs at the top center, including
**Chat** and **Code**. We'll test the Code tab in section 7.

## 3. Install Claude Code (CLI)

Claude Code is installed from the command line. On a Mac you use
**Terminal**, a program that lets you control the computer by typing
commands instead of clicking.

1. Press Cmd+Space, type `terminal`, and press Enter. A window opens
   showing a line that ends with `%` or `$`. This is the prompt; you
   type commands after it.

2. Copy the following command, paste it into the Terminal window
   (Cmd+V), and press Enter:

   ```bash
   curl -fsSL https://claude.ai/install.sh | bash
   ```

3. Wait for the installer to finish.

4. Quit Terminal (Cmd+Q) and open it again (this refreshes the list of
   installed programs), then type:

   ```bash
   claude --version
   ```

   Expected output: a version number such as `2.1.211 (Claude Code)`.
   The exact number will differ; any version number means the install
   worked.

## 4. Log in to Claude Code

1. In Terminal, type `claude` and press Enter.
2. Your browser opens and asks you to sign in. Use the same account as
   in section 1.
3. Return to the Terminal window. Claude Code now shows an interactive
   session: a text box where you can type instructions.
4. Type `/exit` and press Enter to leave the session for now. The full
   test run follows in section 7.

The Desktop app and Claude Code share this login, so you're done once
you've signed in to each.

## 5. Install Git

Git downloads ("clones") the workshop repository to your machine; many
Macs already have it installed.

1. In Terminal, check whether Git is present:

   ```bash
   git --version
   ```

   If Git is already installed, you'll see a line like
   `git version 2.39.5 (Apple Git-154)`; in that case, skip to
   section 6.

2. If a dialog appears offering to install the command line developer
   tools, click **Install** and wait for it to finish (the download can
   take several minutes). If no dialog appears, run:

   ```bash
   xcode-select --install
   ```

   and confirm the dialog.

3. Run `git --version` again to confirm it now shows a version number.

If you use Homebrew, `brew install git` also works, though the Apple
version above is entirely sufficient for the workshop.

## 6. Install uv

uv manages Python and the packages the workshop projects need. It
installs a suitable Python version by itself, so you do not need to
install Python separately.

1. In Terminal, run:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Quit Terminal, open it again, and verify:

   ```bash
   uv --version
   ```

   Expected output: `uv` followed by a version number, for example
   `uv 0.12.3`. Any version number means the install worked.

## 7. Test both surfaces

### Test 1: Claude Code in the terminal

1. In a new Terminal window, create a test folder and move into it:

   ```bash
   mkdir claude-test
   cd claude-test
   ```

2. Type `claude` and press Enter to start a session in that folder.
3. Type a trivial instruction, for example:

   ```text
   Say hello and tell me which folder you are working in.
   ```

4. Expected result: Claude replies in the terminal within a few seconds
   and names the `claude-test` folder.
5. Type `/exit` to end the session.

### Test 2: the Desktop app's Code tab

1. Open the Claude Desktop app.
2. Click the **Code** tab at the top center. If it asks you to upgrade,
   your Pro subscription is not active yet; revisit section 1. If it
   asks you to sign in online, complete the sign-in and restart the app.
3. Select **Local**, click **Select folder**, and choose the
   `claude-test` folder from Test 1 (it is inside your home folder).
4. Type the same trivial instruction as above and send it.
5. Expected result: Claude replies in the app. Look at the mode
   selector next to the send button: current versions start in Auto
   mode on paid plans. For the workshop we use Manual mode, which
   proposes every file change as a diff and waits for your approval;
   you can switch there now or on the day, the handout reminds you.

If both tests pass, you are fully set up. Bring your laptop and charger
on 8 September.

## 8. Troubleshooting

**`command not found: claude` (or `git`, or `uv`) after installing.**
Quit Terminal entirely (Cmd+Q, not just closing the window), open it
again, and run the command again. Newly installed programs only appear
in new terminal sessions.

**The developer tools download stalls or fails.** The command line tools
install in section 5 depends on Apple's update servers and can fail on
slow or restricted networks. Try a different network or eduroam on
campus; if that doesn't help, finish the remaining sections without Git
and bring the Git step to the help desk.

**The Code tab asks you to upgrade or to sign in.** An upgrade prompt
means the account you signed in with has no active paid plan (check
section 1, and confirm app and browser use the same account). A sign-in
prompt is resolved by completing the sign-in in the browser and
restarting the app.

**Anything else.** Come to the workshop room at 8:30 on 8 September with
your laptop and charger. We will finish the setup with you before the
start at 9:00. Nothing in the morning session requires more than what
this guide covers, so a fixable install problem costs you nothing.
