# Independent assessments

The Quizzes navigation entry is independent of lesson completion. The launch bank contains 120 original items in 60 pools, with two lexical variants per pool, and 16 five-question blueprints: 11 B-R chapters, one Cambridge clause-classification topic, two cumulative assessments, one diagnostic and one challenge. Topic filtering also exposes chapter assessments under their existing IDs, so it cannot duplicate their XP cap.

Question types are concept MCQ, tree selection, structure identification, analysis minimal pair, convention application, tree diagnosis and structure repair. Every blueprint mixes at least three kinds across introductory, intermediate and advanced applications relative to its reviewed outcome. Selection, order and option order are deterministic from an attempt seed; the stored manifest survives reload. Minimal pairs/diagnosis/repair concern controlled B-R structural analyses, not arbitrary sentence grammaticality.

Each item maps to an M4 outcome, concept IDs, lesson, exact printed-page sources and chapter profile where applicable. Cambridge uses only reviewed CLS-001 classification. No grammaticality constraint is enabled. Chapter 11 remains text-only. Twenty positive answer trees validate canonically; intentionally wrong candidate diagrams are raw alternatives, never approved analyses. The shared tree component provides SVG and text alternatives, including mobile scrolling.

Feedback is withheld until submission, then uses the existing M3 explanation composer in both JavaScript and Python. The API accepts repository item/version/answer IDs only. Missing/unreviewed sources return the shared no-book-basis state. Results name responses to revisit and link back to lessons; they do not certify mastery.

The separate verification pass is by the same AI assistant, reusing M4's limited source-reviewed claims. The review receipt is transparent about this and binds the bank digest. It is not human instructor approval or whole-book coverage. The representative chapter-2 sample/scoring gate preceded the full bank. Original wording/examples do not copy textbook exercises.

Validation: `python scripts/validate_assessments.py`, `npm run test:assessments`, `python scripts/test_quizzes_browser.py`, and backend `test_quiz_evidence` after the existing transport fixtures. CI includes these and the existing parser/course regressions.

See [progress and deployment](progress-and-deployment.md) and [acceptance report](../reports/milestone-05-acceptance-2026-11-08.md).
