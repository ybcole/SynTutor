# XAI-1 Acceptance — English-only B–R/Cambridge Source Concept Registry

**Date:** 10 November 2026  
**Milestone:** XAI-1 (source concept registry and rule/claim provenance)  
**Status:** **XAI-1 technical implementation and regression checks complete**: 27 model-free concept tests, the source-coverage audit, and the existing parser/browser suites passed. Independent human/instructor linguistic approval remains pending, so no catalog candidate has been enabled in the learner-facing XAI runtime.  
**Branch:** `feature/xai-1-source-concept-registry-2026-11-10`  
**Pull request:** https://github.com/ybcole/SynTutor/pull/54

## 1. Delivered scope versus later milestones

XAI-1 adds source-checked, typed **original explanatory paraphrases and example candidates** for future sentence-specific XAI. This milestone does **not** claim the student can now click any word to see a finished explanation or that SynTutor can correctly flag grammatical mistakes.

| Delivered now | Deferred with explicit review gate |
| --- | --- |
| [English-only concept catalog](../../grammar/xai_concepts/catalog.json): **42** source-page-checked candidates (29 B–R, 13 Cambridge) | An independent human/instructor linguistic review of each claim, exception and example |
| [Strict JSON Schema](../../grammar/xai_concepts/catalog.schema.json) and [fail-closed semantic validator](../../server/xai_concepts.py) | XAI-2: extracting verified head/sister/subject/object/feature relationship facts from each actual canonical tree |
| **Eight** explicit cross-framework mappings including real conflicts and unresolved comparisons | XAI-3: approved, sentence-specific clickable word and constituent explanations |
| **21** distinct contextual template candidates, with required fact slots and source concept IDs | XAI-4: executable Cambridge grammar checks with exceptions/variety scope and independent human rule approval |
| [27 unit tests](../../server/test_xai_concepts.py) and [audit script](../../scripts/audit_xai1_concepts.py) | XAI-5: multiple-error corrections, full reparse and evolving interactive B–R trees |
| Model-free CI integration and pre-existing parser/browser regression suite | A complete, independently verified audit of **every page** in both books, which is not claimed here |

**No source claim in the new XAI-1 registry is marked human-approved.** The existing production registry in `grammar/explanation_templates.json` remains at two earlier teaching templates/four sources, and the Cambridge runtime registry still has **zero enabled constraints**. A targeted assistant source check does **not** count as independent review.

## 2. Actual source comparisons (printed page numbers)

These are **page-bounded primary-source checks** against the attached full volumes, not general textbook recollections or a claim of complete-chapter verification.

| Book and printed pages | Grounded concept families / specific cautions |
| --- | --- |
| B–R Third Edition (2011), **Ch. 2 pp. 29–33** | Basic `S → NP VP`, NP-subject vs VP-predicate, category distinct from function, head and modifier dependence |
| B–R **Ch. 3 pp. 50–53** | Noun head determines NP category; pronouns and names can be complete NPs |
| B–R **Ch. 3 pp. 54–57** | AP/AdvP heads, degree adverbs, PP headed by P with optional NP complement, source-specific one-word locative/temporal PPs |
| B–R **Ch. 3 pp. 58–60** | Coordinated NPs and introductory same-category coordination criterion |
| B–R **Ch. 4 pp. 69–72** | Verb-complement subcategories, `[trans]` object, intransitive VP, ditransitive indirect/direct objects, optional PP modifier |
| B–R **Ch. 6 pp. 116–118, 121–122** | Lexical vs perfect auxiliary *have*, participle forms, nested auxiliary VPs selecting VP complements |
| B–R **Ch. 7 pp. 141–143** | DET + NOM branching NP, NOM modifications, articles, licensed empty determiner for plural count/mass nouns |
| Cambridge 2002, **Ch. 2 pp. 44–46** | Clause versus sentence; **Cambridge does not use S as its syntactic tree category**; noncanonical question/passive is not an error; unlike-category coordination can occur in its framework |
| Cambridge **Ch. 3 pp. 75–76, 105–106** | Modal inflectional restrictions, preterite/participle syncretism, auxiliary ordering and selected verb forms |
| Cambridge **Ch. 3 pp. 143–144** | Definite-past adjuncts normally excluded with present perfect, **but restricted experiential exceptions exist**; no simplistic `perfect + yesterday` error rule |
| Cambridge **Ch. 4 pp. 219–221** | Valency and transitivity differ; selected NP/PP/clausal complements depend on lexical licensing; **some complements are optional**, so absence is not always an error |

### Book-framework differences that must survive into XAI-2/3/4

1. **Sentence vs clause:** B–R's phrase marker uses `S`; Cambridge explicitly reserves `sentence` for text-level units and has `clause` as a syntactic category. **Crosswalk: `analysis_differs`**, not interchangeable labels.
2. **Coordination:** B–R Ch. 3 presents same-category coordination as a teaching test; Cambridge p. 45 discusses coordination of an NP with a clause. **Crosswalk: `analysis_differs`**; never use a blanket different-category-equals-error rule.
3. **Complement and valency:** both discuss verb selection, but CGEL distinguishes core versus non-core complements, optional complements and different subcategorization criteria. **Crosswalk: `terminology_differs`**, further structural conditions needed.
4. **Perfect forms:** B–R *perfect participle* vs CGEL *past participle* for the specifically reviewed perfect auxiliary selection context. **Crosswalk: `terminology_differs`**; no automatic conversion of all labels.
5. **Progressive forms:** B–R *progressive participle* vs CGEL *gerund-participle* in the selected progressive construction. **Crosswalk: `terminology_differs`**.
6. **Modal forms:** B–R *nonfinite stem* vs CGEL *plain form*, reviewed only for modal selection, not equivalent full syntax ontologies.
7. **Auxiliary tree hierarchy:** B–R auxiliary heads VP selecting another VP; CGEL ordering/form selection does **not** by itself settle identical tree representation. **Crosswalk: `unresolved`**.
8. **Aspect and time adjuncts:** B–R participle selection does not contain CGEL's full context-dependent tense/aspect semantics. **Crosswalk: `not_covered`**, never use morphology alone to condemn `yesterday`.

## 3. Design: how XAI-2/3 consume these candidates

A concept's identity includes `book_id`, chapter, **printed page** citation, claim kind, tree label/profile scope, construction preconditions, exceptions and optional alternatives, crosswalk, source-review status, original English explanation, positive/contrast/exception examples, and **disabled runtime flags**.

The separate template candidates specify a target node kind and label, required **licensed fact keys**, a short sentence-contextual explanation and a deep/conditional rationale. Examples:

| Clicked node (future) | Candidate principle | Facts required before rendering |
| --- | --- | --- |
| Subject `NP` of *I hate you* | "The NP *I* functions as subject of the predicate *hate you*." | Exact NP span; immediate S dominance; sister VP span; approved B–R construction |
| Object `NP` of *I hate you* | "The NP *you* functions as the object of transitive verb *hate*." | Exact node ID; verified `[trans]` V; sister NP in licensed VP |
| `VP` in *She had eaten* | "The perfect auxiliary heads an outer VP containing an inner VP." | B–R auxiliary head and its VP complement, not just English word order |
| `NP` in *The red car stopped* | "DET and NOM occupy different constituents of this NP." | Exact DET/NOM daughters and printed-page-backed B–R profile |
| `PP` in *The cat slept beside the window* | "The preposition *beside* heads this PP, selecting the NP *the window*." | Identified P head and licensed NP complement; separate attachment relation |
| `AdvP` *very quietly* | "The adverb *quietly* heads AdvP." | B–R Adv head and modifier relation, not merely suffix `-ly` |

These examples illustrate intended **future** explanations. They are not fabricated model outputs and are **not** activated by XAI-1. Every example in the data is marked `illustrative_not_parser_verified` so it cannot be mistaken for a parser-gold item.

## 4. Semantic validation and defenses

`server/xai_concepts.py` checks:

- complete JSON Schema with unknown fields prohibited, unique concept/crosswalk/template IDs;
- printed-page citations are valid within the **11 B–R** and **20 Cambridge** split-source chapter manifests;
- no client-supplied or review-forged runtime activation; original live explanation templates and Cambridge rule registry remain unchanged;
- exact B–R versus Cambridge book IDs, source-checked method, pending human signoff and disabled `can_diagnose`/`can_repair` flags;
- crosswalks link source concepts from **different books** in the correct order and explicitly prohibit silently changing B–R node labels;
- template categories fit their source concepts; fact placeholders are only approved flat identifiers, not arbitrary attribute expressions or template execution;
- English-only dataset scope is explicit. This metadata and limited negative probes do not constitute a statistical language-identification model.

`pending_by_node` exists solely as an **offline authoring query for later engineering work**; it returns a candidate, with `runtime_eligible:false`, not learner-facing book-certified feedback.

## 5. Verification and commands

```bash
python -m pip install -r requirements-test.txt
python -m unittest -v server.test_xai_concepts
python scripts/audit_xai1_concepts.py --require-valid --output artifacts/xai1-concepts.json
python -m json.tool grammar/xai_concepts/catalog.json >/dev/null
python -m json.tool grammar/xai_concepts/catalog.schema.json >/dev/null
```

The model-free GitHub workflow executes the above checks; the parser-backed/browser CI workflow verifies no regression in existing Generator, Builder, tree rendering or NLP installation. The source data itself is independent of network and model availability.

**CI evidence:** The model-free checks passed in [GitHub Actions run 42729333451](https://github.com/ybcole/SynTutor/actions/runs/42729333451), including all **27 XAI-1 contract tests** and the source-coverage audit. The existing parser-backed and browser regression checks passed in [run 42729333819](https://github.com/ybcole/SynTutor/actions/runs/42729333819).

**Measured catalog inventory:** 42 concepts (29 B–R, 13 Cambridge), 22 classification records, 15 descriptive generalizations, **five non-enabled constraint candidates**, **eight crosswalk records**, 21 authoring templates, **40 distinct cited printed pages across eight book chapters**, and 21 source-linked node/category labels. These are **source coverage counts**, not parsing accuracy or independently approved grammar-rule counts.

## 6. Explicit gaps / human decisions and XAI-2 handoff

**XAI-1 technical work:** the typed English-only catalog, exact printed-page audit, representative concept and original paraphrase candidates, cross-framework distinctions, fail-closed validator, tests and audit command have been implemented.

**Not yet independently signed off:** a qualified human/instructor's review of each linguistic interpretation, alternative analysis and exception, including the disputed coordination and sentence/clause analyses. Those claims cannot be promoted to live teaching without approval and XAI-2 structural evidence. Other book chapters outside the cited extracts are **not** represented as if they had been read and certified.

**Next step is XAI-2:** source-licensed parent/sister/head/feature/role fact graph and measured coverage against the English-only XAI-0 baseline, including exact node-span traces and ambiguities. XAI-3 then composes approved contextual prose; XAI-4 adds independently tested grammatical checks, and XAI-5/7 adds correction lineage and newly generated clickable B–R trees.

**Non-negotiable English-only scope:** no non-English or code-mixed example, training dataset or language-support claim is added. No production grammar model or runtime correction logic is changed.
