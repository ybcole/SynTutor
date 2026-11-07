# Master Prompt — UI/UX Design and System Branding

## Role
Act as SynTutor's product designer and design-systems engineer.

## Objective
Create a cohesive interface for a precise, source-grounded syntax tutor while improving readability, tree density, correction feedback, and responsive use.

## Brand direction
Retain the name SynTutor. Suggested promise: **“Understand structure. Explain grammar.”** Use the syntax tree as the visual identity: nodes, branching, connected constituents, and a clear editorial layout. Keep the voice precise, approachable, and encouraging—not childish. Preserve light/dark themes and use restrained semantic colour.

## Required screens
- Syntax Generator.
- Lessons with B-R and Cambridge tracks.
- Standalone Quizzes.
- Syntax Builder.
- Leaderboard.
- Achievements.
- History/Profile/progress.

## Shared components
Design reusable components for:

- Node/rule explanation evidence.
- B-R/Cambridge source citation.
- Corrected-word annotation.
- Lesson stages and Cambridge insight cards.
- Quiz item, response feedback, and score summary.
- Progress/XP/level displays.
- Achievement cards and unlock states.
- Convention-version indicator and analysis uncertainty state.

## Syntax tree spacing
The current renderer uses fixed `GAP = 26` and `V_GAP = 40`. Prototype smaller values (initial test: horizontal 16–18, vertical 26–30) but implement measured/adaptive spacing rather than a global squeeze. Preserve legibility, connector clarity, and hit targets. Test deep trees, long coordination, multiple branches, triangles, gaps, and mobile screens.

## Correction visualization
Show the corrected sentence and corrected B-R tree. The original incorrect word should be struck through; the corrected word should appear directly below/adjacent and be the only actual leaf value. Keep the full corrected sentence visible, punctuation intact, and original/corrected views reversible. Provide accessible text describing the correction.

## Accessibility and responsive requirements
- Keyboard navigation for trees and Builder.
- Textual tree outline/screen-reader equivalent.
- Do not rely on colour alone to signal errors or correctness.
- Touch-friendly targets and gestures.
- Reduced-motion behavior.
- Desktop/tablet/mobile validation.

## Deliverables

1. Brand/design tokens and interaction principles.
2. Information architecture and navigation prototype.
3. Screen flows for all listed areas.
4. Shared component inventory.
5. Tree density experiments and visual regression cases.
6. Correction annotation interaction spec.
7. Accessibility/responsive review.
8. Usability test plan and findings.

## Stop condition
Do not perform a full CSS redesign without first validating the analysis/evidence component contract. Deliver designs and prototypes for review before broad implementation.
