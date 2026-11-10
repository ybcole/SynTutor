# XAI-2 acceptance — sentence-specific structural fact graph

**Date:** 10 November 2026
**Repository:** ybcole/SynTutor
**Branch:** feature/xai-2-sentence-fact-graph-2026-11-10
**Status:** implemented; CI sign-off tracked in the PR; independent linguistic role approval pending.
**Scope:** English only, no Cambridge grammaticality claims, no live corrections.

## Implemented

- Server-side server/xai_facts.py creates deterministic versioned fact graph on an already validated canonical or working B–R tree. Invalid input fails closed.
- Root, phrase, lexical-category, overt word, elided terminal, gap, zero-word position and opaque labelled/unlabelled triangle nodes are represented without inventing internal structure.
- Node records: IDs, parent, daughters, sibling position, ancestor chain, category, features, explicit index, token span, exact character span and original text.
- Token lookup: smallest node and actual lexical/phrase/clause ancestor, if present. A word inside a triangle stays opaque.
- Atom/edge records: stable IDs, tree paths and evidence status. Explicit movement/control/co-reference annotations remain observed links, not automatically validated linguistic relationships.
- Alternative accepted roots are kept in separate conditional subgraphs.
- Recognized S > NP VP and auxiliary phrase shapes are only candidates. New function, head, complement, adjunct and valency assertions are intentionally withheld pending independent human source approval.
- Existing /api/explain and /api/evaluate return the same sidecar fact graph while maintaining existing templates, channels, statuses and grammar verdict separation.
- grammar/xai_facts.schema.json is the schema; canonical tree input schema is unchanged.

## Safety

XAI-1 catalog contains 42 source-checked concepts and 21 template candidates, all pending independent instructor approval. XAI-2 does not activate them. Source flags supplied on a request are not authorization. Roles/head fields remain unknown_unlicensed. The graph does not grade grammar, diagnose an error, or propose repairs.

## Verification

server/test_xai_facts.py has 11 cases on reviewed lessons and adversarial fixtures: schema and coverage, token ancestry, original whitespace, opacity, provisional status, gaps, alternative isolation, role forgery, invalid input, shared endpoints and unresolved structures. The model-free GitHub Actions workflow runs these tests. Consult the linked PR workflow jobs for actual verification outcomes.

## Pending

1. Independently reviewed role licenses, adjudicated held-out gold cases, complement/adjunct and auxiliary tests.
2. More later-chapter indexed-gap/control examples.
3. XAI-3 contextual explanation composition and frontend use.
4. Cambridge grammar diagnosis (XAI-4) and correction lineage (XAI-5/7).

**Gate:** do not treat unapproved role candidates as teaching claims; merge only after CI passes.
