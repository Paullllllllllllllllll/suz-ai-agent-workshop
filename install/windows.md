# Setup Guide: Windows

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

Requirements: Windows 10 (version 1809 or newer) or Windows 11, an
internet connection, and about 2 GB of free disk space.

## What you will install

- A Claude account on the Pro plan (USD 20 per month)
- The Claude Desktop app (graphical interface)
- Claude Code (the same agent, run from the command line)
- Git (version control; needed to download the workshop repository and
  required by the Desktop app for local sessions on Windows)
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
   the Pro plan.

## 2. Install the Claude Desktop app

1. Go to <https://claude.com/download>.
2. Click **Download for Windows**. (If your laptop has an ARM processor,
   pick **Windows (arm64)** instead; most Windows laptops are x64.)
3. Run the downloaded installer and follow its prompts.
4. Launch Claude from the Start menu.
5. Sign in with the account you created in section 1.

You should now see the Claude app with tabs at the top center, including
**Chat** and **Code**. We'll test the Code tab in section 7, after Git
is installed.

## 3. Install Claude Code (CLI)

Claude Code is installed from the command line. On Windows you use
**PowerShell**, a program that lets you control the computer by typing
commands instead of clicking.

1. Open the Start menu, type `powershell`, and press Enter. A window
   opens showing a line that ends with `>` and starts with `PS`, for
   example `PS C:\Users\yourname>`. This is the prompt; you type
   commands after it.

   Check that the line starts with `PS`. If it does not, you have opened
   the Command Prompt instead of PowerShell; close it and search for
   `powershell` again.

2. Copy the following command, paste it into the PowerShell window
   (right-click pastes), and press Enter:

   ```powershell
   irm https://claude.ai/install.ps1 | iex
   ```

3. Wait for the installer to finish.

4. Close PowerShell and open a new window (this picks up the newly
   installed program), then type:

   ```powershell
   claude --version
   ```

   Expected output: a version number such as `2.1.211 (Claude Code)`.
   The exact number will differ; any version number means the install
   worked.

## 4. Log in to Claude Code

1. In PowerShell, type `claude` and press Enter.
2. Your browser opens and asks you to sign in. Use the same account as
   in section 1.
3. Return to the PowerShell window. Claude Code now shows an interactive
   session: a text box where you can type instructions.
4. Type `/exit` and press Enter to leave the session for now. The full
   test run follows in section 7.

The Desktop app and Claude Code share this login, so you're done once
you've signed in to each.

## 5. Install Git

Git downloads ("clones") the workshop repository to your machine, and
the Desktop app requires it for local sessions on Windows.

1. In PowerShell, run:

   ```powershell
   winget install --id Git.Git -e --source winget
   ```

2. Accept the license prompt if one appears, and wait for the install
   to finish.

3. Close PowerShell, open a new window, and verify:

   ```powershell
   git --version
   ```

   Expected output: a line like `git version 2.55.0.windows.4`.

If the `winget` command is not recognized, download the installer from
<https://git-scm.com/install/windows> instead ("Git for Windows/x64
Setup"), run it, accept all default options, and then verify with
`git --version` in a new PowerShell window.

## 6. Install uv

uv manages Python and the packages the workshop projects need. It
installs a suitable Python version by itself, so you do not need to
install Python separately.

1. In PowerShell, run:

   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. Close PowerShell, open a new window, and verify:

   ```powershell
   uv --version
   ```

   Expected output: `uv` followed by a version number, for example
   `uv 0.12.3`. Any version number means the install worked.

## 7. Test both surfaces

### Test 1: Claude Code in the terminal

1. In a new PowerShell window, create a test folder and move into it:

   ```powershell
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
   `claude-test` folder from Test 1 (it is inside your user folder,
   `C:\Users\<yourname>\claude-test`).
4. Type the same trivial instruction as above and send it.
5. Expected result: Claude replies in the app. By default it works in
   Manual mode: it proposes any file change as a diff and waits for your
   approval before applying it.

If both tests pass, you are fully set up. Bring your laptop and charger
on 8 September.

## 8. Troubleshooting

**`irm` is not recognized as a command.** You are in the Command Prompt,
not PowerShell. Check the prompt: PowerShell shows `PS C:\...>`, the
Command Prompt shows `C:\...>` without the `PS`. Close the window, open
the Start menu, search for `powershell`, and try again.

**`claude`, `git`, or `uv` is not recognized after installing.** Close
every PowerShell window, open a fresh one, and run the command again.
Newly installed programs only appear in new terminal sessions.

**The Code tab shows an error when starting a local session.** On
Windows, local Code sessions require Git. Complete section 5, then quit
the Desktop app entirely and reopen it.

**Anything else.** Come to the workshop room at 8:30 on 8 September with
your laptop and charger. We will finish the setup with you before the
start at 9:00. Nothing in the morning session requires more than what
this guide covers, so a fixable install problem costs you nothing.
