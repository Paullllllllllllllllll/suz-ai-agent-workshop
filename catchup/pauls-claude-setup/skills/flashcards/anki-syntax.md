# Anki Syntax and Output Format (Canonical)

Single source of truth for Anki-importable deck syntax, shared by the
`flashcards` skill and the `flashcard-maker` agent. Edit THIS file when
the syntax or output format changes.

## MathJax Rules (Anki)

- All math must use TeX with these delimiters ONLY:
  - Inline: `\(...\)`
  - Display: `\[...\]`
- Do NOT use: `$...$`, `$$...$$`, `(...)`, `[...]`
- Keep each expression on single line (no literal newlines inside delimiters)

## Cloze Rules (Anki)

- Use exact Anki syntax: `{{c1::...}}`, `{{c2::...}}`, etc.
- Avoid `}}` inside TeX within cloze text
- If unavoidable, insert space before cloze close: `...{a}{b} }` before `}}`

## Code Rules (Anki)

- No markdown code fences (no ```)
- Multi-line code: wrap in `<pre><code>code here</code></pre>`
- Single-line code: plain text inline (no backticks)

## Output Format

Output must be a `.txt` file directly importable into Anki:

```
#separator:Semicolon
#html:true
#deck:[DeckCategory]::[DeckName]
#columns:Front;Back;Tags

[Front];[Back];[space-separated tags]
```

**Format rules**:

- Separator: Semicolon (`;`)
- Encoding: UTF-8. Write non-ASCII characters as they are (ä, ö, ü, ß, é);
  never transliterate them (no `ae`, `oe`, `ue`, `ss` substitutes)
- Quotation marks inside content: use the language's typographic quotes
  (German `„...“`, English `“...”`), not angle quotes (`» «`); they need no
  escaping
- Newlines in content: Replace with `<br>`
- Escaping: Wrap fields containing `;`, `"`, or `<br>` in double quotes; escape internal quotes as `""`
- File content: the header lines, one blank line, then card rows only; no
  trailing markup or text of any kind
- File naming: `[Topic]_[Subtopic].txt` (e.g., `Linear_Algebra_Eigendecomposition.txt`)

**Pre-delivery check** (required): Read the written file back and confirm
that every card row splits into exactly as many fields as `#columns`
declares. Any field that contains `;` or a straight `"` and is not wrapped
in double quotes is an import error; fix it before reporting the deck.

## Examples

### Example: Math Card

```
#separator:Semicolon
#html:true
#deck:Linear_Algebra::Properties
#columns:Front;Back;Tags

What property does a matrix have if \(\det(A)=0\)?;The matrix is singular and not invertible. \(A^{-1}\) does not exist.;Linear_Algebra Properties
```

### Example: Multi-Card File

```
#separator:Semicolon
#html:true
#deck:Statistics::Basics
#columns:Front;Back;Tags

What is the mean of a dataset?;The sum of all values divided by the number of values: \(\bar{x} = \frac{1}{n}\sum_{i=1}^{n}x_i\);Statistics Descriptive
What is standard deviation?;A measure of dispersion around the mean: \(\sigma = \sqrt{\frac{1}{N}\sum_{i=1}^{N}(x_i - \mu)^2}\);Statistics Descriptive
```
