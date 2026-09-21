---
name: flashcards
description: Create Anki flashcards, cloze cards, study materials from any source.
disable-model-invocation: false
argument-hint: "<source-material-or-topic>"
---

# Anki Flashcard Creator

Create well-designed Anki flashcards following best practices for spaced repetition learning. Output files are directly importable into Anki.

## Phase 1: Content Analysis

### 1. Gather Source Material

- If the user provides insufficient detail, ask for clarification on scope, depth, or specific topics
- Determine number of cards requested by user (aim for 20-30 per file for manageable sets)
- Identify key concepts, formulas, and relationships from the source

### 2. Assess Complexity

- Determine if topic requires splitting into multiple cards
- Identify dependencies between concepts
- Plan card sequence for optimal learning
- Group related cards for interleaving practice within sets

## Phase 2: Card Design Principles

### 1. Evidence-Based Learning Principles

- **Retrieval practice**: Cards should test active recall, not recognition
- **Elaborative interrogation**: Use "how" and "why" questions to link new information with existing knowledge
- **Minimal information**: One specific concept per card; split complex topics
- **Learn first, memorize second**: Cards supplement understanding, not replace it

### 2. High-Quality Card Criteria

- **Specific questions**: Clear, focused, unambiguous queries
- **Specific answers**: Concise, precise responses (avoid paragraphs)
- **Avoid leech traps**: Poorly designed cards are hard to remember; prioritize clarity
- **Add redundancy for critical concepts**: Ask the same information from different angles

### 3. Card Types

- **Basic cards (Q&A)**: Preferred format for most content
- **Cloze deletions**: Use sparingly (max 1-3 per card), only when fill-in-the-blank is natural

### 4. Organization

- Use **tags** for filtering and targeted review (e.g., before exams)
- Tags use underscores for multi-word concepts (e.g., `Linear_Algebra`)
- Group cards by retrieval context, not by chapter

## Phase 3: Syntax, Output Format, and Examples

Read `anki-syntax.md` in this skill folder and follow it exactly: MathJax delimiters, cloze syntax, code formatting, the
importable `.txt` header/field format, escaping rules, file naming, and
worked examples. It is the single source of truth shared with the
`flashcard-maker` agent.

## Constraints

- Output files must be directly importable into Anki
- Follow MathJax, cloze, and code syntax rules exactly
- Keep cards focused on single concepts with specific questions and answers
- Use tags for organization; avoid creating many small subdecks
- Ask for clarification rather than guessing on content
