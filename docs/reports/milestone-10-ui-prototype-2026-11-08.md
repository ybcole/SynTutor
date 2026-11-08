# Milestone 10 · UI and correction prototype

Implementation and repository tests on 8 November 2026 (Asia/Manila). The execution plan requires stable screen contracts. The prototype uses the merged Milestones 2–8 and the existing paused rankings screen. Public ranking activation and the Milestone 9 branch are independent of this work.

## Design and navigation

The prototype retains SynTutor, the syntax-tree motif, and the existing light and dark theme tokens. The brand promise is “Understand structure. Explain grammar.” The proposed design uses the current surface, border, ink, muted, and accent tokens. A diagnostic label or status is always visible in text where the interface flags a correction. A dashed branch and the text outline also convey a flagged diagnostic node. The rail already marks the active destination with `aria-current` and collapses into a drawer on narrow screens.

| Screen | Flow and shared components |
|---|---|
| Generator | Enter a sentence, inspect the diagnostic tree through canvas or text outline, and open the same evidence and source citations. A separate action opens an available canonical tree in Builder. |
| Correction | Select a flagged node, preview an offered edit, read the complete corrected sentence and removed/added text, inspect the corrected B-R tree if available, or return to the original. |
| Builder | Construct or import the canonical tree, inspect chapter-aware controls and shared evidence, and recover the local draft. |
| Lessons | Choose the B-R or Cambridge track, follow the lesson stages, use the source panel and scrollable B-R tree, and view completion. |
| Quizzes | Open the independent assessment, submit responses, read shared evidence, and review score or reinforcement. |
| Achievements and profile/history | Inspect existing level, XP and badges. Use the account controls and private analysis history. |
| Leaderboard | Existing paused state. The prototype has no public ranking or consent release dependency. |

This pass reuses the evidence, citation, lesson, quiz, and progress components. It changes the tree geometry, keyboard/touch navigation, correction comparison, and handoff placement. A broader visual redesign remains subject to review.

## Tree and correction behavior

The diagnostic renderer measures labels and reserves each subtree's width. Gaps are 16–18 px horizontally and 28–30 px between rows, outside the node boxes. A long label expands its branch instead of every leaf slot. Fit and focus use measured bounds. The canonical read-only SVG in lesson, quiz, and correction views also reserves measured label width and retains its own scroll and text alternatives.

The Generator outline uses nested lists, named buttons, current selection, and textual diagnostics. The canvas supports keyboard navigation, pointer pan and selection, and zoom. The outline supplies touch-sized zoom and fit actions. Fit animation is skipped when reduced motion is requested.

The preview compares the exact corrected sentence returned by the parser with the submitted edit before replacing the diagnostic canvas. The struck-through original and inserted replacement are annotations beside the full sentence. They do not alter the actual leaf text. Canonical B-R is displayed only when the response contains a matching normalized sentence and tree. The diagnostic fallback has an explicit unavailable message. Returning to the original clears the corrected presentation and retains the learner's input.

## Verification and review

- `node scripts/test_tree_layout.js` checks shallow, deep and wide geometry at three viewport widths, non-overlapping labels, and substitution, insertion, deletion, punctuation, contraction and multi-token edits.
- `python scripts/test_ui_prototype_browser.py` checks desktop, tablet, and mobile, including reduced motion, keyboard outline selection, touch activation, canonical handoff, annotated correction, and return to original. It uses a fixture API and saves screenshots. The model-free workflow attaches those screenshots for review.
- Existing evidence, correction and Builder unit regressions and lesson, quiz, Builder and progression browser regressions passed locally. Static build and packaging checks also passed. The workflow retains real parser and shared-evidence browser checks.

For the review gate, open the CI screenshots and repeat Generator correction on desktop and mobile. Ask learners outside the implementation team to find the correction, explain what changed, return to the original, and locate a cited explanation. Include at least one keyboard-only or assistive-technology session and a tablet check. Record task completion and friction before broad UI changes. No human learner sessions or screen-reader audit were performed in this implementation.
