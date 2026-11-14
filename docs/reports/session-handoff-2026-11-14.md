# Session handoff · Burton-Roberts lesson revision

**Branch:** `feat/lessons/revision-plan`
**Handoff written:** 2026-11-14
**Author of this handoff:** AI agent session (continued ChatGPT/Codex's work)
**Authority:** `docs/planning/SynTutor_Lesson_Revision_Master_Prompt.md` (this document supersedes older lesson guidance where stated).

> Companion file: **`docs/planning/CONTINUE_HERE.md`** — read that first if you are resuming the prompt. This file is the status report; that file is the "what to do next + what to read" instruction sheet.

---

## 1. Purpose of this handoff

The owner is transferring this work to another machine and will continue prompting there. This report records, accurately and without overclaiming:

- what is committed on `feat/lessons/revision-plan`,
- what state each chapter lesson is in,
- what is **not** done (gates, publication, titles, Chapter 6 implementation),
- known issues a new session must not misrepresent.

Everything below was verified by reading the repository in this session. Where something is a design estimate or pending owner review, it is labelled as such. No browser/hosted/production result is claimed unless it is recorded in the referenced pilot reports.

---

## 2. Commit log on the branch (most recent first)

```
1e28b6d  Outline Chapter 6 auxiliary VPs for review
641b155  Add the Burton-Roberts Chapter 5 lesson pilot
ccf17da  Outline Chapter 5 and explain numbered VP levels
a89e9d4  Add the Burton-Roberts Chapter 4 lesson pilot
6d951fe  Outline Chapter 4 and align the Chapter 3 preview card
ac8f1ab  Add the Burton-Roberts Chapter 3 lesson pilot
bf846ee  Outline Chapter 3 and fix revised lesson entry navigation
2541c27  Use book chapter titles and add the Chapter 2 lesson pilot
9fb3218  Prepare the Chapter 2 storyboard and focus lesson validation
880ad06  Add the Burton-Roberts Chapter 1 lesson pilot
4fee10b  Add versioned Foundations checks and incremental lesson XP
018543a  Add chapter contents and resume links to Lessons
8e45ac3  Record the Syntax Foundations Phase 0 audit
```

`1e28b6d` (Chapter 6 outline) was committed in this session but **could not be pushed** from the session environment (no GitHub credentials). See §7 for the exact push command.

---

## 3. Chapter status table

Legend: **Pilot** = implemented as an isolated preview (`?preview=br-0X`). **Outline** = storyboard doc only, not implemented. Gate status per master prompt Phase 4.

| Ch. | Book title (exact 3rd ed.) | Source pp. | Pilot impl. | Storyboard | Pilot report | Browser test | Gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Sentence structure: constituents | 6–23 | ✅ yes | ✅ | ✅ | ✅ | Gate 3/4.1 — owner review + timing pending |
| 2 | Sentence structure: functions | 24–45 | ✅ yes | ✅ | ✅ | ✅ | Gate 4.2 — pending |
| 3 | Sentence structure: categories | 46–66 | ✅ yes | ✅ | ✅ | ✅ | Gate 4.3 — pending |
| 4 | The basic Verb Phrase | 67–86 | ✅ yes | ✅ | ✅ | ✅ | Gate 4.4 — pending |
| 5 | Adverbials and other matters | 87–110 | ✅ yes | ✅ | ✅ | ✅ | **Gate 4.5 — the current gate, pending owner review** |
| 6 | More on verbs — auxiliary VPs | 111–140 | ❌ outline only | ✅ (new) | ❌ | ❌ | Outline awaiting owner approval before any code |
| 7–11 | (per master prompt §D) | 141–268 | ❌ not started | ❌ | ❌ | ❌ | Not started |
| 12 | Cambridge companion | separate | unchanged | n/a | n/a | n/a | Out of scope |

"Owner review + first-time learner timing" are **pending** for every implemented chapter. An AI assertion that a page is correct is **not** acceptance evidence.

---

## 4. Files created/modified per chapter (verified present)

**Content (per chapter):**
- `web/content/lessons/br-01-pilot.json` … `br-05-pilot.json`
- Book tree records already existed and are the source of truth for diagrams: `web/content/book/ch01.trees.json` … `ch11.json` (Chapter 6 = `ch06.trees.json`, convention `V6`).

**Pilot presentation JS:**
- `web/js/constituents-pilot.js` (Ch.1), `functions-pilot.js` (Ch.2), `categories-pilot.js` (Ch.3), `basic-vp-pilot.js` (Ch.4), `adverbials-pilot.js` (Ch.5)
- `web/js/lessons-ui.js` — registers pilots in `pilotArticles` and merges pilot JSON over the catalog when `?preview=` is present.

**Storyboards:** `docs/planning/syntax-foundations-chapter-1..6-storyboard.md`
**Pilot reports:** `docs/reports/syntax-foundations-chapter-1..5-pilot.md`
**Browser tests:** `scripts/test_chapter_{one,two,three,four,five}_pilot_browser.py`

Chapter 6 currently has **only** `docs/planning/syntax-foundations-chapter-6-storyboard.md` (this session). No `br-06-pilot.json`, no `auxiliary-vp-pilot.js`, no browser test, no pilot report yet.

---

## 5. How the preview works (so you can inspect it)

The previews are **not** on the normal Lessons page. They load only when both conditions hold:
1. served from `localhost` / `127.0.0.1`, and
2. the URL contains `?preview=br-0X`.

Mechanism (`web/js/lessons-ui.js`, `openLessons`): when `?preview=` is set it fetches `br-0X-pilot.json` and does `{ ...lesson, ...pilot }`, so **both the content and the book title come from the pilot**.

**Run and open:**
```bash
cd <repo-root>
python3 -m http.server 8000 --bind 127.0.0.1 --directory web
```
| Ch | URL |
| --- | --- |
| 1 | http://127.0.0.1:8000/?preview=br-01#lesson/br-01/introduction |
| 2 | http://127.0.0.1:8000/?preview=br-02#lesson/br-02/introduction |
| 3 | http://127.0.0.1:8000/?preview=br-03#lesson/br-03/introduction |
| 4 | http://127.0.0.1:8000/?preview=br-04#lesson/br-04/introduction |
| 5 | http://127.0.0.1:8000/?preview=br-05#lesson/br-05/introduction |

Navigating away from the `?preview=` URL returns you to the **old published catalog**. To switch chapters, edit the URL (change `br-04` → `br-05`); do not click the sidebar "Lessons" item.

---

## 6. Title situation (important, previously asked)

- **In previews (`?preview=br-0X`):** titles ARE the exact book titles (e.g. *Sentence structure: constituents*, *The basic Verb Phrase*, *Adverbials and other matters*). Content is also the revised content. Both are updated.
- **On the published Lessons page (no `?preview`):** neither content nor titles are updated. It still reads `web/content/lessons/course.json`, which retains the original titles (`Constituents and hierarchy`, `Subject, predicate and category`, etc.). No commit has changed those `course.json` titles since `225122d`.
- This is a tension inside the master prompt: instruction **#18** says use the exact book title "in the Lessons catalog" (i.e. `course.json`), but the gate/isolation rules say **do not modify the published catalog** until a reviewed catalog entry + matching immutable assessment seed + migration gate exist (Phase 2/3, Phase 5 / Gate 5). The pilot reports explicitly state pilots are separate from the published catalog.
- **Decision left to the owner** (recorded as open, not resolved): (a) change `course.json` titles only at publication (recommended, gate-compliant), or (b) a title-only `course.json` edit now (satisfies #18 literally but is a published-catalog edit needing explicit owner authorisation), or (c) force full early publish (not advised).

Do **not** claim the catalog titles are fixed. They are fixed in previews only.

---

## 7. Push status and how to push

`1e28b6d` is committed locally but **unpushed**. This session environment has no GitHub credentials (no token/helper/SSH; terminal prompts disabled), so it could not push and did not attempt to obtain secrets.

From an authenticated terminal:
```bash
cd <repo-root>
git log --oneline -1                 # expect: 1e28b6d Outline Chapter 6 auxiliary VPs for review
git push origin feat/lessons/revision-plan
```

---

## 8. Known issues / do not misrepresent

- No chapter above has owner acceptance or verified first-time learner timing. All timing figures (Ch.1–6 storyboards ~9–10 min) are **design estimates**.
- The `server/app.py` "page not interactive" symptom investigated in this session is a **front-end JS / boot** issue under that server, not proven fixed and not part of lesson content. The static `python3 -m http.server ... --directory web` server is the reliable way to view previews. (See `docs/planning/CONTINUE_HERE.md` §Open problem.)
- Publishing (making revised lessons appear on the real Lessons page with new titles and account-scored XP) is **Phase 5 / Gate 5** and has not happened. No hosted migration or seed has been created or applied.
- Do not modify a published graded question or answer key in place; a change requires a new content version + reviewed seed (master prompt integrity rules).
