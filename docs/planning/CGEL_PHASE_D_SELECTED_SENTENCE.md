# Phase D — Candidate Correction for the Selected Sentence

**Status:** candidate-only, production-disabled. Implemented in
`server/cgel_phase_d.py`; tests in `server/test_cgel_phase_d.py`.

## Scope

Phase D operates on one selected sentence, not a paragraph. It consumes the
candidate-only Cambridge probes, applies their explicit edit hints, reparses
each candidate sentence and reruns the candidate checks. It returns a local
correction candidate and per-finding lineage. It does **not** certify the whole
sentence as grammatical, enable a registry rule, or replace independent source
review.

The original selected text is immutable. The output retains the original text,
its SHA-256 digest and the original findings.

## Pipeline

1. Parse the selected sentence and collect findings from the candidate probe
   registry.
2. Deduplicate identical findings and attach the rule's
   `learner_explanation`, source pages and rule type.
3. Group explicit edit hints by character span and replacement. Findings with
   no edit hint remain unresolved.
4. Build bounded candidate packages:
   - one package per unique edit;
   - one combined package of all non-overlapping edits when there is more than
     one unique edit.
5. Apply each package, reparse the candidate sentence and rerun all candidate
   probes. Parse failures are reported as blocked candidates, not corrections.
6. Record lineage for every original finding:
   - `targeted_cleared` — the target rule is no longer detected;
   - `no_longer_detected` — the rule is absent after a rewrite that did not
     target it;
   - `persists` — the rule is still detected;
   - `new_violation` — a rule appears in the candidate but not in the original.
7. Reject a candidate as non-local if it introduces a new rule ID. Prefer
   candidates with fewer remaining findings, fewer edits and smaller length
   change.
8. Return `candidate_correction`, `partial_candidate_correction`,
   `no_safe_correction`, `no_findings` or `not_evaluated`.

“Cleared” means absent from this candidate check. It is not proof that the
underlying requirement was satisfied or that the rest of the sentence is
correct.

## Tree and XAI binding

Every Phase D finding is also mapped onto the parser tree used for the
candidate check. Each finding carries `tree_binding` (mark node, related nodes,
clause, boundary or unmapped status) and `candidate_explanation` (short/deep
local paragraph). The binding uses the same candidate-only claim boundary as
the correction result: it is evidence for a local observation, not a verified
error.

The canonical tree version and the node-inspector integration are documented in
[CGEL_CANDIDATE_XAI_MAPPING.md](CGEL_CANDIDATE_XAI_MAPPING.md).

## API

```python
from cgel_phase_d import correct_selected_sentence

result = correct_selected_sentence("The guests paniced at the noise.")
```

Key output fields:

- `status`, `production_enabled` (always `false`), `scope`
  (`selected_sentence_candidate_only`);
- `original` — text, SHA-256, findings, blocked probe notes;
- `correction` — a candidate text only when a local candidate is available;
- `best_candidate` — edits, targeted rule IDs, remaining findings, lineage,
  new rule IDs, `safe_local` and score;
- `candidates` — bounded evaluated candidates;
- `unresolved_findings` — original findings without a concrete edit hint;
- `blocked` — parser/probe limitations;
- `caveat` — explicit local-only, non-certifying statement.

## Coverage

The registry adapts the 11 aggregate probe modules produced by the recent
Phase C surface batches (punctuation, spelling, tense/aspect, determiners, verb
form, usage, pronoun case, pro-form, word order, complement selection and final
surface), plus the earlier simple probe functions that do not require an extra
context confirmation flag. Context-gated probes that require an explicit
speaker/interpretation judgment remain blocked or are not invoked.

The deferred semantic specifications are intentionally absent. Their triggers
depend on notional agreement, conditional mood, antecedent/binding relations,
lexical recovery or ellipsis resolution, and are not safe pattern-detector
targets for this phase.

## Safety and limits

- One repair round. Multiple independent errors can be edited together when
  their spans do not overlap; interacting errors that require repeated rounds
  remain future work.
- Candidate count is capped (`max_candidates`, default 12) and the selected
  sentence is capped at 1,200 characters.
- No semantic meaning-preservation proof. A candidate is a local suggestion,
  not an authored rewrite.
- No production path. `grammar/runtime_registry.json` is untouched and no
  candidate finding can activate a Cambridge rule.
- No whole-sentence verdict. A clean candidate means only that the candidate
  probes no longer report a finding.
- Quotation, alignment and parse limitations are reported through `blocked`
  rather than suppressed.

## Tests

```bash
cd server
CGEL_REQUIRE_PARSER=1 python -m unittest -v test_cgel_phase_d
```

The tests cover single and combined independent edits, a persisting finding
under a one-candidate cap, findings without edit hints, clean sentences,
selection bounds, candidate-only status and explanation/source attachment.

## Next work

1. Review the candidate correction payload and expose it behind an explicit
   candidate-only UI flag.
2. Add adapters for context-gated probes without weakening their preconditions.
3. Add a second bounded round only for demonstrated interacting-error cases.
4. Keep production activation behind independent source review, verified
   crosswalks and the fail-closed registry.
