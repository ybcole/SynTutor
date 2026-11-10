# XAI-5 — Error-to-tree localization and immutable revision-lineage acceptance

**Date:** 10 November 2026
**Language:** English only
**Implementation:** XAI-5 technical implementation, tested in CI and parser-backed browser flow
**Grammar authority:** zero independently approved runtime Cambridge diagnostic rules (unchanged from XAI-4)

## What was implemented

- server/xai5_repair.py: source-safe localization of actual XAI-4 token observations and (only when approved) verified findings to **existing** canonical B-R tree nodes, with no invented governor, subject, complement, head or adjunct function.
- Exact raw token and character spans; valid B-R tree spans mapped only when the **sentence text exactly matches** the original. Opaque triangles remain opaque and unresolved trees do not invent word-level nodes. Mappings carry XAI-2 proof atom IDs and are explicitly observational.
- Stable original finding IDs and dependency/issue groups inherited from the XAI-4 independently authorized partial evaluator, with a separate list of **unapproved candidate observations**, not diagnoses.
- A bounded immutable original (u0) and up to **four** learner-written revision versions (v1…v4), each optionally parented to the original or an earlier revision. Every version runs an actual new parser/canonicalizer invocation when available and reruns the **entire eligible XAI-4 check set**; parser failures remain explicitly unresolved.
- Source-original-to-revision token alignment and character offsets, plus step-local alignments for staged edits. Original sentence, original finding IDs and source text are never rewritten.
- Explicit per-finding lineage: satisfied after a verified narrow check, persists, no longer applicable after rewrite, ambiguous or blocked. Disappearance of applicability is **not** conflated with a confirmed satisfied constraint.
- New findings are locally classified as **introduced** only for a witnessed approved-rule SATISFIED→VIOLATED change at the same aligned governor with an edited target; as **unmasked** when the same observed rule/target survives a removed quotation context; and **unknown** otherwise. Source observation IDs identify both before/after witnesses. This is never a global grammaticality judgment.
- Both Flask and stdlib transports expose POST /api/repair-check with an allow-listed payload: text, up to four candidate texts with parent IDs, optional English variety and B-R chapter. Neither client source metadata nor forged approval flags are accepted. A status change is never treated as a whole-sentence correctness certificate.
- XAI-5 localization sidecar is shared by /api/parse, /api/explain and /api/evaluate. The shared Generator/Builder explanation view offers an accessible "Compare a revised sentence" editor that reparses a learner's candidate without mutating the original or claiming an automatic correction. When a completely revalidated revised canonical B-R tree is available, the panel renders the NEW tree and lets learners select its lexical/constituent nodes for new contextual evidence; otherwise it explicitly withholds the unavailable tree. It never reuses the original tree to illustrate a different sentence. No database migrations.
- grammar/xai5_localization.schema.json and grammar/xai5_repair.schema.json are strict output contracts.
- server/test_xai5_repair.py (26 tests) covers original/word/opaque node localization, missing trees, source-proof spans, tamper rejection, exact edits, multi-edit history, alternatives, source safety, and **test-only** approved fixtures for interacting modal and perfect-auxiliary conditions (one edit resolves one finding while another persists; a later edit changes the remaining check). All current English-only grammar rules in production retain 0 approvals.

## Why automatic verified corrections are withheld

The earlier XAI-PRE source audit explicitly identifies its selected 13 claims as assistant-inspected **but not independently human-adjudicated** and keeps every runtime Cambridge diagnostic rule disabled. XAI-5 does not fabricate a reviewer identity or turn assistant judgment into independent review. Therefore the runtime can reparse revisions and show observational differences, but it cannot legitimately assert that "had went" is a Cambridge-certified error nor recommend a correction as globally validated.

An isolated, local synthetic authorization **in tests only** exercises how the system would behave after actual review. It does **not** modify the production allow-list. A generated candidate never claims global grammaticality, semantic equivalence or a guaranteed repair. All sidecars retain explicit uncertainty and rule-coverage counts.

## Separate remaining release conditions

Independent linguistic validation, signed source/crosswalk/exception approval, English variety policies, blind false-positive assessment and a sufficiently broad suite covering agreement, pronoun selection and valency need to happen before enabling those families as production verified grammar diagnostics. A user has delegated implementation decisions to the assistant, but that does not retroactively create an independent human source review. The assistant can and does finish the safe technical milestone without requiring the user to review each artifact.

**Milestone interpretation:** the complete safe XAI-5 technical path is implemented and can be integrated; the full grammar-diagnostic accuracy/release gate cannot be represented as fulfilled until external evidence warrants it. The prior XAI-4 (0 approved rules) limitation is inherited transparently.
