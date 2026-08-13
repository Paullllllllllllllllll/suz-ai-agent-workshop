# Try-out: literature workflows

This is a self-contained 60-90 minute task for the literature track,
built for participants who brought no material of their own. It runs
the same way in Claude Code (CLI) and the Claude Desktop app.

## Start here

Paste the following to begin:

```text
Copy ../../walkthrough/project/papers/ into a new folder papers/ here, then read
all five PDFs and build screening_table.md: one row per paper with columns for
research question, data, method, and main finding.
```

## Material

You will work with five open-access papers on displacement and
residential mobility in Swiss rental housing. They are bundled in this
repository at `../../walkthrough/project/papers/` (relative to this
folder):

| Paper                        | Journal         | License      |
|------------------------------|-----------------|--------------|
| Kauer, Lutz & Kaufmann 2025  | Urban Studies   | CC BY        |
| Lutz, Wicki & Kaufmann 2024  | EPB             | CC BY-NC     |
| Gehriger 2023                | Housing Studies | CC BY-NC-ND  |
| Lacroix & Bertrand 2024      | Housing Studies | CC BY        |
| Pagani, Baur & Binder 2021   | JHBE            | CC BY        |

## Task ladder

Work through the rungs in order. Rung 1 alone constitutes a complete
result. Rung 3 is mandatory for everyone who reaches it, because its
output feeds the closing block at 16:30.

### Rung 1: screening (about 20-30 minutes)

1. Have the agent read all five papers.
2. Ask for a screening table with one row per paper and columns for
   research question, data, method, and main finding.
3. Read the table yourself and mark anything that looks too smooth or
   too vague. You will test one of those cells on rung 3.

You are done when `screening_table.md` exists, has five rows, and you
can point at the cell you trust least.

### Rung 2: comparison (about 20-30 minutes)

1. Pick one mini-question. Examples:
   - Who bears the costs when rental contracts are terminated at scale?
   - Does moving after displacement improve or worsen access and
     location?
   - What role do landlords and institutional owners play in tenant
     mobility?
2. Ask for a synthesis memo of one page or less that states where the
   five papers agree, where they disagree, and what each would say
   about your mini-question.
3. Push back on at least one claim in the memo and make the agent
   defend or revise it from the papers.

You are done when `synthesis_memo.md` exists, names concrete points of
agreement and disagreement, and attributes positions to specific
papers.

### Rung 3: verification (mandatory, about 20-30 minutes)

1. Pick one summary produced on rung 1 or 2.
2. Ask the agent to audit it by listing every claim in the summary and
   tracing each to a page number in the source PDF.
3. Then have a subagent do a blind review: give it only the summary and
   the PDF (not the audit) and ask it to check the summary against the
   paper.
4. Compare the audit and the review. Write three to five lines in
   `verification.md` that state what the blind review caught, what it
   missed, and whether the audit's page references held up.

You are done when `verification.md` exists and names at least one
concrete catch or miss. Bring it to the closing block; the discussion
there starts from these notes.

## Practical notes

Work in a copy of the papers folder. Either copy it into your working
folder (the starter prompt does this) or tell the agent to treat the
original as read-only. Do not let the agent write into `walkthrough/`.

The timings above assume a single pass. If a PDF read stalls, ask the
agent to process the papers one at a time.

You have reached the overall "done" state when you have three files
(`screening_table.md`, `synthesis_memo.md`, `verification.md`) and one
verification finding you can report in a single sentence at 16:30.
