# XAI-6 — Optional AI naturalization: technical acceptance and release decision

**Date:** 10 November 2026
**Repository:** ybcole/SynTutor
**Language policy:** 100% English only
**Technical implementation:** source-scoped naturalizer, JSON contracts, review and budget gates, bounded cache, deterministic fallback and browser support.
**Production decision:** **DISABLED** — deterministic XAI-3 evidence remains live.

## XAI-6 is optional

The XAI master plan requires an independently human-reviewed blind set proving that AI-authored explanation prose is at least as factually faithful as the current baseline and measurably clearer, with no materially increased false claims. No such genuine blind set or independent comparison is available. Synthetic fake-model fixtures prove software mechanics, not linguistic quality, and cannot be promoted into a human-approved report.

**Decision:** complete the optional technical pipeline, tests and no-go evaluation; do not enable model-driven explanations in production. This is an engineering acceptance, not a claim that AI paraphrasing passed its separate quality gate.

## Implemented components

- grammar/xai6_policy.json + .schema.json: explicit model off-switch, zero human-blind evaluation samples, negative independent-review flags and no configured model transport. Future enablement requires ALL quality, reviewer, source, model, cost and timeout gates together.
- server/xai6_naturalizer.py: server-only prompt restricted to XAI-2 validated structural fact atoms and XAI-3 selected-node proof IDs. No user-supplied source authority; no inferred roles, grammaticality claims or corrections.
- grammar/xai6_candidate.schema.json and grammar/xai6_result.schema.json: strict candidate and response shapes. Exact target node, graph analysis ID, English reading level, approved fact IDs and source IDs must match the deterministic baseline. Current structural prose has NO newly licensed book citations; reviewed teaching templates remain in separate unchanged channels.
- Model wording restricted to original XAI-3 prose and a narrow prevalidated set of observation-preserving substitutions, never arbitrary model claims. Source material inside quotation marks remains unchanged. Unsupported synonyms, source pages, fake fact IDs, unsupported roles, corrected tense, invented grammaticality and changed certainty are rejected.
- Per-request caps: 1 model invocation maximum, 6,000 prompt characters, 3,500 response characters, 300 output tokens, reported cost at most USD 0.005 and measured latency at most 1,500 ms. Any future model transport must independently enforce a **hard** network deadline and cost cap; no such transport is configured in production.
- In-process bounded 64-entry LRU; content-hashed key includes analysis hash, target node, exact proof IDs and template text, variety, reading level, rule-set and source-version identities, model ID and reviewer report ID. No persistent learner-text storage or user-text logging.
- server/explanations.py, server/tree_evaluation.py and server/api.py expose the xai6_naturalization sidecar. The original reviewed book evidence, grammar evaluation and repairs are not altered.
- web/js/explanation-evidence.js shows the deterministic baseline unless the future optional model passes all proof and policy gates; it presents a concise accessible disclosure of the disabled model status.
- server/test_xai6_naturalizer.py: 29 targeted source, review, model-failure, adversarial, proof, source-quote, cache, timeout, budget and API parity checks. All approved-policy mock data exists only in the tests, NOT the production registry.
- scripts/audit_xai6_naturalization.py: model-free audit over course and sampled source-tree nodes, showing the current XAI-3 baseline is unchanged with zero actual model calls. This is NOT an independent human readability assessment.

## Explicit nonclaims

No real AI provider has been configured or called, no text has been sent to a model, and no source-backed linguistic judgments have been invented. There is no measured readability improvement or human blind comparison. The XAI-4/5 human review gates still govern any future Cambridge grammaticality corrections; XAI-6 never bypasses them. No new migrations.

## Quality gate and go/no-go

**NO-GO** for enabling model paraphrases in production. Keep deterministic XAI-3 wording live until a valid independent blind readability/accuracy comparison succeeds and a hard-bounded privacy-safe transport is deployed. XAI-7 may consume the optional naturalizer sidecar and the proven deterministic fallback without needing this optional feature enabled.

**Scope of completion:** technical capability, source-claim containment, negative release decision and tests complete; optional AI naturalizer deliberately withheld from production on evidence grounds.
