# Try-out: quantitative analysis

A self-contained 60-90 minute task for the quant track, built for
participants who brought no material of their own. It runs the same way
in Claude Code (CLI) and the Claude Desktop app.

The material is the synthetic dataset from the afternoon demo block,
together with the codebook it was generated from and the generator
itself. All of it is in `synthetic-dataset/`.

## Start here

Paste the following to begin:

```text
Read synthetic-dataset/CODEBOOK.md, then write an analysis script that loads
synthetic-dataset/mobility_2026.csv and estimates occupational status from
education and social origin. Save the table it produces to results/. Then add a
robustness check of your own choosing, and write a short README saying what the
script does, what it assumes, and how to re-run it.
```

Then keep going: make it reproducible. Fix the seed, pin the inputs,
have the script fail loudly if a column it expects is missing, and make
the whole thing run end to end from one command.

## Material

`synthetic-dataset/` holds four files:

| File | What it is |
|------|-----------|
| `CODEBOOK.md` | The specification the data was generated from — sample, variables, target marginals, the generating process, missingness, and the validation the generator has to pass |
| `generate_mobility.py` | The generator, written against that codebook |
| `mobility_2026.csv` | Its output: 2,400 rows |
| `README.md` | How to run the generator yourself |

The dataset is **synthetic**. It is a good way to check that your
recodes fire, your analysis runs, and your pipeline holds together. It
is not evidence about people, and no result from it is a finding.

## If you would rather build than analyse

Generate your own. `CODEBOOK.md` is a worked example of specifying a
data-generating process before writing any code — the point being
`codebook -> generator -> data`, never `rows -> data`. Write a codebook
for something in your own field, have an agent implement it, and make it
check its own output the way `generate_mobility.py` does.

That is the more useful hour of the two, if you have the appetite for it.
