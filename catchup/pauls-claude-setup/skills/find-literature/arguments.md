# find-literature — CLI Options

Options:

- `--format {chicago,bibtex,csljson,ris,endnote,all}` — default `chicago`.
- `--with-paths` — append the absolute attachment file path(s) per hit, so you
  can open the underlying PDF. When you need to read the work, prefer a sibling
  `<stem>.txt` transcription or `_summary`/`_short_summary` file if one sits
  beside the PDF (see `zotero_doc.md`); fall back to the PDF itself.
- `--tag FACET::VALUE` — filter to works carrying this facet tag. Repeatable;
  multiple `--tag` are AND-combined, and combine with the search term. The
  library is faceted by `zotero-curator` Mode C, so this is the precise way to
  slice by `topic:: period:: region:: source-type:: project:: method::
  discipline:: lang::` (plus free-form un-prefixed tags). The term may be empty
  when filtering by tags alone. Examples:
  `--tag topic::migration --tag region::europe`;
  `"Bourdieu" --tag source-type::theory`.
- `--list-tags [PREFIX]` — print the library's facet tags (those with `::`),
  grouped by facet, and exit. Optionally pass a prefix to narrow to one facet,
  e.g. `--list-tags region::` or `--list-tags topic`. Use this to discover
  valid values before filtering. The canonical vocabulary lives in
  `~/.claude/skills/zotero-curator/tag_vocabulary.yaml`.
- `--limit N` — cap results (default 50).
- `--out FILE` — write the chosen format to a file (natural for `ris`,
  `endnote`, `bibtex`, `csljson`, or a Chicago bibliography) instead of stdout.
