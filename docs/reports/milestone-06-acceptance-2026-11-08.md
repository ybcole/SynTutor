# Milestone 06 — Syntax Builder acceptance

Date: 8 November 2026 (Asia/Manila).

The M6 implementation is complete and locally verified. The Builder edits canonical B-R trees, checks the submitted construction rather than reparsing its words, offers chapter-aware controls and preserves advanced source structures. Nine M4 original worked trees provide reviewed construction practice; no new linguistic rule or Cambridge constraint is approved by this milestone.

| Acceptance criterion | Evidence |
|---|---|
| Same serialization as Generator | Canonical schema v1.1.0; ten M4 tree round trips plus every normalized source-corpus fixture; tokens, source-specific node data, gaps/empty nodes, features, indices, movement and alternatives preserved |
| Matching structural/grammatical feedback | Shared `evaluate_analysis` service in Generator responses and Builder `/api/evaluate`; shared M3 composer/UI; benchmark parity and Flask/stdlib/ASGI route checks; grammaticality remains unresolved without enabled constraints |
| Source-grounded validation | Existing canonical schema/profile/span/feature/reference validator and checked palette inventory; known future labels fail, unknown source-specific labels remain unsupported; client source/target claims cannot grant authority |
| Accepted analyses and separate outcomes | Primary/ACCEPTED/PREFERRED structural comparison; rejected/unreviewed alternatives excluded; profile mismatch, invalid construction, target difference and unresolved grammaticality remain separate |
| Editing, saving and recovery | Canvas editing plus labelled node/parent/order/feature/index controls, triangle/gap/empty-position support, canonical JSON, forty undo/redo snapshots, per-identity local drafts and safe malformed/corrupt/unavailable storage handling |
| Accessible practice and mobile | Nine chapter-2–10 targets, progressive requested hints/model reveal, responsive controls, text-based editing and pan/zoom/fit; inspected desktop/mobile Chromium screenshots |

Observed checks: 134 model-free backend tests, JavaScript Builder core/session tests, nine-target/palette contract validator, actual browser construction/check/undo/profile-change/import/reload/help/mobile flow. Existing M4/M5 browser/store/SQL regressions, source validators, shared evidence, legacy correction/quiz, build/upload-filter/runtime packaging checks also run before publishing. CI retains real parser-backed Generator/Builder HTTP/rendered evidence parity and the full gold/chapter suites.

The approval gate is evidenced by the shared M4 benchmark set (early/middle/advanced profiles), full source-structure preservation regression and the existing real parser/HTTP/browser parity test extended to the canonical evaluator. Same-assistant implementation verification is explicit; it is not new human instructor sign-off. The missing detailed prompt was restored from unchanged authoritative criteria.

## Scope and deployment

No new database migration, XP reward or lesson/quiz completion write is introduced. The owner reported M4/M5 migrations applied; this is recorded as owner-reported deployment, not a hosted verification performed by this implementation. M6 drafts stay on the current device/account cache; they do not sync across devices. Deploy both frontend and backend so `/api/evaluate` is available. An older backend yields an explicit unavailable check with draft retained.

Chapter 1's arbitrary PHRASE-a/PHRASE-b schematic labels remain source-specific/unsupported in general validation and are excluded from graded construction targets; Chapter 11 is text-only. General structural well-formedness is not proof of arbitrary linguistic analysis. All source crosswalk and Cambridge runtime gates remain unchanged. Advanced metadata can be edited through canonical JSON; dangling references require repair and are not silently removed. Formal assistive-technology user testing and global UI polish remain later work.

Rollback the frontend/backend changes together; no live database data needs rollback. Keep device drafts/exported canonical work for recovery. See [Builder guide](../builder/README.md).
