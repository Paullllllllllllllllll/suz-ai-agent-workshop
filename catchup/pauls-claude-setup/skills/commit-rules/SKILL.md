---
name: commit-rules
description: git commit, git push, commit changes.
---

# Commit Rules

## Scope & Staging

- Include the changes made in the current session (or since the session's
  last commit). Stage explicit paths, never `git add -A` or `git add .`;
  pre-existing dirty files you did not touch stay unstaged.
- Always exclude IDE files, large datasets, and tool configuration
  (`.claude`). Exclude edits to an existing `.gitignore` unless they are part
  of the requested work; a `.gitignore` authored as part of the deliverable
  (e.g. when initializing a repository) is included.
- If unsure what belongs in a particular commit, ask the user; otherwise
  apply these rules autonomously.
- Commit and push directly to the default branch when that is the repo's
  established practice (linear history of direct commits). Do not branch,
  open a PR, or ask in that case.

## Message Template

Plain text; American English; imperative mood in the header and file
bullets; body wrapped at ~72 characters; no attribution to Claude.

```text
type(scope): short imperative summary

- path/to/file.ext: (append " (new)" or " (removed)" as appropriate)
  - 1-4 imperative bullets describing the change to this file.
- next/file.ext:
  - ...

One to three sentences of rationale: why the change was made and its
benefit.

Notes / next steps:
- Optional, 0-3 short actionable bullets; omit the section if none.
```

- `type`: feat, fix, perf, refactor, docs, chore, test, style, or build.
- `(scope)`: optional; omit the parentheses if empty.
- Header <= 72 characters. Blank line between every section.

## Versioning & Changelog

Applies to every repository you maintain; new repos are covered
automatically. Apply whenever a commit is (or should be) a release.

### Scheme

- Semantic versioning `MAJOR.MINOR.PATCH`; no pre-release suffixes. `0.x`
  versions are legitimate while a pipeline or site is in flux.
- Bare in machine contexts (`1.9.0`); `v`-prefixed in human contexts and git
  tags (`v1.9.0`).
- The manifest version is the single source of truth: `pyproject.toml`
  `[project] version` for Python repos, `package.json` `"version"` for web
  repos. Do not define `__version__` (or equivalent) in the source.

### The Four Loci

Every release updates all four, kept in agreement (drift check: all four
show the same version):

1. Manifest version (bare).
2. README H1 -> `# RepoName vX.Y.Z`.
3. README `## Changelog` -> new top entry.
4. Annotated git tag `vX.Y.Z` at the release commit.

### Changelog

The changelog lives in `README.md` under a `## Changelog` heading; there is
no standalone `CHANGELOG.md`. One bullet per release, newest first, no gaps
and no placeholders:

```text
- **vX.Y.Z** (D Month YYYY) -- one prose paragraph describing the change.
```

- Date: English month, no leading zero on the day (e.g. `4 May 2026`), from
  the release commit's author date.
- Single prose paragraph per entry: no nested bullets, no Keep-a-Changelog
  `Added`/`Changed`/`Fixed` sections.
- Tool repos are complete from `v1.0.0`; research projects and web repos
  from their dated baseline entry — history before the baseline is not
  reconstructed.

### Repo Classes

**Tool repos** (installable packages and command-line tools): the README is
the tool's full documentation. Release per change batch: any merged feature,
fix, or dependency sweep.

**Research projects** (analysis repos): the README is a thin version
carrier — H1, a few sentences of description, a pointer to the project's
research-design document, and the changelog; the design document remains
the documentation of record. Release on milestone: a production data run, a
co-author or paper delivery, a dependency/health sweep, or closing a
design-document milestone; daily commits accumulate between releases, and
the release paragraph summarizes them.

**Web repos** (websites and web apps): the README is the site's
documentation. Release on deploy-worthy milestone: a page or feature
shipped, a design overhaul, a data refresh, or a dependency sweep; routine
content tweaks accumulate between releases.

### Release Checklist

1. Make the code/dependency changes; ensure the test suite passes.
2. Bump the manifest version, then regenerate the lockfile (`uv lock`;
   `npm install --package-lock-only`; or `pnpm install --lockfile-only`) so
   its own package version stays in sync.
3. Update the README H1.
4. Add the `## Changelog` top entry.
5. Commit with a conventional-commit subject ending in `; bump to vX.Y.Z`
   (e.g. `build(deps): adopt mypy 2.x; bump to v1.12.0`); a pure version
   bump with no other change uses `chore(release): vX.Y.Z`.
6. `git tag -a vX.Y.Z -m "vX.Y.Z"`.
7. `git push origin HEAD --follow-tags`.
