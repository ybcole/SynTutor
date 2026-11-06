# Burton-Roberts ↔ Cambridge crosswalk — Milestone 01

**Status:** Initial, evidence-controlled crosswalk. It records candidate comparison areas and the status of the available records. It does not claim a verified equivalence between the two frameworks.

## 1. Verification rule

A B-R/Cambridge mapping is **verified** only after the underlying relevant B-R and Cambridge source passages have been inspected, the concepts and their conditions have been compared in context, the relation has been recorded with both sets of printed-page references, and the mapping has received the required review.

The repository currently contains B-R convention documentation and chapter answer/tree records, but no B-R source PDF or separate source text directory was present in the audited Git tree. The exact B-R edition is still to be confirmed. The Cambridge extraction records themselves explicitly state that B-R mappings remain unverified.

Consequently:

- **Verified same-concept mappings:** none established by this audit.
- **Verified terminology-difference mappings:** none established by this audit.
- **Verified analytical non-equivalences:** none established by this audit.
- **Unverified mappings:** all 196 active Cambridge rule records contain B-R mapping entries marked `unverified`.
- **Candidate comparison areas:** listed below to guide a later source-based review; they are not findings of equivalence or conflict.

This is an intentional evidence boundary, not a claim that the frameworks have no relationships.

## 2. Candidate crosswalk by grammatical area

| Area | B-R evidence available in repository | Cambridge evidence available in repository | Current relation | What must be compared before verification |
|---|---|---|---|---|
| Constituents, phrases, heads, and functions | `CONVENTIONS.md` §§2, 4, 6; Chapters 1–3, V1–V3; functions are read from tree positions rather than represented as invented nodes. | Chapter 2 §1–§2 extraction batches; merged clauses/phrases rules and concepts. | Unverified | Compare the definition of constituent, category versus function, head/dependent distinctions, and the diagnostic criteria. Do not equate terms on label similarity alone. |
| Noun phrases, determiners, pronouns, and nominals | B-R V3 has one-word NP pronoun/name analyses and unlabelled internal NP structure; V7 introduces `NP → DET NOM`, recursive `NOM`, `PRE-DET`, and related refinements. | Cambridge Chapter 2/5 records include noun, NP, determinative, pronoun, fused-head and NP-function concepts. | Unverified | Compare the category of determinatives, the treatment of pronouns, NP constituent structure, fused heads, and the functions licensed by each analysis. |
| Verbs, auxiliaries, tense, and verb features | B-R V4 introduces six lexical V subcategorisation features; V6 uses `MOD PERF PROG PASS TENSE` auxiliary heads, nested VP complements, and present/past tense features; V10 adds non-finite `[-tense]` and `V(I)/V(II)`. | Cambridge Chapter 2/3/4/14 extractions include verb categories, auxiliary/lexical distinctions, inflection, complement selection, and non-finite clauses. | Unverified | Compare lexical versus auxiliary status, head status, tense versus time, agreement, verb forms, valency, and the structural function of each auxiliary. |
| Complements, objects, predicatives, and valency | B-R V4 records six subcategorisation features and reads dO/iO/sP/oP/PC from complement position; V5 distinguishes complements (sisters of V) from adjuncts (sisters of VP). | Cambridge Chapter 2 §4 and Chapter 4 §1.1 supply complement-type and valency records; active COMP rules include classification, descriptive and constraint records. | Unverified | Compare the inventory and definitions of complement, object, predicative complement, oblique, adjunct, and valency. Preserve any difference in function inventory rather than collapsing it. |
| Adjectives, adverbs, and prepositions | B-R V3 distinguishes A/AP, Adv/AdvP, P/PP and DEG; V5 includes adjunct adverbials and particle conventions. | Cambridge Chapters 2, 6, 7 and 8 include word-category and adjunct material, including Cambridge's broader preposition analysis. | Unverified | Compare category membership and phrase structure, including Cambridge's preposition analysis of items traditionally treated as adverbs or subordinators. |
| Adjuncts and adverbials | B-R V5 uses an extra VP layer for adjunct adverbials and an extra S layer for S-adverbials; `CONVENTIONS.md` records chapter-specific simplifications. | Cambridge Chapter 8 §1 and related rule records describe adjunct classes, syntactic realisation, scope, and positions. | Unverified | Compare syntactic category, attachment site, semantic scope, mobility, and whether the apparent parallel labels designate the same structural relation. |
| Finite and subordinate clauses | B-R V6 introduces S-bar in specified questions; V8 uses `S′ → C S`; V9 adds `S″ → C2 S′`; canonical stored labels are `S-bar` and `S-dbar`. | Cambridge Chapters 2, 10 and 11 include clause type, subordinate forms, content clauses, and clause-function distinctions. | Unverified | Compare clause categories, clause type versus syntactic function, finite/non-finite distinctions, complementisers, and clause embedding. |
| Wh- and relative constructions | B-R V9 uses C2/C1 layers, movement gaps and chapter-specific relative-clause structures; `CONVENTIONS.md` records a grading decision about `that` in relatives. | Cambridge Chapters 11–12 include subordinate clause and relative-construction records; Chapter 2 conflict notes mention different relative terminology/analysis. | Unverified; potential terminology/analysis divergence recorded in Chapter 2 conflicts | Compare the exact constructions, gap representation, complementiser/relative marker status, and integrated/supplementary versus restrictive/non-restrictive terminology. |
| Non-finite clauses and control | B-R V10 uses `AUX[-tense]`, indexed gaps/covert subjects, control, and `V(I)/V(II)` distinctions. | Cambridge Chapter 14 §1.1 has nine new records and refines existing non-finite clause rules; further sections remain unprocessed. | Unverified | Compare clause status, missing subjects, control, hollow clauses, auxiliaries inside non-finites, and Type I/II distinctions. |
| Coordination | B-R Chapter 3 has lexical/phrasal coordination examples and chapter-specific category requirements. | Cambridge Chapter 15 §1.1 has coordination and coordinator classification records. | Unverified | Compare headedness, coordinate category, coordinator attachment, mixed-category coordination, layering, and accepted alternatives. |
| Morphology and word formation | B-R V4–V10 includes verbal features and forms; B-R chapter tree data is not a comprehensive Cambridge-style morphology database. | Cambridge Chapters 3, 18 and 19 contain morphology/word-formation classifications and generalisations. | Unverified | Compare the precise unit of analysis and the scope of inflectional/derivational claims; avoid projecting tree conventions onto lexical morphology. |
| Information packaging, deixis, and punctuation | The current B-R tree conventions are principally constituent/phrase-marker conventions; they do not establish a mapping for every discourse or orthographic category. | Cambridge Chapters 16, 17 and 20 contain selected overview/first-section extractions. | Unverified / potentially outside the B-R tree convention scope | Determine which concepts are comparable to B-R source material and which should remain Cambridge-only supporting knowledge rather than forced tree mappings. |

## 3. Specific candidate tensions already recorded in repository data

The three records in `sources/cambridge/chapter_02/conflicts-1.json` are explicitly classified as `cambridge_vs_burton_roberts`. They identify candidate differences concerning:

1. Auxiliary-as-head, determinative category, pronoun-as-noun, copular `be`, the tense/time distinction (including the absence of a future tense category in Cambridge), and the narrower use of “object”.
2. Cambridge's inclusion of many traditional adverbs and subordinating conjunctions within the preposition category.
3. Clause terminology and relative-clause analysis, including the treatment of `that` and the integrated/supplementary distinction.

The conflict records themselves say the corresponding B-R material was not supplied and propose comparison with the B-R chapters before approval. These items therefore remain **unresolved candidate tensions**, not verified non-equivalences.

The conventions file provides relevant B-R terminology and structural descriptions, but the source-page comparison and mapping review are still outstanding.

## 4. Mapping state and review fields

The existing grammar records have fields for `burton_roberts_mapping[].relation` with the values:

- `same`
- `terminology_differs`
- `analysis_differs`
- `not_covered`
- `unverified`

For the current inventory, preserve `unverified`. Do not change it to another relation until the source comparison is completed and documented.

The following review dimensions must remain separate:

| Dimension | Meaning | Current state |
|---|---|---|
| Extraction state | A record was extracted and shaped according to the Cambridge extraction protocol. | Existing records are present; source-by-source coverage is partial. |
| Independent review | A separate second-pass review checked source completeness, rule scope, page references, examples and B-R comparison. | Reports repeatedly state this has not been performed. |
| Human approval | The project owner accepted the record for the current knowledge base. | Existing reports record owner approval. |
| Crosswalk state | The corresponding B-R relation has been verified. | All 196 active rule records remain `unverified`. |
| Runtime eligibility | The record meets the evidence, crosswalk, rule-type, scope, exception and test requirements for production evaluation. | Not established by `APPROVED` alone. |

## 5. Required evidence to resolve a mapping

For each proposed mapping:

1. Identify the relevant Cambridge rule/concept ID and its narrow printed-page citation.
2. Identify the exact B-R chapter convention, concept, tree or worked analysis, with printed page and figure/tree ID.
3. Compare definitions, structural positions, category/function distinctions, scope, conditions, exceptions and accepted alternatives.
4. Choose one relation from the schema only when the evidence justifies it.
5. Add a concise note explaining the relation and both citations.
6. Preserve disagreements as separate framework-specific analyses when a direct translation is false.
7. Record reviewer, date, protocol/content version, and tests before any Cambridge record is made runtime-eligible.

Until then, the correct output is an unresolved mapping or an explicit “no established B-R basis” state.
