# Cambridge cross-domain QA

## First pass

The Phase B baseline contains 3,914 records and 204 diagnostic specifications. The initial scan grouped titles by case-folded word tokens and grouped incorrect diagnostic examples by trimmed text with straight and curly apostrophes treated alike. Three title groups cross catalog domains. One incorrect example occurs in multiple specifications, and both prescribe the same correction. These exact-match scans are a starting point for review. Overlap can also occur between records with different wording or examples.

| Records | Scope decision | Phase C and lesson handling |
|---|---|---|
| CLS-357 and CLS-1451 | Chapter 14 describes the active and passive causative make pattern. Chapter 16 provides a second source specifically for the verbal passive. Both repair the shared example by inserting to. | Use CLS-357 as the primary specification for this construction, with CLS-1451 as corroboration for the passive. A missing-to event on the same governing make–infinitival relation gets one finding. Keep active bare infinitivals as a guard. |
| OTH-007 and PHR-464 | Both cover the contribution of contextual gestures to deixis. OTH-007 gives broader indexing examples, while PHR-464 highlights dependence on the immediate situation. | Combine the material in a lesson and retain both sources. A written sentence alone may not supply the deictic referent. |
| CLS-425 and PHR-095 | Both distinguish determiner function from determinative category. Chapter 2 provides the overview, and Chapter 5 details the phrase types that can fill the function. | Teach CLS-425 as the introductory distinction and use PHR-095 for the fuller classification. |
| CLS-1367 and PHR-636 | Both describe informal discourse-new this. The existential treatment is construction-specific, and the deixis treatment gives wider use and speaker variation. | Teach these as related uses and retain both source scopes. Treat discourse-new this as a guard against an automatic familiarity error. |

The linked records retain their IDs, source citations, original examples and review states. Detector selection in this table is a Phase C design decision and confers no runtime license. A later pass needs to compare paraphrased diagnostics by trigger, governing relation, correction and counterexamples, including potential overlaps with the current parser-backed rules.

## Parser-backed comparison

This pass compares the source scopes with the current implementations in `server/ruleset.py`, `server/matrix.py`, and the inactive Chapter 3 candidate probe. A shared legacy label is insufficient to establish equivalence. Consolidation requires the same grammatical relation and compatible edits. The dispositions below are design decisions for Phase C.

| Cambridge specifications | Existing implementation | Disposition |
|---|---|---|
| COMP-034 | Legacy 6.1 and 6.12 check modal complement form and infinitival to. The matrix also uses C-AUX-FORM. The inactive Chapter 3 probe recognizes third-person singular and infinitival-to cases with typed selection evidence. | One finding per central modal and selected complement. Preserve the distinction between deleting to and changing an inflected verb. Exclude ought to, lexical need and coordinated units. |
| COMP-031 | Legacy 6.12 C-MODAL-STACK looks for adjacent modal surfaces. The inactive probe requires direct same-clause selection and excludes coordination. | One finding for a verified central-modal stack in the target variety. Keep coordinated modals and attested dialectal double modals outside that scope. |
| CLS-100 and CLS-126 | The Chapter 3 probe checks supportive do before another auxiliary for CLS-100. The matrix's generic do-form check expects a plain verb. | Keep auxiliary compatibility separate from lexical verb inflection after supportive do. Lexical have in Does she have a reservation? is valid. Check the matrix question relation even when the subject intervenes between do and the verb. |
| COMP-035, COMP-036 and MORPH-026 | The matrix's auxiliary check accepts either a gerund-participle or a past participle after be and expects a past participle after have. Legacy C-BE-BASE can propose an ing form and C-PASSIVE has a separate missing-be path. | Choose the rule from the verified progressive, verbal passive or perfect relation. A bare form after be is insufficient to select a repair. Keep a missing auxiliary separate from wrong morphology on its complement. Guard copular and participial-adjective readings. |
| CLS-357 and CLS-1451 | Legacy 6.19 C-CAUSATIVE-TO scans an active make/let pattern with a pronoun object and proposes removing to. | The active and passive edits run in opposite directions. For passive causative make, require a verbal passive and use the primary specification selected above. Preserve the valid active bare form and the valid passive to-infinitive. |
| COMP-062 | Legacy 6.9 has tree and token paths for gerund versus infinitival complementation, including enjoy. | Share a finding when both paths identify the same enjoy complement. Scope the Cambridge rule to the action complement and preserve ordinary nominal objects. |
| PHR-197 and COMP-087 | Matrix C-ARTICLE handles article omission, while these specifications both cover a bare singular count role noun as a referential object. | Use COMP-087 as the primary specification for this role-object case and retain PHR-197 as supporting material. Preserve role predicatives after verbs such as appoint and titles before personal names. A missing determiner does not by itself identify the intended definiteness. |
| MORPH-141 and OTH-726 | Matrix C-ARTICLE-MISMATCH and the existing article helper choose between a and an. OTH-726 adds the parenthesised next-sound case. | Treat these as a general condition and a scoped extension. Use the first pronounced sound, including inside a parenthesised modifier read aloud. Keep pronunciation and variety alternatives. Missing articles belong to a separate finding. |
| CLS-130 | Legacy 6.15 C-IMPERATIVE-VERB checks imperative verb form. Some catalog examples have an ordinary declarative reading in isolation. | Require an independently supported directive reading before proposing an edit. Keep valid overt-subject declaratives and avoid inferring imperativity from a third-person ending alone. |

The matrix's finding merge can choose a displayed remediation and suppress particular duplicate cases, but its node-level grouping does not establish that two rules describe the same governing relation. The Phase C test cases should verify one finding for each equivalent relation and preserve separate findings when the required repairs differ. The rows above are a static implementation review. They do not assert parser coverage on the catalog examples.

## Representative overlap probes

Run `python scripts/audit_cgel_overlap_probes.py --matrix` in the configured parser environment to compare the legacy collector and matrix on the same parser trees. Add `--fixtures` to use hand-authored constituency trees for local development. The report contains legacy findings, matrix verdicts, node errors and attached findings. The inactive Cambridge candidate probe is outside this measurement.

| Fixture probe | Observed legacy errors |
|---|---|
| Modal followed by infinitival to | One, C-MODAL-TO |
| Active causative make with infinitival to | One, C-CAUSATIVE-TO |
| Enjoy with a to-infinitival action complement | One, C-GERUND-INFINITIVE |
| Modal followed by goes | Zero |
| Passive causative make missing to | Zero |
| Six controls covering a plain modal complement, ought to, modal coordination, both licensed make forms and a nominal enjoy complement | Zero |

### Configured parser and matrix results

GitHub Actions ran the 11 development probes with the configured parser on PR #103 at `f202b013`. [Parser evidence](https://github.com/ybcole/SynTutor/actions/runs/43215151582/artifacts/13942139723) · [Parser-backed CI](https://github.com/ybcole/SynTutor/actions/runs/43215151582) · [Model-free CI](https://github.com/ybcole/SynTutor/actions/runs/43215151598)

| Probe | Legacy collector | Matrix | Phase C follow-up |
|---|---|---|---|
| She can goes. | No finding | Ungrammatical. `C-AUX-FORM` at *can* and `C-MODAL-VERB-FORM` at *goes* both propose *go*. | Treat the two nodes as evidence for one modal–complement relation under COMP-034. |
| She can to go. | `C-MODAL-TO` | Ungrammatical. Node errors at *can* and *to* both propose deleting *to*. | Keep a single relation-level finding with the deletion as its edit. |
| She made him to wait. | `C-CAUSATIVE-TO` | Ungrammatical. The matrix proposes deleting *to*. | Preserve the active repair and keep it distinct from passive insertion. |
| We were made wait outside. | No finding | Grammatical verdict, with zero node or attached errors. | Prioritize passive causative *make* as missing matrix coverage. |
| She enjoys to run. | `C-GERUND-INFINITIVE` | Ungrammatical. Node errors at *enjoys* and *to* propose the same change. | Consolidate at the selecting verb and action complement relation under COMP-062. |
| Six valid controls | No findings | All six received grammatical verdicts with zero node or attached errors. | Keep all six as development guards and add held-out cases. |

The matrix found four of the five intended errors. The parse API uses its verdict and node details for legacy feedback. The two modal nodes and the two *enjoy* nodes demonstrate overlapping evidence in the payload. This audit did not measure how many cards the interface renders or evaluate the full API, paragraph correction, or held-out accuracy.

### Source checks and next implementation

- **Modal complement form (COMP-034).** CGEL printed p. 106 (PDF p. 126) lists the plain form after a modal and describes central modals as taking bare infinitivals. The source scope supports both modal repairs in the probes. Retain separate edits for inflection and an inserted *to*.
- **Passive causative *make* (CLS-357, supported by CLS-1451).** CGEL printed p. 1234 (PDF p. 1254) explicitly contrasts the active bare infinitival and the passive to-infinitival. Printed p. 1432 (PDF p. 1452) corroborates the alternation. For the first candidate, require evidence of a verbal passive of causative *make* and its selected bare infinitival. Propose inserting *to* before the complement, then reparse. Guard the active bare form, the correctly marked passive, lexical *make*, and purpose clauses. Use one finding keyed to the governing relation and keep both source citations.
- **Page accounting.** The ledger check reports 1,716 extracted pages, 46 documented skips and zero unprocessed pages across 1,764 printed pages. The two pages absent from the split-source set, pp. 70 and 524, render blank at PDF pp. 90 and 544 in the supplied full volume. Their ledger entries preserve the split-source provenance and record the full-volume status.

These targeted source checks leave the independent review, Burton-Roberts crosswalk and held-out evaluation requirements in place. The Cambridge runtime registry still contains zero enabled rules.

### Phase C passive causative candidate

`server/cgel_passive_make_candidate.py` checks a narrow constituency pattern: a form of *be* over a VP headed by participial *made*, followed directly by a bare VP with a plain-form verb. It records the two source citations, governing relation, exact character spans, and an insertion hint. A matching parse is provisional evidence. The probe abstains on unresolved token alignment and quotation scope, and leaves intervening material, coordination and other passive structures for a later pass.

Run `python scripts/audit_cgel_overlap_probes.py --matrix --passive-candidate` with the configured parser. The PR workflow records the parser shape for the known miss, and reparses any proposed correction to record the candidate and matrix outcomes. Fixture tests exercise the intended repair, an embedded passive under a perfect auxiliary, and guards including active causatives, correctly marked passives, purpose infinitivals, predicative adjectives and coordinated complements. A reparse and an empty candidate list alone do not establish grammaticality or safe automatic correction.

### Held-out evaluation of passive causative make

The unchanged candidate ran on 28 original sentences with the configured parser at commit `12be467`. The corpus and expected edits were frozen before the run. [Per-case parser evidence](https://github.com/ybcole/SynTutor/actions/runs/43226736740/artifacts/13947677657)

| Group | Cases | Observed result |
|---|---:|---|
| Be-passive errors | 8 | 4 exact edits. The repaired sentences reparsed with no residual candidate. |
| Stress cases | 4 | 0 edits for a get-passive, an inverted question, an intervening adverb and a coordinated complement. |
| Valid controls | 16 | 14 evaluated with no candidates. Two quotation examples were skipped by the quotation guard. |

Two be-passive misses had a bare verb in the parse but did not meet the required tree shape. The negative included a separate negation node and the agentive by-phrase added a sibling after the lexical VP. The other two missed be-passive cases were analysed as nominal or adjectival rather than verbal. Preserve these cases as regressions. For the next iteration, start with the two misses where the parser already supplies verbal evidence, retain abstention for ambiguous analyses, and use a fresh held-out set to measure the revised candidate.

### Burton-Roberts crosswalk source check

| Structural question | Third-edition source | Implication for CLS-357 |
|---|---|---|
| What licenses the participle in the passive? | Burton-Roberts pp. 119–120 distinguishes passive *be* (PASS) from progressive *be* and uses participial form as evidence. Pp. 125–126 covers promotion of the active object and an optional agentive by-phrase. | A validated PASS relation can support the passive part of the candidate. A Penn VBN tag alone supplies weaker evidence. |
| How is the infinitival contrast represented? | P. 226 uses active causative *make* in example [4] to illustrate the bare form. It represents *to* as a [-tense] auxiliary in [11]. P. 239 provides another active causative in [86] and pp. 240–242 discuss how the intervening NP may relate to the clauses. | The forms are structurally comparable. Cambridge pp. 1234 and 1432 supply the specific requirement for *to* after passive causative *make*. The inspected Burton-Roberts passages supply supporting structural evidence for the crosswalk. |

The Phase C probe currently operates on constituency parser nodes. A production crosswalk still needs an independently checked canonical B-R relation for passive causative *make* and its selected non-finite complement. The catalog mapping stays `unverified` and the registry stays empty. [Burton-Roberts, *Analysing Sentences*, third edition](https://lmsspada.kemdiktisaintek.go.id/pluginfile.php/1032828/mod_resource/content/2/Introduction%20to%20English%20Syntax.pdf)

### Negation and agentive by-phrase follow-up

The candidate now accepts an explicit *not* between the passive auxiliary and its VP and a trailing *by* + NP within the VP headed by *made*. The complement must still be a bare VP headed by a verb in the parse. The proposed insertion remains immediately before that verb, preserving the negation and by-phrase.

On commit a80993c, the original 28-case set now produced 6 exact repairs out of 12 errors, up from 4. Both newly covered cases reparsed without a remaining candidate. The 14 evaluated controls still produced no findings, and the two quotation guards still abstained.

The fresh 22-case set produced 9 exact repairs out of 10 errors, with zero candidates on all 12 evaluated controls. All 9 edits reparsed without a remaining candidate. The one miss was in the combined negation and by-phrase group, where the parser tagged verbal *empty* as an adjective. Keep this miss as a regression and require positive evidence of a verbal complement before attempting to recover it. The new evaluation is focused on the two modifier patterns. Production activation remains disabled. [Parser evidence](https://github.com/ybcole/SynTutor/actions/runs/43227709691/artifacts/13949045993)

### Registry-gated passive make evaluator

The evaluator supports a clause-scoped `passive_make_missing_to` check for CLS-357. It requires explicit standard-English scope, matching parser evidence, and a normalized canonical tree linking the PASS node, both verbs, the subordinate clause, and the promoted subject's index. A finding identifies the original character span and both verb nodes. The insertion remains a hint requiring reparse.

Synthetic allow-list tests exercise the gate and the positive case, the marked passive, stale or missing parser evidence, unresolved crosswalks, and an unrelated rule ID. The actual CLS-357 catalog entry stays spec-only and the production registry stays empty. Independent review of the mapping and a learner-facing explanation are still required before rollout.

### CLS-357 independent review handoff

| Review item | Evidence to inspect |
|---|---|
| Source scope | CGEL p. 1234, Ch. 14 §5.4 gives the active bare and passive to-infinitival alternation. Ch. 16 §10.1.2, p. 1432 corroborates the passive. Review the distinction between causative and lexical *make* and the standard-English scope. |
| Canonical mapping | Burton-Roberts, 3rd ed., pp. 119–120 and 125–127 for PASS and object promotion, and pp. 226 and 238–240 for bare infinitivals and lower-clause structure. Check whether the indexed object and lower subject positions in the proposed projection are justified by those conventions. The Cambridge constraint supplies the repair. |
| Parser evidence | The canonical audit linked the relevant clause and both verbs for all 15 detected cases across the two sets. Inspect the missed nominal/adjectival parser readings, inversion, coordination, and other stress cases before deciding the allowed scope. [Canonical parser evidence](https://github.com/ybcole/SynTutor/actions/runs/43230525553/artifacts/13949698061) |
| Learner text | Review template `CGEL-CLS357-PASSIVE-MAKE-V1` and both Cambridge source records. Test-only approval exercises the explanation on *made* and the following verb in the selected sentence, with the two printed-page references. |
| Activation | Record the independent reviewer and their disposition before changing the catalog, template or runtime allow-list. The API requires explicit `standard_english` for this check. The Generator sends this value when a learner selects Standard English under English variety. Unspecified leaves the variety unset. Switching sentences keeps the selection. |

The parser-backed API regression selects the second sentence of a two-sentence passage. Its test-only approval fixtures exercise the same registry snapshot for the evaluator and explanation. The test checks the sentence-local insertion, source pages, matching nodes, valid first sentence, absent variety and disabled production registry.


### Adjacent modal follow-up

The configured parser evaluation at `2f0339d6` produced six exact repairs across six adjacent COMP-034 cases, with canonical node alignment and zero remaining modal candidates after reparse. The two recovered cases had been tagged as plain verbs. The revised candidate requires a single attested third-person paradigm and excludes an independently attested plain form. Ten valid controls ran without a flag and the quotation control abstained. Negation, inversion, and intervening adjuncts remain outside the adjacent relation. [Parser evidence](https://github.com/ybcole/SynTutor/actions/runs/43330321727/artifacts/13993474759)

### Enjoy action-complement evaluation

Printed p. 221 (PDF p. 241) uses an unlicensed to-infinitival after *enjoy* to illustrate complement selection. The inactive COMP-062 probe requires a direct subjectless infinitival in the constituency tree, adjacent source spans, and an attested gerund-participial replacement. A candidate covers the selecting verb and the lower verb as one relation. Nominal complements, purpose clauses accompanying an object, and embedded infinitivals inside an otherwise licensed complement serve as controls.

Run `python scripts/audit_cgel_overlap_probes.py --enjoy-evaluation` to measure the 16 frozen cases with the configured parser. The report records exact edits, reparse results, and canonical alignment where available. The split infinitive and coordination stress cases are outside the first implementation. Production licensing and the canonical crosswalk remain pending.
