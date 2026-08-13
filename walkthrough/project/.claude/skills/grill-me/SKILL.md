---
name: grill-me
description: Interview the user about their analysis plan one question at a time until the design is watertight. Use when the user wants to stress-test an analysis plan, get grilled on their design, or mentions "grill me".
---

Interview the user about their analysis plan until the design is
watertight. Resolve dependencies between decisions one by one; do not
move on while an answer leaves a hole.

Rules:

- Ask the questions **one at a time**. Wait for the answer before the
  next question.
- For each question, offer your own recommended answer, so the user can
  accept, adjust, or reject it.
- If a question can be answered by looking at the project's data or
  files, look instead of asking.

Cover at least these grounds before declaring the design sound:

- **Data limitations.** What the dataset measures, what it misses,
  coverage gaps, and whether the unit of analysis fits the question.
- **Robustness.** Outliers, alternative periods or subsamples,
  sensitivity of the headline result to the choices made.
- **Interpretation.** What the result can and cannot claim; rival
  explanations; how far the finding generalizes.

End with a short recap: the agreed design, the open risks, and the next
concrete step.
