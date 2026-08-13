---
name: document-analysis
description: Document an analysis script after writing or changing it. Use automatically whenever an analysis script in this project is created or modified.
---

After writing or changing any analysis script, document it before
reporting the work as done. Put the documentation where the next reader
will find it: a module docstring at the top of the script, or a short
companion section in an existing README.

Record four things:

1. **Purpose.** What question the script answers, in one or two lines.
2. **Data in, data out.** Which files or endpoints it reads, which
   files, figures, or tables it writes.
3. **Decisions taken.** Filters, exclusions, transformations, and why.
   A reader must be able to see what was dropped and on what grounds.
4. **How to re-run.** The exact command, normally
   `uv run python <script>`.

Also record data provenance: name the source dataset and its license as
given in `data/README.md`. Keep the whole entry short; a screenful is
the ceiling.
