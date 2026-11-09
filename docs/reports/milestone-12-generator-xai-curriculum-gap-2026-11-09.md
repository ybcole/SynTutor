# SynTutor M12 — Generator notation, XAI, and Cambridge curriculum gap audit

**Review:** 9 November 2026. **Status:** Changes proposed in [draft PR #43](https://github.com/ybcole/SynTutor/pull/43); not a claim of full Burton-Roberts conversion, production deployment, human source approval, or milestone acceptance.

## 1. Why Grammar and Analysis publishes one lesson

The live course JSON (`web/content/lessons/course.json`) has **11** `foundations` lessons and **one** `grammar` lesson, `cgel-clauses` ("Sentences and embedded clauses"), with reviewed Cambridge printed-page sources 44–45. Its `planned_modules` includes **17** additional topics (verb forms through punctuation), all recorded as `planned`, not published or independently reviewed. The catalog deliberately filters published lessons by track and displays the 17 other topics only as placeholders.

This is **incomplete curriculum coverage**, not a missing UI button or a bug in filtering. Source extraction and page inventory do not establish a reviewed lesson's factual scope, original examples, accepted alternatives, answer rationales, or assessment validity. New published modules must be authored, page-checked, given reviewed content status, added to schema/catalog migrations where relevant, and regression-tested before they can award trusted progress or XP.

**M12 UX improvement:** the Grammar and Analysis tab now explains explicitly why only one lesson is available and why 17 are pending. The advanced-Cambridge checklist item stays unchecked.

## 2. Why the Syntax Generator did not display B-R notation

`server/api.py::build_payload` returns two different tree authorities:
- `tree` / `candidate_tree`: raw spaCy + Benepar constituency graph using Penn-style categories. This is **diagnostic**, and its legacy matrix verdict is **not book-verified**.
- `br_analysis.tree`: the canonical Burton-Roberts envelope, produced *only* if an exact verified chapter-example source tree matches the lexical yield and selected convention, or if the narrow, reviewed Chapter V2 `S → NP VP` adapter succeeds. Anything else is `unresolved`.

`web/js/main.js` used to call `renderer.setTree(payload.tree)` even when `br_analysis.status == 'normalized'`. Its notice told the learner a B-R tree existed but did not display it.

**M12 functional changes:**
- Added a primary canonical tree surface (`#canonicalTreeView`) that uses the existing lesson B-R SVG tree renderer when the envelope is normalized and its schema validated. B-R labels, features, empty nodes, indexed gaps and unanalyzed triangles are taken from the approved envelope, not relabelled Penn nodes.
- The older canvas remains an **explicitly labelled Benepar diagnostic fallback** when no authorized canonical conversion exists. It is never titled a Burton-Roberts tree.
- Added an *explicit* "Try limited B-R Chapter 2 analysis" option, which sends `chapter=2` to the backend; the user can switch back to default `FINAL-D1`. This is a basic skeleton and does not assert full coverage.
- Keyboard-focusable canonical SVG nodes have inspectable structural facts, with chapter-aware reviewed evidence requested from the existing `/api/explain` endpoint.

**Remaining limitation:** Arbitrary free input defaults to `FINAL-D1`, for which the general Benepar-to-B-R adapter is **not approved**; many sentences remain unresolved. Full conversion requires source-checked, construction-specific rules for lexical category, features, auxiliary VP layers, DET/NOM, gaps, control, and other conventions, with aligned parser tokens and canonical regression tests. Do not solve this by renaming Penn tags or inventing a source tree.

## 3. Why XAI appeared absent

`grammar/explanation_templates.json` currently contains only **two** reviewed templates: one Cambridge sentence/clause teaching classification and one B-R Chapter 2 `S → NP VP` structural explanation. `server/explanations.py` refuses to publish non-reviewed/unsupported explanations; when the canonical tree is missing it emits `ANALYSIS_UNRESOLVED`, otherwise a non-matching template yields `NO_BOOK_BASIS`.

In addition, `web/js/ui.js` suppressed legacy rule-matrix prose when reviewed evidence existed, and `renderCorrection` could erase the book evidence displayed earlier in `setTreeAuthorityNotice`. Selecting a node could therefore leave little meaningful explanatory content.

**M12 functional changes:**
- Restore the separately labelled reviewed-evidence block after the diagnostic correction panel redraws the inspector.
- Make canonical SVG nodes interactive by click/Enter/Space; display a deterministic observation of the actual B-R node, direct branches, triangle content, token yield and approved-tree source metadata. Fetch and render the specific node's reviewed explanation where supported.
- For raw Benepar nodes, show **diagnostic structural facts and fired legacy rule IDs only**, clearly separated from reviewed book claims; continue to block fabricated or unreviewed explanations.
- Added model-free pure-shape tests and a real-parser browser test that exercises canonical display, keyboard selection, evidence rendering, and opt-in Chapter 2 requests.

**Remaining limitation:** A structural observation of a parse is XAI about *what the system represented*, not a complete book-supported explanation of *why every grammatical rule holds or fails*. The remaining reviewed templates and Cambridge constraint implementations require actual source-by-source validation. The one B-R and one Cambridge template cannot support comprehensive grammatical feedback.

## 4. Acceptance and outstanding master checklist

The master checklist on the M12 draft branch has **140 / 150** actionable boxes checked before this gap audit. **Do not check the remaining ten simply because code exists.** Outstanding evidence requirements:

1. Approve the actual migration and rollback strategy before touching live learner data.
2. Complete independently reviewed advanced Cambridge modules (17 planned).
3. Approve the brand, design tokens, tone and icon language.
4. Conduct usability tests with learners outside the implementation group.
5. Review integrated rollout using *real* Clerk sessions and a Supabase staging database.
6. Complete privacy/security sign-off for XP and leaderboards in the intended hosted environment.
7. Verify upstream/shared rate limiting, worker timeouts and backend failure policy in the real deployment.
8. Implement and validate release feature flags and staged rollout in staging.
9. Obtain explicit rollback approval and record recovery drill results.
10. Publish coverage limits and known ambiguities to learners in the **actual released version**.

The last item is addressed in the draft application's static Generator and course UI, but **not yet published** to the live site because PR #43 is unmerged. It therefore remains unchecked.

## 5. Validation requirements

- [ ] Latest PR #43 model-free CI passes, including `scripts/test_canonical_view.js` and `scripts/test_account_journey_browser.py`.
- [ ] Latest PR #43 parser-backed CI passes, including `scripts/test_explanation_browser.py` (both real and reviewed-fixture runs).
- [ ] Human tester inspects a B-R V2 Chapter 2 example with accurate NP and VP triangles and uses keyboard-only inspection.
- [ ] Human tester submits an unsupported construction and confirms the UI labels it unresolved instead of presenting an invented B-R parse.
- [ ] Author/reviewer checks new Cambridge lesson content against printed pages and approves before publication.
- [ ] Real Clerk/Supabase staging, privacy and rollback gates are completed.

The first two automated gates are measurable from GitHub Actions; the others require approval or live external resources. **M12 and prior unaccepted M9–M11 gates remain open until those tests and sign-offs exist.**
