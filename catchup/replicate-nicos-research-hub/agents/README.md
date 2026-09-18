# Example subagents

Seven agent definitions from Nico's research hub, cut down to the essentials and
made generic. Everything about his own projects, people, tools and machines has
been removed. Copy them as they are, or use them as a starting shape for your
own.

## How to use one

In Claude Code, a subagent is a Markdown file in `.claude/agents/`, either in
your project folder or in `~/.claude/agents/` for all projects. The header
(`name`, `description`) tells Claude when to use the agent, and the body is its
instructions.

1. Copy a file into `.claude/agents/`.
2. Fill in every `<ANGLE-BRACKET>` placeholder: your research focus, and where
   your papers, tasks and notes live.
3. Ask Claude to use it ("use the literature-scorer on the new papers"), or let
   it pick the agent from the description.

## The seven

| Agent | What it does | Needs |
|---|---|---|
| `literature-scorer.md` | Scores new papers for relevance and writes down why | A list of new papers (a CSV, a folder, or a literature database/MCP) |
| `literature-reading-picker.md` | Picks about five papers worth actually reading now, each with a why-this-why-now | Your library plus a short note on current projects |
| `literature-note-drafter.md` | Drafts a literature note for one paper, **as a proposal you approve** | The paper's text; optionally your highlights |
| `project-sentinel.md` | Weekly sweep across projects: stalls, missing next steps, slipping deadlines | A task list and a projects file |
| `memory-steward.md` | Keeps a memory/decisions file honest: duplicates, contradictions, stale entries | A memory file the other agents write to |
| `opportunity-scout.md` | Weekly: grants, special issues and conferences matched to your projects, plus a deadline watch on a list of known calls. Never applies to anything | A short eligibility profile, a watchlist, and web search |
| `orchestrator.md` | Routes questions between agents and escalates the rest to you | Two or more agents and one shared questions/tickets file |

**Start with one.** The scorer or the sentinel is a good first agent. The
orchestrator only makes sense once several agents are writing to a shared queue.

## Design rules they all follow

- **One job each.** An agent that does two things does both badly and is hard
  to debug.
- **Every judgement comes with a written reason.** A silent judgement is where
  compounding mistakes hide.
- **Explicit boundaries.** Each file says what the agent may write and what it
  must leave alone.
- **Gate by the cost of being wrong.** Reversible, logged writes can be
  autonomous. Anything touching your own notes, anything external, and any
  deletion needs your approval.
- **Never invent.** No made-up abstracts, findings, deadlines or status. When
  something is unknown, the agent says so.
