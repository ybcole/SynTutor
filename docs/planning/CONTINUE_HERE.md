# CONTINUE HERE · Burton-Roberts lesson revision

**Read this first when resuming the prompt on a new machine.**
Branch: `feat/lessons/revision-plan`. Authority: `docs/planning/SynTutor_Lesson_Revision_Master_Prompt.md`.

This file gives you (the next AI agent) the context, the exact current state, what to do next, and which repository files to read. It does **not** override the master prompt; where they differ, the master prompt and verified source win.

---

## 0. TL;DR

- Chapters **1–8** have local previews (`?preview=br-0X`), storyboards, pilot reports and browser tests.
- Review the Chapter 8 pilot at **Gate 4.8** before outlining Chapter 9. First-time learner timing remains unverified.
- The published catalog changes during Phase 5.

---

## 1. Files to read first (in this order)

1. `docs/planning/SynTutor_Lesson_Revision_Master_Prompt.md` — the binding spec (sections A–I; §E phases, §F acceptance checklist, §G handoff template).
2. `docs/reports/session-handoff-2026-11-14.md` — historical session report. Use the current master plan and pilot reports for progress.
3. `docs/planning/CONVENTIONS.md` — B-R notation and `[TXT]`/`[IMG]`/`[DERIVED_FROM_INSTRUCTIONS]` status rules.
4. `docs/BR_NATIVE_ENGINE_CONSTRUCTION.md` — authoritative chapter-by-chapter structural summary; §2 "Third Edition conventions" is the notation bible. Chapter 6 row: "*MOD/PERF/PROG/PASS/TENSE recursive VP structure; tense and negation; do-support, question auxiliary fronting and gap.*"
5. The relevant chapter storyboard + pilot report + pilot JS + pilot JSON (see §4).

---

## 2. Source-of-truth data files (never invent figures)

- `web/content/book/ch01.trees.json` … `ch11.json` — the **source-verified tree records**. Chapter 6 is `ch06.trees.json` (convention `V6`, 26 trees, verified figures incl. [53b], [62], [66], [69], [78], [81], [86], [88], [91], [93], [103]).
- `sources/burton_roberts/source_manifest_2026-11-08.json` — chapter page ranges + hashes. Ch.6 = printed pp.111–140, PDF pp.126–155.
- `sources/burton_roberts/reviews/` — independent review receipts.

Any tree a lesson shows must come from these records or be clearly `DERIVED_FROM_INSTRUCTIONS`. Do not use live Benepar/spaCy output as lesson truth (master prompt integrity rules).

---

## 3. How the pilot preview system works (so you don't break it)

- `web/js/lessons-ui.js` has `pilotArticles = { 'br-01': ..., ... }` and `pilotId()` which only returns an id when hostname is localhost/127.0.0.1 **and** `?preview=br-0X` is present.
- In `openLessons`, when a pilot is active: `catalog.lessons = catalog.lessons.map(l => l.lesson_id === preview ? { ...l, ...pilot } : l)`. So the pilot JSON **overrides** content **and title**.
- Pilot JSON schema keys: `title`, `content_version`, `estimated_minutes`, `outcomes`, `preview_sources`, `revised_assessment` (`required_sections`, `opening[]`, `closing[]`). Page bodies live in the matching `*-pilot.js` module, not the JSON.

---

## 4. Per-chapter file map

| Ch | pilot JSON | pilot JS | storyboard | report | browser test |
| --- | --- | --- | --- | --- | --- |
| 1 | `web/content/lessons/br-01-pilot.json` | `web/js/constituents-pilot.js` | `docs/planning/syntax-foundations-chapter-1-storyboard.md` | `docs/reports/syntax-foundations-chapter-1-pilot.md` | `scripts/test_chapter_one_pilot_browser.py` |
| 2 | `br-02-pilot.json` | `functions-pilot.js` | `...chapter-2-storyboard.md` | `...chapter-2-pilot.md` | `test_chapter_two_pilot_browser.py` |
| 3 | `br-03-pilot.json` | `categories-pilot.js` | `...chapter-3-storyboard.md` | `...chapter-3-pilot.md` | `test_chapter_three_pilot_browser.py` |
| 4 | `br-04-pilot.json` | `basic-vp-pilot.js` | `...chapter-4-storyboard.md` | `...chapter-4-pilot.md` | `test_chapter_four_pilot_browser.py` |
| 5 | `br-05-pilot.json` | `adverbials-pilot.js` | `...chapter-5-storyboard.md` | `...chapter-5-pilot.md` | `test_chapter_five_pilot_browser.py` |
| 6 | `br-06-pilot.json` | `auxiliaries-pilot.js` | `...chapter-6-storyboard.md` | `...chapter-6-pilot.md` | `test_chapter_six_pilot_browser.py` |
| 7 | `br-07-pilot.json` | `noun-phrases-pilot.js` | `...chapter-7-storyboard.md` | `...chapter-7-pilot.md` | `test_chapter_seven_pilot_browser.py` |
| 8 | `br-08-pilot.json` | `embedded-clauses-pilot.js` | `...chapter-8-storyboard.md` | `...chapter-8-pilot.md` | `test_chapter_eight_pilot_browser.py` |

Also read: `web/js/lesson-notation.js` (`displayVpLevel` shows VP₁/VP₂), `web/js/lesson-presentation.js`, `web/js/lesson-tree-exercise.js`, `web/js/lesson-core.js`, `web/js/lesson-progress.js`, `web/css/lessons.css`.

---

## 5. What to do next

1. Walk through the [Chapter 8 pilot](../reports/syntax-foundations-chapter-8-pilot.md) for Gate 4.8.
2. After that review, prepare the Chapter 9 storyboard.
3. Phase 5 covers release preparation, published titles, reviewed catalog records and immutable assessment seeds.

## 6. Run a preview (verified commands)

```bash
cd <repo-root>
python3 -m http.server 8000 --bind 127.0.0.1 --directory web
```
Open (edit the `br-0X` to switch chapters; keep `?preview=`):
- Ch.1 http://127.0.0.1:8000/?preview=br-01#lesson/br-01/introduction
- Ch.2 http://127.0.0.1:8000/?preview=br-02#lesson/br-02/introduction
- Ch.3 http://127.0.0.1:8000/?preview=br-03#lesson/br-03/introduction
- Ch.4 http://127.0.0.1:8000/?preview=br-04#lesson/br-04/introduction
- Ch.5 http://127.0.0.1:8000/?preview=br-05#lesson/br-05/introduction
- Ch.6 http://127.0.0.1:8000/?preview=br-06#lesson/br-06/introduction
- Ch.7 http://127.0.0.1:8000/?preview=br-07#lesson/br-07/introduction
- Ch.8 http://127.0.0.1:8000/?preview=br-08#lesson/br-08/introduction

If you drop `?preview=` you are back on the old published catalog.

---

## 7. Open problem tracked from this session (not lesson content)

Symptom: with `python server/app.py`, the page appeared non-interactive / couldn't reach Lessons. Investigation findings:
- `server/app.py` imports and starts correctly; the only failure observed was "Address already in use" when a port was occupied.
- `package.json` real dev server is `python3 server/webapp.py` (`npm run serve`); `app.py` is `serve:legacy`.
- App boot is synchronous in `web/js/main.js` `boot()`; `initLessons(...)` is called late, so any earlier throw (e.g. in `initQuizzes`/`initSyntaxBuilder`, or a bad static import from a pilot module) would leave the UI non-interactive. Not yet root-caused or fixed.
- Reliable workaround for viewing previews: static `python3 -m http.server ... --directory web`.

If asked to fix it: reproduce in a real browser (Playwright/Chromium), capture the console error in `boot()`, and confirm `node --check` passes on all `web/js/*.js` (note: `node` may not be on PATH in a bare shell).

---

## 8. Integrity rules to keep in force (from master prompt)

- No live parser output as lesson truth; authored/source-verified trees only.
- No inventing pages, figures, quotes, receipts, test results, or learner outcomes.
- Do not edit a published answer key in place; use a new content version + reviewed seed.
- Do not touch the published catalog / run destructive migrations / claim hosted results without explicit owner authorisation.
- AI assertion of correctness is not acceptance evidence; owner gates + verified tests are.
- Lesson 12 (Cambridge) stays unchanged and out of scope.

---

## 9. Quick verification checklist before you hand back

```bash
# all files present?
ls web/content/lessons/br-0*pilot.json
ls docs/planning/syntax-foundations-chapter-*-storyboard.md
ls docs/reports/syntax-foundations-chapter-*-pilot.md
# JS syntax (if node available)
for f in web/js/*.js; do node --check "$f" || echo "FAIL $f"; done
# tests named in the master prompt (verify scripts exist on branch first)
npm run test:lessons
npm run test:builder
python scripts/test_chapter_eight_pilot_browser.py
```
Report exact commands and outcomes. Leave failures visible; do not claim passes from reading old reports.
