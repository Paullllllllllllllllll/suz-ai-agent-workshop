# Replicate Nico's research hub

Several people asked how to start with the research hub and the literature
workflow from the 13:15 demo. This folder is for them.

| File | What it is |
|---|---|
| `research-hub-explained.md` / `.pdf` | How the hub and the literature workflow work, how they grew, and the principles behind them. Read this first |
| `hub-tour/index.html` | A clickable copy of the hub's dashboard, filled with placeholder data. Browse it to see what each part does and pick what you want for yourself |
| `agents/` | Seven of my subagent definitions, made generic: copy one into `.claude/agents/` and fill in the placeholders |
| `start-with-your-agent.md` | Instructions for Claude: it interviews you and builds the first small piece of your own version with you |

## Getting started with your agent

Open Claude Code, or a project in Claude Desktop, in an **empty folder**
where your own setup should live, and paste:

```text
Read replicate-nicos-research-hub/start-with-your-agent.md from
https://github.com/Paullllllllllllllllll/suz-ai-agent-workshop/tree/main/catchup
(or from my local clone of that repository) and follow it.
```

The agent asks you a few questions one at a time: what you work on, what
irritates you every week, and which tools you already use. It then
proposes **one** small first version, either a morning brief over your
tasks or a literature scout over your Zotero library, and builds it with
you. Expect about an afternoon.

**Start small.** The full hub took months and grew out of one loop. The
first version is the part worth copying.
