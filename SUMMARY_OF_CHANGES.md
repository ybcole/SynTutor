
# SUMMARY OF CHANGES — Editorial Revision of SynTutor Manuscript (Chapters 1–4)

This log documents all editorial changes made to align Chapters 1–4 of the SynTutor manuscript with the actual system architecture, technical algorithms, and program logic as implemented in the codebase (docs/ARCHITECTURE.md, server/, and FEATURES.md). Edits are categorized by type.

---

## 1. Technical Alignment

| Area | Change | File/Location | Rationale |
|------|--------|---------------|-----------|
| Neural Constituency Parser (benepar_en3) | Chapter 1 Section 1.2 names benepar_en3 explicitly as the pre-trained, non-generative neural constituency parser; Chapter 4 Section 4.2.1 names benepar_en3 in the NLP pipeline; Chapter 3.3.1 formalizes Φ(w,t) = T = argmax score(T\|w). | CHAPTER1_REVISED.md:1.2; CHAPTER4_REVISED.md:4.2.1; CHAPTER3_REVISED.md:3.3.1 | Ensures the Introduction and Methodology reference the exact parser model used in server/parse_engine.py, matching docs/ARCHITECTURE.md. |
| Deterministic Linguistic Constraint Matrix | Chapter 1 Section 1.2 describes the matrix evaluating every parent-child edge across 11 grammatical categories with three states (valid/error/unlisted). Chapter 4 Section 4.2.1 provides the formal evaluation function E(vd,vp). Chapter 3.3.3 details O(|V|) linear-time edge evaluation. | CHAPTER1_REVISED.md:1.2; CHAPTER4_REVISED.md:4.2.1; CHAPTER3_REVISED.md:3.3.3 | Aligns hypothesis testing (H02/Ha2) with the actual algorithmic component server/matrix.py and server/ruleset.py. |
| Positive-Evidence Lexical Licensing | Chapter 1 Section 1.2 names lemminflect/inflect licensing for open-class words, catching malformed inflections ("childs", "runned", "stupids"). Chapter 3.3.4 details suffix-stripping and relative-clause rules (2.7, 5.4). Chapter 4 Section 4.2.1 integrates licensing into the XAI engine. | CHAPTER1_REVISED.md:1.2; CHAPTER3_REVISED.md:3.3.4; CHAPTER4_REVISED.md:4.2.1 | Matches server/licensing.py implementation; closes the blacklist gap described in docs/ARCHITECTURE.md. |
| Hybrid Acceptability/Correction-Search channel | Chapter 1 Section 1.2 describes CoLA RoBERTa detector + distilbert-base-uncased MLM correction search with C-MLM-ANOMALY promotion. Chapter 3.3.5 details combination logic (grammatical only if both accept; unverified when rules clean but model rejects). Chapter 4 Section 4.2.1 integrates the channel. | CHAPTER1_REVISED.md:1.2; CHAPTER3_REVISED.md:3.3.5; CHAPTER4_REVISED.md:4.2.1 | Aligns with server/detector.py and server/corrector.py implementation; ensures H02/Ha2 testing targets this component. |
| Recursive-Descent Parse-String Decoding | Chapter 1 Section 1.2 and Chapter 3.3.2 describe the decoder, NodeBuilder, span alignment guard, and unary chain collapse. Chapter 4 Section 4.2.1 names it as part of the seven-stage pipeline. | CHAPTER1_REVISED.md:1.2; CHAPTER3_REVISED.md:3.3.2; CHAPTER4_REVISED.md:4.2.1 | Matches server/parse_engine.py implementation and docs/ARCHITECTURE.md Stage 4. |
| Hypothesis-to-Method Mapping | Chapter 1 Section 1.5 maps H01/Ha1 to parser accuracy on benchmark corpus, H02/Ha2 to Constraint Matrix grounding (expert validation + zero-unrated audit), H03/Ha3 to Paired Samples t-Test, H04/Ha4 to SUS scoring. Chapter 4 Section 4.4.2 explicitly links each hypothesis to its testing method. | CHAPTER1_REVISED.md:1.5; CHAPTER4_REVISED.md:4.4.2 | Ensures logical consistency between Chapter 1 hypotheses and Chapter 4 evaluation methodology. |
| Chapter 4 completeness | Original CH4 Syntutor.md contained only title metadata (36 lines). Full Chapter 4 written with Research Design, Data Collection, Sampling, Data Analysis, Ethical Considerations, Development Planning, and Evaluation sections. | CHAPTER4_REVISED.md | Chapter 4 was effectively empty; now contains complete research methodology content mirroring Chapter 3's structure but focused on evaluation. |

---

## 2. Terminology Standardization

| Term | Standardization Applied | Chapters Affected |
|------|------------------------|-------------------|
| phrase-structure syntax trees | Used consistently instead of generic "syntax trees" or "constituency trees"; always qualified as phrase-structure | Chapters 1, 2, 3, 4 |
| constituency parsing | Used consistently instead of generic "parsing" or "NLP parsing"; specifies the benepar_en3 neural constituency parser | Chapters 1, 3, 4 |
| XAI | Defined as Explainable AI on first reference; used consistently as acronym thereafter | Chapters 1, 2, 3, 4 |
| deterministic reasoning | Used consistently to describe the constraint matrix + licensing + correction search pipeline, contrasted with "black-box" generative models | Chapters 1, 3, 4 |
| Deterministic Linguistic Constraint Matrix | Full proper name used on first reference; "the matrix" or "constraint matrix" thereafter | Chapters 1, 3, 4 |
| Positive-Evidence Lexical Licensing | Full proper name used on first reference | Chapters 1, 3, 4 |
| Hybrid Acceptability/Correction-Search channel | Full proper name used on first reference | Chapters 1, 3, 4 |
| benepar_en3 | Specific model name used consistently instead of generic "benepar" | Chapters 1, 3, 4 |
| spaCy en_core_web_md | Specific model name used consistently | Chapters 1, 3, 4 |
| C-* constraint codes | Specific constraint identifier format (e.g., C-MLM-ANOMALY) documented | Chapters 1, 3, 4 |
| three-state verdict | grammatical / ungrammatical / unverified terminology standardized | Chapters 1, 3, 4 |

---

## 3. Logical Consistency

| Issue | Before | After | Chapters Affected |
|-------|--------|-------|-------------------|
| H01 referenced "neural consistency parser" | Incorrect model name | Corrected to "neural constituency parser (benepar_en3)" | Chapter 1 |
| H02 referenced "Linguistic Constraint Matrix" without licensing | Incomplete component description | Expanded to "Deterministic Linguistic Constraint Matrix and Positive-Evidence Licensing layer" | Chapter 1 |
| H03/H04 not linked to specific statistical tests | Hypotheses stated without test mapping | Explicitly mapped H03→Paired Samples t-Test, H04→SUS scoring | Chapters 1, 4 |
| Chapter 4 was empty (title page only) | No evaluation methodology | Full Chapter 4 with hypotheses operationalized to testing methods | Chapter 4 |
| Figure numbering inconsistent (3.5.1 vs 3.4) | Mixed figure references across sections | Standardized to 3.4.1, 3.5.1, 3.5.2, 3.6 | Chapter 3 |

---

## 4. Methodological Cohesion

| Area | Change | Rationale |
|------|--------|-----------|
| Agile-Scrum in Chapter 4 | Chapter 4 Section 4.2 references the Agile-Scrum framework from Chapter 3 Section 3.1; Section 4.2.2 details sprint-based verification (gold-corpus audit + frontend state machine walkthrough). | Ensures the Software Development Methodology in Chapter 3 is reflected in Chapter 4's Project Development section. |
| IPO framework alignment | Chapter 3 Section 3.4 (Operational Framework IPO model) is mirrored in Chapter 4 Section 4.6.3 Data Gathering phases (Pre-Intervention → System Intervention → Post-Intervention → Expert Validation), which map to Input → Process → Output. | Confirms the Operational Framework aligns with Research Design and Data Collection procedures. |
| Chapter 2 → Chapter 3 bridge | Section 2.3 Synthesis explicitly maps each identified research gap (black box, visual integration, transparency) to specific SynTutor architecture components (benepar_en3, Constraint Matrix, Licensing, Hybrid channel). | Ensures seamless transition from theoretical literature review to technical methodology. |

---

## 5. Structural Integrity

| Area | Change | Rationale |
|------|--------|-----------|
| Chapter 2 → Chapter 3 transition | Synthesis paragraph (Section 2.3) explains how the "black box" problem in GEC tools (Bryant et al., 2023; Li et al., 2023, 2025; Muralidaran, 2022; Cano et al., 2024) is solved by SynTutor's separation of detection from explanation. | Shows how research gaps are specifically solved by SynTutor architecture. |
| Figure references | All figure references standardized (Figure 3.1.1, 3.2.1, 3.4.1, 3.5.1, 3.5.2, 3.6). | Consistent cross-referencing throughout Chapter 3. |
| Section numbering | Chapter 4 renumbered cleanly: 4.1 Design, 4.2 Project Development, 4.3 Research Design, 4.4 Data Collection, 4.5 Development Planning, 4.6 Evaluation. | Clean hierarchical structure matching Chapter 3. |

---

## How Changes Ensure Accuracy

Each change ensures the manuscript accurately represents the SynTutor system by:

1. **Naming exact models and components** (benepar_en3, en_core_web_md, lemminflect, inflect, textattack/roberta-base-CoLA, distilbert-base-uncased) so the text matches the codebase in server/.
2. **Describing actual algorithms** (recursive-descent decoding, span alignment, O(|V|) matrix evaluation, C-MLM-ANOMALY promotion, three-state verdict) matching server/matrix.py, server/licensing.py, server/detector.py, server/corrector.py.
3. **Linking hypotheses to verification methods** (zero-regression audit for H1, expert validation + zero-unrated audit for H2, Paired Samples t-Test for H3, SUS for H4) so Chapter 4 can empirically test Chapter 1 claims.
4. **Standardizing terminology** so "phrase-structure syntax trees," "constituency parsing," "XAI," and "deterministic reasoning" refer to the same technical concepts across all four chapters.
5. **Bridging Chapter 2 gaps to Chapter 3 solutions** explicitly, showing how the black-box problem in GEC tools is solved by SynTutor's separation of detection from explanation.
