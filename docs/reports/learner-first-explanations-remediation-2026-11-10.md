# Learner-first grammar explanations remediation — 10 November 2026

**Purpose:** Remove the evidence/debugging wall from the explanation pane, and give learners one context-specific grammar paragraph when they choose a word, constituent, or verified feature. This work takes priority over XAI-8 at the user's request.

## Original user-facing defect

Clicking a word such as “are” could display a technical B-R analysis header, a redundant word-span description, book chapter/page references, raw tree-position observations, “not a grammaticality judgment”, detailed fact atoms, disabled AI/model status, Cambridge candidate rule count, a correction form and “No reviewed book evidence” boilerplate. None of these told the learner what the word actually does in the sentence.

## Implemented correction

- New server/learner_explanations.py composes one bounded English paragraph from existing validated fact-graph tree positions, original overt words, phrase labels and token order. Familiar word/phrase types and clear local constructions are explained in plain English. “Are” as a form of “be” followed by “inspecting” describes an action in progress rather than just a leaf span.
- New grammar/learner_explanation.schema.json is a strict response contract; no new source IDs, full-sentence grammar certification or unlicensed error verdict may be inserted. All original XAI-2–7 evidence stays in the server response for source/safety tests, not in the normal teaching UI.
- Shared renderEvidence displays one paragraph only; source-review machinery, diagnostics, fact IDs, book pages, model-status comments, Cambridge blocked rule counts and repair forms are removed from the normal learning view. Quiz feedback displays a concise, previously reviewed answer rationale where available.
- Generator removes the duplicate B-R heading, raw canonicalObservation text and source-page notes; sentence analysis initially shows a plain-English summary, and selecting a node replaces it with the relevant explanation.
- Lessons, Quizzes and revised-tree previews use the same single-paragraph renderer. Verified tense/valency feature selections explain the feature in plain English. Keyboard selection, exact B-R tree geometry, focus highlighting and zoom remain available.
- The legacy suggestion UI avoids unverified claims of “Verified correction” and does not advertise internal book-review statuses.
- The older optional XAI-6 model pipeline remains disabled, and 0 unapproved Cambridge error checks are enabled. XAI-5 revision recheck API and original finding-lineage gates remain accessible in the backend, rather than being embedded in every clicked-word explanation.

## Validation requirements

- Python tests on actual lesson/source trees, sentence words, noun/verb/adjective phrases, progressive auxiliary “is” and test-only “are”, uncertain structures, source review forgery, and Generator/Builder contract parity.
- Model-free JavaScript DOM test proving exactly one plain text paragraph, no source citations or injected HTML, and grounded feature explanations.
- Real parser-backed Chromium tests for Generator, Builder, Lessons, Quizzes, clicked word changes, responsive layout and correction recheck backend.
- Offline all-tree coverage/length audit. This is not a human grammaticality or teaching-effectiveness study.

## Explicit limits

When the selected tree does not justify a particular formal role, prose remains conservative. No human review or rule activation is invented; full independent linguistic evaluation and XAI-8 release hardening remain separate future work. The books continue as internal linguistic reference and provenance, not intrusive learner-facing citations.
