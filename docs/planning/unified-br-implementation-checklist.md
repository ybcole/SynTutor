# Unified Burton-Roberts implementation checklist

The project owner approved the [unified notation specification](br-label-xai-master-plan-2026-11-09.md) and authorized implementation on 9 November 2026. This checklist tracks the rollout separately from the textbook lesson and milestone release checklists.

## 1. Establish the first supported construction

- [x] Record the unified notation decisions and their printed-page evidence.
- [x] Approve the specification for implementation.
- [x] Confirm the current canonical envelope, candidate parser and Builder integration points.
- [x] Implement a guarded FINAL-D1 projection for the first finite intransitive declarative, including the Chapter 7 NOM refinement, stacked verb features and a VP adjunct (F01).
- [x] Verify canonical structure, token alignment, provenance, preserved parser evidence and abstention on unsupported inputs.
- [ ] Review and register contextual B-R explanations for every node in F01. Reuse the lexical node’s explanation for its selectable word, if needed.
- [ ] Verify real spaCy/Benepar output, canonical display and node selection through the Generator.

The first backend construction is in [draft PR #45](https://github.com/ybcole/SynTutor/pull/45). The 170 model-free tests passed locally. The real-parser test and learner-facing display remain separate acceptance checks.

## 2. Expand construction coverage

- [ ] Extend simple NP, VP and lexical frame coverage using source-backed cases, including complement/adjunct contrasts.
- [ ] Add auxiliary VP layers, passive and yes/no inversion (F02, F11).
- [ ] Add finite embedded clauses, content vs. relative *that*, and temporal P vs. subordinator (F05–F08).
- [ ] Add matrix wh, embedded wh and relative clauses with typed gaps (F03–F06).
- [ ] Add non-finite complement structures, Type I/II and control (F08–F10).
- [ ] Verify particles, scope, extraposition, ambiguity and abstention cases (F12–F17).
- [ ] Require source-cited explanations and model-backed acceptance fixtures as each construction is enabled.

## 3. Validate the integrated flow

- [ ] Verify chapter exercises still preserve their source-specific figure conventions.
- [ ] Verify feature rows, gaps and indices in the rendered tree and check keyboard access to each node’s explanation.
- [ ] Measure canonical conversion coverage and per-node explanation coverage separately.
- [ ] Review the results before making the canonical tree the default free-analysis display.
