# Try-outs

Starter packages for the afternoon hands-on tracks. Each folder is
self-contained; open its README and paste the starter prompt.

| Track | Folder | Material |
|---|---|---|
| Literature | `literature/` | Five open-access papers on Swiss rental housing (in `walkthrough/`) |
| Quant | `quant/` | Option A: synthetic mobility dataset from a codebook (Nico); option B: messy analysis script on a real historical panel (`historical-panel/`) |
| Pipelines | `pipelines/` | Four unharmonized historical panels to merge into one |

## Data removal after the workshop

The CSV files under `quant/historical-panel/data/` and
`pipelines/inputs/` are working files from Paul Götz's research data
bank, shared for the workshop day only. They are not public-domain releases and must be deleted from the
repository after the workshop. To do so:

```bash
git rm tryouts/quant/historical-panel/data/*.csv tryouts/pipelines/inputs/*.csv
git commit -m "Remove workshop-day datasets from try-outs"
```

Then update `quant/historical-panel/README.md` and
`pipelines/README.md` to state that participants must supply the files
themselves or contact the author.
Note that the files remain in the git history; rewriting history is a
separate decision.
