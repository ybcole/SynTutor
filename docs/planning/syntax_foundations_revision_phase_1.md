# Syntax Foundations revision · Phase 1

**Status:** Implemented and tested. Ready for the Gate 1 walkthrough.
**Branch:** `feat/lessons/revision-plan`, based on the rollout at `7df6b1e`. Phase 0 handoff at `8e45ac3`.

## Learner walkthrough

1. Open Chapter 1. The desktop article has a **Chapter contents** sidebar. Use it to open **Comparing Flat and Nested Trees**. The page title receives focus and the section gets its own URL.
2. Open **Structural Ambiguity**, use browser Back and Forward, then reload. Each action should restore the corresponding reading page. From the catalog, **Resume lesson** returns an unfinished chapter to its most recent available section on that device.
3. On mobile, open **Chapter contents** above the article and select another section. The list collapses and focus moves to the title. Pressing Escape while the list is open closes it and returns focus to the toggle.
4. Open a fresh chapter and select an opening-check answer. Leave and return before submitting to see the selection restored. For an embedded Builder draft, use **Guide me** to make one edit, navigate away and return. The edit remains available to **Check my tree**.
5. Compare **Visited** with **Finished**. Browsing a worked example updates reading history. The existing progress bar, assessments and awards still use the verified stage flow. The closing check opens after the earlier stages have been recorded.

## Changes and verification

- `web/js/lessons-ui.js` gives article pages stable section IDs and accepts per-chapter section definitions. The twelve existing articles use an adapter around their original headings and renderers. Reading history is scoped to identity and lesson version. A legacy chapter link, stale section link or unavailable assessment link resolves to an available page. Old Builder drafts remain accessible within version 1.0.0. Later versions get their own exercise namespaces.
- `web/css/lessons.css` adds the desktop rail and mobile disclosure with the existing theme colours. `web/js/main.js` clears lesson URLs when another workspace takes over.
- The Lessons browser suite passed all 12 current lessons and exercised section links, Back/Forward, reload, legacy/stale links, keyboard focus, touch navigation, draft recovery, separate reading and assessment progress, mobile width and dark/light rendering. The Builder browser suite passed after its embedded exercise assertion was updated to the existing **Check my tree** label.
- `npm run test:lessons`, `npm run test:assessments`, `npm run test:builder`, `python3 scripts/validate_builder_contracts.py` and `python3 scripts/validate_assessments.py` passed. `python3 scripts/validate_lessons.py` still stops at the pre-existing Chapter 2 receipt mismatch documented in Phase 0. No content or receipt was edited here. Browser testing used a local guest session with simulated external services. Hosted account sync and manual screen-reader testing are pending.
- The published question sets, one-time XP, chapter completion policy, source anchors and Chapter 12 content are the existing ones. Reading bookmarks stay on the device. Persisted drafts in this phase cover the opening check, existing closing attempt and embedded Builder. Legacy practice retakes and small reading interactions still reset when the chapter is reopened.

**Gate 1 review.** Try the Chapter 1 sidebar on desktop and the mobile disclosure. Confirm the section labels and the distinction between Visited and Finished. Phase 2 follows with the new assessment and XP contract before the Chapter 1 curriculum pilot.
