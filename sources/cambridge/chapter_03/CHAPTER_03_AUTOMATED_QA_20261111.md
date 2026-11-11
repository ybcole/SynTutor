# Cambridge Chapter 3 — Cross-domain QA and Phase C candidate readiness

**Date:** 2026-11-11  
**Scope:** CGEL Chapter 3, printed pp. 71–212, against the supplied complete 1,862-page PDF and committed SynTutor rule files.  
**Gate:** machine-checkable integrity + targeted primary-source spot checks; **NOT** independent linguistic adjudication of every rule or live detector activation.

## I. Verifiable source/accounting inventory

- The ledger accounts for **142** chapter pages: **139 extracted expository pages** (74–212) and **3 chapter-contents-only skips** (71–73). No Chapter 3 page remains unprocessed.
- SynTutor's **887-record catalog contains 695 rule records citing Chapter 3** across *agreement, clauses, complementation, morphology, other, and word_categories*; this includes **691 newly extracted records** plus 4 previously approved legacy records. It is incorrect to audit only `other.json`.
- Across the 695 Chapter 3-linked rules, the types are **574 classifications**, **69 descriptive generalizations**, **38 constraints**, **8 stylistic/prescriptive reports**, and **6 variety-restricted entries**.
- Lifecycle: **691** new records remain `NEEDS_REVIEW`; **4** preexisting records are `APPROVED`. This distinction is preserved, with no new owner approval inferred.
- **All 695** still have *unverified* Burton-Roberts crosswalks. The current Cambridge runtime allow-list is empty. **0 new live CGEL detectors** and **no measured precision/recall** are asserted.
- Of the error-capable records, **34 constraint specifications** and **1 Standard-English variety-restricted error specification** have `spec_only` diagnostic blocks, i.e. **35 candidate checks**. Four older approved constraints — `AGR-002`, `MORPH-004`, `MORPH-005`, `MORPH-006` — still have **no diagnostic block**. Their approval is not the same as runtime readiness.
- One source-index inconsistency was repaired: the four legacy records' Chapter 3 printed **p. 75** citation formerly used **p. 5** of a *chapter-split* PDF as `pdf_pages`. The full 1,862-page source uses **one-based PDF p. 95** for printed p. 75. These four locators have been normalized. Their linguistic claims and approval states have **not** been rewritten. Other chapters' split-local PDF references remain outside this Chapter 3 fix.

## II. Primary-source checkpoint audit (not a substitute for a full semantic review)

The following high-risk source claims were checked against the user's complete PDF and compared with the stored source-linked Cambridge records. These are short paraphrases, not transcriptions of book prose:

| Printed CGEL page(s) | Rule IDs / issue | Directly checked exception or restriction | Consequence for Phase C |
|---|---|---|---|
| **75** | AGR-002, MORPH-004/005/006 | Core modal auxiliaries do not vary by subject person/number and lack the ordinary non-finite secondary forms; auxiliaries have special negative primary forms | Separate auxiliary vs lexical verb and rule out spurious third-person modal agreement errors |
| **107, 199** | CLS-119, OTH-453 | A **genuinely remote** conditional consequent needs a modal auxiliary; an open conditional does not | **Same principle at two printed sites**; cross-link records and deduplicate any future same-span detection |
| **141** | OTH-098 | The past preterite does not locate a state as continuing up to the present under *ever since*; perfect aspect is licensed | Distinguish present-inclusive continuation from a finished past interval |
| **143–146** | OTH-102 | Definite completed-past adjuncts such as *yesterday* normally disallow the present perfect **but exceptions exist**: an *already*-marked experiential reading can override the exclusion on p. 145 | A blanket string rule “have + yesterday = error” would be unsound |
| **156** | OTH-158 | In one backshifted report, a sequence beginning unshifted cannot then switch back to preterite solely for that same reporting link; relevance to current deictic time is contextual | Do not flag unrelated independently past events or a different embedded temporal relation |
| **161** | OTH-182 | Infinitival perfect is possible with some catenatives, but not with temporally inseparable *begin* and causative *make* | Predicate identity and temporal selection must be established before flagging |
| **167–168** | OTH-216 | A strongly stative containment/composition predicate rejects ordinary progressive in a *purely fixed* state, but progressive may convey a genuinely dynamic reinterpretation | Require stative/dynamic reading rather than banning all progressive forms of a lexical item |
| **191** | OTH-377 | Future-oriented temporal adjuncts use present rather than pure futurity *will*; conditional antecedents permit special predictability/volition uses | Distinguish a temporal adjunct from an embedded interrogative or modal conditional |
| **197** | OTH-439 | Positive past *could* cannot normally assert one completed, perfectively viewed success, whereas habitual capacity, negatives and ongoing perceptions remain allowed | A simple occurrence of *could* is never an error test |
| **200** | OTH-458 | An unreal finite complement of *wish* normally requires the remote preterite; a separate *hope* construction is not governed by that requirement | Identify the matrix predicate, complement boundaries and intended remoteness first |
| **211–212** | OTH-570–OTH-601 | *Be going to* has more matrix-time focus than *will*, but permits distant plans; *was going to* does not entail eventual completion, unlike special formal narrative *would* | Keep semantic/register differences explanatory, not corrective |

The checkpoint process did **not** mechanically prove every one of the 695 paraphrases true. It specifically guards against broad false-positive rules in future detectors. It does not change the `NEEDS_REVIEW` status.

## III. Resolved cross-references, not duplicate activation

- Linked **CLS-119 ↔ OTH-453** (remote-conditional apodosis obligation; printed pp. 107 and 199).
- Linked **CLS-100 ↔ COMP-030** (the supportive *do* / second-auxiliary constraint; printed pp. 93–94 and 105).
- Both pairs remain separate source records; they must not independently multiply a single learner error in any future XAI output. They remain specification-only; no parser implementation or approval was inferred.

## IV. Candidate-only evaluation corpus

A reproducible seed corpus is generated by `tools/audit_cgel_ch03.py` from the **35** Chapter 3 rule diagnostic blocks, using original wrong/corrected minimal pairs, stored false-positive guards, and original correct sentences. No textbook examples are newly copied into the corpus.

**Committed file:** `evaluation/cgel_ch03_candidate_corpus.json`. **277 candidate cases**, distributed as follows:

| Family | Candidate error cases | Valid/guard cases | 10 wrong / 10 valid gate |
|---|---:|---:|---|
| word_order | 22 | 58 | Count threshold reached; not independently adjudicated |
| verb_form | 18 | 51 | Count threshold reached; not independently adjudicated |
| tense_aspect | 16 | 58 | Count threshold reached; not independently adjudicated |
| missing_word | 6 | 20 | **4 additional error examples needed** |
| extra_word | 6 | 15 | **4 additional error examples needed** |
| article_determiner | 2 | 5 | **8 additional error and 5 valid examples needed** |

Total: **70 proposed wrong/corrected pairs** and **207 candidate valid or guard cases**. These are **source-derived development candidates**, not held-out gold-standard annotation. Counts meeting the numeric threshold do **not** establish accuracy or coverage; no detector was run on these candidates to report precision or recall.

## V. Executable gates and remaining blockers

The new `tools/audit_cgel_ch03.py --check` runs in CI and fails if Chapter 3 pages, evidence paths, source page offsets, unique rule IDs, type/severity boundaries, required minimal pairs, false-positive guards, or the generated candidate corpus drift out of sync. `tools/test_cgel_ch03_qa.py` tests these invariants and the cross-referenced duplicate rules. Its runtime safety check prevents new `NEEDS_REVIEW` or `spec_only` records from silently entering the Cambridge enable-list.

Outstanding **Phase C** gates, *not claimed complete*:

1. Independent adjudication of each scoped constraint and its source exceptions across all 695 Chapter 3 references. A successful structural audit does not substitute for this.
2. Resolve Burton-Roberts crosswalks; all 695 are still unverified and therefore **cannot pass the existing runtime registry eligibility gate**.
3. Migrate the four legacy approved constraints lacking diagnostic blocks without inventing unsupported corrections or bypassing their review lifecycle.
4. Implement source-aware, construction- and variety-sensitive deterministic checks with token/character spans, both governing relation tokens, diagnostic IDs and safe corrections.
5. Convert development candidate examples into a genuinely adjudicated held-out coverage set, fill the remaining per-family gaps, and **measure** false positives and recall only after implementing real detectors.
6. Preserve the XAI PRE/4–7 constraints that partial checker output must never certify the whole sentence as correct; Phase D must reparse and reevaluate interacting edits.

**Result claimed by this batch:** source-page accounting already complete; 695-record **automated structural quality audit**, 11 targeted printed-page checkpoints, four corrected legacy full-volume locators, explicit overlapping-rule links, and a candidate-only English evaluation corpus. **No newly enabled detection or independent expert approval is claimed.**
