---
name: unslop
description: Cut AI tells and mannered prose from any draft — chat replies, papers, documentation, comments.
disable-model-invocation: true
argument-hint: "(no arguments; run on the draft in context)"
---

# Unslop

Edit text to remove AI patterns and mannered prose.

## Process

1. Scan for the patterns below.
2. Rewrite. Preserve meaning, match intended tone.
3. Self-audit twice: "What makes this obviously AI generated?" and "Where
   is this performing instead of saying?" Fix remaining tells.

## Patterns to detect and fix

Rule numbers are stable ids that other skills cite. A removed rule leaves a gap.

### Content

1. **Superficial -ing phrases.** "highlighting...", "ensuring...", "reflecting...", "showcasing...", "fostering...". Delete or expand with real sources.
2. **Vague attributions.** "Experts believe", "Industry reports suggest", "Some critics argue". Name the source or delete.

### Language

1. **AI vocabulary.** Additionally, crucial, delve, enduring, enhance, fostering, garner, interplay, intricate, landscape (abstract), pivotal, showcase, tapestry (abstract), testament, underscore, vibrant. Replace with plain words.
2. **Fancy ways to say "is".** "serves as", "stands as", "boasts", "features". Just say "is" or "has".
3. **"Not just X, but Y."** State the point directly instead.
4. **Rule of three.** Forcing ideas into groups of three. Use the natural number.
5. **Synonym cycling.** Protagonist, main character, central figure, hero all in one paragraph. Pick one, repeat it.
6. **False ranges.** "from X to Y" where X and Y aren't on a meaningful scale. List topics directly.

### Style

1. **Em dash overuse.** Em dashes are permitted but sparing: roughly one per 200 words, and never two in the same paragraph. Past that budget, or where the dash is doing a comma's job, rewrite with a comma or end the sentence. Do not substitute en dashes or hyphen-as-dash. Keep the budget; it
    applies in place of a stricter "no em dashes" rule.
2. **Colon overuse.** Colons are fine before a list or example. Not as mid-sentence connectors. "If you're coming from traditional automation: instead of registering event handlers, you describe conditions" adds nothing with the colon. Rewrite to let the point stand on its own without comparison framing. "Describing when the scheduler should fire works best as plain English." Same meaning, no crutch punctuation.
3. **Boldface overuse.** Don't bold every proper noun or acronym.
4. **Inline-header lists.** The tell is a bold label and colon that restates the line: "**Performance:** Performance improved...". Convert those to prose. A bold lead-in that ends in a period, names the item, and is followed by genuinely new detail ("**Schema in TypeScript.** Tables live in one file.") is fine, not a tell.
5. **Title case headings.** Use sentence case.
6. **Decorative emojis.** Remove from headings and bullets.
7. **Curly quotes.** Replace with straight quotes.

### Communication artifacts

1. **Chatbot phrases.** "I hope this helps!", "Let me know if...", "Of course!", "Certainly!", "Found the smoking gun!" Remove.
2. **Sycophantic tone.** "Great question! You're absolutely right!" Respond directly.

### Filler

1. **Filler phrases.** "In order to" becomes "To". "Due to the fact that" becomes "Because". "It is important to note that" gets deleted.
2. **Excessive hedging.** "could potentially possibly be argued that it might" becomes "may".
3. **Generic conclusions.** "The future looks bright." State specific plans or facts.

### Jargon

1. **Abstract metaphor nouns.** Substrate, wedge, vector, locus, vantage, nexus, primitive (as noun), harness (as metaphor), surface (as in "API surface"), bedrock, scaffolding (as metaphor), modality, paradigm, gold-plating, ratchet (as metaphor), evacuate (for moving code), endgame, north star, flywheel. These read as technical but usually have a plainer concrete word. "Substrate" becomes "base". "Wedge in" becomes "add". "Vector" becomes "way" or "method". "Gold-plating" becomes "more than the job needs". "Ratchet" becomes the mechanism's real name or "a limit that only tightens". "Evacuate" becomes "move out". "Endgame" becomes "the last phase". Pick the concrete word.

### Plain speech

1. **Say what it does, not how it feels.** "the database stays close at hand", "SQL you can read", "types that follow your schema" name a feeling. The fix names the mechanism or a number: "`.toSQL()` returns the exact string sent to the database", "a column rename fails the build". Ask what the sentence tells the reader to do or know, then write that. If you can't restate it as a concrete instruction, fact, or number, cut it. One more check: if the sentence could appear unchanged in another project's docs, it says nothing about this one. Cut it.
2. **Shorten or split dense sentences.** If the reader has to backtrack to parse a sentence, break it in two or drop clauses. One idea per sentence.
3. **Active voice.** Prefer it. Catch "is/are/was/were + past participle" and name the actor: "queries are validated" becomes "the compiler validates queries", "the file is parsed by the loader" becomes "the loader parses the file". Passive is fine only when the actor is unknown or genuinely doesn't matter.
4. **Cut adverbs, or use a stronger verb.** "runs quickly" becomes "is fast" or the number. "significantly improves" becomes the measured delta. An adverb propping up a weak verb means the verb is wrong.
5. **Prefer the plain word.** "utilize" becomes "use", "leverage" becomes "use", "facilitate" becomes "help", "numerous" becomes "many", "in the event that" becomes "if". The fancier synonym is rarely clearer.
6. **Mannered prose.** The central rule; rules 26, 27, 30, and 31 are its special cases. Mannered prose substitutes metaphor and flourish for direct statement. Instead of "a parameter worth varying", the mannered writer produces "a dial worth turning"; instead of "this point still matters", "this point earns its keep". The phrases exist to display the writer, not to convey the idea, and readers can tell. That is why mannered prose irritates: it makes the reader work harder so the writer can perform. It is also imprecise, because metaphors drag in connotations the writer did not choose and cannot control. The fix is to say what you mean; when a literal phrase is available, use it. Catch the full range, not only the stock examples: aphorisms ("wire it or delete it"), rhetorical fragments for effect, personified code or documents ("the plan holds it", "the paper argues"), figurative verbs ("rides along", "stands on", "sits atop"), abstract nouns as sentence subjects where a person or thing is available, and stock framing phrases ("the question is not X but Y", "what makes this work is").
7. **Over-compression.** Dropped articles, verbless fragments, symbol-speak, and abbreviations that make the reader decode instead of read. "Parser rejects bad date → exit 2, no write" becomes "The parser rejects a bad date, exits with code 2, and writes nothing." Write whole sentences with their articles and verbs, and spell out arrows and abbreviations.
