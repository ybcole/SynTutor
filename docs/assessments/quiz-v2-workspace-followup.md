# Quiz V2 and syntax workspace follow-up

Source: `origin/feat/quiz-v2` at `68d47e25c8e0377f102c856519dcc4efcb67b890`, fetched before implementation. The prior uncommitted refinement was byte-for-byte identical to that remote revision and was preserved in a named Git stash before the local branch advanced. No divergent builder commits were integrated.

## Behavior

- Review your Errors has no adjacent track pill. Its focus explanation uses only submitted results, grouped by instructional topic, ranked by the existing smoothed topic-performance evidence with repeated misses as a tie-breaker. Single-miss wording explicitly qualifies the evidence; no completed mistakes produces a neutral empty state. Existing personalized selection is unchanged.
- Chapter footers put the native subtopic disclosure on the left and General Chapter Quiz action on the right. The controlled, vertically stacked list expands below that row. Ordinary difficulty labels, drafts, resume handlers, manifests and scoring remain intact.
- Ten short descriptions were selectively expanded using the concepts actually assessed; the rest of the authored catalog copy was retained.
- The single existing Builder canvas and controls dock below the Generator. Manual words and construction feedback use separate fields from generated analysis. Generating an analysis does not replace the manual model. Closing/navigating away retains the existing account-scoped draft lifecycle; lesson and quiz embedded builders still reuse the same implementation.
- Mobile Builder controls occupy separate rows; the Nodes palette does not cover Construct/zoom. Fit reserves palette space. Theme changes repaint the canvas.
- Account-only History now lives within the Generator side panel, with the icon at its upper left. Entries show sentence, local date/time and Reopen analysis, using neutral borders and accessible focus states. Underlying diagnostics and stored validity values are unchanged.
- History ranges are rolling elapsed-time windows: 24 hours, 7×24 hours, 30×24 hours, or all stored history. Boundaries are inclusive, future timestamps are excluded from finite windows, offsets are respected, and timezone-less timestamps are interpreted as UTC. Missing/invalid timestamps appear last in all-time results and are excluded from finite windows. Rows are sorted newest first without modifying them.
- History is fetched in account-filtered pages, then filtered locally. Range changes reuse the cache; a saved analysis or identity change invalidates it. Account changes discard cached rows, close the panel and reset the range. Reopening uses the existing analysis replay path.

## Focused educational audit

Retained the seven previous versioned corrections. Inspected the correction/evaluation contract for punctuation items, reconstruction token handling, representative clause/complementation and category examples, and required format coverage. Whole-bank overlap screening still provides candidates rather than educational certification.

**Confirmed defect corrected:** `mixed:cgel-ch20:functions:grammar_correction:12` asks for a terminal question mark, but the inherited text normalizer strips trailing periods. Consequently, `Did anyone check the final totals?.` incorrectly scores as correct. A separately versioned replacement (`:revision-2`, `2.0.1`) explicitly requires one terminal question mark and opts into punctuation-sensitive evaluation. The original item and its grading behavior remain available for historical manifests. New attempts exclude the original; no old score, verified XP catalog entry or server award policy changes.

**Not a defect:** the question-tag reconstruction token `didn’t` and accepted text `didn't` differ only typographically; the existing evaluator correctly normalizes them. The browser fixture now follows that normalization when constructing an answer rather than failing on the apostrophe style.

**Further human review:** selected constrained sentence-correction questions accept only an authored list of answers, so additional grammatical paraphrases may warrant editorial review. Some reused sentence frames and short metalanguage blanks remain scaffolded practice; overlap or low word count alone is not a reason to retire them. The prescriptive/descriptive track's coordinated pronoun item explicitly specifies formal Standard English; other register-sensitive correction prompts should receive individual linguistic review before any blanket edits. This pass does not certify all 2,722 original active legacy/formal/mixed questions as independently reviewed or wholly novel.

The post-change inventory contains 120 legacy items, 1,774 formal items, and 836 mixed entries including eight retained historical originals with replacements. The 1,263 automated overlap candidates (1,261 active) are unchanged by this particular correction. Run `node scripts/audit_quiz_content.mjs output.json` to reproduce the screening inventory. All Syntax/Grammar mandatory interactive formats remain available.

## Verification

Passed:

- `npm run test:quiz-v2`, including history-window, evidence-only review focus, insufficient-data, versioned punctuation and compatibility regressions.
- `npm run test:assessments` and `npm run test:builder`.
- `npm run test:lessons`, `npm run test:correction`, `npm run test:evidence`.
- `scripts/test_quiz_v2_browser.js`: footer alignment, disclosure keyboard behavior, track-pill removal, personalized review, mixed formats, scoring, reload/resume, account switching and responsive themes.
- `scripts/test_builder_generator_browser.mjs`: Generator input/analysis, manual draft preservation across generation, dragging/connections, Clear/Edit/Construct/Fit/zoom, responsive toolbar/palette geometry, and lesson builder regressions.
- `scripts/test_history_browser.mjs`: panel geometry, neutral entries, timestamps, time windows, empty states, cache reuse, account isolation, replay and guest guard.

Screenshots in `/tmp/syntutor-builder-browser` were visually inspected for desktop/mobile light/dark, History layout, chapter footer layout, and manual Builder controls/tree rendering. Browser suites use fixture API responses and synthetic accounts; they do not establish live production NLP availability or exercise real student accounts. Database tests use isolated local PGlite databases. No production database writes, schema changes or deployment changes were made.

Implementation uses the existing Supabase client with explicit owner filtering and existing RLS. The Supabase skill's security guidance was checked; the current JavaScript `.range()` documentation was consulted. No credentials or new dependencies were introduced.

Delivery targets one task commit pushed explicitly as `HEAD:refs/heads/feat/quiz-v2`, after a fresh fetch and ancestor check, followed by remote SHA verification. The final response reports the verified SHA and push status. `main` is untouched.
