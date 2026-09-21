---
name: documentation-reorganization
description: Audit, consolidate, reorganize project docs (CLAUDE.md, README, design doc).
argument-hint: "[project-root-path] [confirm|auto]"
---

# Documentation Reorganization

Consolidate and de-duplicate every `CLAUDE.md`, `README.md`,
`configs/manifest.yaml`, and stray Markdown document in a project, plus
the project's design document (for example `docs/DESIGN.md`; it may also
live outside the repository, in which case its path is in the root
`CLAUDE.md`). The target state is a clean layered documentation stack
where each layer carries only the information appropriate to it:

- **`configs/manifest.yaml`**: the processed-artifact registry — every
  artifact under `data/processed/` with its producer notebook, consumers,
  and schema summary. Must mirror what is actually on disk and in the
  notebooks; carries no prose documentation.
- **CLAUDE.md** (root and sub-layers): higher-level orientation for its
  layer — scope, status, and pointers to the layer below. No architectural
  detail, no methodological reasoning, no completed-work narrative.
- **Design document**: architecture, data inventory, methodology,
  analytical decisions, and active work-module tasks (`- [ ]` lines). The
  single source of truth for research design.
- **README.md**: user-facing install / usage; no internal decision logs.
- **Stray docs**: retain only if they serve a distinct, current purpose;
  otherwise archive or delete.

## Modes

Second argument; default `confirm` when absent.

- **`confirm`** (default): two-stage workflow. Run the audit, write the
  plan, present it for user approval, and do not touch any file before
  the plan is approved.
- **`auto`**: run the audit, then execute immediately without plan
  approval. The plan (§Stage 2 structure) becomes the internal execution
  order; deliver it afterward as a report of applied changes. Exceptions
  that are NEVER auto-applied, in either mode, and are instead collected
  in a "requires user decision" list at the end of the report:
  - Design-document task edits beyond ticking verifiably done work, and
    any design-content changes.
  - Removal of `configs/manifest.yaml` entries.
  - File deletions of anything that is neither orphaned nor archived
    first.

**Scope boundary**: this skill edits, moves, archives, and deletes
Markdown files, plus `configs/manifest.yaml` (registry reconciliation
only — entries, paths, schemas, producer/consumer lists). It does not
touch code, data, notebooks, or other non-Markdown documentation.

## Stage 1 — Audit

1. In confirm mode, enter plan mode; in auto mode, skip this step.
2. Enumerate every `.md` file in the project, plus
   `configs/manifest.yaml` if present, plus the project's design
   document. Include the project root,
   `src/`, `notebooks/`, `data/`, `reports/`, `scripts/`, `tests/`, and any
   `docs/`. Exclude `backup/` and `Literature/` trees by default (confirm
   with the user if uncertain).
3. Read each enumerated file.
4. Build a **doc map**: filename → owning layer. Layers:
   - `root` — `CLAUDE.md` and `README.md` at the project root.
   - `design` — the project's design document.
   - `sub-folder` — `CLAUDE.md` files deeper in the tree.
   - `package` — docs inside `src/<package>/`.
   - `notebook-adjacent` — docs co-located with specific notebooks.
   - `scratch` — `extras/scratch/`, RA folders, one-off notes.
   - `orphaned` — files with no evident current purpose.
5. Diagnose each file against the taxonomy (see §1.1 below).
6. Run the cross-reference check (§1.2).

### 1.1 Taxonomy-Based Diagnosis

For each file, record findings:

**CLAUDE.md files** should be layer-orientation only. Flag:

- Sections that duplicate content belonging in the design document
  (architecture descriptions, data-product inventories, methodology
  summaries, analytical decisions).
- Content that belongs to a lower layer (file-level detail that should be
  read from the code itself; sub-package specifics that should be in a
  sub-folder `CLAUDE.md`).
- Completed-work narrative ("we recently added X", "as of last week"),
  which is changelog bloat.
- Stale status lines that no longer match the state of the code.
- Pointers to files that no longer exist.

**The design document** should own architecture, data inventory,
methodology, analytical decisions, and active TODOs. Flag:

- Missing sections required by the design-document template (if the
  portfolio has one).
- Drift between the design document and the actual code (stated modules
  that don't exist; stated data products with no on-disk artifact; stated
  pipelines not reflected in `src/`).
- Completed tasks still unticked (agents may tick verifiably done work;
  other task edits need explicit user approval).
- Open tasks with no evidence of intent (abandoned rather than active).
- Content that belongs in `CLAUDE.md` (layer orientation) rather than in
  the design document.
- Overly long and detailed prose, which belongs in the paper draft, and
  not in the design document, which should be concise.
- Discussion of analyses that are no longer relevant to the project since
  they have been superseded or abandoned should get at most a minimal pointer.

**`configs/manifest.yaml`** should be a complete, accurate registry of
processed artifacts. Flag:

- Registered artifacts whose `path` has no on-disk file, or whose
  declared producer / consumer notebooks no longer exist.
- Files under `data/processed/` (CSV / JSON) with no manifest entry.
- Schema summaries that no longer match the artifact's actual columns
  (spot-check headers).
- Stale entries for renamed or superseded artifacts.

**README.md** should be user-facing install / usage. Flag:

- Internal-only decision logs.
- Design-document-style research narrative.
- TODO lists that belong in the design document.
- Missing install section or absent `uv sync` / `pip install -e` guidance
  (if the project is installable).

**Stray docs / changelog-style notes**: identify whether each is:

- a live reference that belongs in `docs/`;
- a historical note that belongs in `backup/` with a dated archive
  filename;
- genuinely orphaned and should be deleted.

### 1.2 Cross-Reference Check

- Every Markdown link target exists (relative paths; absolute paths to
  project files).
- Every design-document task line is still live work.
- Every repo/paper-side pointer to the design document resolves.
- Portfolio-index `CLAUDE.md` pointers to this project remain accurate.
- Sibling-project cross-links (e.g., shared `settings.json` notes) still
  resolve.

## Stage 2 — Write the Plan

In confirm mode, present §§2.1-2.5 for approval before executing §2.4.
In auto mode, execute directly and deliver the same structure as a
post-hoc report, with the "requires user decision" list appended.

### 2.1 Context

What is wrong with the current documentation state: bloat in `CLAUDE.md`,
drift in the design document, stale cross-references, orphaned files. Be
specific; cite individual files and sections.

### 2.2 Target Doc Tree

List every Markdown file that will exist after the reorg, annotated with
its role. Follow the layer convention strictly. Example (adapt to the
project):

```
<project-root>/
├── CLAUDE.md                       # layer orientation: scope, status, pointers
├── README.md                       # user-facing install + usage
├── configs/manifest.yaml           # processed-artifact registry (reconciled)
├── data/CLAUDE.md                  # data provenance + read-only warnings
├── notebooks/CLAUDE.md             # notebook inventory (if > ~10 notebooks)
├── src/<package>/CLAUDE.md         # (optional) package orientation
├── docs/DESIGN.md                  # design document (if kept in the repo)
├── docs/                           # live user-facing references (if any)
└── backup/                         # archived historical docs; never edited
```

### 2.3 Files to Rewrite, Trim, Archive, or Delete

Exhaustive table. For each file:

| Path | Action | Rationale |
|------|--------|-----------|
| `CLAUDE.md` | Rewrite | Strip completed-work narrative; migrate architecture §2 into design doc. |
| `docs/DESIGN.md` | Trim | Close TODOs 4, 7, 9 (work done); add §5 "Data Products". |
| `old_changelog.md` | Archive | Move to `backup/old_changelog_DD_MM_YYYY.md`. |
| `scratch_notes.md` | Delete | No references; content superseded. |

Note every file requiring user approval for TODO edits.

When stating a post-trim line-count target for the design document,
derive it from the action table itself: sum the lines of the sections
marked keep plus the compressed size of the sections marked trim. Do not
quote an aspirational round number — protected content (data inventories,
design decisions, live TODOs) sets a hard floor, and execution must honor
the keep list over the target when the two conflict.

### 2.4 Migration Steps

Strict order:

1. **Snapshot (git-aware)** — files tracked by git with a clean status
   need no zip; git history is the backup. Zip only the files git does
   not protect, into `backup/<project>_docs_DD_MM_YYYY_vN.zip`:
   - docs that are gitignored or untracked (`CLAUDE.md` files are often
     gitignored — check with `git check-ignore -v`, not `git status`,
     which omits ignored files);
   - tracked docs carrying uncommitted modifications;
   - any untracked or ignored file slated for deletion or archival.
   Windows caveat: `Compress-Archive` silently collapses same-basename
   files (e.g., several `CLAUDE.md`) into one entry; build the zip with
   path-preserving tooling (`System.IO.Compression` or `zip -r`).
2. **Migrate architectural / analytical content** from each `CLAUDE.md`
   into the design document (with user approval if TODOs are touched).
3. **Rewrite `CLAUDE.md` files** to minimum-viable scope: scope, status,
   pointers only. Target word-count ceiling configurable; 400 words per
   file is a reasonable default.
4. **Trim the design document**: close completed TODOs (with approval),
   add missing sections, reconcile drift against the code.
5. **Update the README**: move internal-only content into the design
   document; keep install and usage.
6. **Reconcile `configs/manifest.yaml`**: add entries for unregistered
   on-disk artifacts, fix wrong paths / producers / consumers / schemas,
   and remove entries for artifacts that no longer exist (with user
   approval for removals).
7. **Archive or delete stray docs** per §2.3.
8. **Repair cross-references**: every link resolves, including the
   repo/paper-side pointers to the design document.
9. **Run the verification suite** (§2.5).

### 2.5 Verification

Runs once at the end; confirm every check passes.

- **Link resolution**: every Markdown link target resolves.
- **Task integrity**: every design-document task line maps to live work;
  done work is ticked; all task edits beyond ticking were user-approved.
- **Layer discipline**: each `CLAUDE.md` is within its word-count ceiling, with
  no architectural / methodological leakage.
- **Duplication audit**: `ripgrep` for near-duplicate paragraph-length prose
  across `CLAUDE.md` and the design document; duplicates removed or
  redirected.
- **Portfolio-index integrity**: higher-level `CLAUDE.md` references to this
  project still resolve.
- **Manifest reconciliation**: every manifest entry resolves to an on-disk
  artifact and its producer / consumer notebooks; every `data/processed/` file
  is registered.
- **Manual read-through**: root `CLAUDE.md` and design document read
  cleanly end to end.

## Constraints

- Design-document tasks: tick verifiably done work freely; any other task
  or design-content edit needs explicit user approval.
- Never modify files under `backup/`.
- Never modify files under `Literature/` trees.
- Do not touch code, data, notebooks, or non-Markdown documentation
  other than `configs/manifest.yaml`.
- Manifest edits are registry reconciliation only: never invent schemas
  — read them from the artifact headers or the producer notebook.
- Keep a single copy of the design document; if it lives outside the
  repository, do not create a project-root copy to keep in sync.
