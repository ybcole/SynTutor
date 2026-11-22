# H02 Reference Inventory — Cambridge Grammar Rules and Implemented Coverage

**Project:** SynTutor: An Explainable AI-Based Framework for Syntax Tree-Driven Grammar Analysis and Learning Using NLP  
**Date Prepared:** 2026-11-22  
**Status:** Pre-evaluation reference inventory (SynTutor has **not** been run on the proposed evaluation dataset)

---

## 1. Primary Authoritative Reference Verified

| Field | Verified Value |
| :--- | :--- |
| **Authors** | Rodney Huddleston & Geoffrey K. Pullum (with Laurie Bauer, Betty Birner, Ted Briscoe, Peter Collins, David Denison, David Lee, Anita Mittwoch, Geoffrey Nunberg, Frank Palmer, John Payne, Peter Peterson, Lesley Stirling, Gregory Ward) |
| **Title** | *The Cambridge Grammar of the English Language* (CGEL) |
| **Edition** | **2002 original edition** (Cambridge University Press; ISBN-13 `9780521431460`) |
| **Inspected File** | `/Users/kiyel/Downloads/Cambridge_Grammar_Chapters_1-20-1.pdf` |
| **File Size** | `9,290,880` bytes |
| **SHA-256** | `0c2fe2c22d881d3684482069c787aea7fd8490b92d211bfd027e02498b555a25` (matches [source_manifest_2026-11-08.json](file:///Users/kiyel/Desktop/SynTutor/sources/cambridge/source_manifest_2026-11-08.json)) |
| **Page Coverage** | `1,762` PDF pages covering **Chapters 1–20**, printed pages **1–1764** |

---

## 2. SynTutor's Actual Implemented Grammar Evaluation Architecture

Before selecting H02 evaluation items, the repository was inspected to map **what SynTutor genuinely implements** (so H02 tests real implemented grammar coverage rather than out-of-scope phenomena, while also documenting governance limitations transparently):

1. **Linguistic Constraint Matrix (`server/matrix.py`, `server/ruleset.py`, `server/licensing.py`):**
   - `170` `C-*` constraint identifiers in `server/matrix.py`, `135` in `server/ruleset.py`, and `9` positive-evidence lexical/relative identifiers in `server/licensing.py`.
   - Organized into `11` numbered `RULEBOOK` categories (`1.1`–`11.8`):
     - `1.x` Word forms & morphology (`1.1`–`1.13`)
     - `2.x` Agreement (`2.1`–`2.14`)
     - `3.x` Articles & determiners (`3.1`–`3.8`, `3.15`)
     - `4.x` Nouns (`4.1`–`4.3`)
     - `5.x` Pronouns (`5.1`–`5.7`)
     - `6.x` Verbs (`6.1`–`6.20`)
     - `7.x` Adjectives & adverbs (`7.1`–`7.7`)
     - `8.x` Prepositions (`8.1`–`8.6`)
     - `9.x` Sentence structure (`9.1`–`9.15`)
     - `10.x` Punctuation & orthography (`10.1`–`10.10`)
     - `11.x` Meaning & usage (`11.1`–`11.8`, mostly context-advisory `METHOD_C`)
2. **Cambridge Rule Registry & Runtime Evaluator (`grammar/cambridge_runtime_overlay.json`, `server/cambridge_evaluator.py`, `server/cgel_phase_d.py`):**
   - `3,914` total extracted rules in `grammar/rules/*.json`, of which **193 rules** are enabled in the runtime overlay via deterministic `candidate_probe_set` checks spanning **15 CGEL chapters**:
     - Ch. 1 (1), Ch. 3 (34), Ch. 4 (13), Ch. 5 (32), Ch. 6 (2), Ch. 7 (2), Ch. 10 (14), Ch. 13 (13), Ch. 14 (7), Ch. 15 (3), Ch. 16 (7), Ch. 17 (23), Ch. 18 (10), Ch. 19 (15), Ch. 20 (17).
   - **Critical Governance Note:** All 193 runtime-enabled Cambridge rules currently operate under `owner_waiver: true, independent_review: false`, and the example sentences stored inside `grammar/rules/*.json` are tagged `origin: "ai_authored"`. **None** of those `ai_authored` examples were reused in our proposed 100-sentence dataset; instead, every Cambridge item in `H01_H02_PROPOSED_100_SENTENCES.csv` was verified directly against printed pages of `Cambridge_Grammar_Chapters_1-20-1.pdf` and audited for `0/100` repository-wide contamination.
3. **Explainable AI (XAI) Layer (`server/explanations.py`, `server/learner_explanations.py`, `server/xai_facts.py`, `server/xai_composer.py`, `server/xai7_unified.py`):**
   - Enforces fail-closed source provenance (`structural` channel requires B–R reviewed records; `grammatical` and `remediation` channels require Cambridge/server-evaluated findings) and surfaces `NO_BOOK_BASIS` / `ANALYSIS_UNRESOLVED` rather than fabricating textbook citations when evidence is absent.

---

## 3. Verified Cambridge Grammatical Rules Mapped to Proposed H02 Test Items

The proposed dataset allocates **50 ungrammatical items (`U01`–`U50`)** across **6 major grammar domains** (plus **50 grammatical controls `G01`–`G50`**, including **19 exact minimal pairs `P01`–`P19`**). Every rule below was verified directly in `Cambridge_Grammar_Chapters_1-20-1.pdf` (and `Syntax_Reference_Chapters_1-11-1.pdf` for `U03`–`U06`):

### Domain 1 — Verb Form, Auxiliaries & Modals (`10` ungrammatical items: `U01`–`U10`)

| Item ID (Pair) | Grammar Phenomenon | Verified Reference Locator | SynTutor Rule Mapping | Expected Judgment & Primary Correction | Valid Alternatives |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `U01` (`P01`) | Past participle used as finite main verb | CGEL Ch. 3, §1.2, p. 76 `[4ib]` | `MORPH-025` / `C-VBN-SIMPLE-PAST` | Ungrammatical → *She took the car.* | *She has taken the car.*; *She had taken the car.* |
| `U02` (`P02`) | Perfect `have` + preterite instead of past participle | CGEL Ch. 3, §1.2, p. 76 `[4iib]` | `MORPH-026` / `C-AUX-FORM` | Ungrammatical → *She had taken the car.* | *She took the car.* |
| `U03` | Supportive `do` with copular `be` negation | B–R Ch. 6, p. 132 `[102b]` (cf. CGEL Ch. 3 §2.1.1) | `CLS-100` / `COMP-030` | Ungrammatical → *Kubla wasn't extravagant.* | *Kubla was not extravagant.* |
| `U04` | Lexical verb inverted without `do`-support | B–R Ch. 6, p. 131 (cf. CGEL Ch. 3 §2.1.2 p. 93) | `CLS-103` / `C-QUESTION-INVERSION` | Ungrammatical → *Did he dance?* | None (canonical closed interrogative) |
| `U05` (`P08`) | Supportive `do` with perfect `have` in question | B–R Ch. 6, p. 132 `[98a]` (cf. CGEL Ch. 3 §2.1 p. 93) | `CLS-100` / `COMP-030` | Ungrammatical → *Have they gone?* | None |
| `U06` | Supportive `do` with progressive `be` in question | B–R Ch. 6, p. 132 `[97a]` (cf. CGEL Ch. 3 §2.3 p. 105) | `COMP-030` / `CLS-100` | Ungrammatical → *Are they going?* | None |
| `U07` | Double modal (`will can`) | CGEL Ch. 3, §2.3, p. 105 `[40ii]` | `COMP-031` / `C-MODAL-STACK` | Ungrammatical → *He will be able to swim soon.* | *He can swim soon.* |
| `U08` (`P09`) | Auxiliary ordering: perfect before modal | CGEL Ch. 3, §2.3, p. 105 `[41ib]` | `COMP-033` / `C-AUX-FORM` | Ungrammatical → *She could have won first prize.* | *She had been able to win first prize.* |
| `U09` (`P10`) | Auxiliary ordering: progressive before perfect | CGEL Ch. 3, §2.3, p. 105 `[41iib]` | `COMP-033` / `CLS-333` | Ungrammatical → *He has been reading my mail.* | *He is reading my mail.* |
| `U10` | Modal in `to`-infinitival (`to can`) | CGEL Ch. 3, §2.4(a), p. 106 `[45ia]` | `C-MODAL-ABLE` / `C-TO-BASE` | Ungrammatical → *I'd like to be able to swim.* | *I would like to be able to swim.* |

### Domain 2 — Subject–Verb Agreement (`9` ungrammatical items: `U11`–`U19`)

| Item ID (Pair) | Grammar Phenomenon | Verified Reference Locator | SynTutor Rule Mapping | Expected Judgment & Primary Correction | Valid Alternatives |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `U11` | Simple 3rd-person singular SVA *(researcher minimal-pair variant)* | CGEL Ch. 4, §3.1, p. 237 `[4i]` | `C-SUBJECT-AGREEMENT` / `2.1` | Ungrammatical → *The minister knows the candidates.* | *The ministers know the candidates.* |
| `U12` | SVA across intervening PP (`accuracy of the quotes have`) | CGEL Ch. 5, §18.1, p. 500 `[7ii]` | `C-SUBJECT-AGREEMENT` / `2.2` | Ungrammatical → *...the accuracy of the quotes has not been disputed.* | None |
| `U13` | Coordinated concrete NP subjects (`John and his father amazes`) | CGEL Ch. 5, §18.3, p. 508 | `C-COORD-SUBJ-AGREE` / `2.3` | Ungrammatical → *John and his father amaze me.* | None |
| `U14` (`P14`) | Disjunctive singular coordination (`Either Mary or John are`) | CGEL Ch. 5, §18.3, p. 508 `[31i]` | `C-CORRELATIVE-AGREE` / `2.3` | Ungrammatical → *Either Mary or John is sure to go.* | None |
| `U15` | Distributive `each...and each...` coordination | CGEL Ch. 5, §18.3, p. 508 `[28i]` | `C-INDEFINITE-AGREE` / `2.8` | Ungrammatical → *Each dog and each cat has to be registered.* | *Dogs and cats have to be registered.* |
| `U16` (`P13`) | Collective noun with whole-group predicate (`consist of`) | CGEL Ch. 5, §18.2, p. 502 `[10i]` | `C-COLLECTIVE` / `2.5` | Ungrammatical → *The committee consists of two academic staff and three students.* | None |
| `U17` (`P05`) | Plural-only `cattle` with singular determiner & verb | CGEL Ch. 5, §3.2.2, p. 345 `[38b]` | `PHR-062` / `C-PLURAL-ONLY` | Ungrammatical → *These cattle belong to my uncle.* | *Those cattle belong to my uncle.* |
| `U18` | Singular `-s` disease noun (`Shingles are`) | CGEL Ch. 5, §3.2.3, p. 346 `[40]` | `PHR-065` / `C-PLURAL-ONLY` | Ungrammatical → *Shingles is often excruciatingly painful.* | None |
| `U19` | Existential `there` with full-word copula *(researcher minimal-pair variant)* | CGEL Ch. 4, §3.2.2, p. 242 | `C-EXISTENTIAL-VERB` / `2.4` | Ungrammatical → *There are only two problems remaining.* | None (preserves plural quantity) |

### Domain 3 — Pronoun Case, Genitives & Reflexives (`9` ungrammatical items: `U20`–`U28`)

| Item ID (Pair) | Grammar Phenomenon | Verified Reference Locator | SynTutor Rule Mapping | Expected Judgment & Primary Correction | Valid Alternatives |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `U20` | Accusative pronoun as matrix finite subject (`Me made...`) | CGEL Ch. 5, §16.2.1, p. 459 `[7ib]` | `PHR-283` / `C-PRONOUN-CASE` | Ungrammatical → *I made up some new curtains.* | None |
| `U21` (`P12`) | Accusative pronoun as embedded finite subject (`him is`) | CGEL Ch. 5, §16.2.1, p. 459 `[7ivb]` | `PHR-283` / `C-PRONOUN-CASE` | Ungrammatical → *I think he is mad.* | *I think him mad.* |
| `U22` (`P06`) | Nominative pronoun as direct object (`arrested he`) | CGEL Ch. 5, §16.2.1, p. 461 `[17ib]` | `PHR-289` / `C-PRONOUN-CASE` | Ungrammatical → *The police arrested him on Friday.* | None |
| `U23` (`P07`) | Nominative pronoun as object of preposition (`near I`) | CGEL Ch. 5, §16.2.1, p. 461 `[17iiib]` | `PHR-289` / `C-PREP-PRON-CASE` | Ungrammatical → *Pamela was standing near me.* | None |
| `U24` (`P17`) | Nominative subject of `for`-infinitival (`For he to go`) | CGEL Ch. 5, §16.2.1, p. 461 `[17ivb]` | `PHR-290` / `CLS-285` | Ungrammatical → *For him to go alone would be risky.* | None |
| `U25` | Accusative `whom` as interrogative subject | CGEL Ch. 5, §16.2.3, p. 464 `[28ia]` | `PHR-295` / `C-PRONOUN-CASE` | Ungrammatical → *Who wrote the editorial?* | None |
| `U26` | Nominative `who` after fronted preposition (`To who`) | CGEL Ch. 5, §16.2.3, p. 465 `[33ib]` | `C-PREP-PRON-CASE` | Ungrammatical → *To whom are you referring?* | *Who are you referring to?* |
| `U27` | Dependent genitive `my` without head noun | CGEL Ch. 5, §16.4, p. 471 | `PHR-305` / `C-POSSESSIVE` | Ungrammatical → *Max's attempt wasn't as good as mine.* | *Max's attempt wasn't as good as my attempt.* |
| `U28` | Inadmissible reflexive after spatial `with` (`with themselves`) | CGEL Ch. 17, §3.1.1, p. 1489 `[22iii]` | `C-REFLEXIVE-ANTECEDENT` | Ungrammatical → *They took their cousin with them.* | None |

### Domain 4 — Determiners, Articles & Count/Non-Count Nouns (`7` ungrammatical items: `U29`–`U35`)

| Item ID (Pair) | Grammar Phenomenon | Verified Reference Locator | SynTutor Rule Mapping | Expected Judgment & Primary Correction | Valid Alternatives |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `U29` | Bare singular count nominal as subject (`Old man gave...`) | CGEL Ch. 5, §2, p. 329 | `PHR-028` / `C-ARTICLE` | Ungrammatical → *The old man gave it to me.* | *An old man gave it to me.*; *That old man gave it to me.* |
| `U30` | `every` + non-count singular noun (`every crockery`) | CGEL Ch. 5, §3.1, p. 339 `[20ib]` | `PHR-044` / `C-UNCOUNTABLE` | Ungrammatical → *He broke all the crockery.* | *He broke every piece of crockery.* |
| `U31` | `all` + bare singular count noun (`All cup`) | CGEL Ch. 5, §3.1, p. 339 `[22a]` | `C-COUNT-MASS` / `3.8` | Ungrammatical → *All cups had been broken.* | *All the cups had been broken.*; *The whole cup had been broken.* |
| `U32` | `another` + unquantified plural noun (`Another bodies`) | CGEL Ch. 5, §3.4, p. 353 `[70i]` | `C-DET-NOUN-AGREE` / `3.8` | Ungrammatical → *Another body had been discovered.* | *Other bodies had been discovered.* |
| `U33` | Fused-head `the` (`than the from France`) | CGEL Ch. 5, §6.1, p. 371 `[8iii]` | `PHR-126` / `C-DETERMINER` | Ungrammatical → *...more popular than that from France.* | *...more popular than the wine from France.* |
| `U34` (`P11`) | Fused-head `every` (`Every of them`) | CGEL Ch. 5, §7.4, p. 379 `[23ib]` | `PHR-140` / `C-DETERMINER` | Ungrammatical → *Each of them was cut in two.* | *Every one of them was cut in two.* |
| `U35` | `a`/`an` liaison before silent-h *(researcher clause framing)* | CGEL Ch. 18, §6.4, p. 1618 `[15i]` | `MORPH-141` / `C-ARTICLE-MISMATCH` | Ungrammatical → *It was an honest mistake.* | None |

### Domain 5 — Complementation, Valency & Word Order (`8` ungrammatical items: `U36`–`U43`)

| Item ID (Pair) | Grammar Phenomenon | Verified Reference Locator | SynTutor Rule Mapping | Expected Judgment & Primary Correction | Valid Alternatives |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `U36` | `enjoy` + `to`-infinitive (`enjoys to be`) | CGEL Ch. 4, §1.2, p. 221 | `COMP-062` / `C-GERUND-INFINITIVE` | Ungrammatical → *He enjoys being lazy.* | *He likes to be lazy.* (lexical change) |
| `U37` (`P03`) | `borrow` double-object frame (`borrowed her the money`) | CGEL Ch. 4, §8.2.1, p. 309 `[42iva]` | `C-VERB-CLAUSE-PATTERN` / `6.20` | Ungrammatical → *I borrowed the money for her.* | None (preserves verb `borrow`) |
| `U38` (`P04`) | `explain` double-object frame (`explained her the problem`) | CGEL Ch. 4, §8.2.1, p. 309 `[42iia]` | `COMP-202` / `C-VERB-CLAUSE-PATTERN` | Ungrammatical → *I explained the problem to her.* | None (canonical light NP) |
| `U39` | Light NP direct object postposed after PP (`returned to Jo the books`) | CGEL Ch. 4, §4.1, p. 247 | `C-OBJECT-ORDER` / `9.15` | Ungrammatical → *I returned the books to Jo.* | None |
| `U40` | Adverb intervening between verb and object (`saw often Tom`) | CGEL Ch. 4, §4.1, p. 247 | `CLS-117` / `C-ADVERB-PLACEMENT` | Ungrammatical → *She often saw Tom.* | *She saw Tom often.* |
| `U41` | `enough` intervening between verb and NP object (`like enough the idea`) | CGEL Ch. 6, §2.2, p. 535 `[22iiia]` | `WCAT-046` / `C-INTENSIFIER` | Ungrammatical → *He doesn't like the idea enough.* | None |
| `U42` (`P15`) | Passive causative `make` missing `to` *(researcher minimal-pair variant)* | CGEL Ch. 14, §5.4, p. 1234 `[35ii]` | `CLS-357` / `CLS-1451` / `C-CAUSATIVE-TO` | Ungrammatical → *We were made to feel guilty.* | *They made us feel guilty.* (active) |
| `U43` | Passivisation of active-only verb `befall` | CGEL Ch. 16, §10.1.2, p. 1432 `[16ib]` | `C-INTRANSITIVE-PASSIVE` / `6.5` | Ungrammatical → *A strange adventure befell him.* | None |

### Domain 6 — Clauses, Polarity, Comparatives, Coordination & Punctuation (`7` ungrammatical items: `U44`–`U50`)

| Item ID (Pair) | Grammar Phenomenon | Verified Reference Locator | SynTutor Rule Mapping | Expected Judgment & Primary Correction | Valid Alternatives |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `U44` (`P16`) | Remote conditional apodosis missing modal auxiliary | CGEL Ch. 3, §2.4(d), p. 107 `[46ii]` | `CLS-119` / `C-CONDITIONAL-WILL` | Ungrammatical → *If you came tomorrow, you would be able to help with the flowers.* | *If you came tomorrow, you could help with the flowers.* |
| `U45` | NPI `at all` in positive declarative | CGEL Ch. 9, §4.1, p. 826 | `C-NPI-LICENSING` / `3.7` | Ungrammatical → *She didn't like it at all.* | *She liked it.*; *She did not like it at all.* |
| `U46` (`P18`) | Omitted subject relativiser (`the letter drew...`) | CGEL Ch. 12, §3.1, p. 1037 | `C-RELATIVE-CLAUSE` / `9.10` | Ungrammatical → *This is the letter that drew our attention to the problem.* | *This is the letter which drew our attention to the problem.* |
| `U47` | `fewer` with non-count singular noun (`fewer money`) | CGEL Ch. 13, §4.1.2, p. 1127 | `CLS-1159` / `C-COUNT-MASS` | Ungrammatical → *Kim has less money than Pat.* | None |
| `U48` (`P19`) | Mixed gerund-participial and `to`-infinitival subject coordination | CGEL Ch. 15, §3.1(b), p. 1324 `[6]` | `CLS-1035` / `C-PARALLEL` | Ungrammatical → *Cycling there or going on foot would be dangerous.* | *To cycle there or to go on foot would be dangerous.* |
| `U49` | Comma splice before connective adjunct `however` | CGEL Ch. 20, §3.2.3, p. 1742 `[15ii]` | `OTH-708` / `C-COMMA-SPLICE` | Ungrammatical → *...bank fees; however, government charges apply.* | *...bank fees. However, government charges apply.* |
| `U50` | Genitive apostrophe on personal pronoun (`your's`) | CGEL Ch. 20, §8.3, p. 1763 | `OTH-761` / `C-APOSTROPHE` | Ungrammatical → *This is yours.* | None |

---

## 4. Cambridge Rules and Phenomena Excluded from Objective Single-Key Scoring

To preserve descriptive linguistic accuracy and prevent prescriptive bias in H02 scoring, the following phenomena — explicitly marked by Huddleston & Pullum (2002) as **varietal (`%`), stylistic, optional, or discourse-dependent (`#`)** — are **excluded** from the objective ungrammatical benchmark:

| Phenomenon | CGEL Reference | Why Excluded from Objective Error Scoring |
| :--- | :--- | :--- |
| **Coordinate nominative `I` after preposition/verb** (`%between you and I`, `%represent Helen and I`) | Ch. 5, §16.2.2, p. 463 `[23i]` | CGEL explicitly classifies final-coordinate `I` as so widespread in speech that it constitutes a variety of Standard English (`%`), not categorical `*` ungrammaticality. |
| **Contracted existential `There's` + plural NP** (`%There's only two problems remaining`) | Ch. 4, §3.2.2, p. 242 | CGEL marks cliticised `There's` with plural post-verbal NPs as acceptable in informal Standard English (`%`); only uncontracted full-word `There is` (`U19`) is tested. |
| **`less` with count plural nouns** (`He made less mistakes`) | Ch. 13, §4.1.2, p. 1127 `[17vi]` & n. 16 | CGEL notes divided usage and prescriptive stigma on `less` + count plurals, whereas `fewer` + non-count singular (`*fewer money`, `U47`) is categorically ungrammatical. |
| **Optional plural override with collective nouns** (`The committee have not yet come to a decision`) | Ch. 5, §18.2, p. 502 `[8ii]` | CGEL states plural override is fully grammatical in Standard English (especially BrE); only predicates that **forbid** plural override (`*The committee consist of...`, `U16`) are scored objectively. |
| **`who` vs. `whom` as verb/stranded-preposition object** (`Who did you meet?`, `Who are you referring to?`) | Ch. 5, §16.2.3, pp. 464–465 `[26]`, `[31]` | Style alternation between formal `whom` and neutral/informal `who`; only categorical violations (`*Whom wrote...` `U25` and `*To who...` `U26`) are tested. |
| **Prescriptive myths rejected by CGEL** (split infinitives, stranded prepositions, sentence-final prepositions, singular `they` with indefinite antecedents) | Ch. 1, §2.2; Ch. 5, §17.2.4 | Categorically grammatical in Standard English according to CGEL; penalizing them would inject prescriptive error into the rubric. |
| **Purely pragmatic/contextual semantic oddities (`#`)** (e.g., first-mention definiteness, register mismatch, ambiguous coreference, collocation preferences `METHOD_C` in `server/ruleset.py`) | CGEL Ch. 1 §5; `server/ruleset.py` §11 | Cannot be adjudicated objectively on isolated single sentences without discourse context. |
| **Non-standard dialectal negative concord (`!He didn't say nothin'`)** | Ch. 9, §6.2, p. 846 `[6]` | Marked `!` (non-standard dialect) rather than universal syntactic ill-formedness and homonymous with Standard English double semantic negation (`He didn't say nothing` = "he said something"). |
