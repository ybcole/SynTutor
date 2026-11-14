# Candidate XAI Tree Mapping

**Status:** candidate-only, production-disabled. Implemented in
`server/cgel_candidate_xai.py`; tests in `server/test_cgel_candidate_xai.py`.

## Short answer to the phase question

The repository already had three different things:

1. **Rule-level explanations** — every Cambridge diagnostic in
   `grammar/rules/*.json` has a `learner_explanation` and source pages.
2. **Node-level structural XAI** — `xai_facts` builds a fact graph from the
   canonical B-R tree, and `xai_composer` / `learner_explanations` turn selected
   node facts into the short “why this node” paragraph used by the inspector.
3. **Approved-rule XAI** — `xai4_partial` / `xai5_repair` evaluate only
   independently approved runtime rules. There are currently zero approved
   Cambridge runtime rules.

What was missing was the bridge from the **187 candidate Phase-C findings** to
actual syntax-tree nodes and to a context-aware candidate paragraph. That
bridge is now `cgel_candidate_xai`.

## What is mapped

For each candidate finding:

- collect every explicit character span from `edit_hint` and `relation`;
- map the mark span to the smallest covering node;
- map subject/verb, left/right, first/second and other relation spans;
- distinguish the mark node from related nodes;
- map punctuation/insertion spans that have no token to a **boundary** between
  the left and right token nodes;
- attach the nearest clause and phrase;
- report `mapped_relation`, `mapped_span`, `unmapped` or `unavailable`.

The result is attached to Phase D findings as `tree_binding` and
`candidate_explanation`. It is also exposed through `/api/explain` when the
request includes `include_candidate_xai: true`.

## Tree authorities

- `canonical_fact_graph` — the observed B-R/XAI-2 graph when the canonical
  analysis is available. This is the tree authority used by the node inspector.
- `benepar_candidate_parse` — the parser tree used by the candidate probes when
  canonicalization fails or is not available. The output says so explicitly.

The fallback is important for ungrammatical sentences: canonicalization often
fails closed on exactly the inputs a candidate check is meant to inspect.

## Explanation shape

Each mapped item has a short and deep paragraph:

- **short** — names the affected node, the related tree position, the clause,
  the source rule's learner explanation, and the candidate edit if one exists;
- **deep** — adds the rule statement, source citation, node IDs, binding status
  and the candidate-only caveat.

Example:

> In this sentence, the candidate check links the noun phrase “The repair
> crew” to the verb phrase “arrived at dawn” inside the clause “The repair
> crew, arrived at dawn.” Keep the subject and verb together. A comma is
> available exceptionally when it prevents a genuine misreading. A candidate
> edit would delete “,”; it has not been applied. Candidate observation only;
> not a verified error.

The paragraph is deterministic. No model is called.

## API and UI

`POST /api/explain` accepts:

```json
{
  "tree": {...},
  "node_id": "optional-node-id",
  "include_candidate_xai": true
}
```

The default is `false`, so existing production explain behavior is unchanged.
When enabled, the response gains `candidate_xai` with:

- `status`, `tree_authority`, `items`, `focus_node_ids`;
- per item: `rule_id`, source pages, `tree_binding`, `explanation`;
- `unmapped_finding_ids` and `blocked` notes;
- `production_enabled: false` and `whole_sentence_certified: false`.

The node inspector (`web/js/explanation-evidence.js`) requests the candidate
section on node-specific requests and renders it under
“Candidate grammar checks — not verified errors.” Whole-tree requests do not
request candidate XAI.

`/api/parse` accepts the same `include_candidate_xai` flag. The web client sends
it when it needs candidate node marking, and the payload carries
`candidate_xai` inside `explanation_evidence` (and as a top-level convenience
field). The canonical B-R tree marks affected/related nodes red; the legacy
parser tree marks the smallest nodes covering the candidate token spans. Red is
a UI affordance for the candidate check, not a production error label. The
canonical tree help text and the node group tooltip both say the mark is
candidate-only.

Legacy matrix errors are bridged separately by `web/js/legacy-node-map.js`.
That module maps remediation edit positions to the exact canonical target word
(or, when no remediation target exists, the smallest covering canonical node),
so the canonical tree marks the same word and the inspector shows a
“Legacy diagnostic — not book-verified” section with the suggested fix. The
detail is not inherited by every descendant or ancestor node. This is a display
bridge, not a promotion of the legacy rule.

## Coverage and limits

- All candidate findings that expose a character span are mapped. Findings
  without a span are returned as `unmapped` with a reason.
- The 11 deferred semantic specifications are not included. Their triggers
  depend on notional agreement, conditional mood, binding or ellipsis
  resolution.
- The mapping does not license grammatical functions, heads, subject/object
  roles or source-authority claims. It maps spans to observed nodes.
- A mapped finding is not a verified error. It remains candidate-only and
  cannot activate a registry rule.
- The canonical graph is preferred; the parser fallback is labelled and is not
  presented as a canonical analysis.
- Context-gated probes that require an explicit interpretation confirmation
  remain blocked or are not invoked.

## Tests

```bash
cd server
CGEL_REQUIRE_PARSER=1 python -m unittest -v test_cgel_candidate_xai
```

The tests cover parser-tree binding, canonical relation binding, punctuation
fallback, node filtering, unmapped findings, Phase D attachment, the
`/api/explain` opt-in, and the production-disabled claim boundary.
