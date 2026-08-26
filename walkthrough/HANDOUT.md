# Morning Walkthrough — Handout

This document mirrors the slides for the morning session (9:00-12:15)
on Claude Code (the CLI) and the Claude Desktop app. Pick one surface and
stay on it; every step names what differs between the two. If you
missed the morning, this handout is self-contained: work through it
top to bottom at your own pace.

Throughout, text in a fenced block is a prompt to paste into the agent
verbatim:

```text
Like this.
```

## Part 0: Setup (do this before 10:00)

Before we begin, you need the toy project on your machine and an agent
session running inside it.

1. **Get the repository.** Either clone it:

   ```text
   git clone https://github.com/Paullllllllllllllllll/suz-ai-agent-workshop
   ```

   or, if you do not use git, open that URL in a browser and choose
   Code, then Download ZIP, and unpack it.

2. **Copy the project folder out of the clone.** Copy
   `walkthrough/project/` (the whole folder) to a working location of
   your choice, for example a `swiss-rents` folder in your documents,
   or on your desktop.
   Use your file manager; no command line needed. You will modify this
   project all morning; working on a copy keeps the clone clean, so
   you can always diff against or restart from the original.

3. **Start your agent inside the copied folder.**

   - **CLI:** open a terminal, change into the copied folder
     (`cd path/to/swiss-rents`), and run `claude`, or open
    the terminal directly in the folder through right click
    -> terminal (powershell).
   - **Desktop app:** open the Code tab, choose Local, click
     Select folder, and pick the copied folder.

**The working-directory contract.** The project's `.claude/` folder
(skills, rules, subagents) and its `CLAUDE.md` load only if the
session starts inside the project folder. An agent started one level
up, or in your home directory, knows nothing about this project. If
the agent later seems ignorant of the skills, this is the first thing
to check, on either surface.

## Part 1: LLMs and Coding Agents (9:00-10:00)

In this section, we try out a few simple examples based on the
explanations given in the slides. Follow along by prompting the agent
in the CLI or desktop app in parallel with what is shown on the screen
in the front. Run these prompts in the session you started in Part 0.
Desktop and CLI take the same prompts; the differences sit in how
permissions and modes appear, named below.

### 1.1 The agent loop

An agent is a language model that can call tools (read files, run
commands, search) in a loop until the task is done. Here is a simple
example that lets you see the loop at work:

```text
What files are in the current folder? List them and say in one line
what each one seems to be for.
```

Expected: the agent calls a file-listing tool, you see the tool call
and its result, then a summary naming `CLAUDE.md`, `pyproject.toml`,
`data/`, `papers/`, and `.claude/`. A pure chat interface cannot do this;
the tool call is the difference. It takes only a few seconds.

- **CLI:** the tool call and its output appear inline in the terminal
  transcript.
- **Desktop:** the tool call appears as a step in the conversation;
  the app also has an integrated terminal, which you will not need
  yet.

### 1.2 The permission dialog

Because agents act on your machine, any action that changes something
requires your approval. Let's trigger the permission dialog deliberately:

```text
Create a file called hello.txt containing one sentence about what you
did in the previous step.
```

Expected: before anything is written, the agent asks for permission to
create the file. Approve it. Then check that `hello.txt` exists in
the folder.

- **CLI:** the permission request appears in the terminal; permission
  modes (Manual, Accept edits, Plan, Auto) are switched with
  Shift+Tab.
- **Desktop:** the permission request appears in the conversation;
  the same four modes sit in the mode selector in the toolbar.

Stay in Manual for now: you see and approve every action, which is
exactly what a beginner should do.

### 1.3 Reading files

```text
Read hello.txt and quote its exact content back to me.
```

Expected: the agent reads the file and quotes it verbatim, without a
permission prompt — reading inside the project folder is allowed by
default on both surfaces; only changes need approval. This asymmetry
(read freely, write with consent) is the permission model in one
sentence.

### 1.4 Cleaning up, and a second permission flavor

```text
Delete hello.txt.
```

Expected: a permission request again, this time for a shell command
rather than a file edit, since deletions run through the command line
under the hood. Approve it; the file is gone. Same dialog placement as in
1.2 on both surfaces.

These four prompts demonstrate the whole mechanical basis of the
morning: prompts in, tool calls out, permissions in between. Everything
after the break builds on these moves.

## Part 2: One Research Workflow, End to End (10:00-12:15)

We will now walk through one toy research project at a deliberate
pace. The project asks a real if modest question: how do average rents
vary across Swiss cantons, and how robust is the pattern? We will work
with five open-access papers and two public datasets. The workflow has
five steps:

| Step | Content                          | Time    | Clock       |
|------|----------------------------------|---------|-------------|
| 1    | Project tour and conventions     | 20 min  | 10:00-10:20 |
| 2    | Subagent literature analysis     | 30 min  | 10:20-10:50 |
|      | Break                            | 10 min  | 10:50-11:00 |
| 3    | Live data fetch                  | 20 min  | 11:00-11:20 |
| 4    | Exploratory analysis, robustness | 30 min  | 11:20-11:50 |
| 5    | Stress-test and analysis plan    | 25 min  | 11:50-12:15 |

### Step 1: Project Tour and Conventions (20 min)

An agent is only as good as the context it starts with. This project
ships that context in files: `CLAUDE.md` as project memory, skills as
invokable procedures ('fancy prompts'), rules as standing constraints,
subagents as delegable specialists. All of it is loaded automatically
when you started the session inside the folder. The first prompt
demonstrates this.

```text
What do you know about this project? Name the research question, then
list every skill, rule, and agent available to you, each with the file
it is defined in and one line on what it does.
```

Expected: without opening anything you pointed it to, the agent states
the rent question and lists three skills (`fetch-swiss-rents`,
`document-analysis`, `grill-me`), one rule (`reproducibility`), and
two agents (`paper-reader`, `skeptic-reviewer`), with their paths
under `.claude/`. It knows all this because `CLAUDE.md` was read at
session start.

Now look at how a skill is built:

```text
Show me .claude/skills/fetch-swiss-rents/SKILL.md and explain how the
description field decides when this skill gets used.
```

Expected: the agent displays the file (a YAML header with `name` and
`description`, then plain-language instructions) and explains that
the description is what the agent matches against your request: a
skill is prose, not code, and writing one means writing instructions
a careful colleague could follow. Note the degradation rule at the
bottom of the skill; we'll return to it later.

Finally, prepare the Python environment for the rest of the workflow:

```text
Run uv sync to set up the Python environment.
```

Expected: a permission request for the shell command, then one to two
minutes of dependency installation (pandas, matplotlib, and friends
from `pyproject.toml`).

- **CLI:** approve the command in the terminal; the install output
  scrolls by inline.
- **Desktop:** approve the command in the conversation, or run
  `uv sync` yourself in the app's integrated terminal — both work.

If the agent does not know the project, the session started outside
the project folder. End it and redo Part 0, step 3. If `uv` is missing,
see the install guide in `install/`.

### Step 2: Subagent Literature Analysis (30 min)

Reading five PDFs in the main conversation would flood it with text.
Instead, we will use subagents: a subagent reads in its own separate
context and returns only the distilled result. The `paper-reader`
agent is defined in `.claude/agents/paper-reader.md` and reads exactly
one paper, returning a five-heading summary (question, data, method,
main finding, relevance to this project). Dispatching it five times in
parallel is one prompt:

```text
Read papers/README.md for the citations. Then dispatch the
paper-reader agent once per PDF in papers/ — five runs, in parallel —
and give me the five structured summaries.
```

Expected: five subagent runs launch at once; each reads its paper end
to end. After a few minutes (parallel, so roughly the time of the
longest single paper, not the sum) you get five uniform summaries
covering redevelopment displacement, transit densification, the Basel
mass cancellations, asylum migrants' housing trajectories, and
tenants' residential mobility. Subagents run identically on both
surfaces; the Desktop app lacks agent teams and headless mode, but
neither is used here.

While the readers work, note what you did not do: you did not open a
PDF, and the summaries follow one fixed structure because the agent
definition imposes it — comparability by construction.

Then synthesize:

```text
Across the five summaries: which data sources and methods recur, and
what do the papers collectively say about who is exposed to rent
increases and displacement in Switzerland? One page, with the papers
cited by author and year as given in papers/README.md.
```

Expected: a one-page comparison drawing on all five summaries, with
citations matching the README table. One to two minutes.

The project also carries a `skeptic-reviewer` agent, an adversarial
referee that checks a finished result against the project files
instead of praising it. If time allows, run it on the comparison you
just received:

```text
Have the skeptic-reviewer agent review the comparison you just wrote.
```

Expected: a two-to-three sentence verdict plus a ranked list of
concrete problems, typically claims stronger than five summaries can
bear. This producer-and-auditor pattern appears again in the afternoon.

If the agent reads the papers itself instead of dispatching, prompt it
explicitly: "Use the paper-reader agent, do not read the PDFs yourself."
If one subagent fails on a PDF, rerun just that paper.

**Break (10 min).** Leave your session open; it keeps its memory.

### Step 3: Live Data Fetch (11:00-11:20)

The `fetch-swiss-rents` skill encodes everything needed to fetch the
two rent datasets: endpoints, licenses, a required `User-Agent` header
for the Zurich API, and an explicit fallback rule. If a download
fails, the skill uses the local snapshots in `data/` and reports which
path it took. The skill never aborts on a network error.

Invoke the skill by name:

```text
/fetch-swiss-rents
```

- **CLI:** type `/` and the skill list appears; select or type
  `fetch-swiss-rents` and press Enter.
- **Desktop:** type `/` in the message box for the same list, or pick
  the skill from the + menu.

Expected: the agent fetches the BFS cantonal rents workbook (XLSX,
years 2000, 2003, and 2010-2024) and the City of Zurich rent records
(JSON via the CKAN API), approving one or two network commands on the
way, and reports for each dataset which path it took: live download
or local fallback. Either report is a success; the skill states its
provenance instead of failing silently. One to three minutes.

The Zurich dataset is delivered by a public API answering a structured
request. Query it:

```text
From the Zurich rent data: how has the median rent (qu50) for 3-room
market housing developed over the available years? A short table is
enough.
```

Expected: a small year-by-median table drawn from the JSON records,
which carry mean and quartiles by year, district, room count, and
cooperative versus market housing. Under two minutes.

If a 403 error appears from the Zurich API, the `User-Agent` header
was likely skipped; point the agent back at the skill. If both
downloads fall back to the local files, nothing is lost: the snapshots
in `data/` are complete, and the rest of the morning runs on them
unchanged.

### Step 4: Exploratory Analysis and Robustness (11:20-11:50)

Here we address robustness checks and reproducible, documented scripts.
The `reproducibility` rule requires every figure and table to come
from a script; the `document-analysis` skill fires automatically
whenever an analysis script is written or changed. Watch both trigger
themselves without being mentioned in the prompt.

```text
Using the BFS dataset, write a script that computes the average rent
per canton across all available years and reports the gap between the
most and least expensive cantons. Follow the project's conventions.
```

Expected: the agent writes a Python script (not a throwaway
calculation in chat; the rule forbids results that exist only in the
transcript), runs it via `uv run python`, and reports the ranking:
Zug, Zurich, and Geneva at the top, with a sizable gap to the cheapest
cantons. Because `document-analysis` applies automatically, the script
carries a docstring recording purpose, data in and out, decisions
taken, and the re-run command, and it credits the BFS as the OPEN-BY
license requires. Three to five minutes, a few permission approvals
for file writes and script runs.

This step produces several file edits in a row. If approving each one
gets tedious, switch the permission mode from Manual to Accept edits
(Shift+Tab in the CLI, the toolbar mode selector in the Desktop app),
and switch back afterward.

Now comes the robustness check. Agents make reruns cheap: simply prompt
them to run some robustness checks and perform any other analyses you
see fit.

```text
Rerun the analysis twice: once dropping Zurich and Geneva as outlier
cantons, and once splitting the period into 2000-2014 and 2015-2024.
Does the ranking hold in each case? Summarize in a short table.
```

Expected: the agent extends or parametrizes the script, reruns it, and
answers with a compact comparison: the broad ranking is stable, the
gap narrows without the two big urban cantons. The documentation is
updated to record the new variants, again unprompted.

If the agent computes in chat instead of writing a script, remind it
of the reproducibility rule and rerun. If pandas fails on the XLSX
(German headers, multi-row layout), tell the agent to inspect the raw
sheet first and adjust. Debugging its own script is normal agent work,
and current models generally handle this type of task without issues.

### Step 5: Stress-Test and Plan (11:50-12:15)

This step inverts the usual workflow. So far you prompted and the
agent acted; now you bring an idea, and the agent interrogates you
about the precise implementation before anything gets built. Planning
precedes execution.

Start by switching the agent into plan mode, where it reads and asks
but changes nothing — the right setting for design work. On the CLI,
press Shift+Tab until the mode indicator shows plan mode; on Desktop,
pick Plan in the mode selector in the toolbar.

Now describe the analysis you have in mind and hand the interrogation
to the `grill-me` skill (courtesy of Matt Pocock). It interviews you
one question at a time, offering its own recommended answer with each
question, until the design holds and you and the agent have reached a
shared understanding:

```text
/grill-me I want to argue that the cantonal rent differences we found
are driven by urbanization. Interview me about how exactly this
analysis should be implemented before we write the plan.
```

Expected: the agent asks exactly one question, on data limitations,
robustness, or interpretation, and proposes an answer you can accept,
adjust, or reject. Answer honestly; the next question builds on your
answer. Where the answer sits in the project's own files, the skill
looks instead of asking. Expect four to six rounds over ten minutes.
It ends with a recap: agreed design, open risks, next step.
Skill invocation is as in Step 3: `/` on both surfaces, or the plus
menu on Desktop.

Because you are in plan mode, the agent writes this into its plan file
and presents it for your approval — plan mode saves the plan for you,
so no separate document is needed. Read it before approving: it should
reflect the interview rather than a generic template, with your
concessions from the grilling appearing as stated limitations. Two to
three minutes. Approving the plan ends plan mode, and the agent stands
ready to execute against it.

If the agent does not automatically write to the plan, just ask it for
the plan:

```text
Now write the plan for the analysis we just agreed on: research
question, data and its limitations, method, robustness checks, and
what the analysis can and cannot claim.
```

If the agent fires several questions at once, hold it to the skill:
"one question at a time, as the skill says." If the plan reads generic,
point at the interview: "Base every section on what we just agreed, not
on boilerplate."

Notice this step's order: the cheap part (running the analysis) came
before the expensive part (knowing what the analysis may claim) only
because this is a toy. In real work, run the grilling and write the
plan first, then let the agent execute against it, or divide this
up into seperate sessions (use one session to explore literature,
ideas, data, use another to write a plan for creating the infra-
structure for the actual analyses).

## What You Take Home

> **The project keeps working after today.** Your copied folder is a
> complete, self-contained agent project: start a session inside it
> any time and the skills, rules, and agents load exactly as they did
> this morning. Every piece is a plain-text file you can read, edit,
> and imitate — swap the datasets, rewrite `CLAUDE.md`, and the same
> scaffold carries your own research.
>
> **This afternoon** builds on these patterns: advanced workflow demos
> (13:15) — a research hub that runs overnight, then a synthetic
> dataset built from a codebook — followed by a live literature
> workflow (14:30) and hands-on work in tracks (pipelines,
> quantitative analysis, literature workflows, or a project of your
> own choosing) on your own material or the fresh dataset (14:50).
> The day closes with an open discussion on responsible AI use
> (16:30); the reading list behind it is `READING_LIST.md` in the
> repository, and it travels with the follow-up package.
>
> **Skipped setup?** The `install/` folder in the repository has the
> guides for both surfaces on Windows and macOS. Further reading:
> the Desktop quickstart
> (<https://code.claude.com/docs/en/desktop-quickstart.md>), skills
> (<https://code.claude.com/docs/en/skills.md>), and subagents
> (<https://code.claude.com/docs/en/sub-agents.md>).
