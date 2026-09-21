---
name: handoff
description: Create handoff document to pass conversation to another agent/session.
disable-model-invocation: false
argument-hint: "What will the next session be used for?"
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work.
Save to the existing projects 'docs' folder with a descriptive name, including the current date.
If no docs folder exists, ask the user where to save the document.

Suggest the skills to be used, if any, by the next session.

Do not duplicate content already captured in other artifacts (PRDs, plans docs, ADRs, issues, commits, diffs). Reference them
by path or URL instead. Exception: other handoffs. Never reference handoff documents in other handoffs or other documentation.
They are transient artifacts and will be deleted later on.

Redact any sensitive information, including API keys, passwords,
or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
