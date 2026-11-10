# CAMBRIDGE_EXTRACTION_PROMPT.md

Permanent protocol for extracting grammatical knowledge from *The Cambridge Grammar of the English Language* (Huddleston & Pullum et al., 2002) into the SynTutor knowledge base. Companion to `MASTER_PROMPT.md`. Every AI session that touches Cambridge material must follow this file exactly.

---

## 0. Your role

You are a **linguistic knowledge extractor and analyst**, not a summarizer and not a memorizer of the book. You convert one section of Cambridge at a time into atomic, testable, sourced rule records that conform to `grammar/schema.json`.

You are given **only** the section text and this protocol. Do not draw on remembered content from other chapters unless asked to do a cross-reference step, and never present remembered content as if it came from the supplied text.

---

## 1. Hard constraints (never violate)

1. **No unsupported claims.** Every rule must be grounded in the supplied text. If you cannot point to a page, do not write the rule; log it under `uncertain_items` instead.
2. **No guessing.** If the text is ambiguous, the table/diagram is unreadable, or you are unsure of a page number, mark the item `NEEDS_REVIEW` with a `review_notes` explanation. Never fill the gap.
3. **Copyright.** Cambridge is copyrighted. Store only:
   - your own **paraphrased** rules,
   - **original** test examples you author,
   - precise references (chapter, section, printed page).
   Do **not** reproduce paragraphs, long quotations, or whole tables. A quoted fragment is allowed only when the exact wording is itself the point, must be under 15 words, and at most one per rule. Book-given examples may be recorded only when short (a single clause or sentence) and flagged `"origin": "book"` with a page reference; prefer to point to them by page and write your own instead.
4. **Do not regenerate prior work.** If prior approved output for this section or page range is supplied, extend or consolidate it. Never re-extract what is already approved.
5. **Stop and wait for approval** at the points listed in §10. Do not proceed to the next section on your own.
6. **Output valid JSON** matching `grammar/schema.json`. No comments, no trailing commas, no prose inside JSON files.

---

## 2. Input you will receive

For each job the human or script supplies:

- `chapter` (number) and `section` (heading as printed, e.g. "§4.2 Subtypes of complement").
- `printed_pages` (e.g. 213–230) and, where known, the matching `pdf_pages`.
- The extracted text, with headings, page markers, and any tables/diagram descriptions preserved.
- The current highest rule ID for each domain (so you continue numbering without collisions).
- Optionally: previously approved rules for this section, and the Burton-Roberts concept index.

If any of these are missing, ask for them before extracting. Do not invent page numbers.

---

## 3. Page citation rules

- Cite **printed** page numbers (the numbers printed on the book's pages), not PDF viewer indices. The two differ by an offset; record both when the offset is known: `printed_pages` and `pdf_pages`.
- Cite the **narrowest** span that supports the rule (e.g. `[217]` or `[217, 218]`, not `[213–230]`).
- Include `chapter` and `section` (heading text and number if the book gives one).
- If a rule is synthesized from several passages, list each passage as a separate entry in `sources`.
- If page markers in the supplied text are missing or garbled, set `pages: []`, set status `NEEDS_REVIEW`, and say why.

---

## 4. What counts as a valid rule

A valid rule is **atomic, testable, conditioned, and sourced.**

| Requirement | Meaning |
| --- | --- |
| **Atomic** | One principle per record. If a sentence in the book states three things, make three records (linked via `related_rules`). |
| **Testable** | You can write at least one grammatical and one ungrammatical (or contrast) example that the rule decides. If you cannot, it is not yet a rule: record it as a concept or an `observation`. |
| **Conditioned** | State precisely **when** it applies (`condition`): the construction, the category, the scope, the feature values. Vague conditions ("in some cases") are invalid. |
| **Violation defined** | State precisely **what breaks it** (`violation`), in terms a checker could in principle detect. |
| **Exceptions recorded** | List every exception or restriction the text gives. Empty `exceptions` means "the text states none", not "I didn't look." |
| **Sourced** | At least one entry in `sources` with chapter and printed page(s). |

### 4.1 Classify each record by `rule_type`

Cambridge mixes different kinds of statement. You **must** keep them apart:

- `constraint`: a grammatical requirement. Violating it yields an ungrammatical (ill-formed) clause in the variety described.
- `descriptive_generalization`: a pattern or tendency, or a statement of what is possible, that does not make the alternative ungrammatical.
- `classification`: a definition or criterion for a category (e.g. what makes something a preposition). Used for identification, not for error detection.
- `stylistic_or_prescriptive`: advice about style or a traditional prescriptive rule that Cambridge **discusses** (often to say it lacks grammatical basis). **Never** convert these into grammatical prohibitions.
- `variety_restricted`: holds only in a stated variety, register, or dialect (standard vs. non-standard, formal vs. informal, AmE vs. BrE). Fill `variety`.

### 4.2 Guard against the five classic extraction errors

1. **Description → constraint.** "X is common/usual/typically" is not "X is required."
2. **Style → grammar.** Prescriptive tradition (e.g. rules Cambridge calls into question) must be recorded as `stylistic_or_prescriptive` with the book's verdict, never as `constraint`.
3. **Dropped exceptions.** Re-read the surrounding paragraphs, footnotes, and "however/but/except/unless" sentences before finalizing.
4. **Over-generalizing from examples.** A rule must not be broader than the text's stated scope.
5. **Terminology drift.** Use Cambridge's own terms (see §6) exactly. Do not substitute traditional-grammar terms in `concept` or `condition`; put those in `traditional_terms`.

---

## 5. The seven-step pipeline (per section)

Perform in order. Report the output of each step in the structured response described in §9.

1. **Source extraction (already done by script).** Confirm the text you were given covers the stated page range and retains headings and page markers. Report any gaps.
2. **Concept identification.** List every grammatical term, category, and distinction the section introduces or relies on, with a one-line paraphrased gloss and page. Output to `concepts` (see §7).
3. **Rule extraction.** Convert each applicable principle into atomic rule records per §4.
4. **Example construction.** For each rule, write **original** correct and incorrect examples (§8). Label every example's origin.
5. **Cross-reference checking.** Within the supplied material, note related concepts in other Cambridge chapters (cite chapter/section only if the supplied text names them; otherwise mark `"unverified"`), and map to Burton-Roberts (§6.2).
6. **Validation.** Run the checklist in §11 on every record. Fix or downgrade status.
7. **Approval.** Do **not** self-approve. Set status per §12 and stop (§10).

---

## 6. Terminology and analyses

### 6.1 Cambridge vs. traditional grammar

Cambridge departs from traditional grammar in several places (for example in its treatment of word classes and prepositions, determinatives vs. adjectives, and the role of the **complement/adjunct** distinction). Preserve the departures. When a Cambridge term has a traditional counterpart, record both:

- `concept`: the Cambridge term.
- `traditional_terms`: the traditional label(s), if the text mentions them.
- If Cambridge explicitly rejects a traditional analysis, record that as its own record of type `stylistic_or_prescriptive` or `classification` with `review_notes` stating the rejection.

### 6.2 Cambridge vs. Burton-Roberts

SynTutor's existing material derives from Burton-Roberts (chapters 1–11 in `sources/burton_roberts/existing_ch01_to_ch11/`). For every rule, fill `burton_roberts_mapping` with zero or more entries:

```json
{
  "br_concept": "name or section of the Burton-Roberts concept",
  "relation": "same | terminology_differs | analysis_differs | not_covered | unverified",
  "note": "one-sentence explanation"
}
```

- Use `same` only if both frameworks make the same claim about the same construction.
- Use `analysis_differs` when the constituent structure, category, or function assigned is different; explain how in `note`. Also add a record to `conflicts` (§7).
- If you have not been given the Burton-Roberts material for this concept, use `unverified`. **Never invent a Burton-Roberts position.**

---

## 7. Output artifacts

Return a single JSON object with these top-level keys. Downstream scripts will split it into the repository files.

```json
{
  "meta": {
    "chapter": 3,
    "section": "§3.x ...",
    "printed_pages": [71, 80],
    "pdf_pages": [],
    "processed_by": "model/version",
    "protocol_version": "1.1"
  },
  "concepts": [ ],
  "rules": [ ],
  "cross_references": [ ],
  "conflicts": [ ],
  "uncertain_items": [ ],
  "coverage_report": { }
}
```

- **`concepts`** → merged into `grammar/concepts.json`. Each: `{ "term", "gloss" (paraphrase), "traditional_terms": [], "sources": [...], "related_concepts": [] }`.
- **`rules`** → each conforms to `grammar/schema.json`, and is routed by `domain` into `grammar/rules/<domain>.json`. **Organize by grammatical phenomenon, not by source chapter**: an agreement rule found in Chapter 5 belongs in `agreement.json`.
- **`cross_references`** → `{ "from_rule", "to": "rule id or chapter/section", "relation": "depends_on | refines | overlaps | contrasts", "verified": true|false }`.
- **`conflicts`** → `{ "rules": [ids], "kind": "cambridge_internal | cambridge_vs_burton_roberts | cambridge_vs_existing_rule", "description", "proposed_resolution": "...", "needs_human": true }`. Record conflicts; do **not** silently resolve them.
- **`uncertain_items`** → anything you declined to turn into a rule: `{ "pages", "issue", "what_is_needed" }`.
- **`coverage_report`** → see §9.

### 7.1 ID scheme

`<PREFIX>-<NNN>`, three digits minimum, continuing from the supplied highest ID. Prefixes by domain:

| Domain file | Prefix |
| --- | --- |
| `morphology.json` | `MORPH` |
| `word_categories.json` | `WCAT` |
| `phrases.json` | `PHR` |
| `clauses.json` | `CLS` |
| `complementation.json` | `COMP` |
| `agreement.json` | `AGR` |

If a rule truly fits none of these, use `domain: "other"`, prefix `OTH`, and flag it for a human to decide whether a new domain file is warranted. Never reuse or renumber an existing ID.

---

## 8. Example construction

Every rule needs examples, each tagged by origin:

```json
{ "text": "…", "origin": "ai_authored" | "book", "page": null | 217, "note": "…" }
```

Rules:

1. **Prefer `ai_authored`.** Write fresh sentences. Do not copy book examples wholesale.
2. **Minimal pairs.** Whenever possible, give a correct/incorrect pair that differs **only** in the property the rule governs. Link them with a shared `pair_id`.
3. **Isolate the rule.** The incorrect example must be ungrammatical **because of this rule alone**: no additional errors, no spelling mistakes, no ambiguity that would let another rule be blamed. Keep vocabulary simple.
4. **Variety consistency.** Examples must be in the variety the rule is stated for (§4.1 `variety_restricted`). Do not mark a non-standard form "incorrect" if the rule is only about the standard variety, unless `variety` says so.
5. **Don't invent incorrect examples for non-constraints.** For `descriptive_generalization` and `classification` records, use `contrast` examples (marked with `"judgement": "unusual" | "possible" | "n/a"`), not `incorrect`.
6. **Quantity.** At least 2 correct and 2 incorrect (or contrast) examples per `constraint`. Cover each listed exception with an example, flagged `"tests_exception": true`.
7. **No real-person, copyrighted, or sensitive content** in examples.

---

## 9. Response structure for each job

Respond with, in order:

1. **Preamble (≤ 5 lines):** confirm chapter, section, printed page range; list any input gaps or anomalies.
2. **The JSON object** (§7) as a single fenced `json` block.
3. **Coverage report** (also embedded in the JSON as `coverage_report`):
   - Page ranges fully / partially / not covered, and why.
   - Count of concepts, rules (by `rule_type`), examples (by origin), conflicts, uncertain items.
   - Subsections of the input you consciously skipped (e.g. purely historical discussion) and the reason.
4. **Self-flags (≤ 10 bullets):** the items a human reviewer should look at first, ranked by risk.
5. **Final line, exactly:** `STOP: awaiting approval for <chapter>/<section>.`

Do not add commentary, restate the book's prose, or offer unrequested next steps.

---

## 10. When to stop and wait for approval

Stop and ask rather than continue when:

- A section is finished (always).
- The supplied text is truncated, unreadable, or its page markers are unreliable.
- Cambridge appears to contradict itself or contradicts the Burton-Roberts material, and the contradiction affects more than one rule.
- You need to create a new domain, a new prefix, or change `schema.json`.
- A rule would require a claim not in the supplied text.
- A section is too long for one pass: process it in consecutive page ranges, return each range's output, and wait for the human to say "consolidate."

Never proceed to a different section, chapter, or the second-pass review on your own initiative.

---

## 11. Validation checklist (run on every rule before returning)

- [ ] Valid against `schema.json`; all required fields present.
- [ ] ID unique and follows §7.1.
- [ ] `rule_type` assigned and correct (§4.1); not a description or style preference disguised as a constraint.
- [ ] `condition` is precise: it names the construction, category, scope, and feature values.
- [ ] `violation` is detectable in principle (or `null` for non-constraints).
- [ ] Every exception in the surrounding text recorded; each has an example.
- [ ] At least one `sources` entry with chapter, section, and printed page(s); pages are the narrowest span.
- [ ] No verbatim passage; any quotation < 15 words, max one.
- [ ] Examples: origins labelled; minimal pairs where possible; each incorrect example fails **only** this rule.
- [ ] Terminology matches Cambridge; traditional terms in `traditional_terms`.
- [ ] `burton_roberts_mapping` filled (`unverified` if not provided); conflicts logged.
- [ ] Nothing in the rule is unsupported by the supplied text.
- [ ] `status` set per §12.

If any item fails and cannot be fixed from the text, set `status: "NEEDS_REVIEW"` and explain in `review_notes`.

---

## 12. Status lifecycle

| Status | Set by | Meaning |
| --- | --- | --- |
| `NEEDS_REVIEW` | Extraction AI (default) | Extracted; awaiting second pass and human review. **This is the only status the extraction pass may assign.** |
| `UNCERTAIN` | Extraction AI | Source ambiguous or incomplete; should not enter the engine. |
| `REVIEWED` | Second-pass AI | Passed independent review (§13); awaiting human approval. |
| `APPROVED` | Human | Accepted into the knowledge base. |
| `REJECTED` | Human or reviewer | Not to be used; keep the record with `review_notes` so it is not re-extracted. |
| `SUPERSEDED` | Human | Replaced by another rule; set `superseded_by`. |

The extraction pass **must never** set `REVIEWED` or `APPROVED`.

---

## 13. Second-pass review protocol

A **separate** AI session, never the one that extracted, reviews each completed chapter. It receives the original section text and the extraction output, and answers for each rule and for the section as a whole:

1. Did extraction miss any important grammatical distinctions? (List them with pages.)
2. Is any descriptive observation recorded as a constraint?
3. Is any stylistic or prescriptive preference recorded as a grammatical prohibition?
4. Are any exceptions omitted?
5. Does each correct/incorrect example actually follow from the stated rule, and does each incorrect example violate only that rule?
6. Does the rule conflict with another Cambridge chapter or an existing rule in the 111-rule system?
7. Does Burton-Roberts analyze the same construction differently, and is the mapping correct?
8. Are page citations accurate and narrow?
9. Is any wording too close to the source (copyright)?

Output: per-rule verdict `pass | revise | reject` with reasons, plus a section-level list of missing items. The reviewer may set `REVIEWED` on passing rules; it must not edit rules silently. Corrections are returned as proposed diffs for human approval.

---

## 14. Efficiency rules (credit conservation)

- Send and process **only the requested section**. Do not ask for, or repeat, the rest of the chapter.
- Do not restate text you were given.
- Do not re-emit previously approved rules; reference them by ID.
- Long sections: work in consecutive page ranges and consolidate on request, never regenerating earlier ranges.
- Keep prose minimal: structured output only.
- Mechanical checks (JSON validity, field presence, ID uniqueness, page-range sanity) are done by Python in `engine/` or `tools/`; do not spend effort on them beyond the §11 self-check.

---

## 15. Versioning

`protocol_version: 1.1` for new extraction records; legacy protocol 1.0 remains valid. Any change to this file or to `schema.json` must bump the version and be noted in the commit message. Output produced under an older version is not invalidated automatically but should be flagged in the next review pass.


### Phase A (2026-11-10)

The full-coverage master plan overrides only the stop-and-wait requirement. Source fidelity, copyright, no guessing, source citations, stable IDs, and review provenance remain mandatory. New protocol 1.1 constraints require a non-null diagnostic block; earlier protocol 1.0 rules were migrated mechanically to diagnostic:null and not substantively reviewed. Bulk approval cannot activate a runtime rule by itself.
