# Legacy lesson audit and migration

Every one of the 20 top-level hard-coded topics was inspected. The old module
mixed Penn/Benepar labels, parser-predicted targets, unsupported instructional
prose, account locks and a replayable 25-XP completion path. None is reused as
source authority or left behind an active lesson/deep-link entry point.

The original module is preserved at `archive/legacy-lessons/tree-quiz.js` as
historical source, outside the public static build. The runtime imports
`lessons-ui.js`, `lesson-core.js` and `lesson-progress.js`. The legacy matrix
content audit remains a regression check, not a new instructional registry.

| Legacy topic | Disposition | Current/reviewed destination or explicit gap |
|---|---|---|
| NP | Needs B-R reframing; rewritten | br-07 core DET/NOM; modifier/possessive extensions planned |
| ADJP | Needs label correction; rewritten | br-03 AP/DEG/A |
| ADVP | Needs B-R reframing; archived | AdvP extension mapped under Chapter 3; no new unreviewed lesson |
| VP | Needs feature/attachment correction; rewritten in scoped units | br-04, br-05, br-06, br-10; other complementation patterns planned |
| PP | Source topic reusable after rewrite; archived | Chapter 3 PP extension planned |
| QP | Parser-only category cannot be carried over | Quantifier material mapped to NP/Cambridge expansion |
| S | Category/function/text distinction corrected | br-02 and cgel-clauses |
| SQ | Parser category retired | Auxiliary-fronting extension under B-R 6 planned |
| SBARQ | Parser label retired; scoped rewrite | br-09 C1/C2 and typed object gap |
| SBAR | Parser label retired; scoped rewrite | br-08 S-bar/C/S |
| SINV | Advanced topic moved out of core | Clause-type/information-packaging expansion planned |
| WHNP | Duplicated wh grouping; label retired | br-09 object-wh scope; other cases planned |
| WHADJP | Duplicated wh grouping; label retired | Chapter 9 other wh-category extension planned |
| WHADVP | Duplicated wh grouping; label retired | Chapter 9 other wh-category extension planned |
| WHPP | Duplicated wh grouping; label retired | Chapter 9 pied-piping/stranding extension planned |
| CONJP | Parser category retired | Coordination extension/optional module planned |
| UCP | Advanced mixed-category analysis moved | Optional Cambridge coordination module planned |
| PRT | Parser label needs B-R Prt rewrite | Chapter 5 phrasal-verb extension planned |
| FRAG | Unsupported universal lesson/grade removed | No fragment grading published without source/register review |
| INTJ | Advanced non-core topic moved | Optional Cambridge content pending source-specific lesson review |

No existing `quiz_progress`, `player_stats` or history row is deleted or marked
as mastery of a new B-R lesson. New versioned progress keys start independently.
Old local guest XP is not silently imported into the new lesson reward ledger.
Legacy bookmarks can be re-opened through the new catalog; old parser labels
are not treated as canonical content IDs. Standalone assessment migration is M5.
