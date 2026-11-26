# SynTutor unified Burton-Roberts notation

Specification for free sentence analysis · 9 November 2026

SynTutor uses one cumulative notation for free analysis across Chapters 1–11 of Noel Burton-Roberts, *Analysing Sentences*, 3rd ed. (2011, ISBN 9781408233740). Chapters and printed pages identify the evidence for each rule. A sentence can combine several chapters’ rules in one tree. This proposal makes the existing `FINAL` idea in [CONVENTIONS.md](../../CONVENTIONS.md) explicit. The chapter versions remain applicable to textbook transcriptions and exercises that ask learners to reproduce a specific figure. The workbook is the working inventory for this specification.

## Every-sentence requirement

For each sentence accepted by the Generator, the released system must return at least one canonical `FINAL-D1` tree for the submitted wording. The default display uses the canonical tree. A Benepar diagnostic, a schema-valid tree with a guessed construction, an unresolved response, or a tree for a corrected sentence alone counts as a coverage failure. The approved first declarative is a development fixture.

The tree and the grammaticality assessment answer different questions. For an erroneous sentence, retain its original words in the observed tree and record anomalies separately. If a correction is proposed, build its tree as a distinct analysis. For genuine structural ambiguity, present the supported alternatives or ask the learner to select a reading. Where Burton-Roberts leaves a construction underspecified, record and review any project extension separately and identify it in the explanation.

Track three independent measures: whether the original sentence receives a validated canonical tree, whether that structure matches reviewed reference analyses, and whether every displayed node has contextual evidence. The release gate requires zero uncovered sentences in the agreed regression and held-out sets, including erroneous and ambiguous cases. A finite test set measures that set’s coverage. Keep unresolved development cases as actionable gaps and add verified fixes as regression cases.

## Chapter coverage

| Chapter | What the unified tree carries forward | Printed pages |
| --- | --- | --- |
| 1 · Constituency | Immediate dominance, ordered children, constituency tests and explicit abbreviation by triangle. Expand validated phrases in free analysis. | 6–23 |
| 2 · Functions | Basic `S → NP VP`; category and function are separate. Explain roles using structural positions. | 24–45 |
| 3 · Categories | Lexical and phrasal categories, names and pronouns, and coordination at the actual category level. | 46–66 |
| 4 · Basic VP | Lexical `V` with one supported complement frame; complements are sisters of `V`. | 67–86, especially 71–72 and 79 |
| 5 · Adverbials | Recursive `VP` and `S` for adjunct attachment, particles, phrasal features and context-licensed ellipsis. | 87–110 |
| 6 · Auxiliary VPs | Auxiliary-headed VP layers, tense on the finite carrier, do-support, negation, passive and auxiliary fronting. | 111–140 |
| 7 · NPs | `DET` and `NOM`, expanded noun structure (including PartP headed by V-part) and Appendix NOM refinement. | 141–170, especially 166–168 |
| 8 · Subordination | Clausal embedding, finite subject and object wrappers, extraposition, clausal predicatives and complements of A/N/P. | 171–195 |
| 9 · Wh-clauses | `C1` and `C2`, two clause layers when licensed, wh-gaps and relative attachment. | 196–223 |
| 10 · Non-finite clauses | Clause-level `[-tense]`, covert subjects, control, co-indexing and construction-specific verb complementation. | 224–253 |
| 11 · Grammars | Background on grammaticality, speaker variation and grammar as a model. Adds no new display category in this specification. | 254–268 |

## Conflict decisions

| ID | Overlap | Unified rule | Printed evidence |
| --- | --- | --- | --- |
| U01 | `Sentence`, `PHRASE-x`, early triangles | Use `S` and validated categories for free analysis. A triangle is an abbreviated constituent with a supported category or a book-licensed omission, never a category inferred from an early placeholder. ACA is a separate abbreviated teaching view. | Ch1 pp. 14–17; Ch2 pp. 29–30; Ch8 pp. 171–173 |
| U02 | Functions vs categories | Store subject, predicate, complement and adjunct as roles. The tree uses category labels such as `NP`, `VP`, and `PP`. Keep roles distinct even when categories match. | Ch2 pp. 29–31; Ch4 p. 79; Ch5 pp. 87–90 |
| U03 | `[intrans]` and other verb features | Attach the frame to the lexical `V` node. Render each bracketed feature below the category and above the word, within the same node. A supported intransitive use has zero complements, even with an adjunct. Determine the frame from the use in this clause, including gaps or licensed ellipsis. | Ch4 pp. 71–72, [22] and [26], p. 79; Ch5 pp. 95–99 |
| U04 | Valency, phrasal status and tense | Store separate fields. Features can coexist on a node. For the unified display, order applicable rows frame, phrasal status, then tense. Assign `[pres]` or `[past]` only to the finite carrier, whether lexical or auxiliary. In inversion, the original auxiliary node retains its features and dominates a gap, while `C1` displays the fronted word. | Ch5 p. 94 [35]; Ch6 p. 113 [8]–[9], pp. 130–131; Ch9 p. 199 [11b] |
| U05 | Complements, adjuncts and auxiliaries in VP | An ordinary complement is a sister of lexical `V`. A VP adjunct is a sister of an already formed VP inside a higher VP. An auxiliary heads its own VP and takes a VP complement. An S-adverbial attaches to an S within a higher S. Track displaced attachment without a supported analysis as a coverage gap during development. | Ch4 pp. 67–79; Ch5 pp. 87–93, 99–101; Ch6 pp. 123–124 |
| U06 | Early or core NP vs Appendix | Adopt the Ch7 Appendix refinement throughout free analysis. In a common-noun NP, use `DET` where licensed, plus `NOM`. A nominal adjunct is sister of an inner `NOM`, including a unary `NOM → N` when required. An N complement is sister of `N` inside `NOM`. Retain name/pronoun and other licensed special cases. | Ch7 pp. 141–146, 166–168 [11]; Ch9 pp. 205–206 [38]–[39] |
| U07 | `C`, `Comp`, `C1` | Use `C1` for the lower complementiser position in `S′ → C1 S`, including Ch6 yes/no inversion and licensed Ch8 subordinate structures. Preserve overt or empty occupancy according to the construction. Earlier `C` and `Comp` correspond only where the structural role agrees. | Ch6 pp. 130–131; Ch8 pp. 173–174, 185 [61]; Ch9 pp. 198–199 |
| U08 | `S`, `S′`, `S″` | Use basic `S` for the clause core. Add `S′` for a licensed lower layer and `S″ → C2 S′` for a licensed higher wh/relative layer, including covert relatives. A matrix wh-question can have fronted auxiliary in C1. Embedded wh typically leaves C1 empty. Matrix subject wh does not itself license inversion. | Ch9 pp. 198–203, 205–208; Ch10 pp. 230–231, 235–236 |
| U09 | Several uses of *that* | Use `DEM` inside `DET` for demonstrative *that*, `C1` for content-clause *that*, and `C2` for relative *that* under the book’s adopted teaching analysis. Recognize relatives by the internal dependency and gap. | Ch7 pp. 142–146; Ch8 pp. 173–174; Ch9 pp. 207–208 |
| U10 | Clause after P vs a subordinating conjunction | Validate the head and its construction. Ch8 temporal `since/after/before/until` with a plain clausal complement use `PP → P S`; a P selecting *whether* takes `S′`. A genuine adverbial subordinator fills C1. Ch10 also excepts non-finite P complements from its default S′ wrapper; check the specific case. | Ch8 pp. 184–187 [61], [67c], [71]; Ch10 pp. 229–230, 234 |
| U11 | N complement vs relative modifier | A noun content clause is sister of `N`. A restrictive relative is sister of `NOM` within a higher `NOM`. A non-restrictive relative is sister of `NP` within a higher `NP`. Determine the reading from the relation to the noun phrase; commas alone are insufficient. | Ch9 pp. 204–211 |
| U12 | Finite and non-finite clauses after V | Retain the NP wrapper for finite clausal direct objects in Ch8 and the NP for a clausal subject. A finite clausal subject-predicative may be bare `S′` as a sister of copular V. For Ch10 non-finite verb complementation, omit the six-way frame on the selecting V and the automatic NP wrapper on its clause. Keep finite tense on the selecting verb when applicable. | Ch8 pp. 175–181; Ch10 pp. 236–239, 243 |
| U13 | `V(I)` vs `V(II)` | When the Ch10 distinction applies, Type I takes one clause with an overt subject. Type II takes a matrix NP object and a clause with a covert subject; identify the actual controller, including the subject-control pattern of *promise*. A clause with a covert subject after a lone selecting verb does not by itself imply Type II. | Ch10 pp. 238–243 [101b]–[102b] |
| U14 | Infinitival `to`, prepositional `to`, untensed forms | Infinitival `to` heads an auxiliary VP and displays `[-tense]` by itself. In applicable bare infinitival and participial clauses, place `[-tense]` on the initial V or auxiliary as the source specifies. An untensed verb selected lower in an auxiliary chain does not automatically carry this clause-level feature. | Ch6 pp. 113–120; Ch10 pp. 225–229, 243 |
| U15 | Gap, covert subject, empty position and ellipsis | Distinguish typed `•` gaps, covert subjects, empty C1/DET slots, and recoverable `E` ellipsis. Apply the Ch10 indexing convention to supported control and movement links. Free covert subjects have no index. Draw movement arrows as overlays. | Ch5 pp. 95–99; Ch6 pp. 127, 130–131; Ch9 p. 199; Ch10 pp. 224–225, 236 |
| U16 | Extraposition vs ordinary complement | Identify expletive *it*, the relation of the delayed clause to the main clause and the licensed book pattern. Use the Ch8 extraposed-subject structure, including the book’s treatment of *seem/appear* in that use. | Ch8 pp. 176–178, 183–184 |
| U17 | Benepar and Cambridge overlaps | Keep Benepar labels as evidence and Cambridge claims in their own channel. Only B-R sources and the explicit integration decisions above authorize B-R structure and its explanations. | Source policy in CONVENTIONS.md; primary rules U01–U16 |

## Display and storage

The compact form `(V[intrans][past] sighed)` denotes one lexical node, two feature rows and one overt word. On the diagram the order is `V`, then `[intrans]`, then `[past]`, then *sighed* connected as the terminal. Chapter 4 p. 72 [22] demonstrates the placement of `[intrans]`; Chapter 6 p. 113 [8]–[9] demonstrates the stacked tense pattern. The combined rendering of *sighed* applies both conventions.

Keep category, features, role, children, token IDs, empty-position kind, index/links and source rule separate in the analysis. Reuse `S-bar` and `S-dbar` internally and render `S′` and `S″`. Use the existing `FINAL` identifier with Appendix NOM enabled for unified free analysis. A chapter reference on a node records provenance. The current [canonical schema](../canonical-burton-roberts-tree.schema.json) requires a chapter in its profile object and uses a single token span. Check schema compatibility before runtime integration, including provenance from several chapters, exact token membership for discontinuities and zero-width anchors for gaps. Validate by overt token IDs so inserted structure cannot duplicate or consume words.

## Worked tree

**The tired students sighed quietly.** This is a SynTutor example applying Chapters 2–7 together.

```text
(S
  (NP (DET (ART The)) (NOM (AP (A tired)) (NOM (N students))))
  (VP (VP (V[intrans][past] sighed)) (AdvP (Adv quietly))))
```

The outer VP covers *sighed quietly* and the inner VP covers *sighed*. The lower NOM covers *students*; *tired* modifies it. The article and nominal occupy separate branches. The period stays in the input tokens. The tree shows the syntactic constituents.

A second composition check is **Did the tired students sigh quietly?** The same NP and adjunct structure combine with `S′ → C1 S`. *Did* fills C1, the `TENSE[past]` node in its original VP takes the linked gap, and lexical *sigh* still carries `[intrans]`. Chapter 6 pp. 130–131, Chapter 9 p. 199 and Chapter 10 p. 225 support the construction and indexing policy.

## Per-node explanations

Select a reviewed template using the canonical category, construction, child/parent relation, role and features. Bind exact submitted words through token IDs. For empty nodes, name the linked phrase, carrier, antecedent or surrounding construction with evidence for the absence. Each rendered feature is explained on its owning node. Overt terminal labels are surface text; if selectable, they share the explanation of the node that owns them. Every published node has an explanation with B-R printed-page citations or an explicit unavailable status during development. Gate publication of a fully explained canonical tree on complete reviewed coverage. Keep genuine ambiguity as evidence-backed alternatives or mark it unresolved.

| Node in the worked example | Sentence-specific explanation | Printed evidence |
| --- | --- | --- |
| S | “The tired students” is the subject NP and “sighed quietly” is its predicate VP. | Ch2 pp. 29–30 |
| Subject NP | “The tired students” is the NP immediately under S. It contains the determiner “The” and the nominal “tired students.” | Ch2 pp. 29–30; Ch7 pp. 141–142 |
| DET | “The” fills the determiner position of “The tired students.” | Ch7 pp. 141–142 |
| ART | “The” is the article that fills DET in this NP. | Ch7 pp. 141–142 |
| Outer NOM | “Tired students” consists of the modifier “tired” and the nominal “students.” | Ch7 pp. 166–168 |
| AP | “Tired” heads an adjective phrase that modifies the nominal “students.” | Ch3 p. 55; Ch7 pp. 166–168 |
| A | “Tired” is the adjective heading the modifier AP. | Ch3 p. 55 |
| Inner NOM | “Students” forms a nominal on its own, which gives “tired” a NOM sister. | Ch7 pp. 166–168 |
| N | “Students” is the noun head of the inner nominal. | Ch7 pp. 141–142, 166–168 |
| Outer VP | “Sighed quietly” combines the VP “sighed” with the adjunct “quietly.” | Ch5 pp. 87–90 |
| Inner VP | “Sighed” forms a VP by itself in this sentence because the verb takes no complement in this use. | Ch4 pp. 71–72 |
| V | “Sighed” is intransitive in this use and carries the past tense. “Quietly” modifies the VP headed by “sighed.” | Ch4 pp. 71–72; Ch5 pp. 87–90; Ch6 p. 113 |
| AdvP | “Quietly” forms an adverb phrase functioning as an adjunct to “sighed.” | Ch3 p. 56; Ch5 pp. 87–90 |
| Adv | “Quietly” is the adverb heading that adjunct phrase. | Ch3 p. 56 |

The explanations above are drafts. [The runtime registry](../../grammar/explanation_templates.json) contains one reviewed B-R structural template for basic S → NP VP and a separate reviewed Cambridge teaching template. Confirm narrower figure references for each draft and review its matching conditions before runtime publication.

## Implementation and acceptance

1. Establish the unified rules in CONVENTIONS.md for free analysis. Preserve source-figure behavior in the lesson-specific rules. Check the schema and renderer for distinct category and feature rows, licensed empty kinds, indices, and source and transformation IDs.
2. Convert and validate constituents using Benepar as candidate evidence. Resolve construction and lexical frame before applying structural rewrites. Attach provenance to each rewrite. For unknown valency, displaced adverbials or unresolved clause attachment, record a specific failure with candidate evidence during development. These cases block the all-sentence release gate until covered by a validated analysis.
3. Verify combined fixtures for declarative, yes/no, subject wh, object wh, content vs relative *that*, temporal P vs subordinator, noun complement vs modifier, finite vs non-finite verb complement, Type I vs Type II, free vs controlled subject, passive with an original object gap, and lexical valency vs adjunct. Include ambiguous and unsupported counterparts. Check hierarchy, feature ownership and placement, token yield, movement links and explanatory coverage.
4. Publish only verified rules and reviewed contextual templates. Apply the every-sentence release gate and track structural agreement and per-node explanation coverage separately.
