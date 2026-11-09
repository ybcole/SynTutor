# SynTutor — master plan for Burton-Roberts labels and book-grounded per-node XAI

**Proposed specification, 9 November 2026. No automatic relabeling approved by this document.**  
**Book:** Noel Burton-Roberts, *Analysing Sentences: An Introduction to English Syntax*, third edition, Pearson/Longman, 2011, ISBN 9781408233740. Verify claims against the user's compiled `Syntax_Reference_Chapters_1-11.pdf` with **printed page** and actual figure, not just PDF text extraction.

This plan operationalizes [`CONVENTIONS.md`](../../CONVENTIONS.md), the [source-authority matrix](../source-authority-matrix.md), the [canonical tree schema](../canonical-burton-roberts-tree.schema.json) and existing [source review](../../sources/burton_roberts/reviews/2026-11-08-conventions.json). The complete working inventory is an accompanying spreadsheet **SynTutor_BR_Labeling_XAI_Master_Sheet_2026-11-09.xlsx** (12 profiles, 53 node cases, 27 crosswalk gates, 12 conflicts, 53 original node-XAI drafts, sentence-attested examples and approval checks). This repository plan **does not imply** that spreadsheet review has been approved or deployed.

## Decision 1 — Separate three different authorities

1. **Candidate parse:** spaCy + Benepar produces tokens, character offsets, Penn-style labels and a parse tree. Keep it unchanged as parser evidence and diagnostic fallback. Benepar does not decide B-R labels.
2. **Canonical B-R representation:** a *profile-scoped, source-justified transformation* creates B-R nodes, structural edges, empty positions, movement, features and accepted alternatives. Validate against the canonical schema and chapter rules. Each derived node must retain the source/transform rule IDs that justify it.
3. **Source-licensed explanations:** an XAI composer computes observable facts from each validated B-R node, then applies a reviewed paraphrase template backed by B-R chapter and printed page. Cambridge is reserved for independently reviewed grammatical descriptions/constraints and must not rename B-R phrase-marker categories.

**Never implement a universal Penn-label replacement map.** Even though `ADJP→AP` and `ADVP→AdvP` may be conditional category aliases, `SBAR→S′`, `SBARQ→S″`, `DT→DET`, `NP→NOM` and flat `VP→VP` are not valid string-only transformations.

## Decision 2 — Version the conventions by the lesson and construction

| Profile | Book introduction / active notation | Mandatory distinction |
| --- | --- | --- |
| V1 / Ch1 | `Sentence`, `PHRASE-x`, triangles | Do not retroactively assign NP/VP categories |
| V2 / Ch2 | `S→NP VP` (pp.29–30) | Subject/predicate are functions, not tree labels |
| V3 / Ch3 | `N, A, Adv, P, DEG, AP, AdvP, PP`, `name`, `pronoun` | NP internals are not yet DET/NOM |
| V4 / Ch4 | lexical `V` with six subcategorization features | A V's complements are sisters of V |
| V5 / Ch5 | extra VP for adjuncts; S-adverbials, `Prt`, ellipsis `E` | VP adjunct vs V complement is a structural distinction |
| V6 / Ch6 | auxiliary-headed VPs (`MOD/PERF/PROG/PASS/TENSE`), `S-bar→C S` in relevant questions | Ch6 `C` is the landing position for fronted auxiliary |
| V7-CORE / Ch7 | `NP→DET NOM`, recursive `NOM`, ART/DEM/Q/POSS/PRE-DET | Proper names/pronouns can have nonbranching NPs; empty DET is possible |
| V7-APPENDIX-D1 | alternative higher NOM adjunct layer | Explicit variant; do not change V7-CORE gold shapes |
| V8 / Ch8 | `S-bar→C S` for subordinate clauses (p.174) | Overt or absent C; some P+S structures are not S′ |
| V9 / Ch9 | `S-dbar→C2 S-bar` and `S-bar→C1 S` (pp.198–199) | Higher C2 houses fronted wh expression; typed gap; lower C1 houses aux/subordinator or is empty |
| V10 / Ch10 | `[-tense]` nonfinite VP, covert NP/index/control, V(I)/V(II) | No automatic six-way valency for clause complements |
| FINAL-D1 | accumulated V10 + selected Appendix D1 refinement | Target for free analysis, **not** proof arbitrary Benepar output can convert |

**Storage vs display:** store canonical `S-bar` and `S-dbar`, render them as **S′** and **S″**. Store `C` for V6–V8 and `C1`/`C2` for V9+. Use book `AP` and `AdvP`, not Penn `ADJP` and `ADVP`. Do not confuse the Chapter 8 `C` position with a determiner spelled *that*.

**S-bar evolution:** This is an intentional extension of the book's descriptive apparatus, not inconsistent naming. `S′` introduced for auxiliary inversion is also used for embedded clauses; Ch9 adds `S″` as an additional, higher position for wh-fronting. It is **not** appropriate to change every `S′` to `S″` in later chapters.

## Decision 3 — Transform structures, not pixels or superficial labels

Recommended normalized API shape:

```json
{
  "parser_candidate": {"tree": "untouched Penn-style parser result"},
  "br_analysis": {
    "status": "normalized | unresolved | rejected",
    "convention_profile": {"version": "V9", "chapter": 9, "profile_id": "V9"},
    "tree": "validated canonical B-R envelope or null",
    "derivations": [
      {"node_id": "n1", "operation": "CREATE_S_DBAR", "rule_id": "BR-CW-16",
       "source": {"book": "B-R", "chapter": 9, "printed_page": 199, "figure_id": "11b"}}
    ],
    "reasons": []
  }
}
```

In real code the source fields and tree must use existing schema definitions; the JSON above illustrates the **separation of concerns**, not a new committed API schema. If `br_analysis.status != normalized`, show the parser graph clearly as a **Benepar diagnostic candidate**, not a B-R phrase marker.

Crosswalk priority:

1. Exact, unique, source-reviewed B-R figure match in the **selected profile**, retaining original labels and accepted alternatives.
2. Tested contextual aliases for genuinely equivalent categories and spans.
3. Guarded structural rewrite (NP→DET/NOM, auxiliary VP layers, complementiser/wh layers, gaps, indices), with a proof trace for each created node.
4. If any required lexical, structural, alignment or provenance check fails: **ABSTAIN**, preserve the parser tree and record a specific reason.

## Decision 4 — XAI must explain *every licensed node* using exact sentence spans

Existing implementation: [`grammar/explanation_templates.json`](../../grammar/explanation_templates.json) contains **two reviewed templates**, one B-R `S→NP VP` explanation and one Cambridge sentence/clause teaching note. [`grammar/concepts.json`](../../grammar/concepts.json) contains lexical/grammatical concepts, not 1:1 B-R node explanations. [`web/content/lessons/course.json`](../../web/content/lessons/course.json) has source-cited lesson prose and examples, also not a general-purpose node-template registry. The current [`server/explanations.py`](../../server/explanations.py) allows only `label, surface, sentence, node_id, rule_id` slots—insufficient to explain sibling, head, complement, controller or movement relations.

For **each node** in an accepted B-R tree, compute facts *server-side*:

```json
{
  "node_id": "n23",
  "label": "NOM",
  "profile_id": "V7-CORE",
  "surface": "sad clowns",
  "token_span": [1, 3],
  "parent_label": "NP",
  "parent_surface": "the sad clowns",
  "head_word": "clowns",
  "modifier_surface": "sad",
  "child_labels": ["AP", "N"],
  "functional_role": "nominal",
  "source_record_id": "book-example-or-source-review-ID",
  "applied_conversion_rule_ids": ["BR-CW-03"]
}
```

Those are **observations from a validated structure**; they are not themselves proof of grammaticality. Bind them to a *chapter-specific template*:

> In the NP “the sad clowns,” NOM covers “sad clowns.” The adjective phrase “sad” modifies the noun “clowns” at this nominal level. **Source:** Burton-Roberts, Chapter 7, relevant verified figure and printed page.

The example above is **original proposed wording**, not a reviewed production template or a claim that the example matches a particular book figure. A template must have its own ID, approved source claim, exact figure/page, applicable profile/conditions, exception handling, independent reviewer and test fixture. Claim-bearing text must use reviewed templates, **not the raw Benepar tag or a guessed LLM rationale**.

Output for each selected node should include two separately labeled sections:
- **Observed B-R structure:** exact sentence words, dominance, immediate children, head/modifier/complement where justified, and whether it is a triangle/gap/empty position.
- **Why this representation follows the book:** the matching reviewed template with printed-page citation. If none applies, show `NO_BOOK_BASIS` rather than create a claim.

For a normalized B-R tree, aim for **100% node coverage** (including terminals, triangles, empty positions, traces, non-finite/aux features) by developing source-reviewed templates, not by generating one generic explanation. An unsupported free-form sentence gets a diagnostic explanation of observed parser output, explicitly *not* B-R source-approved XAI.

## Decision 5 — Acceptance and implementation order

1. **Approve profile and notation conflicts**, especially S′/S″/C/C1/C2, the two NOM profiles, ellipsis vs movement gaps, and source figure alternatives. The owner must choose the default user experience.
2. **Make a machine-readable master crosswalk** from the spreadsheet with source IDs, structural predicates, applicability boundaries, negative examples, status and independent approval. Keep it distinct from the legacy 111-rule matrix and Cambridge grammaticality registry.
3. **Audit at least several B-R figures per chapter** and distinguish evidence from actual printed book diagrams vs derivations from book instructions. Record original tree, source page, figure, review status, ambiguity and accepted alternative.
4. **Build the structural converter** in small, versioned units (start V2 basic; V3 simple AP/PP; V4–V6 VP layers; V7 NP; V8–V9 clause layers; V10 nonfinite/control), preserving raw Benepar and explicit abstention.
5. **Build and review one contextual node template per label/use**, then bind it to validated facts and a source page. Existing reviewed templates do not authorize all later nodes.
6. **Golden regression and counterexamples:** compare full hierarchy and features, not label strings; test `that` as DET vs C, `to` as P vs nonfinite aux, unlabelled wh triangle, empty C1, nested VP adjunct, NOM appendix and ambiguous source trees.
7. **User-testing and staged rollout:** learners inspect a real sentence and every node's source citation; keyboard access and an "unresolved" state are mandatory. Deploy behind a feature flag only after recorded approval and rollback.

**Acceptance rule:** a case ships only if `profile_supported && transform_validated && source_reviewed && every_node_has_valid_xai_or_explicit_no_basis && tests_green && reviewer_approved`. Target full XAI coverage by *completing reviews*, not by silently converting `NO_BOOK_BASIS` into confident prose.

## Current repository impact and ownership

- The earlier [M12 draft PR #43](https://github.com/ybcole/SynTutor/pull/43) already contains exploratory canonical-display and XAI UI changes. Treat them as **experimental** until this specification and their matching golden tests are approved. This spec is a **separate docs-only PR**, not a merge of that implementation.
- The final master checklist should **not** be marked fully complete on the strength of this plan. Human book-source review, chapter conversions, independent learner XAI review, Clerk/Supabase staging, and production deployment gates are separate pieces of evidence.
- Practical first implementation after approval: V2 `S→NP VP` and two contextual node explanations (subject NP and predicate VP) from pp.29–30, in addition to the existing S template. Build outward by independently reviewed book chapters.
