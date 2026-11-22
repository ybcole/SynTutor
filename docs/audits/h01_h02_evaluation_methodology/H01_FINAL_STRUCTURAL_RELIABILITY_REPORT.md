# SynTutor — H01 Final Structural Reliability Engineering & Independent Evaluation Readiness Report

**Thesis:** *SynTutor: An Explainable AI-Based Framework for Syntax Tree-Driven Grammar Analysis and Learning Using NLP*  
**Repository:** `/Users/kiyel/Desktop/SynTutor`  
**Branch:** `fix/syntutor-system-reliability-xai`  
**Date:** 2026-11-22  
**Scope:** Exclusive engineering remediation and architectural audit of **H01 (Burton–Roberts `FINAL-D1` syntax-tree generation)** while preserving H02 behavior, rules, and frozen Evaluations V1, V2, and V3 untouched. **No V4 evaluation has been constructed or executed** pending availability of independently verified, uncontaminated complete-tree Burton–Roberts gold references (per Phase VIII protocol).

---

## Executive Summary

1. **Engineering Remediation Complete (All 10 H01 V3 Failure Categories + 4 Newly Discovered Silent Structural Bugs):**
   - Resolved all nine previously unnormalized Evaluation V3 structural constructions (gerundial subject-control complements, coordinated `NML` premodifiers & fronted temporal NPs, subject-wh single-VP `SQ` questions, general transitive + stranded-preposition wh-extraction, shared-`DET` coordinated `NOM` subjects, non-overlapping passive + stranded-PP wh-interrogatives, extraposed noun-complement `that`/`whether` clauses with compound-particle nouns, Type I ECM vs. subject-control embedded wh-extraction with explicit structural ambiguity preservation, and sentential non-restrictive relative clauses) plus the `V3-G05` benefactive `for`-ditransitive low-attachment defect.
   - Simultaneously eliminated **four silent "plausible-but-wrong" structural errors** uncovered during the Phase I/III/IV audit: (a) extraposed noun-complement clauses misanalyzed as transitive verb objects (`V3-G39`: *A rumour is spreading that...*), (b) duration/temporal `for`-adjuncts and geographical `LOC`/`GPE` `to`-adjuncts blindly promoted to `ditrans` V-sister complements (*baked a loaf for two hours*, *mailed three parcels to Lisbon*), (c) gerund-only verbs silently falling through to `V[intrans]` + VP-adjunct `S-bar` (*Elena contemplated leaving the firm.* and even ungrammatical *\*contemplated to leave*), and (d) comma-delimited sentential `, which` clauses swallowed as `V[trans]`/`V[ditrans]` objects with erroneous `C1` auxiliary inversion.
2. **Independent Development & Full Regression Verification:**
   - **Independent H01 Dev/Adversarial Benchmark (`n = 48`, verified `0%` overlap with V1/V2/V3/book):** jumped from **`13/48 (27.1%)`** BEFORE to **`45/48 (93.8%)`** AFTER (`+66.7 pp`), with all 3 remaining items producing structurally valid alternate parses rather than errors or crashes.
   - **Full Server Test Suite:** **`970/970 (100.0%)`** executed non-socket tests PASSED (`1,029` discovered, `0` failures, `0` non-socket errors, `45` skipped, `14` macOS sandbox localhost socket `PermissionError` tests), including **`135/135`** targeted H01/B–R/H02 reliability tests and the new [test_h01_structural_reliability.py](file:///Users/kiyel/Desktop/SynTutor/server/test_h01_structural_reliability.py).
   - **Zero Regression on Published Book Diagrams (`Track 1`, `n = 216+1`):** `62.98%` raw all-attempts F1, `67.00%` aligned LF1, `83.35%` triangle-aware LF1 (`112/204` exact), `91.56%` zero-triangle Ch. 3–10 LF1 (`n = 65`), and `8/8` exact on Figure `[79b]`.
   - **Zero H02 Impact:** Verified **`0/100`** verdict or correction drifts across all 100 frozen Evaluation V3 sentences (`arm_a_packet`), with zero edits to any H02 module.
   - **Regression-Only Diagnostics on Historical V1/V2/V3 Grammatical Sets (explicitly NOT unseen generalization evidence):** V1 Track 4 rose `45/50 → 49/50 (98.0%)`; V2 Track 4 rose `44/50 → 48/50 (96.0%)`; V3 Track 2 rose `12/17 → 17/17` (`47/62 → 62/62` relations) and Tracks 3–4 rose `41/50 → 50/50`.
3. **Scientific Readiness Verdict on Unseen Complete-Tree Accuracy:**
   - **Unseen complete-tree labeled F1 and exact match remain `UNVERIFIED` (`NOT READY` for confirmatory V4 execution).** All `252` printed phrase markers in Burton–Roberts' 3rd edition Chapters 1–10 are already imported into `web/content/book/` (development-exposed), and Burton–Roberts' *Answer Book for the Further Exercises* / Routledge companion instructor keys are publisher-gated for verified adopting instructors. We document both the official publisher-verification path (with strict 3rd vs. 4th/5th edition compatibility guards) and an independent blinded two-linguist gold annotation protocol (Section E & F) required before freezing and running any V4 confirmatory benchmark.

---

## Section A — Root-Cause Audit (End-to-End Pipeline Trace)

Every H01 V3 failure (9 unnormalized sentences + `V3-G05`) was traced step-by-step through `Sentence → spaCy (en_core_web_md) → Benepar (benepar_en3) → final_d1_projection.py → burton_roberts.py`. **Crucially, 9 of the 10 failures originated inside `server/final_d1_projection.py`, NOT Benepar**; only `V3-G05` involved an upstream Benepar low-NP attachment bias compounded by `final_d1_projection.py`'s lack of semantic selection constraints.

| ID & Sentence | Benepar Parse Summary | Exact Failing Stage & Reason | Root Architectural Defect |
|---|---|---|---|
| **`V3-G01`** *John considered visiting his great aunt.* | `(VP (VBD considered) (S (VP (VBG visiting) (NP his great aunt))))` — **Benepar correct** | `final_d1_projection.py:vp()` — `Non-finite complement has no supported control analysis` | `consider` was in `TYPE_I` but omitted from undifferentiated `SUBJECT_CONTROL`; gerundial (`-ing`) vs. infinitival (`to`) control frames were conflated. Worse, gerund verbs outside `TYPE_I` (e.g., `contemplate`, `admit`, `postpone`) silently fell through to VP-adjunction as `V[intrans]`. |
| **`V3-G05`** *Laura saved a place for Martha.* | `(VP (VBD saved) (NP (NP a place) (PP (IN for) (NP Martha))))` — **Benepar low-NP bias** | `final_d1_projection.py:vp()` normalized as `V[trans] + NP(a place for Martha)` | Benepar attached benefactive `for Martha` inside the direct-object NP, and `vp()` had no joint verb-frame + noun-selection + animate-beneficiary check to distinguish benefactive ditransitives from NP-internal `for`-complements, while blindly over-promoting `for two hours` and `to Africa` to `ditrans`. |
| **`V3-G18`** *That evening, Laura learned the Health and Safety Regulations by heart.* | `(S (NP That evening) (,) (NP Laura) (VP learned (NP the (NML Health and Safety) Regulations) (PP by heart)))` — **Benepar correct** | `final_d1_projection.py:nml_phrase()` — `Unsupported CC phrase` | `nml_phrase()` lacked `self.coordinate(...)` support for coordinated nominal premodifiers (`NML(N CC N)`). Additionally, `is_time_np()` checked `dependency(node)` only on token `span[0]` (`"That"`=`det`) instead of the NP's head (`"evening"`=`npadvmod`), breaking other fronted temporal NPs (*The next morning*, *Last winter*). |
| **`V3-G20`** *Who was laughing?* | `(SBARQ (WHNP Who) (SQ (VP (VBD was) (VP (VBG laughing)))))` — **Benepar valid** | `final_d1_projection.py:wh_gap()` & `wh_clause()` → `question()` — `Unsupported inversion or question tag` | `wh_gap()` assumed `SQ` subject wh-questions always had flat `(SQ (AUX) (VP ...))` rather than single-VP `(SQ (VP ...))`, misclassifying `link.kind` as `"object"` and routing a subject-wh clause into auxiliary-inversion `question()`. |
| **`V3-G24`** *Whose toothbrush did he clean his keyboard with?* | `(SBARQ (WHNP Whose toothbrush) (SQ did (NP he) (VP clean (NP his keyboard) (PP with))))` — **Benepar correct** | `final_d1_projection.py:vp()` (`incoming.kind == "preposition"`) — `Wh-phrase has no unique stranded preposition` | Stranded-PP projection special-cased only `RECIPIENT_TO` and `{"put", "place"}` when an overt direct-object NP preceded the stranded `PP`, crashing on every general transitive verb with a stranded adjunct PP. |
| **`V3-G27`** *Regrettably, your dancing and colourful language are frightening the guests.* | `(S (ADVP Regrettably) (,) (NP (PRP$ your) (NML (NML dancing) (CC and) (NML colourful language))) (VP are frightening the guests))` — **Benepar correct** | `final_d1_projection.py:np()` — `AP has no identifiable head` | `np()` only searched for a **leaf** head noun after `DET`; when a single determiner scoped over a coordinated `NML` branch, `head` was `None` and `np()` fell into the elided-head `AP` branch (`the poor`), crashing on `modifier([NML], adjective=True)`. |
| **`V3-G33`** *Who were they given to?* | `(SBARQ (WHNP Who) (SQ were (NP they) (VP given (PP to))))` — **Benepar correct** | `final_d1_projection.py:vp()` (`passive is not None`) — `Overlapping dependencies inside passive VP` | The `passive` guard rejected any co-occurring `incoming` wh-gap unless `kind in {"adverbial", "pp"}`, falsely treating a promoted passive object gap (`they₂`) and a stranded-PP wh-gap (`Who₁ ... to •₁`) as overlapping dependencies. |
| **`V3-G38`** *The thought occurred to him that he should have done the washing up.* | `(S (NP The thought) (VP occurred (PP to him) (SBAR that he should have done (NP the washing (RP up)))))` — **Benepar valid** | Two stages: (1) `vp()` — `Unclassified VP dependent SBAR`; (2) `np()` — `Unsupported nominal dependent RP` | (1) `clause()` only handled extraposition for expletive `"it"`, ignoring extraposition from a `CLAUSAL_NOUN` subject NP (which also caused `V3-G39` *A rumour is spreading that...* to emit a silently wrong `V[trans]` object tree!). (2) `np()` rejected compound noun+particle `(NN washing) (RP up)`. |
| **`V3-G41`** *I wonder who the men expected to see them.* | `(S I (VP wonder (SBAR (WHNP who) (S (NP the men) (VP expected (S (VP to (VP see them))))))))` — **Benepar correct** | `final_d1_projection.py:vp()` — `Object gap conflicts with the verb frame or an overt object` | Because the non-finite complement had no overt surface subject, `vp()` blindly assumed `SUBJECT_CONTROL` (co-indexing `the men` as lower subject) and pushed the `who` object gap down into `to see them` (whose object slot is already filled by `them`), instead of testing Type I ECM embedded-subject extraction (`expected [•₁ to see them]`). |
| **`V3-G47`** *Lomax argued for trampolines, which surprised me.* | `(S Lomax (VP argued (PP for trampolines) (,) (SBAR (WHNP which) (S (VP surprised me)))))` — **Benepar correct** | `final_d1_projection.py:vp()` — `Unclassified VP dependent SBAR` | `clause()` lacked a peeler for clause-level comma-delimited sentential non-restrictive relative clauses (`S → S + S-dbar`). Worse, when no PP intervened (*The train arrived early, which nobody had expected*; *She passed all the exams, which was astonishing*), `vp()` silently swallowed `, which ...` as a `V[trans]`/`V[ditrans]` object and inverted auxiliaries into `C1`. |

### Additional Silent ("Plausible-but-Wrong") Structural Defects Uncovered & Fixed
1. **Extraposition misanalyzed as direct object (`V3-G39`):** *A rumour is spreading that the Prime Minister has resigned.* previously normalized as `V[trans](spreading) + NP(S-bar)` instead of `S → NP(A rumour) + VP(PROG is, VP(V[intrans] spreading)) + S-bar(that ...)`.
2. **Duration/temporal & geographical `PP`s blindly promoted to `ditrans`:** `final_d1_projection.py:1635` classified *any* `V(DITRANSITIVE) + NP + PP(to/for)` as `V[ditrans]` V-sister complements — misanalyzing *Daniel baked a loaf for two hours* (`for two hours` = duration adjunct `aA`), *He left a note for the morning* (`for the morning` = temporal adjunct `aA`), and *Holden wrote ten letters to Africa* / *Trevor mailed three parcels to Lisbon* (`LOC`/`GPE` = directional adjunct `aA`, per B–R Ch. 4 Ex. 2(a) p. 83) as indirect objects.
3. **Gerund-only verbs falling through to `V[intrans]` + VP-adjunct:** *Elena contemplated leaving the firm* (and ungrammatical *\*Elena contemplated to leave the firm*) fell through to `vp()`'s trailing-adjunct loop, emitting `V[intrans]` with an uncontrolled adjunct `S-bar`.
4. **Comma-delimited `, which` clauses swallowed as `NP(S-bar)` complements with false `C1` inversion:** *The train arrived early, which nobody had expected* turned intransitive `arrived` into `V[trans]`; *She passed all the exams, which was astonishing* turned `passed` into `V[ditrans]` and erroneously fronted `was` into `C1` inside a relative clause.

---

## Section B — Engineering Changes & Phase IV Architectural Audit

### B.1 Modified Production Files & Cryptographic Checksums (H01 Scope Only)

| File | SHA-256 | Modified Functions / Components |
|---|---|---|
| [server/final_d1_projection.py](file:///Users/kiyel/Desktop/SynTutor/server/final_d1_projection.py) | `be77b8bb7ff4b63e0cf2b3e77ce55a50bddddf98c5f26109eb8e787d21fd737f` | `AmbiguousProjection`, frame lexicons (`TO_SUBJECT_CONTROL`, `ING_SUBJECT_CONTROL`, `ING_FREE_CONTROL`, `ING_ONLY_VERBS`, `RECIPIENT_TO`, `BENEFACTIVE_FOR`, `LOCATIVE_COMPLEX`, `EXTRAPOSITION_NP_VERBS`, `FOR_SELECTING_NOUNS`, `ANIMATE_HEAD_NOUNS`, `INANIMATE_LOCATION_NOUNS`, `SELECTED_PP["argue"]`), `nml_phrase()`, `np()`, `nonfinite_head_kind()`, `nonfinite()`, `vp()`, `is_time_np()`, `is_which_relative_sbar()`, `is_temporal_pp()`, `is_inanimate_location_pp()`, `is_animate_recipient_or_beneficiary()`, `detach_low_benefactive_for()`, `classify_post_object_pp()`, `peel_sentential_relative()`, `subject_head_noun()`, `extract_np_extraposed_sbar()`, `clause()`, `wh_gap()`, `wh_clause()`. |
| [server/burton_roberts.py](file:///Users/kiyel/Desktop/SynTutor/server/burton_roberts.py) | `f3c5bc6c001768e21bd6242ea63bb8fb4def505f3afd43ed518755ef1ae7ae87` | `_final_projection()`: catches `AmbiguousProjection` separately from `ProjectionUnavailable`, preserving `status="unresolved"`, emitting distinct diagnostic code `"STRUCTURAL_AMBIGUITY"` (separating genuine ambiguity from unsupported constructions), and exposing `ambiguous=True` + `alternative_readings` on the result and `working_tree["notes"]`. |
| [server/test_h01_structural_reliability.py](file:///Users/kiyel/Desktop/SynTutor/server/test_h01_structural_reliability.py) | `539cc88d76f9294332df55f96adb59a07e7825b236aab3a0d5c115b0d9634e49` | New permanent Phase VII structural & adversarial test suite (`9` test methods covering all remediated families, negative controls, ambiguity guards, schema 1.1.0 validation, yield preservation, and determinism). |

**Zero V3 sentence strings or IDs appear anywhere in production code.** Zero H02 modules (`matrix.py`, `ruleset.py`, `corrections.py`, `licensing.py`, `analysis_api.py`, `parse_engine.py`) were modified.

### B.2 Burton–Roberts Linguistic Justifications for Key Transformations
- **Gerundial vs. Infinitival Complements (B–R Ch. 10 pp. 228–243, Fig. `[79b]` p. 239):** Subjectless `-ing` complements of `ING_SUBJECT_CONTROL` verbs (`consider`, `contemplate`, `admit`, `postpone`, `remember`, `enjoy`, etc.) project as `VP → V + S-bar(C1[], S(NP(•₁), VP(V[-tense], ...)))` with matrix subject co-indexed `1`, never as ordinary NP objects. `ING_FREE_CONTROL` verbs (`forbid`, `allow`, `prohibit`, `involve`) project with an unindexed free covert subject `{gap: True}`. Gerund-only verbs followed by a subjectless `to`-infinitive (*\*Elena contemplated to leave the firm*) raise `ProjectionUnavailable` rather than falling into adjunct attachment.
- **Coordinated `NML` & Shared-`DET` Coordinated `NOM` (B–R Ch. 3 pp. 62–65; Ch. 7 pp. 142–144, `[12]–[16]`):** Premodifying bare-noun coordinations project as `N → N CC N` inside `NOM` without relying on capitalization (*trade and tariff agreements*, *Health and Safety Regulations*); shared-determiner coordinated nominals project as `NP → DET + NOM(NOM CC NOM)` (*your [dancing and colourful language]*).
- **Subject-Wh Single-VP `SQ` (B–R Ch. 9 Discussion 2 `[14]`, p. 213):** Unwraps Benepar's `(SQ (VP ...))` shell while guarding against matrix auxiliary inversion with an overt subject (`Who did you discover was giving the lecture?`) and preserving copular `C1` fronting (`Whose is this?`, `Who was laughing?`) vs. empty `C1` on lexical main verbs (`Who laughed?`).
- **General Stranded-PP & Non-Overlapping Passive+Wh Extraction (B–R Ch. 6 pp. 125–127; Ch. 9 pp. 211–212, 221):** Replaces verb-specific `RECIPIENT_TO`/`put`/`place` hardcoding with a unified unique-stranded-PP resolver across both active and passive VPs. Distinguishes complement stranded PPs (`ditrans` `to`/`for`, `complex` locative, `prep` `SELECTED_PP`) from general adjunct stranded PPs (`VP → VP(core) + PP(P, NP(•))`), never misclassifying the wh-phrase as the direct object of the verb. Permits non-overlapping passive object gap (`•_subj`) + stranded-PP wh-gap (`•_wh`) and passive double-object ditransitives (`What were the winners awarded?`), while rejecting genuine overlaps on monotransitive/intransitive verbs.
- **Phase III Complement vs. Adjunct vs. NP-Modifier PP Classification (B–R Ch. 4 pp. 72–79, 83; Ch. 5 Ex. 2d):** Separates `RECIPIENT_TO`, `BENEFACTIVE_FOR`, and `LOCATIVE_COMPLEX`, and applies joint structural + selectional constraints (`fentity`, temporal head check, inanimate geographic `LOC`/`GPE` exclusion, institutional recipient retention for *sold ... to the museum*, animate beneficiary check, and `FOR_SELECTING_NOUNS` guard against detaching *a ticket for the opera* or *a textbook for beginners*).
- **Extraposed Noun Complements (B–R Ch. 8 pp. 178, 183, 195 Further Ex. 4):** Extracts trailing `that`/`whether` `SBAR` from `VP` to `S → NP + VP + S-bar` (`BR08-S-EXTRAPOSITION`) only when the subject head noun is in `CLAUSAL_NOUNS` and the predicate is an extraposition-hosting intransitive/unaccusative/non-reporting-passive or already has an intervening complement under a non-propositional verb — keeping propositional transitive verbs (*The report confirmed that...*) inside `VP`.
- **Dual-Frame Embedded Wh-Nonfinite Disambiguator & `AmbiguousProjection` (B–R Ch. 10 pp. 243, 252):** Explicitly trials BOTH `TYPE_I` ECM (embedded subject gap) and `SUBJECT_CONTROL` (internal complement gap) when an incoming wh-NP gap meets a subjectless non-finite complement. Emits the unique licensed parse when exactly one succeeds (`V3-G41`, *Who do you believe to be responsible?*, *I wonder who the coach chose to replace.*), and raises `AmbiguousProjection` (`STRUCTURAL_AMBIGUITY`) when both succeed (*I wonder who the men wanted to help.*) — never forcing an unsupported unique parse.
- **Sentential Non-Restrictive Relatives (B–R Ch. 9 pp. 210, 222 Further Ex. 6):** Peels clause/VP-level comma-delimited `, which` `SBAR`s (and 3sg-verb `, which` clauses misattached by Benepar inside plural final NPs) and projects `S → S + S-dbar` via `self.relative()` (keeping `C1` empty, zero false auxiliary inversion), while leaving genuine NP-modifying relatives (*Milo bought the bicycles, which were expensive.*) attached to `NP`.

### B.3 Phase IV Architectural Audit Assessment
Evaluating `final_d1_projection.py` against all eight Phase IV architectural principles:
1. **Surface constituency vs. grammatical function:** Preserved strictly — grammatical functions remain derived from structural configuration (`V`-sister vs. `VP`-adjunct vs. `S`-daughter), never inserted as non-B–R tree labels.
2. **Explicit verb argument frames:** Substantially improved — split undifferentiated `SUBJECT_CONTROL` into `TO_SUBJECT_CONTROL` / `ING_SUBJECT_CONTROL` / `ING_FREE_CONTROL` / `ING_ONLY_VERBS`, and split `DITRANSITIVE` into `RECIPIENT_TO` / `BENEFACTIVE_FOR` / `LOCATIVE_COMPLEX` with explicit selectional predicates (`classify_post_object_pp`, `detach_low_benefactive_for`).
3. **Consistent intermediate structures vs. Benepar tree quirks:** Benepar's idiosyncratic wrappers (single-VP `SQ`, wrapped `NP(NP, VP)` inside `SQ`, flat `DT+NN+RP`, low-attached benefactive `for`-PP, buried 3sg sentential `which`-clause) are normalized systematically at well-defined entry points (`wh_gap`/`wh_clause`, `vp`, `clause`) rather than scattered ad-hoc patches.
4. **Remaining architectural limitation (honestly disclosed):** `final_d1_projection.py` still depends on hand-curated lexical sets (`CLAUSAL_NOUNS`, `ANIMATE_HEAD_NOUNS`, `FOR_SELECTING_NOUNS`, `EXTRAPOSITION_NP_VERBS`, `SELECTED_PP`). While principled lexical-frame tables are standard in rule-based HPSG/LFG/B–R grammars, rare out-of-vocabulary verbs or world-knowledge-dependent PP ambiguities (e.g., *Milo voted for the proposal, which delighted his colleagues*) remain bounded by spaCy NER/POS evidence and the curated lexicon.
5. **Alternative analyses & structural diagnostics:** Added `AmbiguousProjection` + `"STRUCTURAL_AMBIGUITY"` diagnostic code + `alternative_readings` metadata, cleanly distinguishing genuine structural ambiguity (`I wonder who the men wanted to help.`, `Max found Bill an amusing companion.`) from unsupported constructions (`PROFILE_MAPPING_NOT_APPROVED`) and invalid inputs.
6. **Terminal yield & schema invariants:** Every emitted tree is validated end-to-end by `validate_canonical_tree()`, `final_d1_display_labels()`, `audit_br_constructions()`, and JSON Schema 1.1.0 (`Draft202012Validator`), guaranteeing 100% terminal-yield preservation and zero Penn tag leakage.

---

## Section C — Before / After Development Results (Independent 48-Sentence Benchmark)

Evaluated on a separate 48-sentence H01 development & adversarial benchmark (`scratch/h01_dev_corpus.py`), verified **`0` exact matches** against V1, V2, V3, and `web/content/book/` (`DEV_CORPUS_EXACT_OVERLAP: []`).

| Category | `n` | Before Sprint | After Sprint | Delta | Notes |
|---|---:|---:|---:|---:|---|
| **A. Gerundial complements & negative controls** | 5 | `0/5 (0.0%)` | **`4/5 (80.0%)`** | `+80.0 pp` | `A1–A3` & `A5_neg` pass; `A4` (*forbids parking beside the entrance*) parsed legitimately as nominal NP (`parking` = `NN`), while clausal `forbids entering the tunnel` passes with free-control `S-bar` (`test_h01_structural_reliability.py`). |
| **B. Fronted temporal NPs & coordinated NMLs** | 3 | `0/3 (0.0%)` | **`3/3 (100.0%)`** | `+100.0 pp` | Lowercase (`trade and tariff`, `water and energy`) & capitalized (`Parks and Wildlife`) NMLs + `The next morning` / `Last winter`. |
| **C. Subject-wh questions (prog/perf/lex/pass)** | 5 | `3/5 (60.0%)` | **`5/5 (100.0%)`** | `+40.0 pp` | `Who laughed?` & `Who was invited?` fixed; `Whose is this?` & long-distance `Who did she notice was leading...` verified. |
| **D. Stranded prepositions + direct object wh** | 5 | `0/5 (0.0%)` | **`5/5 (100.0%)`** | `+100.0 pp` | Active transitive, possessive wh, trailing adjunct, benefactive `for`, and long-distance extraction. |
| **E. Coordinated gerundial / shared-DET subjects** | 3 | `1/3 (33.3%)` | **`3/3 (100.0%)`** | `+66.7 pp` | Shared `POSS` over coordinated `NOM` (`his singing and loud laughter`, `their research and field trials`) + bare gerund+NP. |
| **F. Passive wh-interrogatives** | 5 | `0/5 (0.0%)` | **`5/5 (100.0%)`** | `+100.0 pp` | Stranded `to`, stranded `for` (including Benepar wrapped `NP(NP, VP)`), stranded locative `on`, stranded adjunct `with`, and double-object passive. |
| **G. Extraposed noun complements & neg control** | 4 | `1/4 (25.0%)` | **`4/4 (100.0%)`** | `+75.0 pp` | `The suspicion arose...`, `News spread rapidly that...`, `the clearing up` compound-particle N, plus negative control `The report confirmed that...`. |
| **H. Embedded wh-nonfinite & ambiguity guard** | 4 | `1/4 (25.0%)` | **`4/4 (100.0%)`** | `+75.0 pp` | Unambiguous Type I ECM (`H1`, `H2`), subject-control (`H3`), and genuine ambiguity preserved as `STRUCTURAL_AMBIGUITY` (`H4_ambig`). |
| **I. Sentential vs. NP-modifying relatives** | 4 | `1/4 (25.0%)` | **`3/4 (75.0%)`** | `+50.0 pp` | `I2`, `I3`, `I4_np_rel` pass; `I1` (*Milo voted for the proposal, which delighted his colleagues*) retains Benepar's valid singular-NP attachment (genuinely ambiguous between NP and clause antecedent). |
| **P3. Complement vs. adjunct vs. NP-modifier PPs** | 10 | `6/10 (60.0%)` | **`9/10 (90.0%)`** | `+30.0 pp` | All benefactive `for`, duration `for two hours`, NP-internal `ticket for the opera`, recipient `to his cousin`, geographical `to Lisbon`, and `complex` pass; `P5` (*left a message for the morning*) normalized cleanly as NP-modifier (NOT `ditrans`), while VP-attached *left a note for the morning* demotes cleanly to VP-adjunct (`test_h01_structural_reliability.py`). |
| **TOTAL (Unchanged 48-Sentence Dev Benchmark)** | **48** | **`13/48 (27.1%)`** | **`45/48 (93.8%)`** | **`+66.7 pp`** | Zero crashes, zero schema errors, zero corrupt trees; latency `46.7 ms/sent` BEFORE vs `39.4–55.7 ms/sent` AFTER (no performance regression). |

---

## Section D — Regression Results & H02 Preservation Audit

### D.1 Automated Unit & Integration Test Suites

| Test Suite | Discovered / Executed | Passed | Failed | Skipped | Notes |
|---|---:|---:|---:|---:|---|
| **New Phase VII H01 Suite** (`test_h01_structural_reliability.py`) | 9 | **9** | **0** | 0 | `100%` pass (`OK`); determinism, yield, schema 1.1.0, all 10 families + ambiguity guards. |
| **Parser Runtime + New H01 Suite** (`test_parser_runtime` + `test_h01_structural_reliability`) | 21 | **21** | **0** | 0 | `100%` pass (`OK`), including `Whose is this?` `C1₂` copular fronting regression caught & fixed during verification. |
| **Targeted H01/B–R/H02 Suites** (`8` modules) | 135 | **135** | **0** | 0 | `test_h01_structural_reliability`, `test_burton_roberts`, `test_br_tree`, `test_br_tree_schema`, `test_br_tree_fixtures`, `test_h01_h02_reliability`, `test_h01_h02_comprehensive_reliability`, `test_nlp_reliability_regressions`. |
| **Full Server Test Suite (Offline, Non-Socket)** | 970 non-socket (`1,029` total) | **970** | **0** | 45 | `0` failures, `0` non-socket errors; `14` localhost HTTP socket tests blocked by macOS sandbox `PermissionError` (none modified). |

### D.2 Historical Regression Diagnostics (Strictly Regression Evidence — NEVER Reported as Unseen!)

| Benchmark (Historical / Dev-Exposed) | Pre-Sprint Baseline | Post-Sprint Result | Regression Verdict |
|---|---:|---:|---|
| **Track 1 Published Book PARSEVAL (`n=216+1`, dev-exposed)** | `62.98%` raw / `67.00%` aligned / `83.35%` tri-aware (`112/204` exact) / `8/8` Fig. `[79b]` | **`62.98%` raw / `67.00%` aligned / `83.35%` tri-aware (`112/204` exact) / `8/8` Fig. `[79b]`** | **ZERO REGRESSIONS** (`ch5-ex2d` institutional recipient *sold ... to the museum* caught and fixed!) |
| **V1 Grammatical Track 4 Regression (`n=50`, non-unseen)** | `45/50 (90.0%)` | **`49/50 (98.0%)`** | **ZERO REGRESSIONS** (`+4` resolved) |
| **V2 Grammatical Track 4 Regression (`n=50`, non-unseen)** | `44/50 (88.0%)` | **`48/50 (96.0%)`** | **ZERO REGRESSIONS** (`+4` resolved) |
| **V3 Grammatical H01 Regression (`n=50`, non-unseen)** | Track 2: `12/17` (`47/62` rels); Track 3: `41/50`; Track 4: `41/50` | **Track 2: `17/17` (`62/62` rels); Track 3: `50/50`; Track 4: `50/50`** (Simple `15/15`, Mod `20/20`, Cplx `15/15`) | **ZERO REGRESSIONS** (`V3-G44` long-distance subject-wh regression caught & fixed; `V3-G39` extraposition also structurally corrected) |
| **H02 Zero-Impact Audit on Frozen V3 (`n=100`, Arm A)** | Frozen V3 `h02_details.json` | **`0/100` verdict or correction drifts** | **100% H02 PRESERVED** |
| **Frozen V1, V2, V3 Archive SHA-256 Checksums** | `10/10`, `7/7`, `7/7` | **`10/10 OK`, `7/7 OK`, `7/7 OK`** | **100% ARCHIVES INTACT** |

---

## Section E — Complete-Tree Reference Availability Audit (Phase V)

Establishing genuinely **unseen complete-tree labeled F1 and exact match** is the primary remaining scientific requirement for H01. A systematic audit of available authoritative sources yields the following verified status:

### E.1 Inventory of Authoritative Burton–Roberts Resources

| Resource | Availability & Access Path | Edition Compatibility with SynTutor (`3rd ed., 2011, FINAL-D1`) | Usability as Unseen Complete-Tree Gold |
|---|---|---|---|
| **1. Burton–Roberts 3rd Ed. Textbook PDF** (`Syntax_Reference_Chapters_1-11-1.pdf`, ISBN `9781408233740`) | Available locally (verified SHA-256 in `source_manifest_2026-11-08.json`). | Exact authoritative target edition. | **NOT USABLE as unseen complete-tree gold:** all `252` printed diagrams (Ch. 1–10) were already imported into `web/content/book/` (`216` in Track 1), and `161/252 (63.9%)` use pedagogical triangles (`△`). Unused *Discussion of exercises* items provide only **partial** functional/ACA answers, never complete trees. |
| **2. Burton–Roberts 3rd Ed. *Answer Book for the Further Exercises*** (Pearson/Longman, referenced p. x) | **Not present** in repository or attached PDF; traditionally publisher-restricted to instructors. | Exact authoritative target edition (`3rd ed.`), if obtained through authorized academic channels. | **PRIMARY IDEAL SOURCE if legitimately obtained** — contains complete author-drawn phrase markers for Ch. 4–10 *Further Exercises* (verify per-item triangle usage and zero overlap with `web/content/book/` and V1/V2/V3). |
| **3. Routledge 4th Ed. (2016) & 5th Ed. (2022) Instructor Resources / Companion Website** (`routledge.com`, `routledgetextbooks.com`) | Officially restricted to verified course instructors via Routledge's Instructor Resources registration form (student site provides extra practice activities without full instructor answer keys). | **Requires explicit per-rule compatibility audit:** 3rd ed. already abolished 1st/2nd-ed. `Vgrp` in favor of auxiliary-selected VP complements (preserved in 4th & 5th ed.); 4th ed. refined functional/category notation; **5th ed. (2022) refreshed example sentences and expanded its final chapter toward formal X-bar syntax.** Never mix 4th/5th-ed. trees silently into a 3rd-ed. `FINAL-D1` gold set without documenting and reconciling any bar-level, `NOM`, `S-bar`/`CP`, or non-finite convention differences. | **USABLE ONLY after verified instructor acquisition + documented edition-compatibility mapping + zero-overlap audit.** |
| **4. Unofficial peer-to-peer student uploads** (Studocu, Scribd, Stuvia, YouTube) | Publicly searchable online. | Unverified authorship, frequent transcription errors, mixed editions. | **REJECTED** — fails academic provenance and authority standards. |
| **5. Independent Expert-Annotated Complete-Tree Gold Corpus** (Proposed Fallback Protocol) | Can be commissioned cleanly with thesis adviser / linguistics faculty. | Authored natively under frozen SynTutor 3rd-ed. `FINAL-D1` guidelines (`docs/canonical-burton-roberts-tree-schema.md` + `CONVENTIONS.md`). | **RECOMMENDED PATH** if Routledge instructor Answer Book cannot be obtained. |

### E.2 Proposed Independent Expert Annotation Protocol (When Published Complete Trees Are Unavailable)
If authorized publisher access to the 3rd-edition *Answer Book* is unavailable, establish a rigorous **50–60 sentence unseen complete-tree gold benchmark** via:
1. **Sentence Selection & Anti-Contamination:** Select `50–60` fresh grammatical sentences stratified evenly across Simple (`15–20`), Moderate (`15–20`), and Complex (`15–20`) levels — spanning all major B–R Ch. 3–10 phenomena (complements vs. adjuncts, auxiliaries, Ch. 7 Appendix D1 `NOM`, subordinate/extraposed clauses, wh-questions/relatives, sentential relatives, non-finite control/ECM/gerunds, coordination, passives) — with **verified `0` exact and `0` Jaccard ≥ 0.55 near-duplicate overlap** against V1, V2, V3, `web/content/book/`, and all test/dev suites.
2. **Blinded Independent Double-Annotation:** Two qualified linguistics annotators (e.g., syntax faculty/graduate syntacticians) independently construct complete, zero-triangle `FINAL-D1` JSON phrase markers (`schema v1.1.0`) from the raw sentences using a written annotation manual anchored strictly to Burton–Roberts 3rd ed. (2011) — **never viewing Benepar or SynTutor outputs**.
3. **Explicit Ambiguity & Alternatives Recording:** Where a sentence legitimately permits two B–R analyses, both annotators record primary + `accepted_alternatives` with explicit linguistic rationales.
4. **Inter-Annotator Agreement & Adjudication:** Compute pre-adjudication inter-annotator agreement (labeled PARSEVAL F1, exact tree match, attachment $\kappa$), resolve disagreements via a third senior syntactician / thesis adviser, validate 100% of adjudicated gold trees against `docs/canonical-burton-roberts-tree.schema.json` and `validate_canonical_tree()`, and freeze with SHA-256 checksums **before running SynTutor once**.

---

## Section F — Independent Evaluation Readiness & Phase VI Evaluation Protocol

### F.1 Current Readiness Verdict
> **INDEPENDENT COMPLETE-TREE EVALUATION READINESS: `NOT READY (BLOCKED ON EXTERNAL GOLD TREES)`**

SynTutor's H01 engineering implementation and regression stability are ready, **but meaningful unseen complete-tree accuracy CANNOT yet be measured** because zero uncontaminated, independently verified complete-tree Burton–Roberts gold phrase markers are currently on hand. In strict adherence to Phase VIII, **Evaluation V4 has NOT been fabricated or executed.**

### F.2 Pre-Registered Phase VI Separated Evaluation Specification (Ready for Future V4 Once Gold Trees Exist)
Once authoritative complete-tree gold references are frozen, the V4 H01 evaluator must strictly separate all six top-level measurements and seven diagnostic stratifications:

1. **Complete-Tree Labeled F1 (Primary Confirmatory H01 Metric):** Micro- and macro-averaged labeled constituent PARSEVAL F1 against complete, zero-triangle authoritative gold trees under a pre-declared representational normalization policy (character-offset span alignment for equivalent contraction/hyphen tokenizations; pre-declared handling of empty `DET`/`C1`, movement gaps `•`, and `accepted_alternatives` scored by max-matching valid alternative). **All-attempts denominator mandatory** (unresolved trees contribute `0` matched constituents and full gold span count).
2. **Complete-Tree Exact Match:** Percentage of entire predicted trees matching any pre-registered gold analysis (`root` + labels + features + hierarchy), strictly separated from labeled F1.
3. **Partial-Reference Agreement:** Evaluated strictly on published partial answers (if any subset lacks full trees); explicitly labeled *partial*, never conflated with complete-tree accuracy.
4. **Canonical Rule Compliance:** Deterministic B–R Ch. 1–10 label, root, X-bar `NOM`, and interrogative `C1`/`C2` structural compliance.
5. **Conversion Consistency:** Schema 1.1.0 validity, yield preservation, and determinism.
6. **Coverage:** Proportion of attempted sentences resolving to `status == "normalized"`, with `STRUCTURAL_AMBIGUITY` and `PROFILE_MAPPING_NOT_APPROVED` counts reported separately.
7. **Mandatory Diagnostic Stratifications:** (a) Simple / Moderate / Complex; (b) Complement vs. adjunct attachment accuracy; (c) Clause boundary accuracy; (d) Wh-dependency & gap accuracy; (e) Coordination accuracy; (f) Multi-clause (`>= 2` clauses) performance; (g) Separate reporting of any triangle-abbreviated or Ch. 1–2 introductory-label diagrams (never artificially reconstructing omitted subtrees).

### F.3 Mandatory 9-Step Gate Checklist Before Executing V4
- [x] **1. Production H01 remediation complete** (`server/final_d1_projection.py`, `server/burton_roberts.py`).
- [x] **2. Improvements demonstrated on separate independent dev corpus** (`13/48 → 45/48`, `0%` overlap; `970/970` non-socket server tests passing; `0/100` H02 drift).
- [ ] **3. Authoritative unseen complete-tree gold references acquired or independently double-annotated & adjudicated.**
- [ ] **4. Benchmark difficulty and construction representativeness audited.**
- [ ] **5. Primary PARSEVAL & exact-match normalization/scoring rules pre-registered.**
- [ ] **6. Code, gold trees, dataset, and scorer frozen with SHA-256 manifest.**
- [ ] **7. Automated zero-contamination audit (`0` exact + `0` near-paraphrase overlap vs. V1/V2/V3/dev/book/repo).**
- [ ] **8. Scorer verified on independent synthetic unit fixtures + zero-call gold-lookup sentinel.**
- [ ] **9. Single-shot execution of V4 (zero post-hoc edits or re-runs).**

---

## Section G — Complete H01 Metric Compliance Table

*Historical frozen unseen Evaluation V3 remains the latest genuinely unseen H01 benchmark. Post-sprint results on V1/V2/V3 are strictly separated below as non-unseen regression diagnostics.*

| Measurement & Exposure Class | Denominator & Score | 95% CI | 80% Target Status |
|---|---:|---|---|
| **Unseen Complete-Tree Labeled F1 (Confirmatory H01 Target)** | *No unseen gold trees* | — | **`UNVERIFIED`** |
| **Unseen Complete-Tree Exact Match** | *No unseen gold trees* | — | **`UNVERIFIED`** |
| **Track 1 — Dev-Exposed Book PARSEVAL Raw All-Attempts (`n=216`, current)** | `991` / `1195` G / `1952` P = **`62.98%`** | — | **NOT MET** *(raw; penalized by `151` textbook `△`/Ch.1–2 trees)* |
| **Track 1 — Dev-Exposed Book PARSEVAL Aligned (`n=204`, current)** | `67.00%` LF1 (`71.53%` UF1; `37/204` exact) | — | **NOT MET** *(dev-exposed)* |
| **Track 1 — Dev-Exposed Triangle-Aware PARSEVAL (`n=204`, current)** | **`83.35%`** LF1 (`88.98%` UF1; `112/204` exact) | — | **MET** *(dev-exposed)* |
| **Track 1 — Dev-Exposed Ch. 3–10 Zero-Triangle Complete Diagrams (`n=65`)** | **`91.56%`** LF1 (`92.50%` UF1; `37/65` exact) | — | **MET** *(dev-exposed)* |
| **Track 1 — Figure `[79b]` Source Verification (`n=1`, p. 239)** | **`8/8 (100.0%)`** exact | — | **MET** |
| **Frozen Unseen V3 — Track 2 Partial Published Relations (All-Checked)** | `12/17 (70.59%)` | Wilson `[46.87%, 86.72%]` | **NOT MET** *(latest frozen unseen)* |
| **Frozen Unseen V3 — Track 2 Partial Published Relations (Total Rels)** | `47/62 (75.81%)` | Wilson `[63.85%, 84.75%]` | **NOT MET** *(latest frozen unseen)* |
| **Frozen Unseen V3 — Track 3 B–R Rule Compliance** | `41/50 (82.00%)` | Wilson `[69.20%, 90.23%]` | **MET** *(latest frozen unseen)* |
| **Frozen Unseen V3 — Track 4 Conversion Consistency** | `41/50 (82.00%)` | Wilson `[69.20%, 90.23%]` | **MET** *(latest frozen unseen)* |
| **Post-Sprint Independent Dev Corpus (`n=48`, 0% overlap — dev evidence)** | `45/48 (93.75%)` *(up from `13/48 = 27.08%`)* | Wilson `[83.16%, 97.85%]` | **DEV PASS** *(not final confirmatory)* |
| **Post-Sprint Regression Check on V3 (`n=50`, NON-UNSEEN regression)** | T2: `17/17` (`62/62`); T3: `50/50`; T4: `50/50` | — | **REGRESSION PASS** *(never report as unseen)* |
| **Post-Sprint Regression Check on V1 / V2 Track 4 (NON-UNSEEN)** | V1: `49/50 (98.0%)`; V2: `48/50 (96.0%)` | — | **REGRESSION PASS** *(never report as unseen)* |

---

## Section H — Final Assessment

### H.1 What Is Engineering-Solved
- Every documented H01 failure mode from Evaluation V3 (all 9 unnormalized constructions plus the `V3-G05` benefactive `for`-ditransitive misattachment) has been resolved through generalizable, Burton–Roberts-grounded transformations in [final_d1_projection.py](file:///Users/kiyel/Desktop/SynTutor/server/final_d1_projection.py) and [burton_roberts.py](file:///Users/kiyel/Desktop/SynTutor/server/burton_roberts.py).
- Four previously undetected "plausible-but-wrong" structural errors (extraposition misanalyzed as direct object, temporal/geographical PPs mispromoted to `ditrans`, gerund-only verbs falling through to `V[intrans]` + adjunct, and sentential `, which` clauses swallowed as verb objects with false `C1` inversion) have been systematically eliminated.
- Genuine structural ambiguity (*I wonder who the men wanted to help.*, *Max found Bill an amusing companion.*) now fails closed with an explicit `"STRUCTURAL_AMBIGUITY"` diagnostic and enumerated `alternative_readings` instead of forcing a single unsupported parse.
- Zero regressions occurred across `970/970` non-socket server tests, `216+1` Track 1 book diagrams, V1/V2/V3 H01 regression checks, and all `100/100` frozen V3 H02 verdicts/corrections.

### H.2 What Remains Unresolved
1. **Upstream Benepar Parse Ambiguity Without Syntactic Disambiguators:** When a sentence is genuinely ambiguous between NP-modification and clause-modification without number-agreement or semantic disambiguators (e.g., *Milo voted for the proposal, which delighted his colleagues*), Benepar's single top-1 parse commits to one attachment; SynTutor currently preserves that single valid analysis rather than generating a multi-parse forest from Benepar's $k$-best beam.
2. **Lexical-Frame Coverage Boundaries:** Because SynTutor intentionally fails closed when frame evidence is insufficient, rare verbs, non-standard idioms, or constructions outside the curated Burton–Roberts 3rd ed. Ch. 1–10 lexicon remain `unresolved` rather than guessing.
3. **Absence of Unseen Authoritative Complete-Tree Gold References:** Without either the publisher-authorized Burton–Roberts *Answer Book* (verified for edition compatibility) or an independently double-annotated, blinded complete-tree gold corpus, unseen complete-tree labeled F1 and exact match remain **`UNVERIFIED`**.

### H.3 What Can and Cannot Be Scientifically Claimed Today
- **Scientifically Defensible Claims:**
  - SynTutor achieves `91.56%` labeled F1 on complete zero-triangle Burton–Roberts Ch. 3–10 diagrams (`n=65`, development-exposed), `83.35%` triangle-aware labeled F1 (`n=204`, development-exposed), `8/8` exact match on Figure `[79b]`, and `82.0%` unseen B–R rule compliance and conversion consistency on frozen Evaluation V3 (`n=50`).
  - Following principled structural remediation of 10 documented failure classes and 4 silent attachment/complementation defects, SynTutor improved from `27.1%` to `93.8%` structural accuracy on an independent 48-sentence development/adversarial corpus (`0%` overlap with V1–V3/book), passed `970/970` non-socket server tests, preserved `100%` of H02 behavior (`0/100` V3 drift), and eliminated all 10 historical V3 H01 failure modes on regression testing.
- **Claims Strictly Prohibited Until V4 Gold-Standard Validation:**
  - **Do NOT claim** `>= 80%` unseen complete-tree labeled F1 or unseen complete-tree exact match yet.
  - **Do NOT substitute** Track 3 compliance (`82%`), Track 4 conversion consistency (`82%`), dev-corpus scores (`93.8%`), or post-hoc V3 regression results (`50/50`) as confirmatory unseen complete-tree accuracy.
  - **Do NOT cite** H01 as finally validated until Step 3–9 of the Section F.3 independent gold-standard protocol are executed once on a newly frozen, zero-contamination complete-tree benchmark.
