# XAI-7 — Unified evidence and accessible learning-mode interface

**Implementation date:** 10 November 2026
**Language policy:** English only
**Acceptance scope:** Shared server evidence and interactive frontend; exact CI outcomes will be recorded on PR #60.

## Mode parity and one source-review boundary

The existing reviewed explanations service generates the same xai7_unified record for Generator/parser, Builder/evaluation and selected-node evidence. Quiz feedback carries the same typed envelope with mode=quiz and explicitly unavailable tree facts; it does NOT invent an analysis. A quiz reviewed answer tree may separately fetch actual per-node evidence from the identical /api/explain service.

Lessons now use /api/explain + renderEvidence, rather than extracting only book-channel text into a separate custom lesson paragraph. XAI-5 learner-authored correction revisions use the same renderer and only their newly reparsed canonical B-R tree, never a renamed original tree.

server/xai7_unified.py and grammar/xai7_unified.schema.json define selected nodes, witnessed parent/siblings, literal features, citation metadata, separately verified local findings and whole-sentence noncertification. Reviewed source gates and conflicts are unchanged. The new record does NOT invent source rules, a syntactic head, subject, object, governor, correction or grammaticality verdict. Production still enables zero new XAI-4 Cambridge diagnostic rules. Unapproved token observations cannot produce verified error highlights.

## User interactions

- Generator: the selected existing B-R word, phrase or feature is highlighted with its witnessed tree relatives and shared brief/deep explanations. Raw Benepar candidates cannot become source-backed B-R syntax solely through highlighting.
- Builder: its selected node uses the same evidence composer. The Builder's independent target/structure feedback remains separate from grammaticality.
- Lessons: real worked B-R nodes and their recorded feature labels support mouse/keyboard inspection, same shared evidence, explicit brief/deep controls, and localized mobile zoom; unchanged authored teaching and XP stages remain available offline.
- Quizzes: after assessment submission, the original source-reviewed quiz feedback remains. A different inspector for its reviewed answer tree provides the same selected-node B-R explanation without overwriting quiz evidence or updating XP.
- Corrections: the XAI-5 user-revised sentence is independently reparsed and displays that new tree in the same node inspector; no original-tree reuse or blanket grammar pass.

Tree geometry, source word order, canonical node identity and B-R category conventions remain intact. Interactive positions are buttons with accessible labels and keyboard Enter/Space actions. Recorded feature-row selection never asserts grammatical role. The zoom bounds are 70% to 180% and tree overflow is localized.

## Source pages and transparent limitations

Eligible book records identify exact printed-page numbers, editions and source IDs. The renderer shows those citations. However the repository does not supply verified publicly accessible PDF deep links for every printed page. XAI-7 does not invent page-level URLs or pretend a publisher homepage resolves directly to a particular page. Actual source-page links require audited accessible URLs or licensed hosted source files.

Optional XAI-6 model paraphrasing stays disabled pending a valid independent human blind clarity and fidelity comparison. New Cambridge rule approvals, syntax accuracy, expert reviews and correction safety remain separate XAI-8 work. The unified display does not silently override these gates.

## Acceptance and regressions

- New Python tests cover the unified schema, real lesson/quiz/answer-tree/generator/builder records, unresolved and provisional cases, source citations, literal feature labels, client approval injection, synthetic ONLY local verified-governor focus and preserved XAI-3 proof atoms.
- New Node tests cover exact SVG selection, observed parent/sibling focus, approved error focus, stale highlight clearing and mode integration.
- Real Chromium plus parser-backed checks exercise Generator/Builder parity, selected word focus, explicit brief/deep controls, source-grounded Lessons and Quizzes, recorded feature selection, keyboard and mobile zoom. Only passing current-head CI can justify merge.
- No changes to live database tables, user progress, source book passages, or production runtime-enabled grammar rules.

**Engineering gate:** all-mode UI evidence and browser parity must pass. Page deep-links where inaccessible, human linguistic approval and a claim of universal grammar accuracy are explicitly excluded from the completion claim.
