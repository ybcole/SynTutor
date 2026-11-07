# Master Prompt — Syntax Generator

## Role
Act as the senior NLP/parser and computational syntax engineer for SynTutor. Implement the new Syntax Generator only after the canonical B-R tree contract and framework crosswalk have been approved.

## Objective
Produce a source-grounded B-R-compatible syntax analysis from user input, evaluate applicable reviewed Cambridge rules, and return explainable evidence. Benepar may remain the initial candidate constituency parser, but its output is not the final tree standard.

## Repository context
Inspect `server/parse_engine.py`, `server/api.py`, `server/matrix.py`, `server/ruleset.py`, `server/detector.py`, `server/corrector.py`, `CONVENTIONS.md`, B-R chapter JSONs/validators, and `grammar/schema.json`/`grammar/rules/` before changing code.

## Requirements

1. Preserve the raw Benepar parse and metadata for diagnostics.
2. Add a B-R normalizer that maps/restructures only where the transformation is supported by source conventions and gold fixtures.
3. Represent B-R labels, features, triangles, gaps, indices, elided elements, token spans, convention versions, and accepted alternatives.
4. Keep movement arrows/lines separate when the book says they are not part of the phrase marker.
5. Enforce chapter-specific convention profiles in chapter exercises; use the declared final profile for free-form analysis.
6. Validate the resulting tree against schema, token order, word coverage, hierarchy, feature legality, and convention version.
7. Return unresolved/ambiguous analysis where the adapter cannot safely decide. Never silently force a Penn-style tree into a false B-R analysis.
8. Evaluate only runtime-enabled Cambridge rules. Extraction approval alone does not enable a constraint.
9. Distinguish `constraint`, `variety_restricted`, `descriptive_generalization`, `classification`, and `stylistic_or_prescriptive` behavior.
10. Return one reusable analysis payload for Syntax Generator, Syntax Builder, Lessons, and Quizzes.
11. Treat CoLA/other acceptability models as secondary signals, never as authorities that invent explanations.

## Corrected sentence visualization data

Return a structured edit/annotation object containing original text, corrected text, original/corrected token alignment, edit spans, and affected terminal IDs. Support replacements, insertions, deletions, and multi-token edits. The corrected tree must contain corrected words only; the renderer will show the original form struck through and the corrected form underneath/adjacent.

## Testing requirements

- Run existing B-R chapter validators.
- Add normalizer tests for every supported transformation.
- Compare outputs against B-R gold trees and accepted alternatives.
- Test token alignment, punctuation, contractions, multi-sentence input, gaps, triangles, indices, and non-finite forms.
- Test each implemented Cambridge rule against positive, negative, and exception examples.
- Add regression tests for legacy valid/invalid corpora.
- Test failure/fallback behavior for missing models and unresolved analyses.

## Deliverables

1. Updated architecture/API contract.
2. Canonical B-R tree schema and normalizer.
3. Structural validator.
4. Runtime rule registry integration.
5. Corrected sentence alignment output.
6. Automated test suite and actual test output.
7. File/change report and unresolved limitations.

## Stop condition
Do not migrate all lessons, rewrite the Builder, redesign the UI, or remove Benepar in this workstream. Stop when the Generator meets agreed gold/normalization/regression gates and the owner reviews the result.
