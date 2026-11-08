# Repository layout

| Location | Contents |
|---|---|
| `web/` | Active browser app, CSS, JavaScript and book/content fixtures |
| `server/` | Python API, parsing, normalization, correction and backend tests |
| `grammar/` | Schemas, concepts, rules and runtime eligibility registry |
| `sources/` | Source extraction records and review evidence |
| `scripts/`, `tools/` | Build, content generation, audits and development utilities |
| `benchmarks/`, `evaluation/` | Evaluation inputs and tooling |
| `supabase/` | Database migrations |
| `docs/planning/` | Authoritative plan, checklist and workstream prompts |
| `docs/reports/` | Milestone reports and verification evidence |
| `docs/research/` | Thesis/chapter drafts |
| `docs/archive/planning/` | Historical `_updated` plan/checklist snapshots, not current authority |
| `docs/archive/` | Old repomix snapshot and scratch document |
| `archive/legacy-web/` | Historical root browser files, preserved without changing active `web/` |

`README.md` stays at root for Hugging Face metadata. `CONVENTIONS.md`,
`MASTER_PROMPT.md` and `CAMBRIDGE_EXTRACTION_PROMPT.md` stay at root because
they are linguistic governance entry points referenced by source and runtime evidence.
Deployment, package and dependency configuration also stays at root.

Both Python transports serve `web/`; the static build copies `web/` into `dist/`.
The organization commit does not change these runtime paths. Tests remain beside
the backend because their imports and CI working directories depend on that layout.

The relocation table below records every moved file. Internal Markdown links were
rebased, and current documentation references were updated. Existing published
GitHub URLs and older commits retain their historical paths. Open PR #30 modifies
three relocated planning/report files; carry its edits into their new locations
when merging. GitHub reported #30 mergeable before this cleanup; that does not
predict whether its future merge will require rename resolution.

| Previous path | Current path |
|---|---|
| `CH4 Syntutor.md` | `docs/research/CH4 Syntutor.md` |
| `CHAPTER1_REVISED.md` | `docs/research/CHAPTER1_REVISED.md` |
| `CHAPTER2_REVISED.md` | `docs/research/CHAPTER2_REVISED.md` |
| `CHAPTER3_REVISED.md` | `docs/research/CHAPTER3_REVISED.md` |
| `CHAPTER4_REVISED.md` | `docs/research/CHAPTER4_REVISED.md` |
| `FEATURES.md` | `docs/FEATURES.md` |
| `SUMMARY_OF_CHANGES.md` | `docs/SUMMARY_OF_CHANGES.md` |
| `SynTutor_ An Explainable AI-Based Framework for Syntax Tree-Driven Grammar Analysis and Learning Using NLP.md` | `docs/research/SynTutor_ An Explainable AI-Based Framework for Syntax Tree-Driven Grammar Analysis and Learning Using NLP.md` |
| `chapter3.md` | `docs/research/chapter3.md` |
| `css/style.css` | `archive/legacy-web/css/style.css` |
| `index.html` | `archive/legacy-web/index.html` |
| `js/auth.js` | `archive/legacy-web/js/auth.js` |
| `js/config.example.js` | `archive/legacy-web/js/config.example.js` |
| `js/main.js` | `archive/legacy-web/js/main.js` |
| `login.html` | `archive/legacy-web/login.html` |
| `master_checklist.md` | `docs/planning/master_checklist.md` |
| `master_checklist_updated.md` | `docs/archive/planning/master_checklist_updated.md` |
| `master_plan.md` | `docs/planning/master_plan.md` |
| `master_prompt_concerns_matters_to_be_addressed.md` | `docs/planning/master_prompt_concerns_matters_to_be_addressed.md` |
| `master_prompt_others.md` | `docs/planning/master_prompt_others.md` |
| `master_prompt_syntax_generator.md` | `docs/planning/master_prompt_syntax_generator.md` |
| `master_prompt_ui_ux_design.md` | `docs/planning/master_prompt_ui_ux_design.md` |
| `repomix-output.xml` | `docs/archive/repomix-output.xml` |
| `syntutor_12_prompt_execution_plan.md` | `docs/planning/syntutor_12_prompt_execution_plan.md` |
| `syntutor_12_prompt_execution_plan_updated.md` | `docs/archive/planning/syntutor_12_prompt_execution_plan_updated.md` |
| `syntutor_milestone_02_progress_report.md` | `docs/reports/syntutor_milestone_02_progress_report.md` |
| `tmp_test.md` | `docs/archive/tmp_test.md` |

## Milestone 04 organization update

Active lesson content/schema: `web/content/lessons/`. Runtime: `web/js/lesson-core.js`, `lesson-progress.js`, `lessons-ui.js` and `web/css/lessons.css`. Curriculum map/audit/deployment contract: `docs/curriculum/`. Source checks remain under `sources/*/reviews/`. The former `web/js/tree-quiz.js` is preserved at `archive/legacy-lessons/tree-quiz.js`, outside the static build. Existing user records are not moved or rewritten. The earlier PR #30 rename note above is historical; that work was merged before M4.
