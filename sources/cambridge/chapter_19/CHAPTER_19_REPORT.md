# Cambridge Chapter 19 — extraction report

## Scope and source
- *The Cambridge Grammar of the English Language*, Chapter 19, **Lexical word-formation**, **§1.1 Established words and potential words**, printed pages **1623–1624**, uploaded PDF pages **3–4**.
- Both printed pages are partially covered: introductory matter precedes §1.1 on p. 1623; §1.2 and its footnote begin on p. 1624. Those adjacent passages are excluded.
- The source pages were read in extracted text and visually checked against the original PDF including footnote 2 on p. 1624. The latter distinguishes existing inherited words from disallowed novel formations without declaring all existing historical items ungrammatical.
- The user expressly approved the required Chapter 19 changes. **An independent second-pass AI review has not been performed.**
- Protocol: `CAMBRIDGE_EXTRACTION_PROMPT.md` version 1.0.

## Eight new owner-approved morphology rules
- **MORPH-016** (classification): established words.
- **MORPH-017** (classification): potential words.
- **MORPH-018** (classification): nonce-words distinguished from potential words.
- **MORPH-019** (descriptive_generalization): stylistic preference distinguished from morphological grammaticality.
- **MORPH-020** (descriptive_generalization): productive layered verb-to-adjective-to-noun formation.
- **MORPH-021** (classification): nonproductive -ric formation in established lexical words.
- **MORPH-022** (classification): nonproductive verb-object agent-compound pattern.
- **MORPH-023** (descriptive_generalization): dictionary inventories versus grammatical word inventories.

## Approved prior-rule refinement
- **MORPH-009** now links the already-approved classification of complex lexical bases to the Chapter 19 source illustrating layered derivation (`verb → -able adjective → -ity noun`), without changing its earlier inflectional analysis or rule number.

## Crucial distinctions and limitations
- **Established words** are individually familiar lexical items, including inherited formations that a current productive rule would not generate.
- A **potential word** is morphologically grammatical but **not established**; a **nonce-word** is one that has been used but has not become established. A potential word need not already have been used.
- **Grammaticality here concerns morphology**, not subjective elegance. A speaker's dislike of a well-formed coinage is not evidence that its formation is ungrammatical.
- Productive successive `-able` and `-ity` can support new nominal derivatives, but no unrestricted claim is made that the sequence is available with every verb.
- Existing historic forms such as *bishopric* and *pickpocket* remain valid lexical items despite the loss of productivity of the particular formation patterns that yielded them.
- The unproductive `-ric` and plain verb + direct-object noun agent-naming patterns are **not general bans on all compound words, all nonce words, or every imaginative analogy**.
- Dictionary entry lists contain familiar **multiword** expressions, while many morphological possibilities are **not** dictionary entries. Dictionary status and morphological grammaticality are separate.
- Hypothetical example coinages are clearly described as hypothetical; their absence from contemporary dictionaries is **not claimed or independently verified**.
- No new grammaticality error-detection constraints were created.

## Counts, validation and remaining work
- **8 new approved rules** (5 classifications and 3 descriptive generalisations), **12 concepts**, **32 original AI-authored examples**, **17 cross-references**, **1 approved prior-rule refinement**.
- **0 identified conflicts**; **3 logged uncertainties** concerning nonproductive-form boundaries, affix-selection details, and establishment evidence for nonce words.
- Consolidated stacked branch: **188 active rule records and 260 distinct concept terms**. Full JSON schema, uniqueness, source, example and internal-reference validation will be verified after the commit.
- Burton-Roberts comparison remains **unverified** because comparison sources/index were not inspected.
- Chapter 19 §§1.2–5.10.3 remain **unprocessed**. Do not treat this first-section report as completion of all Chapter 19 content.
- No uploaded PDF, copyrighted tables, long quotations or complete original book examples have been committed.

**APPROVED: 19/§1.1 Established words and potential words.**
