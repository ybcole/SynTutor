# Quiz V2 refinement delivery

Review base: **feat/quiz-v2**, commit `c79341c702e0f3f51ac30b275c05dc47be0c9bc3`.
Working branch: `refine/quiz-v2`, tracking `origin/feat/quiz-v2`.

The remote was fetched before implementation; its latest tip matched the verified commit. The initial workspace was clean at `f8c3c05`. Its history remains on `work` and `preserve/cloud-work-f8c3c05`. Neither `f8c3c05` nor `249c1b4` was merged or cherry-picked. No pushes, merges, deployments, remote database writes, or student-data modifications were performed.

The local Git base is verified. Codex Cloud's review-target configuration is not exposed by the available tools, so its automatic target cannot be verified or changed here. Any subsequent PR must explicitly target `feat/quiz-v2`, not `main`. A portable patch is supplied separately in `/workspace/quiz-v2-refinement.patch` and applies to the base above.

## Behavior

- Lessons-style chapter cards expose General Chapter Quiz through their primary Start Quiz action; existing drafts resume through that action.
- Subtopic quizzes remain vertically stacked in a keyboard-accessible native disclosure, with concise descriptions.
- Review your Errors stays above the track folder; redundant card question-count badges and Resume Unfinished Quizzes are removed. Saved drafts remain intact and resumable through the corresponding cards.
- Existing original application/analysis questions and mixed-format selection are retained: Syntax includes blanks, reconstruction, syntax correction and tree building; Grammar includes blanks, reconstruction and grammar correction, alongside application MCQs.
- Format-specific inputs, evaluation, submission-gated feedback, and best-score XP awards remain intact.
- Profile XP reads current total / next-level threshold XP (for example `250/360 XP`), beneath the matching progress bar and aligned left. The bar continues to show progress within the current level.

## Validation

`npm run test:quiz-v2`, `npm run test:assessments`, lesson progress/database tests, foundation progress, and `npm run test:builder` pass. Database checks use isolated PGlite databases, not connected student databases.

The full browser regression suite passed with zero page errors at 390px and 1360px in light and dark themes. Desktop, stacked chapter, mixed-format, results, profile XP, and mobile screenshots are available in `/tmp/syntutor-builder-browser`.

The browser regression runner supports `QUIZ_V2_CHROMIUM_PATH` for installed system Chromium and `QUIZ_V2_PLAYWRIGHT_MODULE` for an external Playwright installation. It checks chapter launches, stacked subtopics, mixed-format answers/scoring, draft reload/resume, personalized review, account isolation, XP placement, and mobile/theme layouts.

## Focused correction pass — 2026-11-17

See [the content audit](quiz-v2-content-audit.md) for seven confirmed question defects, versioned replacements, historical compatibility, screening methods and the limits of the educational review. All chapter/subtopic descriptions are now authored assessment copy; the General Chapter Quiz button sits after the subtopics in a bottom-right footer. Shared disclosure styles are restored and XP hover text explains cumulative thresholds versus within-level progress.
