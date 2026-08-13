# Extending the literature workflow to your Zotero library

The workshop editions run on bundled sample files so they work on any machine.
At home, you can run the same pattern (select, read, condense, register)
against a real Zotero library. The steps below describe the pattern
generically, so adapt the paths and identifiers to your own setup.

## Enable the local API

Zotero 7 ships a local HTTP API, off by default. Enable it under Settings >
Advanced > "Allow other applications on this computer to communicate with
Zotero". While Zotero is running, the API listens at
`http://localhost:23119` and serves your library over the same endpoint
schema as the Zotero web API — but locally, without an API key, and without
your library leaving the machine.

Clients that speak the web API can usually point at the local one. With
pyzotero, for example:

```python
from pyzotero import Zotero

zot = Zotero(0, "user", local=True)
items = zot.top(limit=25)
```

## Safety model

Treat the Zotero database as read-only for any agent, without exception:

- Reads go through the local API (pyzotero or plain HTTP). Searching, listing
  collections, exporting citations, and pulling attachment paths are all safe
  this way.
- Writes never touch the database directly, neither through the API nor by
  editing `zotero.sqlite` on disk. When a change is needed (fixing metadata,
  adding tags), have the agent generate a script that you review line by line
  and then run yourself in Zotero's own console (Tools > Developer > Run
  JavaScript). Zotero's internal API then performs the write inside the
  application, with its own transaction handling and undo trail.

The point of the split is auditability: the agent proposes, you inspect, the
application executes. A corrupted `zotero.sqlite` can cost you the library.

## Configuration

Any setup needs three pieces of local configuration:

- The library ID: `0` works for the local API's user library; group libraries
  need their numeric ID (visible in the URL on zotero.org).
- The data directory, where Zotero stores `zotero.sqlite` and the `storage/`
  folder with attachment PDFs (shown under Settings > Advanced > Files and
  Folders). Agents need this path to read attachment files directly once the
  API has resolved an item to its storage key.
- Zotero itself must be running: the local API is served by the desktop
  application, not a daemon.

Keep these in a project-level configuration file or environment variables, not
hard-coded in prompts, so the workflow moves between machines.

## Read-only versus write operations

Safely read-only via the local API:

- Full-text and metadata search across the library.
- Exporting citations and bibliographies in any supported style.
- Duplicate detection (compare titles, DOIs, and ISBNs across items).
- Listing items with missing fields (no DOI, no abstract, no attachment).

Writes, which belong in a reviewed script run inside Zotero:

- Adding or removing tags.
- Editing item metadata (correcting titles, completing author lists).
- Importing new items or attachments.
- Merging duplicates and moving items between collections.

## Two-line starter

```text
Ask your agent to: read my Zotero library via the local API and list items
missing DOIs — read-only, no changes to the library.
```
