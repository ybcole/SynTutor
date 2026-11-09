# CONVENTIONS.md — Tree-drawing rulebook for SynTutor

**Source of truth:** Noel Burton-Roberts, *Analysing Sentences: An Introduction to English Syntax* (edition as in the supplied PDFs; the PDFs mention a Second Edition preface, so confirm the edition). Chapters 1–11.

**Purpose:** This file tells any AI (or human) exactly how trees are drawn, labelled, and graded *in each chapter*, because the book **changes its conventions as it goes**. Read §0 before generating anything.

**Copyright note:** This is a public repo. Everything here is paraphrase plus very short example phrases for tree shapes. Do not paste passages of the book or its exercise text into the repo. Cite as `Ch7 p.149` (printed page numbers).

---

## 0. Rules for the AI (read first)

1. **The B-R book is the authority for B-R tree shape.** Do not use Penn Treebank /
   Benepar conventions, textbook X-bar theory, or your own habits to decide a
   canonical B-R tree. Benepar may provide a candidate parse to a separately
   validated adapter, but its output is not canonical. If the B-R book does not
   support a structural decision, output `UNSURE` and stop for human review.
   Cambridge may support broader grammatical claims, but cannot change a B-R
   phrase-marker convention.
2. **Textbook figures and lesson trees carry a chapter convention** (V1–V10, §1). Draw them using the conventions of their own chapter. **Never "upgrade" an early-chapter tree to later conventions**, and never use a later convention in an earlier chapter (e.g. no `NOM` before Ch7, no `S′` before Ch6).
3. **Functions are not nodes.** Subject, direct object, adjunct, etc. are *read off* tree positions (§6). They are never drawn as labels in a phrase marker (Ch2 p.30; Ch5 p.88).
4. **Triangles are legitimate.** A triangle means "internal structure not analysed here." Use triangles exactly where the book does (the exercise text usually says which constituents to triangle). A triangle normally carries its category label; Chapter 9 explicitly permits an unlabelled wh triangle under C2. Preserve that omission rather than inferring a label.
5. **Gradable analyses vs. alternatives:** some exercises have more than one accepted analysis (§9). Store them in `accepted_alternatives`, don't pick one silently.
6. **Evidence grading:** every convention below is tagged `[IMG]` (checked against the book's page images) or `[TXT]` (taken from the book's text only; shape of the tree not yet visually checked). For `[TXT]` items, transcribe from the page image before using them as gold trees.
7. **Every explanation shown to a learner must be source-grounded (see §14).**
   Structural claims about a B-R tree must use B-R definitions, tests, worked
   answers, and conventions with chapter+printed-page citations. Broader
   grammatical claims may use separately reviewed Cambridge records with exact
   printed-page citations, explicit conditions, and exceptions. Keep the source
   authorities visible and do not force an unverified cross-framework mapping.
   If the relevant source gives no basis, show nothing invented: use
   `NO_BOOK_BASIS` or `NO_CAMBRIDGE_BASIS`, as applicable.

---

## 1. Convention versions at a glance

| Ver. | Chapter | What the trees look like from here on |
|---|---|---|
| **V1** | Ch1 (p.6) | No categories. Top node can be `Sentence`; other phrase nodes are unlabelled or lettered `PHRASE-a/b/c`. Words are direct children of their phrase. Triangles introduced. |
| **V2** | Ch2 (pp.24–45; categories pp.29–30) | The p.24 introductory `Sentence` display is retained. The categorical top split is `S → NP VP` (subject/predicate). Only `S`, `NP`, `VP` labels. Everything else still triangle or `PHRASE-x`. |
| **V3** | Ch3 (p.46) | Lexical + phrasal categories: `N, NP, A, AP, DEG, Adv, AdvP, P, PP`; `name` / `pronoun` words; co-ordination. Internal NP nodes are still **unlabelled/lettered** (no `NOM` yet). |
| **V4** | Ch4 (p.67) | `V` appears, with **sub-categorisation features**: `[trans] [intrans] [ditrans] [intens] [complex] [prep]`. Complements are sisters of V inside VP. |
| **V5** | Ch5 (p.87) | **Two levels of VP**: adjunct adverbials are sisters of VP inside a higher VP. S-adverbials are sisters of S inside a higher S. `Prt`, `[phrasal]`, ellipsis `E`. |
| **V6** | Ch6 (p.111) | Auxiliaries `MOD PERF PROG PASS TENSE` as heads taking VP complements; tense features `[pres]/[past]`; **gaps `•`**; question fronting to `C` under `S′`. |
| **V7** | Ch7 (p.141) | **NP rebuilt**: `NP → DET NOM` (except pronoun/name NPs). `NOM` is recursive. Also `PRE-DET`, `PartP`, compound `N`. (Appendix = optional refinement, see D1.) |
| **V8** | Ch8 (p.171) | Subordinate clauses: `S′ → C S`. Clauses as subject/object sit under `NP`. Clause complements of V/A/N/P. Extraposition. Abbreviated clausal analysis (ACA). |
| **V9** | Ch9 (p.196) | `S″ → C2 S′`, with `S′ → C1 S`. Wh-fronting to C2 leaving a gap. Relative clauses (restrictive = sister of NOM; non-restrictive = sister of NP). |
| **V10** | Ch10 (p.224) | Non-finite clauses: `[-tense]` auxiliary (`to`), **indices / control**, covert subjects `•`, verb types `V(I)` / `V(II)`. Clause complements of V **drop the old 6-way features and the NP node.** |
| — | Ch11 (p.254) | Theory chapter. No new trees (see §10). |

**Free analysis uses `FINAL-D1`**, one cumulative notation across the book with the Chapter 7 Appendix NOM refinement. The construction determines which rules apply. Chapter numbers on rules and nodes identify their source evidence. A guarded adapter can produce a canonical tree for a supported construction and otherwise leaves the candidate unresolved. For the first supported declarative, a lexical V carries `[intrans]` then `[past]` as feature rows under the same V and above the word (Ch4 p.72 [22], Ch6 p.113 [8]–[9]).

---

## 2. Tree notation (what to store)

### 2.1 Labelled-bracket text form (for transcription and review)

```
(LABEL[feat,feat]_i child child ...)   node; features in [], index as _i
word                                   terminal, plain text
(LABEL△ w1 w2 w3)                      triangle: constituent not analysed further
•  or  •_n                             gap / covert NP, optional index n
<that>                                 element present structurally but not overt (elided C, etc.)
```

Examples (all `[IMG]` unless noted):

```
Ch5 [12]  (S (NP△ Max) (VP (VP (V[trans] spotted) (NP△ those wildcats)) (PP△ in the spring)))
Ch7 [4]   (NP (DET (ART the)) (NOM (AP (A sad)) (N clowns)))
Ch9 [11b] (S″ (C2 what) (S′ (C1 is) (S (NP△ Vince) (VP (VP (PROG[pres] •) (VP (V[trans] taking) (NP •))) (PP△ to Athens)))))
```

### 2.2 JSON form (what the app loads)

```json
{
  "label": "VP",
  "features": [],
  "index": null,
  "triangle": false,
  "children": [ { "word": "spotted" } ]
}
```
Terminals: `{"word":"spotted"}`. Gap: `{"gap":true,"index":1}`. Elided: `{"word":"that","elided":true}`. Triangle: `"triangle": true` with `"words":["those","wildcats"]` instead of `children`.

### 2.3 Label spelling (canonical, store these)

| Store as | Display as | Notes |
|---|---|---|
| `S-bar` | S′ | Book text/figures print S′; PDF text extraction garbles the primes. |
| `S-dbar` | S″ | |
| `AdvP` | AdvP | Book says "AdvP". Never `ADVP`. |
| `AP` | AP | Never `ADJP`. |
| `DEG` | DEG | Ch3 text says "deg"; figures use DEG. Use `DEG`. |
| `C` (V6–V8), `C1` / `C2` (V9+) | same | `C` = `C1`. Ch8 [61] figure prints `Comp`; treat as `C`. |
| `[-tense]` | [-tense] | In Ch10 the node for `to` carries just this label (no letter). Store as label `"AUX"` with feature `-tense`. |

### 2.4 Things that are **not** part of a phrase marker
Movement arrows and dotted lines (Ch6 p.127; Ch9 p.199: "not part of the phrase marker, but help"). Store movement separately as `movement: [{from, to}]` if you want it, never as tree structure.

### 2.5 Dominance vocabulary (Ch1 p.17, Ch2 p.31) — implement exactly
- **Node**: any labelled point that can branch.
- **Dominates**: everything below it joined by lines. **Immediately dominates**: no intervening node.
- **Mother / daughter / sister**: immediate dominance relations.
- **Constituent test:** a word sequence is a constituent iff **one node dominates all and only those words**. (Auto-grades Ch1 Ex1, Ex4.)
- An element belongs **directly to only one phrase** at a time (Ch1 p.17).

---

## 3. Master inventories

### 3.1 Categories and nodes

| Label | Meaning | Intro | Notes |
|---|---|---|---|
| `Sentence` | top node | V1 | Replaced by `S` from Ch2 |
| `PHRASE-a/b/c` | placeholder phrase | V1 | Used until the category is introduced |
| `S` | sentence/clause | V2 | |
| `NP`, `VP` | noun / verb phrase | V2 | |
| `N`, `A`, `Adv`, `P`, `DEG` | lexical cats | V3 | `DEG` = degree adverb |
| `AP`, `AdvP`, `PP` | phrasal cats | V3 | |
| `name`, `pronoun` | words that are full NPs | V3 | `(NP (name Max))`, `(NP (pronoun they))`; also used in V7 |
| `V` | verb | V4 | always with features from V4 |
| `Prt` | particle (phrasal verbs) | V5 | |
| `MOD PERF PROG PASS` | auxiliaries | V6 | each heads a VP and takes a VP complement |
| `TENSE` | `do` as tense-carrier | V6 | `(TENSE[past] did)`; negation attaches: `did not` |
| `S′` (`S-bar`), `C` | clause + complementiser | V6/V8 | V6 only for fronted aux in questions; V8 for all subordinate clauses |
| `DET` → `ART DEM Q POSS` | determiner slot and its fillers | V7 | `ART` the/a; `DEM` this/that; `Q` some/any/no…; `POSS` my/John's |
| `PRE-DET` | all, both, half | V7 | sister of an NP inside an NP |
| `NOM` | intermediate nominal level | V7 | recursive |
| `PartP` | participle phrase (pre-modifier in NOM) | V7 [TXT] | |
| `S″`, `C2`, `C1` | wh-clause layer | V9 | |
| `[-tense]` aux | `to` | V10 | |

### 3.2 Features (written on V and auxiliaries)

| Feature | Intro | Meaning |
|---|---|---|
| `[trans]` `[intrans]` `[ditrans]` `[intens]` `[complex]` `[prep]` | V4 | the six verb sub-categories |
| `[phrasal]` | V5 | stacks: `V[trans,phrasal]` (Ch5 [35], [39] `[IMG]`) |
| `[pres]` `[past]` | V6 | tense. Only the **first** verb in a sequence is tensed. Stacks with sub-cat: `V[ditrans,past]` |
| `[-tense]` | V10 | non-finite |
| `V(I)` / `V(II)` | V10 | verb type for clause complements, shown in parentheses (Ch10 p.243 `[IMG]`) |

### 3.3 Functions (read from positions; §6)
`S` (subject), `P` (predicate), `H` (head), `M` (modifier), `C` (complement), `dO`, `iO`, `sP` (subject-predicative), `oP` (object-predicative), `PC` (prepositional complement), `aA` (adjunct adverbial, Ch5), `sA` (S-adverbial, Ch5).

### 3.4 Gaps, indices, ellipsis
- `•` = gap from movement (passive Ch6; wh Ch9) or covert NP (Ch10).
- **From Ch10 on, always co-index** controlled gaps, including movement gaps (Ch10 p.225).
- `E` = ellipted element in utterances (Ch5 [46]) [TXT].

---

## 4. Chapter-by-chapter conventions

Each entry: **new vocabulary → drawing rules → tests → traps → lesson units → gradable exercises**.

### Ch1 — Constituents (V1)
- **Vocabulary:** structure, constituent, immediate constituent, hierarchy, phrase, phrase marker, node, dominate, immediately dominate, ungrammatical (*), triangle.
- **Rules:** Words are not direct children of S; sentences consist of **phrases**. A phrase inside a phrase is normal. No labels beyond `Sentence` / `PHRASE-x`. Use triangles when internals don't matter.
- **Core tree facts `[IMG]`:** *beside a stream* = `(PHRASE (beside) (PHRASE (a) (stream)))` — `a` groups with `stream` (Ch1 [25b]).
- **Tests introduced:** omission, replacement by a single word, wh-question, movement, sense. (+ pronoun test used for NP later.)
- **Traps:** a sequence can be a constituent in one sentence but not another (*old Sam*, [30]); a stream **cannot** be directly attached to both *beside* and *that had dried up* (an element belongs directly to one phrase only).
- **Lesson units:** (1) What is structure? (bicycle/wheel/spoke) (2) Hierarchy & immediate constituents (3) Why sentences aren't strings of words (4) Constituency tests (5) Phrase vs. constituent (6) Node/dominate vocabulary (7) Structural ambiguity.
- **Gradable exercises:** Ex1 (dominance Y/N), Ex2 (immediate constituents), Ex3 (build trees: *their rather dubious jokes*, *men from the Ministry*), Ex4 (constituent Y/N), Ex6 (three analyses of *Old Sam sunbathed beside a stream*; **Ch2 adopts (a)**: `[Old Sam] [sunbathed beside a stream]`), Further Ex2/3.

### Ch2 — Functions (V2)
- **Vocabulary:** subject, predicate, sister, mother, daughter, head, modifier, complement, dependency (one-way vs two-way).
- **Rules `[IMG]`:** `S → NP VP`. Subject = **the NP immediately dominated by S**; predicate = **the VP immediately dominated by S**. Triangles for NP and VP. `PHRASE-x` still used inside.
- **Dependency facts:** subject~predicate = two-way, subject first. Modifier~head = one-way (modifier optional; may precede or follow head). Head~complement = two-way (complement obligatory; head generally first). Every phrase has exactly one head; the head's category = the phrase's category.
- **Test:** yes/no question — the phrase that moves is the subject (insert `do` if no auxiliary; expletive *it/there* still count as subjects).
- **Trap:** [16] *As a matter of fact, …* can't be split into just NP+VP (S-adverbial, Ch5).
- **Key tree `[TXT]` (unlabelled):** `(PHRASE-a their (PHRASE-b (PHRASE-c rather dubious) jokes))` — *rather* modifies *dubious*, not *jokes*; incorrect alternatives [38], [39] are used for teaching.
- **Lesson units:** (1) Subject & predicate (2) The question movement test (3) NP vs VP identification by combining phrases (4) Sisters/mothers/daughters (5) Head, modifier, complement (6) Reading modification structure from meaning (7) Ambiguity (*more exciting ideas*, *the old Romanian history teacher*).
- **Gradable:** Ex1 (subject/predicate), Ex2 (category), Ex3–5 (trees; ambiguity — **multiple accepted trees**).

### Ch3 — Categories (V3)
- **Vocabulary:** lexical vs phrasal category, noun (proper/common, count/mass), pronoun, adjective (gradable/non-gradable), degree adverb, general adverb, preposition, head~complement in PP, co-ordination.
- **Rules `[IMG, low-res]`:**
  - `(NP (name Max))`; `(NP (pronoun they))` — one-word phrases are still full NPs.
  - `(PP (P beside) (NP△ a stream))`; one-word PP: `(PP (P there))`.
  - AP: `(AP (DEG very) (A energetic))`; AdvP: `(AdvP (DEG more) (Adv obviously))`; *more obviously artificial* = `(AP (AdvP (DEG more) (Adv obviously)) (A artificial))` `[TXT]`.
  - **Internal NP structure stays unlabelled:** `(NP their (PHRASE-b (PHRASE-c extremely subtle) (N tactics)))` — top node `NP`, head `N`, middle nodes `PHRASE-x`. **No DET/NOM yet.**
  - **Co-ordination:** mother and both conjuncts share one category; the co-ordinator is a plain word: `(NP (NP (name Max)) and (NP (name Adrian)))`; lexical: `(PP (P (P up) and (P down)) (NP△ the staircase))`; phrasal: `(PP (PP (P in) (NP△ …)) and (PP (P under) (NP△ …)))`. Shared modifier: `(AP (DEG too) (A (A hot) and (A stuffy)))` vs `(AP (AP (A stuffy)) and (AP (DEG too) (A hot)))`.
- **Tests:** replacement by pronoun (full NP, not N); **co-ordination test** for both constituency and category; head determines phrase number/gender.
- **Trap:** a pronoun replaces a full NP, never a bare N (*\*the they*).
- **Lesson units:** (1) Categories from distribution (2) Nouns & sub-types (3) Pronouns (4) Lexical vs phrasal; head determines category (5) One-word phrases (6) Adjectives, degree & general adverbs (7) AP/AdvP (8) Prepositions & PP (9) Co-ordination as a test.
- **Gradable:** Ex1 (identify categories), Ex2 (NPs, heads, functions), Ex3 (draw trees, triangles only where info missing), Ex4 (stacked DEG: `so very touchy` has an inner AP), Further Ex2–3 (co-ordination).

### Ch4 — The basic VP (V4)
- **Vocabulary:** lexical vs auxiliary verb, sub-categorisation, the six verb types, direct/indirect object, subject-/object-predicative, prepositional complement, government/case.
- **Rules `[TXT]` + `[IMG]` via Ch5 trees:** complement = **sister of V inside VP**. Feature on V decides the complement's function:

| Feature | Frame | Functions |
|---|---|---|
| `[intrans]` | V | none |
| `[trans]` | V NP | dO |
| `[ditrans]` | V NP NP *or* V NP PP(to/for) | iO + dO (first NP is iO; in the PP version the PP is iO) |
| `[intens]` | V AP/NP/PP | sP |
| `[complex]` | V NP AP/NP/PP | dO + oP |
| `[prep]` | V PP | PC |

- An `[intrans]` verb alone is a full VP: `(VP (V[intrans] sighed))`.
- **Traps:** NP complement of `[trans]` = dO vs. NP complement of `[intens]` = sP (sP attributes a property to the subject; dO names a separate individual). A PP after a ditransitive is the iO only if it corresponds to the NP indirect object (to/for + animate). *Max found Bill an amusing companion* is ambiguous: `[ditrans]` vs `[complex]`.
- **Tests:** omission (complement obligatory), pronoun case (objective after V/P), paraphrase NP+NP ↔ NP+PP.
- **Lesson units:** (1) Lexical vs auxiliary (2) Word class ambiguity (*open, content, export*) (3) Complement vs optional modifier (4) Transitive (5) Intransitive (6) Ditransitive (7) Intensive & predicatives (8) Complex transitive (9) Prepositional verbs (10) Summary decision table.
- **Gradable:** Ex1 (functions + sub-category), Ex2 (PP in ditransitive?), Ex3 (construct), Ex4 (draw with triangles — all six patterns), Further Ex1–3.

### Ch5 — Adverbials and other matters (V5)
- **Vocabulary:** adjunct adverbial (VP-adverbial), sentence adverbial (disjunct/conjunct), pro-form (*do so*), phrasal verb, particle, ellipsis, grammaticality vs acceptability.
- **Core rule `[IMG]`:** *Complements of V are sisters of V; adjunct adverbials are sisters of VP.* This creates **two levels of VP**:
  `(S (NP△ Max) (VP (VP (V[trans] spotted) (NP△ those wildcats)) (PP△ in the spring)))`.
- Repeated adjuncts stack: each adds another `VP → VP + adjunct`.
- **S-adverbials `[IMG]`:** `(S (S (NP△ Buster) (VP△ admitted everything)) (AdvP△ frankly))`; initial: `(S (PP△ in short) (S△ you're fired))`.
- **Phrasal verbs `[IMG]`:** `(VP (V[trans,phrasal] called) (NP△ the boss) (Prt up))`; with unsplit particle the V can be a triangle: `(V[trans,phrasal]△ called up)`.
- **Tests:** *do so* replaces only a VP (shows VP levels; *\*Max put his car… and Max did so* fails because *put his car* is not a VP); particle movement distinguishes phrasal verb+NP from prep verb+PP; adverbial mobility.
- **Book's own simplifications (do not over-generalise):** Adverbials can appear in many positions that don't fit "sister of VP". The book says it will **only** represent adjuncts as sisters of a VP within a higher VP and S-adverbials as sisters of S within S, and tells you not to represent "displaced" adverbials (pp.92–93, 100–101). For two adjuncts (*hardly slept last night*), the **following** adjunct is higher (*last night* modifies *hardly slept*; Disc.3).
- **Ellipsis:** an obligatory complement can be understood from context; mark with `E` (e.g. ellipted iO). Don't re-sub-categorise the verb because of ellipsis unless the sense truly differs (*play*).
- **Lesson units:** (1) Adjuncts vs complements (2) Two VP levels (3) *do so* test (4) Mobility of adverbials (+ the book's simplification) (5) Phrasal verbs & particle test (6) Ellipsis (7) S-adverbials.
- **Gradable:** Ex1 (functions incl. `aA`, `sA`), Ex2 (trees), Ex3 (ellipsis vs sub-category), Ex4 (*appear*), Ex5 (*do so*).

### Ch6 — Auxiliary VPs (V6)
- **Vocabulary:** finite/non-finite, tense (only present and past), agreement, modal, perfect, progressive, passive, `do`-support, fronting, gap.
- **Fixed order `[TXT]`:** `MOD < PERF < PROG < PASS < lexical V`. Only the first verb is tensed; each verb's form is set by the verb before it.
- **Core rule `[IMG]`:** **an auxiliary is the head of its own VP and takes a VP complement.**
  `(S (NP△ you) (VP (MOD[past] should) (VP (PERF have) (VP (V[trans] written) (NP△ an essay)))))`.
  `(S (NP△ Monsieur Blanc) (VP (PROG[pres] is) (VP (V[trans] studying) (NP△ the menu))))`.
  *Do not* confuse with Ch5: sister-of-VP-and-daughter-of-VP marks an adverbial **unless** the sister is an auxiliary. Verbs never function as adverbials.
- **Tense feature** goes on the first verb node only: `[pres]`/`[past]`; stack with sub-cat features (`V[trans,past]`).
- **Adverbials with auxiliaries (book's assumptions):** (1) an adverbial that precedes a verb modifies the following VP; (2) sentence-final adverbials modify the **lexical** VP; (exception) certain time adverbials modify the higher PROG VP (*were going to India next week last week*).
- **Passive `[IMG]`:** object → subject, leaving a gap `•` in the object position; agent *by*-phrase = adjunct on the lexical VP:
  `(S (NP△ Max) (VP (PASS[past] was) (VP (VP (V[trans] fired) (NP •)) (PP△ by the boss))))`.
  The `[trans]` feature stays on the verb even though the object slot is a gap. `oP` stays `oP` in a passive of a `[complex]` verb. With a ditransitive, the **first** object becomes the subject.
- **Negation `[IMG]`:** attach *not/n't* to the tensed auxiliary node (triangle): `(MOD[past]△ would not)`. With no auxiliary, supply `do`: `(TENSE[past]△ did not)` over a bare-stem V.
- **Questions `[IMG]`:** the tensed auxiliary fronts to **`C`, sister of S and daughter of `S′`**, leaving a gap:
  `(S′ (C does) (S (NP△ Byron) (VP (TENSE[pres] •) (VP (V[intrans] dance)))))`.
  `have` and `be` can behave like auxiliaries even as lexical verbs (`be` always does).
- **Lesson units:** (1) Finite vs non-finite; tense (2) Lexical vs auxiliary (3) MOD (4) PERF (5) PROG (6) PASS (7) Auxiliary order (8) Where auxiliaries sit in VP (9) Adverbials and auxiliaries (10) Passive & gaps (11) Negation & `do` (12) Question fronting & `S′`/`C`.
- **Gradable:** Ex1, Ex3 (trees with triangles for NP/AP/PP/AdvP but **not VP**), Further Ex2 (classify *be*), Ex3.

### Ch7 — The structure of NPs (V7)
- **Rebuilt rule `[IMG]`:** every NP except pronoun-only and name-only NPs **branches into `DET` + `NOM`**.
  `(NP (DET (ART the)) (NOM (N clowns)))`, `(NP (DET (ART the)) (NOM (AP (A sad)) (N clowns)))`.
  Pronoun/name NPs stay non-branching: `(NP (pronoun they))`, `(NP (name Daisy))`.
- **DET fillers:** `ART` (the, a), `DEM`, `Q` (some, any, no, each, every, either, neither), `POSS` (my…, John's). A word counts as DET only if it can't co-occur with an article. **Empty DET** is required for bare plurals and mass nouns (*essays*, *smoke*) — `(NP (DET ∅) (NOM (N essays)))`.
- **Possessive** `'s`: a full NP + `-s` can fill DET (`POSS`); recursive (*Hieronimo's brother's behaviour*). Exact subtree shape `[TXT — transcribe from p.144]`.
- **PRE-DET** (all, both, half, double…): sister of an NP **inside** an NP: `(NP (PRE-DET all) (NP (DET (ART the)) (NOM (N men))))` `[TXT]`.
- **NOM is recursive; one NOM per modifier `[IMG]`:**
  `(NP (DET (ART a)) (NOM (AP (A new)) (NOM (AP (A red)) (N car))))`.
- **Pre-modifiers in NOM:** AP, quantifying adjectives (*many, few, little, much*; numerals), participle phrases (`PartP`), and noun modifiers. A noun modifier is **not phrasal**: compound nouns are dominated by `N` (*roof maintenance*), and always sit last.
- **Post-modifiers:** PP and some AP, as sisters of N/NOM inside NOM. Order of `NOM` nesting is decided **by meaning** (see two patterns A/B below).
- **Pro-form test:** *one(s)* = pro-**NOM** (never N alone in the base analysis).
- **Friendly Head Principle:** a modifier whose own head wants to be near the head noun appears post-nominally if it has a complement (*the chef responsible for the sauces*).
- **Pronoun modification:** indefinite pronouns (*something outrageous*) = coalesced DET+N; *some of the animals* uses an **elliptical head** analysis (DET/PRE-DET stays a determiner, the N is ellipted).
- **Appendix refinement (optional; see D1) `[IMG via Ch9]`:** a modifier that is a **sister of NOM** (adjunct) always needs an extra, possibly non-branching, NOM above N: `(NOM (NOM (N clowns)))` under `sad`. **Complements** are sisters of **N** and don't trigger the extra NOM. Parallel: sister-of-N = complement, sister-of-NOM = adjunct (cf. sister-of-V vs sister-of-VP).
- **Lesson units:** (1) Non-branching NPs (2) DET + NOM (3) Determiners, empty DET (4) Possessives (5) Pre-determiners (6) Pre-modifiers (AP, QA, PartP, N) (7) Recursive NOM (8) Post-modifiers PP/AP (9) Meaning decides NOM nesting (10) Pro-form *one* (11) Pronouns with modifiers (12) Appendix.
- **Gradable:** all trees "complete, no triangles"; Ex (c) is ambiguous (two trees); Ex (f) has co-ordination (state its level: N, NOM or NP); Further Ex2 Sets I–III; Ex2 revision of simple sentences.

### Ch8 — Sentences within sentences (V8)
- **Vocabulary:** recursion, complex vs compound sentence, subordinate/superordinate, main clause, ACA (abbreviated clausal analysis), complementiser, extraposition, expletive *it*, that-clause, whether-clause, subordinating conjunction.
- **S′ rule `[IMG]`:** from now on **every subordinate clause is `S′ → C S`**: `(S′ (C that) (S△ he was in command))`. An absent complementiser is drawn as elided: `(C <that>)`. (Ch8 [47] prints it as "(that)".)
- **Clause functions and their tree positions `[IMG]`:**
  - **Subject / direct object clause:** the `S′` is dominated by an **`NP`** (replaceable by *it*; becomes subject in passives).
  - **Extraposed subject:** `S′` is a daughter of the main `S`: `(S (NP it) (VP△ disconcerted her) (S′△ that the king …))`. Verbs like *seem, appear, happen* are `[intrans]` here.
  - **Subject-predicative clause:** `S′` directly (no NP): only after copula *be*.
  - **Complement of A:** sister of A in AP: `(AP (A happy) (S′ (C <that>) (S△ …)))`.
  - **Complement of N:** sister of N in NOM: `(NP (DET (ART the)) (NOM (N fact) (S′△ that you received…)))`.
  - **Complement of P (only whether-clauses):** `(PP (P about) (S′ (C whether) (S△ …)))`. *After, until, before, since* are **prepositions** taking S directly: `(PP (P since) (S△ you came))` — **no S′**.
  - **Adverbial clause:** subordinating conjunction sits in `C`; the `S′` is a sister of VP (or S for S-adverbials): `(VP (VP (MOD[pres] will) (VP (V[intens] be) (AP△ rather dull))) (S′ (C if) (S …)))`. Phrasal complementisers (*as if, so that, as soon as*) are triangles in C.
  - *It is certain that…* = extraposed subject (AP is just *certain*); *William is certain that…* = AP with clausal complement.
- **ACA notation:** triangles for clauses numbered `S1` (main), `S2…`; all complementisers go **inside** the triangle. Labelled-bracket twin: `S1[… S2[…]]`.
- **Lesson units:** (1) Complex vs compound (2) Main/subordinate; counting clauses by lexical verbs (3) ACAs (4) `C`/`S′`: *that*, *whether* (5) Clausal subjects & extraposition (6) Clausal objects (7) Clause + AP (8) Clause + N (9) Clause + P (10) Adverbial clauses (11) Choosing the right S′ position.
- **Gradable:** Ex1–2 (ACAs with functions), in-text trees.

### Ch9 — Wh-clauses (V9)
- **New layer `[IMG]`:** `S″ → C2 S′`, `S′ → C1 S`.
  - **C1:** filled by *that, whether*, subordinating conjunctions, and (main clauses) fronted tensed auxiliaries.
  - **C2:** filled by fronted **wh-phrases** (whole phrase, e.g. *which icon*), in main **and** subordinate wh-clauses.
  - Fronting leaves a **gap of the right category** where the phrase came from.
  `(S″ (C2 what) (S′ (C1 is) (S (NP△ Vince) (VP (VP (PROG[pres] •) (VP (V[trans] taking) (NP •))) (PP△ to Athens)))))`.
- **Book's assumptions (use them as stated):** all clause-initial wh-expressions are in C2; **auxiliary-fronting to C1 happens in all non-echo main questions**, even with a wh-subject (no change in word order). The category of the wh-phrase in C2 **need not be labelled**, but the category of the **gap** must be. In subordinate wh-clauses C1 is empty (no aux-fronting).
- **Echo questions** have no fronting (`Vince is taking what to Athens?`).
- **Relative clauses `[IMG]`:** wh-clauses that are modifiers.
  - **Restrictive:** sister of NOM inside a higher NOM: `(NP (DET (ART the)) (NOM (NOM (N conclusion)) (S″△ which Gomez disputes •)))`.
  - **Non-restrictive:** sister of NP inside a higher NP: `(NP (NP (DET△ the) (NOM (N dogs))) (S″△ which have rabies))`.
  - **Noun-complement clause** is different: sister of **N** (V8 rule), has no gap, complementiser *that* in C1.
  - **Decision adopted by the book for *that* in relatives:** *that* is a relative pronoun in **C2** (alternative: C1 with an ellipted wh-phrase). Relative clauses always contain a gap; noun-complement clauses never do.
- **Tests:** *one* + complement clause is bad (`*the one that Mars is inhabited`), *one* + relative clause is fine (`the one which Gomez disputes`).
- **Lesson units:** (1) Wh-words as replacements (2) Wh-questions: two frontings (3) The second C position (4) Gaps by category (5) Echo questions (6) Wh-subject convention (7) Subordinate wh-interrogatives (8) Relative clauses (9) Restrictive vs non-restrictive (10) *that* in relatives (11) Complement clause vs relative clause.
- **Gradable:** Ex1 (question formation), Ex2 (embedding relatives), Ex3 (restrictive/non-restrictive + one tree), Ex4 (ACAs with clause types), in-text trees.

### Ch10 — Non-finite clauses (V10)
- **Vocabulary:** finite vs non-finite, covert NP, control, free vs controlled, index/co-indexing, bare infinitive, *to*-infinitive, passive participle, -ing participle, Type I / Type II verbs.
- **Features and nodes `[IMG]`:**
  - Non-finite V carries `[-tense]`: `(V[trans,-tense] darn …)`.
  - **`to` is a `[-tense]` auxiliary** (replaces MOD): `(VP ([-tense] to) (VP (V[trans] taste) (NP△ the wine)))`. MOD never appears in non-finite clauses; PERF/PROG/PASS can: `(VP ([-tense] to) (VP (PERF have) (VP (PASS been) (VP (V[trans] beaten) (NP •_1)))))`.
  - -ing participles are **not** "progressive"; attach `[-tense]` to the -ing V (lexical or auxiliary).
- **Covert subjects:** draw `(NP •_i)`; co-index with the controller (`NP_i`) in the higher clause. A covert NP is **free** (general reference) or **controlled**.
- **Complementisers in non-finite clauses:** C1 = *for* (only *to*-infinitives with overt subject) or *whether* (covert subject, controlled or free); C2 = fronted wh-phrase. Subject can't be fronted to C2. Non-finite relatives have a **covert wh in C2**, restrictive only (sister of NOM), no bare infinitives.
- **Functions** (re-use V8 positions): subject (NP over S′), extraposed subject (not with overt-subject -ing), complement of A (two adjective types: *reluctant* [subject controls subject] vs *impossible* [subject controls object]), complement of P (-ing only), adverbial (incl. with subordinating conjunction), complement of N (covert subject controlled by the possessive determiner), modifier in NP.
- **Complement of V — the big change `[IMG]`:** the six-way features are **not** used when the complement is a non-finite clause, and the clause is **not** put under an NP. Instead:
  - **Type I** (*believe, expect, want, know…*): one clause complement with an **overt** subject: `(VP (V(I)[past] expected) (S′ (C1) (S (NP△ the bear) (VP ([-tense] to) (VP (V[intrans] dance))))))`.
  - **Type II** (*persuade, ask, force, promise…*): direct-object NP **plus** a clause with a **covert, controlled** subject: `(VP (V(II)[past] persuaded) (NP_1△ the bear) (S′ (C1) (S (NP •_1) (VP ([-tense] to) (VP …)))))`. *Promise* is the exception: the subject controls.
  - Tests: *there* as subject only after Type I; the NP after Type II can't be expletive *there* and must be agentive.
- **Lesson units:** (1) Finite vs non-finite (2) Covert subjects & control (3) Four non-finite forms (4) *to* as `[-tense]` (5) Participle clauses (6) `for`/`whether` (7) Non-finite wh-clauses and relatives (8) Functions of non-finite clauses (9) Verb complementation Types I/II (10) Testing Type I vs II.
- **Gradable:** Ex1 (covert constituents: controlled or free, controller), Ex2 (ambiguity of *impossible to move*), in-text trees.

### Ch11 — Languages, sentences and grammars
No tree conventions. See §10.

---

## 5. Cumulative tree-shape rules (derived; final form V10)

Derived from the book's descriptions, not stated by the book as a rule list.

```
S      → (S-adverbial) NP VP                    S-adverbial = sister of S inside S
S′     → C1 S                                    (every subordinate clause; main clauses only for fronted aux)
S″     → C2 S′                                   (wh-clauses)
VP     → AUX VP                                  AUX ∈ {MOD, PERF, PROG, PASS, TENSE, [-tense] to}
VP     → V (complements per V's features)        complements are sisters of V
VP     → VP adjunct | adjunct VP                 adjunct adverbial: AdvP / PP / NP / S′
NP     → pronoun | name | DET NOM | NP PP-less…   (see below)
NP     → PRE-DET NP
NP     → NP S″                                   non-restrictive relative
NP     → DET NOM
NOM    → N | AP NOM | NOM PP | N complement | NOM S″
DET    → ART | DEM | Q | POSS | ∅
AP     → (DEG|AdvP) A (complement)
AdvP   → (DEG) Adv
PP     → P (NP | S′[whether] | S)                 S directly for after/until/before/since
X      → X and X                                  co-ordination: mother and conjuncts have the same category
```
Complement slots on V by feature: see §4 Ch4 table. Clause complements (Ch10): `V(I) S′` / `V(II) NP S′`.

---

## 6. Functions are derived from positions (implement as code)

| Function | Position in the tree | Chapter |
|---|---|---|
| Subject | NP immediately dominated by S | 2 |
| Predicate | VP immediately dominated by S | 2 |
| Head | the daughter whose category matches the phrase | 2 |
| Complement of V | sister of V; *which* function (dO/iO/sP/oP/PC) comes from V's feature | 4 |
| Adjunct adverbial (aA) | sister of VP, daughter of VP | 5 |
| S-adverbial (sA) | sister of S, daughter of S | 5 |
| Auxiliary | head of its VP; its sister VP is its complement | 6 |
| Determiner | `DET`, sister of NOM | 7 |
| Pre-determiner | sister of NP inside NP | 7 |
| Modifier in NP | sister of NOM inside NOM (adjunct) | 7, Appx |
| Complement in NP | sister of N inside NOM | 7 Appx, 8 |
| Restrictive relative clause | sister of NOM inside NOM | 9 |
| Non-restrictive relative clause | sister of NP inside NP | 9 |
| Complement of A / P | sister of A / P | 8 |
| Clausal subject / object | `S′` under an `NP` (V8/V9 only; not Type I/II) | 8 |
| Extraposed subject | `S′` daughter of the main S, expletive *it* subject | 8 |
| Subject-predicative clause | `S′` directly under VP | 8 |
| Fronted wh-phrase | C2; function = function of its gap | 9 |

---

## 7. Test inventory (for "why is this a constituent / category?" explanations)

| Test | Shows | Chapter |
|---|---|---|
| Omission | optional constituent | 1 |
| Replacement by single word (it, there, someone…) | constituent | 1 |
| Wh-question / answer | constituent (and its kind) | 1 |
| Movement as a unit | constituent | 1 |
| Sense test | constituent (weak; fallible) | 1 |
| Yes/no question movement | subject | 2 |
| Pronoun replacement | full NP (not just N) | 3 |
| Co-ordination | constituency **and** category | 3 |
| *do so* | VP (not V) | 5 |
| Particle movement | phrasal V + NP vs V + PP | 5 |
| Aux fronting / *not* attachment | auxiliary vs lexical verb | 6 |
| By-phrase / passive | transitive vs intensive (objects only) | 6 |
| Pro-NOM *one* | NOM (adjunct vs complement) | 7, 9 |
| Replacement by *it* | clause under NP | 8 |
| Gap test | relative clause vs noun-complement clause | 9 |
| Expletive *there* / agentive NP | Type I vs Type II verb | 10 |

---

## 8. Grading profiles (what `compareTrees` must check, per chapter)

| Version | Compare | Triangles | Notes |
|---|---|---|---|
| V1 | spans only | span of triangle = span of its words | labels ignored (`Sentence`, `PHRASE-x`) |
| V2 | spans + `S/NP/VP` labels | allowed for NP, VP | |
| V3 | spans + categories | allowed where exercise says | internal NP nodes: label-agnostic (lettered) |
| V4 | + features on V | allowed for NP/AP/PP/AdvP | feature must match sub-category |
| V5 | + VP level structure | | `aA` = sister of VP is **structural** — check it |
| V6 | + auxiliary nodes, tense features, gaps | triangles on NP/AP/AdvP/PP (not VP) | gap position must match; movement arrows ignored |
| V7 | + `DET/NOM/N/PRE-DET` | **no triangles** in NP exercises | NOM count = modifier count; allow appendix extra-NOM if D1 says so |
| V8 | + `S′`, `C`, NP-over-clause rules | clause triangles | check C position and that PP-S has no `S′` |
| V9 | + `S″`, `C1/C2`, gaps by category | | wh-phrase category in C2 optional |
| V10 | + indices/control, `[-tense]`, `V(I)/V(II)` | | indices must co-refer correctly |

General: **leaf text must match**; layout is irrelevant; compare as unordered nothing — **order matters** (left-to-right).

---

## 9. Judgement calls, accepted alternatives, and book simplifications

Store these as `accepted_alternatives` or `book_simplification` fields.

| # | Where | Issue | Policy |
|---|---|---|---|
| J1 | Ch1 Ex6 | Three analyses of *Old Sam sunbathed beside a stream* | All three are valid in Ch1; **from Ch2 on, (a) `[Old Sam][sunbathed beside a stream]` is the one used.** |
| J2 | Ch2 Ex3/5 | Ambiguous phrases (*more exciting ideas*; *the old Romanian history teacher*) | Accept the set of analyses the book lists; each tied to a meaning. |
| J3 | Ch3 | `a stream` etc. | Co-ordination of NPs inside NPs: conjunct category = mother category. |
| J4 | Ch5 | Displaced adverbials | Book **does not represent** them (pp.92–93). Only represent adjuncts as `VP → VP + adjunct`. Mark the sentence `book_simplification: true`. |
| J5 | Ch5 | S-adverbial placement | Same simplification (pp.100–101). |
| J6 | Ch6 | Adverbials near auxiliaries | Use the book's Assumptions 1–2 and the time-adverbial exception. |
| J7 | Ch7 | `[A]` vs `[B]` pre-/post-modifier nesting | Decided **by meaning** per example; some examples allow either (book says "either analysis is possible"). Provide both and the meaning-based hint. |
| J8 | Ch7 further Ex2 Set II(a) | *coffee and oranges* | Three analyses possible; accept all, prefer the simplest. |
| J9 | Ch8 | Clausal objects under NP | Book's choice (NP over S′); Ch10 reverses this for Type I/II. |
| J10 | Ch9 | *that* in relatives | Adopted: C2. Alternative (C1 + ellipted wh) acknowledged but **not** to be graded as correct. |
| J11 | Ch10 | Type I vs Type II | The book says analyses are contested; use the Type I/II decisions the book lists (Disc.7). |
| J12 | Ch7 | Pronoun-like determiners (*some of the animals*) | Elliptical-head analysis is the book's chosen one. |

### Open decisions for the project owner

| ID | Decision | Recommendation |
|---|---|---|
| **D1** | Adopt the Ch7 **Appendix** (extra non-branching NOM) as the default in V7+? | **Yes from Ch9/final profile** — Ch8 Disc.6 and Ch9 figures [39], [59] already draw it. Offer a flag `appendix_nom: true/false` so Ch7 lessons can stay "core". |
| D2 | S′ naming | Store `S-bar`, display S′ (§2.3). |
| D3 | Do trees in the app show functions? | No — compute and show them as an overlay (§6). |
| D4 | Do you keep the old Penn-style lessons? | Keep them under "Parser view"; book lessons are separate. |

---

## 10. Chapter 11 and the "why" lesson

Ch11 has no phrase markers. Use it for a **capstone, text-only unit** that connects everything: a language as a set of sentences; why a finite list (*Justen*) can't describe a natural language; *and* and relative clauses give infinitely many sentences; grammar as a finite set of rules giving a general definition of "sentence"; phrase markers **describe** sentences but don't by themselves **predict or explain** ungrammaticality (the ill-formed *\*Stream a beside sunbathed Sam* can still be given a tree). Use it as the closing lesson of the course, after the tree chapters. No gradable trees.

---

## 11. Map to SynTutor's existing (benepar / Penn Treebank) engine

Advisory only. Keep the parser for the free-form "Analyze any sentence" mode and label it the **parser's view**.

| Book (V10) | Parser (PTB-style) | Consequence |
|---|---|---|
| `AP`, `AdvP` | `ADJP`, `ADVP` | rename if converting |
| `S′` / `S″` / `C1` / `C2` | `SBAR` / `SBARQ` + `WH*` | no clean 1-to-1 |
| `NP → DET NOM` (+ recursive NOM) | flat `NP` (your NP lesson says modifiers are flat sisters) | **Not reproducible automatically.** NP lessons must use book-authored trees |
| Double `VP` for adjuncts | adjuncts flat inside VP | not reproducible |
| Auxiliary as head with VP complement | nested VP for modals, but flat for others | partial |
| `MOD PERF PROG PASS TENSE` | `MD VBZ VBP VBD …` | map by form, not by structure |
| gaps `•`, indices, `[-tense]`, features, `PartP`, `PRE-DET`, `NOM` | not produced | cannot be derived from benepar |

Conclusion: **lesson gold trees must be authored from the book**; the parser can only supply a rough starting tree to be corrected by hand.

---

## 12. Verification status

| Item | Status |
|---|---|
| Ch5 [12], [35], [39], [55a/b], [58] | `[IMG]` |
| Ch6 [52], [53b], [78], [86], [88], [91], [93] | `[IMG]` |
| Ch7 [1]–[4], [36]; Appx NOM (via Ch9 [39], [59]) | `[IMG]` |
| Ch8 [11a], [24], [36], [47], [54], [61], [67c], [71] | `[IMG]` |
| Ch9 [11a/b], [39], [59], [60] | `[IMG]` |
| Ch10 [6], [11], [12], [17], [37], [101b], [102b] | `[IMG]` (check the bottom node of [12]) |
| Ch3 [7], [14], [18], [19], [29], [30], [40], [41] | `[IMG]` at low resolution — confirm |
| Ch2 [33], [36] | `[TXT]` |
| Ch4 trees | `[TXT]` (shapes follow from rules; confirm on page images) |
| Ch7 possessive `'s`, `PartP`, compound `N`, pronoun modification, `PRE-DET` | `[TXT]` |
| **Ch1: all figures [2], [3a/b], [5], [25a-c], [34], [35], Ex1, Ex3, Ex6(a-c)** | `[IMG]` **done** — `book/ch01.trees.json`, checked by `book/validate_ch01.py` against the book's own Ex1/Ex2/Ex6 answers (all pass). Note: [35]'s top node is printed starred in the book. |
| Ch1 Further Ex2, Ex3 | No book answer; trees are fully fixed by the exercise wording → stored as `DERIVED_FROM_INSTRUCTIONS` |
| Chapters 2–10 figures, exercise answers and all "Discussion of exercises" trees | **Not yet transcribed — repeat the Ch1 page-image pass chapter by chapter, in book order.** |

---

## 13. Checklist before accepting any generated chapter file

- [ ] `convention_version` set and **only** that version's labels/features used (§1, §3).
- [ ] No functions drawn as nodes.
- [ ] Every tree's leaves equal its sentence's words, in order (gaps/elided aside).
- [ ] Every node except the root has exactly one mother.
- [ ] Triangles only where the book (or the exercise instruction) uses them; each has a label except the source-permitted unlabelled wh triangle under C2 (V9+).
- [ ] Ch5+: adjuncts are sisters of VP, complements are sisters of V.
- [ ] Ch6+: auxiliaries head a VP and take a VP complement; tense feature only on the first verb.
- [ ] Ch7+: NP is `DET NOM` unless pronoun/name; NOM count = modifier count.
- [ ] Ch8+: every subordinate clause is `S′ → C S` (except S directly under PP for *after/until/before/since*).
- [ ] Ch9+: wh-phrases in C2 with a correctly categorised gap.
- [ ] Ch10+: indices present on controlled gaps; no 6-way feature on V with clause complements; Type I/II used.
- [ ] Anything unsure marked `UNSURE`, not guessed.
- [ ] Book's own answers (exercise "Discussion" sections) pass the validator.
- [ ] No long quotations from the book.
- [ ] Every explanation/hint/feedback string has `source` (chapter, page, kind) and a `concept_id` from the glossary (§14). None is written from model knowledge.


---

## 14. Explanations (XAI) must come from the book

**Rule:** anything the app tells a learner about *why* an answer is right or wrong,
what a term means, or why a tree has its shape must be grounded in a reviewed
linguistic source. Use Burton-Roberts for phrase-marker shape, tree labels,
structural functions, and the chapter-specific method. Use reviewed Cambridge
records for broader grammatical categories, constructions, constraints, conditions,
and exceptions. The sources remain distinct; Cambridge does not override B-R tree
conventions. The AI is never an independent source of linguistic reasoning. The
same applies to free-form analysis: no explanation may be shown unless it maps to
a source record with a printed-page citation.

### 14.1 What counts as a valid source
| `kind` | Meaning | Example |
|---|---|---|
| `definition` | The book defines the term | node, dominates, constituent (Ch1 p.17) |
| `test` | The book presents a diagnostic | omission, replacement, wh-question, movement (Ch1 pp.11-14); *do so* (Ch5) |
| `worked_answer` | The book's own "Discussion of exercises" reasoning | Ch1 Ex4 (a)-(g), pp.21-22 |
| `principle` | A stated principle | an element belongs directly to one phrase only (Ch1 p.17) |
| `convention` | A drawing convention of that chapter | `S → NP VP`; auxiliary heads its own VP (Ch6) |
| `cambridge_concept` | A broader grammatical concept from an independently reviewed Cambridge record | Category/construction distinction with exact printed page and concept ID |
| `cambridge_constraint` | A grammatical constraint or variety-restricted condition from an independently reviewed Cambridge record | Condition, violation, relevant variety/register, exceptions, and exact printed page |

Anything else (the model's own grammar knowledge, Penn Treebank / Benepar
reasoning, unreviewed extracts, or unrelated textbooks) is **not** a valid source.
A Cambridge record is valid for its stated grammatical domain only after
independent review, printed-page verification, crosswalk review where relevant,
and approval for the intended use.

### 14.2 How explanations are produced
1. **Engine computes the facts** (which node dominates which words, which test applies, which function a position gives, per §6). Facts are code, not AI opinion.
2. **Fact → book template.** Each failure or success type maps to a stored template that paraphrases the book and cites it. Example: a sequence that is not a constituent → "No single node dominates all and only these words" (Ch1 p.17). Slots (words, node names) are filled by code.
3. **An LLM may only (a) fill slots or (b) rephrase a template for reading level, without adding claims.** A post-check rejects any output containing a claim not present in the template.
4. **No template → no explanation.** Show the result, then `NO_BOOK_BASIS` plus a pointer ("see Ch N, p. X"). Log it so a template can be written from the book later.

### 14.3 Chapter-aware explanations
- An explanation uses **the conventions of the chapter the learner is in** (`convention_version`). Do not explain a Ch3 NP with `NOM`.
- If a later chapter revises the analysis, append a short `superseded_by` note citing that chapter (e.g. "refined in Ch7"), not the revised rule itself.
- Where the book calls its own analysis a simplification (Ch5 pp.92-93, 100-101; §9 J4/J5), the explanation must say so.
- Where the book accepts more than one analysis (§9), the explanation names every accepted analysis and the meaning each goes with.

### 14.4 Storage format
```json
{
  "id": "ex-ch1-ex4c-why",
  "concept_id": "constituent",
  "text": "paraphrase written by us, one or two sentences",
  "source": {"chapter": 1, "page": 22, "kind": "worked_answer", "ref": "Ex4(c)"},
  "convention_version": "V1",
  "superseded_by": null,
  "status": "APPROVED | NEEDS_REVIEW"
}
```
Rules: `text` is our paraphrase (public repo; no passages, quotes of at most a few words); `source.page` is the **printed** page; `NEEDS_REVIEW` items never ship.

### 14.5 Starter template table (Chapter 1; extend per chapter)
| Engine fact | Template idea (paraphrase) | Source |
|---|---|---|
| No node dominates all and only the words | A word sequence counts as a constituent only if one node dominates exactly those words and no others. | Ch1 p.17 `definition` |
| Words sit under two different phrases | An element can belong directly to only one phrase at a time. | Ch1 p.17 `principle` |
| Flat tree for a sentence | A tree with every word directly under the sentence gives the sentence no structure beyond word order. | Ch1 pp.9-10 `principle` |
| Sequence replaceable by one word | Replacing a sequence by a single word without changing the overall structure is evidence it is a constituent. | Ch1 pp.12-13 `test` |
| Sequence can answer a wh-question | Answers to wh-questions are phrases. | Ch1 p.13 `test` |
| Sequence moved as a unit | Movement of a sequence as a unit indicates it is a phrase. | Ch1 p.14 `test` |
| Sequence omissible as a unit | Omitting a sequence and still having a good sentence indicates a phrase (not every phrase is omissible). | Ch1 pp.11-12 `test` |
| Word sequence is a constituent in one sentence, not another | A sequence that can be a constituent is a phrase, but need not be one in every sentence containing it. | Ch1 pp.15-16 `principle` |
| Ambiguous sentence | Different groupings of the words give different meanings; deciding the constituents is part of deciding the meaning. | Ch1 p.18 `worked_answer` |

### 14.6 Rule-matrix and parser mode
The 111 rules / 210 explanations in the existing engine are **not** book-sourced. Before they are shown: tag each with a book `concept_id` + page and rewrite the text from the book, or hide the explanation. Parser output is labelled "parser's view" and shows no explanation beyond the book-mapped ones.

### 14.7 Validator additions
- Fail the build if any explanation lacks `source.chapter`, `source.page`, `source.kind`, or a known `concept_id`.
- Fail if `source.page` is outside the chapter's printed page range (Ch1: 6-23).
- Fail if `text` shares a run of more than 12 consecutive words with the book (run against extracted chapter text).

## Source verification update — 8 November 2026

The supplied eleven chapters match the **third edition**, Pearson Education, copyright 2011, ISBN 9781408233740, printed pp.6–268. See `sources/burton_roberts/source_manifest_2026-11-08.json` and the scoped review receipt in `sources/burton_roberts/reviews/2026-11-08-conventions.json`. The older verification table above records the original transcription pass, not a claim that this review checked every image.

The approved canonical schema is now 1.1.0. It distinguishes zero-word empty DET (V7+), C1 (V9+) and E ellipsis (V5+) from movement gaps and overt terminals. Unlabelled C2 triangles are explicit, not guessed category labels. Existing 1.0.0 envelopes remain accepted for the original subset. The Chapter 9 p.213 PP alternative is text-licensed, not a second printed figure. Source anomalies and review states remain visible.
