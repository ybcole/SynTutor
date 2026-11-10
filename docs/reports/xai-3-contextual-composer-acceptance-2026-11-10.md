# XAI-3 — Contextual explanations and evidence-bound short/deep composer

**Date:** 10 November 2026
**Language policy:** ENGLISH_ONLY
**Implementation branch:** feature/xai-3-contextual-composer-2026-11-10
**Status:** implementation complete; CI verified separately; independent linguistic function approval remains outstanding.

## Delivery

XAI-3 adds a deterministic, offline observation-only explanation layer on top of XAI-2's validated fact graph. The XAI-2 graph remains the factual input and is never modified. A planner selects node-relevant verified atom IDs including child-edge proofs. A composer writes concise and expanded original English observations naming each actual word/constituent, immediate parent and daughters/siblings, literal features, and exact original token intervals. A chapter-specific tree may contain gaps, zero-width categories, opaque triangles, movement annotations and accepted alternatives; these are described without guessing missing internal structure or grammatical functions.

Delivered modules:
- server/xai_planner.py — per-node proof and role safety checks.
- server/xai_composer.py — deterministic short/deep contextual prose, no LLM dependency.
- grammar/xai_composer.schema.json — strict versioned output with proof atom IDs, tree paths and uncertainty.
- server/explanations.py / server/tree_evaluation.py — compatible sidecar under contextual_explanations in /api/explain and /api/evaluate.
- web/js/explanation-evidence.js — accessible "In this sentence" contextual text, expandable "Why this is shown" including atom IDs and path evidence. All displayed text uses textContent; existing book-sourced channels remain separate.
- web/js/main.js — selects real word terminal IDs (not their parent), preserves parent display annotations, guards against late-response selection races and permits provisional working-tree observations when validated.
- server/test_xai_composer.py — 15 unit/contract cases including gold B-R trees, unseen English minimal pairs, proof integrity and no forged roles.
- scripts/test_explanation_browser.py — real-browser selected V/word short/deep assertions and Generator/Builder evidence parity.
- .github/workflows/syntax-generator-tests.yml — XAI-3 validation integrated into the model-free CI gate.

## Safety and authority

The new output has claim_status STRUCTURAL_OBSERVATION_ONLY, source_ids [], function_status unknown_unlicensed. It is not a new Burton-Roberts teaching rule, not Cambridge grammaticality checking and not a correction. The existing two reviewed templates and their source/printed-page gating remain intact. The 42 XAI-1 concept candidates and 21 candidate templates are **not** activated; independent instructor approval is still required for head, subject, object, complement, adjunct, valency or auxiliary selection explanations. A matching S > NP VP tree is only a shape observation, not automatically licensed grammatical function. Two books' category conventions remain distinct.

The renderer reports both one-line context and expanded evidence on a clicked node. When no node is chosen, it reports the number of observed tree positions, not an indiscriminate wall of text. A provisional tree always receives provisional wording and no new book-backed claims. Missing or invalid tree input cannot manufacture prose. There is no network/LLM dependency.

## Acceptance criteria and tests

Tested targets include S, NP, VP, NOM, PP, AP, AdvP, lexical V/N/P/A, word terminals, unlabelled triangles, explicit gaps and alternatives where present in the validated source. Exact strings/positions and node-specific difference are checked against corpus and unseen English minimal pairs. CI workflows contain the existing parser-backed baseline/Generator/Builder browser tests and model-free source/Builder/lesson checks; actual pass/fail status is documented on the PR after execution rather than assumed.

**Gate:** no generic definition-only fallback; no invented words, children, source citations, grammaticality or role; source metadata forgery must have no effect. Independent expert/adjudicated function accuracy and broad live corrections are out of scope, remain pending for XAI-4/5/8.

## Remaining work

Independently human-reviewed construction licenses and held-out function adjudication; causal relation explanations requiring those licenses; broader verified movement/control examples; explanation cross-mode feature parity and correction highlighting planned in XAI-7; source-approved grammatical diagnostics and repair history in XAI-4/5.
