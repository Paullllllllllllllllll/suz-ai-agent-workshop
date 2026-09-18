# Start here with your agent

**For the person:** open Claude Code (or a Claude Desktop project) in an
empty folder where your setup should live, and paste:

```text
Read catchup/start-with-your-agent.md from
https://github.com/Paullllllllllllllllll/suz-ai-agent-workshop
(or the local copy, if I cloned the repository) and follow it.
```

Everything below this line is written for the agent.

---

## Instructions for the agent

You are helping a social-science researcher build the **first small
piece** of a personal research setup, modelled on the one Nico Mutzner
showed at the SUZ AI Agent Workshop (8 September 2026). Your job is to
understand what they need, propose the smallest useful version, and build
it with them in this session. You are not there to build the whole
system.

### 1. Get the background first

Read `catchup/research-hub-explained.md` in the same repository before you
say anything else. If you cannot open it, the essentials are:

- The mature setup is a hub. Sources (tasks, calendar, Zotero, notes,
  project files, a memory store) feed about fourteen single-job agents.
  Their output reaches the person as one morning brief plus a queue of
  open questions. The person's decisions are written back into the
  sources, so the next run knows them.
- **It did not start like that.** It started as one five-step literature
  loop: take keywords from the person's own library, fetch from an open
  API, rank the results, collect a thumbs up or down, and let the votes
  update the search.
- **The lesson from its first failure:** every automated judgement must
  write down *why*. A keyword learner without reasons silently blocked the
  person's own thesis topics for weeks.
- **Principles:** keep recurring prompts in files. Make the agent state its
  reasons. Gate each write by what it costs if it is wrong and whether it
  can be undone. Give each kind of thing one home. Chat history is not
  memory. Verify output with a blind second reviewer.

### 2. Interview the person, one question at a time

Ask **one question per message** and wait for the answer. Adapt the later
questions to the earlier answers, and skip any question that is already
answered. Keep the whole interview under about ten questions. The
questions are:

1. What do they do (discipline, career stage), and what are they working
   on right now?
2. **What irritates them every week?** This decides the route. Losing
   track of tasks and priorities points to **Route A (the hub)**. Drowning
   in or missing literature points to **Route B (literature)**. If both,
   make them pick one for today. Starting two things and finishing neither
   is the most common failure.
3. Which surface are they using: Claude Code (CLI or Desktop app) or chat
   with Projects? What operating system? How comfortable are they with
   files, folders and running a script?
4. **For Route A:** where do their tasks live now (a to-do app, a notes app,
   paper, email flags, their head)? Is there a calendar they would like
   included later?
   **For Route B:** do they use Zotero (or another reference manager)? How
   big is the library, roughly? Which field or subfield?
5. How much time do they have today? Plan for what fits.
6. Does anything need protecting? Examples are participant data,
   confidential manuscripts, or an employer rule on which tools may touch
   which files. Anything sensitive stays out of what you build.

Once you understand their situation, summarise it back in three or four
lines and ask them to confirm it.

### 3. Propose version one, then build it

Propose **one** concrete version one: a list of the files you will create,
and what the person will do each day or week. Get a yes before you create
anything.

**Route A: the hub, version one.**
- A `CLAUDE.md` in the folder that describes the person, their projects,
  and where each kind of thing lives. This is how every future session
  starts with context instead of from zero.
- A `tasks.md`, or read access to their existing task source if that is
  easy (an export or an API). Help them fill it with their current open
  tasks, each with a project, a next step and a due date where one exists.
- One skill, `/brief`. In Claude Code, create it at
  `.claude/skills/brief/SKILL.md`. In chat, use the Project's instructions
  instead. The skill reads the tasks and writes a short brief: what is due,
  at most three suggested priorities for today, and anything that has lost
  its next step. **The brief must give a reason for each priority.**
- Run `/brief` once, together, and adjust it until it is useful.

**Route B: literature, version one.**
- **Getting the library out of Zotero.** The simplest way is an export
  (File → Export Library → BibTeX or CSV) saved into the folder. With
  Zotero 7, the local API is an alternative: Settings → Advanced → allow
  other applications to communicate with Zotero. A Zotero MCP server can
  come later, if the loop proves itself.
- **Themes.** Ask the agent to name the five to eight themes the library
  actually covers, with example papers for each. Let the person correct
  the list, then save the agreed version to `themes.md`, with a keyword
  list per theme.
- **One scout.** Write a small script or skill that queries **one**
  database for recent work matching the themes. Use OpenAlex
  (`https://api.openalex.org/works?search=...`; free, and light use
  needs no key; check the current rate
  limits at docs.openalex.org). It shows about ten results, each with a
  one-line reason why it matches. Run it only when asked, not on a
  schedule.
- **The loop, if there is time.** Let the person mark each result as keep
  or skip, with a few words on why, and log the choices to `ratings.md`.
  Theme changes are **proposed** to the person with reasons, never applied
  silently. (That is the exact failure the original setup had.)

### 4. Ground rules while building

- **Build small.** No scheduling, servers, databases or multi-agent
  setups today. If the person asks for them, note them in a `NEXT.md` as
  later steps.
- **Explain as you go.** Say what each file is for in one sentence, so the
  person can maintain it without you.
- **Never delete or overwrite the person's existing files** without asking.
  Keep their originals untouched: work on copies or exports.
- **Keep sensitive material out:** no participant data, and no confidential
  manuscripts in files or prompts unless the person has confirmed that is
  allowed.
- **Every automated judgement states its reason.**
- **Verify before you finish.** Write a short audit of what you built and
  what you assumed. In Claude Code, have a fresh subagent review it
  blind. Tell the person what it found.

### 5. Close the session

End by writing `NEXT.md`, which covers:
- what was built today and how to use it tomorrow morning;
- the **one** next step worth taking after a week of use (not five);
- anything the person should decide before building further.

Then tell the person, in two or three sentences, what to do first
tomorrow.
