# Cambridge Chapter 9 — extraction report

## Scope and approval
- Source: *The Cambridge Grammar of the English Language*, Chapter 9 "Negation", **§1.1 Tests for clause polarity**.
- Processed printed pp. **786–787**, local PDF pp. **2–3**, only the section text; the preceding chapter introduction and following §1.2 are excluded.
- Owner approved all required Chapter 9 items on 2026-11-05. **Independent second-pass AI review was not performed.**
- Protocol: `CAMBRIDGE_EXTRACTION_PROMPT.md` version 1.0.

## Integration
- One new approved constraint: **CLS-060** — obligatorily invert subject and finite auxiliary where a negative constituent occurs in the prenucleus.
- Three existing approved-rule refinements: **CLS-019** (not even as supplement), **CLS-020** (neither/nor/so; either/too; the limits of reversed-polarity tag diagnostics), **CLS-021** (four diagnostics of clause polarity).
- Added 6 concepts; 6 original test examples in the new rule; 8 cross-references.
- Reviewed same-polarity tags explicitly: the source allows positive-positive tags with distinct pragmatic force and negative-negative tags for some speakers. Inversion is not restricted to negatives (also triggered by connective so and prenuclear only).
- The source does **not** license a global ban on same-polarity tags or permit inference of negative polarity from inversion alone.
- No new domain or schema changes; no duplicate previously approved entries.

## Validation and source caveats
- New CLS-060 has 4 correct and 2 incorrect examples, each with source pp. 787 and two minimal pairs.
- Prior active records retained; check before commit: 127 total rules and 149 unique concept terms, zero duplicate IDs and unresolved internal rule references.
- No known conflicts or uncertain items arising from the supplied section.
- Burton-Roberts mapping remains **unverified** because that source material was unavailable.
- The separate second-pass AI review is still outstanding; this approval records the user's express instruction, not a claim of independent review.

## Coverage
- §1.1 fully processed. Both printed pages are physically partial: p. 786 follows introduction; p. 787 precedes §1.2.
- §1.2 and all later sections through §7.2 **not processed**. The stop boundary remains in effect.

**APPROVED: 9/§1.1 Tests for clause polarity.**
